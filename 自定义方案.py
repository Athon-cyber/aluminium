# -*- coding: utf-8 -*-
import os
import sys
import job
import xlwt
import xlrd
import math
import json
import time
import random
import pickle
import winsound
import numpy as np
from abaqus import *
from odbAccess import *
from caeModules import *
from abaqusConstants import *
from functools import cmp_to_key
from matplotlib.path import Path
from collections import defaultdict
from driverUtils import executeOnCaeStartup



# ==============================================================================
# 材料定义
# ==============================================================================
def Wdc():
    m.Material(name='bc')
    m.materials['bc'].Density(table=((2.8E-09,),))
    m.materials['bc'].Elastic(table=((70000.0, 0.3),))
    m.materials['bc'].Plastic(table=(
        (260.0, 0.0),   # 初始屈服应力（对应塑性应变为0）
        (310.0, 0.002), # 塑性应变0.2%时的应力
        (330.0, 0.005), # 塑性应变0.5%时的应力
        (350.0, 0.01),  # 塑性应变1%时的应力
        (370.0, 0.02),  # 塑性应变2%时的应力
        (385.0, 0.03),  # 塑性应变3%时的应力
        (400.0, 0.05),  # 塑性应变5%时的应力 (假设为抗拉强度附近)
        (390.0, 0.06),  # 假设下降段开始，应力略有下降
        (370.0, 0.08),  # 应力进一步下降
        (340.0, 0.10)   # 接近断裂，应力继续下降
    ))
    m.Material(name='GT')
    m.materials['GT'].Density(table=((7.85E-09,),))  # 7850 kg/m³
    m.materials['GT'].Elastic(table=((210000.0, 0.3),))  # 210GPa
    m.materials['GT'].Plastic(table=(
        (800.0, 0.0),  # 初始屈服强度800MPa
        (850.0, 0.001),  # 塑性应变0.1%时应力
        (900.0, 0.003),  # 塑性应变0.3%时应力
        (930.0, 0.005)  # 补充一点，体现小变形硬化
    ))


# ==============================================================================
# 自动创建基准面与分割面
# ==============================================================================
ALL_FACE_Point = []  # 所有面的API内参坐标
ALL_EDGE_Point = []  # 所有边的API内参坐标

def auto_create_datums_and_partition_faces(part, part_name, planes_definition, extrusion_depth=None):
    global ALL_FACE_Point, ALL_EDGE_Point
    # 收集当前所有面的坐标（通过集合去重）
    def update_face_coords():
        face_coords = set()
        for face in part.faces:
            face_coords.add(tuple(face.pointOn))  # 转为元组存入集合去重
        ALL_FACE_Point[:] = list(face_coords)
    # 收集当前所有边的坐标（通过集合去重）
    def update_edge_coords():
        edge_coords = set()
        for edge in part.edges:
            edge_coords.add(tuple(edge.pointOn))  # 转为元组存入集合去重
        ALL_EDGE_Point[:] = list(edge_coords)
    feature_set_name = 'Set-face-%s' % part_name
    created_datum_ids = []
    for principalPlane, offsets in planes_definition:
        # 如果偏移列表为空，则跳过该基准面创建
        if not offsets:
            continue
        # 仅当有偏移值时才创建基准面
        for offset in offsets:
            datum_plane = part.DatumPlaneByPrincipalPlane(principalPlane=principalPlane, offset=offset)
            created_datum_ids.append(datum_plane.id)
    # 过滤有效基准面ID
    valid_datum_ids = [did for did in created_datum_ids
                       if did in part.datums and part.datums[did].__class__.__name__ == 'DatumPlane']
    # 创建特征集合（无论是否切分，都需要初始集合）
    def create_feature_set():
        if feature_set_name in part.sets:
            del part.sets[feature_set_name]
        part.Set(faces=part.faces, name=feature_set_name)
    create_feature_set()
    # 初始收集坐标（无论是否切分，都需要初始坐标）
    update_face_coords()
    update_edge_coords()
    # 仅当有有效基准面时才执行切分（无基准面则不切分）
    if valid_datum_ids:
        for datum_id in valid_datum_ids:
            try:
                if feature_set_name not in part.sets:
                    raise ValueError("特征面集合 %s 不存在，无法继续切分" % feature_set_name)
                target_faces = part.sets[feature_set_name].faces
                if not target_faces:
                    continue
                current_datum_plane = part.datums[datum_id]
                part.PartitionFaceByDatumPlane(datumPlane=current_datum_plane, faces=target_faces)
                create_feature_set()
                update_face_coords()
                update_edge_coords()
            except Exception as e:
                continue
    else:
        print("零件 %s 无需要执行的切分操作（偏移列表为空）" % part_name)

# ==============================================================================
# 计算自定义参数
# ==============================================================================
## 网格大小
Me = 5.0
## 用于计算的CPU数量
Nc = 8
## job文件名
qqmtname = 'ququ720'
wyjzname = 'weiyi720'
## 柱子长度
BZC = 720
## 加载位移
displacement_value = -5

Tt = 2
Lo = -1000  # 用于模态位移基准值（750相关参数）

target_dir = r"C:\temp\3weiyi720720"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

os.chdir(target_dir)

odb_path = os.path.join(target_dir, "%s.odb" % qqmtname)

JZ = 1

output_file = "first.pkl"
source_model_name = "DQL"
new_model_name = "Static_Load_Model_Defect"

# ==============================================================================
# 建模初始化
# ==============================================================================
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
## 模型名
m = mdb.Model(name='DQL')
## 构件名
BZ = m.ConstrainedSketch(name='BZ-skech', sheetSize=3000.00)

BZ.Line(point1=(-15.00, -90.00), point2=(-25.00, -100.00))
BZ.Line(point1=(-60.00, -100.00), point2=(-25.00, -100.00))
BZ.Line(point1=(-60.00, -100.00), point2=(-60.00, -65.00))
BZ.Line(point1=(-40.00, -45.00), point2=(-60.00, -65.00))
BZ.Line(point1=(-40.00, -45.00), point2=(-40.00, 45.00))
BZ.Line(point1=(-60.00, 65.00), point2=(-40.00, 45.00))
BZ.Line(point1=(-60.00, 65.00), point2=(-60.00, 100.00))
BZ.Line(point1=(-25.00, 100.00), point2=(-60.00, 100.00))
BZ.Line(point1=(-25.00, 100.00), point2=(-15.00, 90.00))
BZ.Line(point1=(15.00, 90.00), point2=(-15.00, 90.00))
BZ.Line(point1=(15.00, 90.00), point2=(25.00, 100.00))
BZ.Line(point1=(60.00, 100.00), point2=(25.00, 100.00))
BZ.Line(point1=(60.00, 100.00), point2=(60.00, 65.00))
BZ.Line(point1=(40.00, 45.00), point2=(60.00, 65.00))
BZ.Line(point1=(40.00, 45.00), point2=(40.00, -45.00))
BZ.Line(point1=(60.00, -65.00), point2=(40.00, -45.00))
BZ.Line(point1=(60.00, -65.00), point2=(60.00, -100.00))
BZ.Line(point1=(25.00, -100.00), point2=(60.00, -100.00))
BZ.Line(point1=(25.00, -100.00), point2=(15.00, -90.00))
BZ.Line(point1=(-15.00, -90.00), point2=(15.00, -90.00))
BZ.Line(point1=(15.00, 90.00), point2=(40.00, 45.00))
BZ.Line(point1=(40.00, -45.00), point2=(15.00, -90.00))
BZ.Line(point1=(-15.00, -90.00), point2=(-40.00, -45.00))
BZ.Line(point1=(-40.00, 45.00), point2=(-15.00, 90.00))

## 几何建模
p = m.Part(name='BIANZHU', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseShellExtrude(sketch=BZ, depth=BZC)
# 支持空偏移列表（不执行切分）
daogui_planes = [(XYPLANE, []), (XZPLANE, []), (YZPLANE, [])]
auto_create_datums_and_partition_faces(part=p, part_name='BIANZHU', planes_definition=daogui_planes, extrusion_depth=1000)

## 装配
a = m.rootAssembly
part0101 = a.Instance(name='ZHU', part=m.parts['BIANZHU'], dependent=ON)
part0101.translate(vector=(0, 0.0, 0))

# ==============================================================================
# 材料赋予
# ==============================================================================
Wdc()

m.HomogeneousShellSection(name='Section-1', preIntegrate=OFF, material='bc', thicknessType=UNIFORM, thickness=Tt, thicknessField='', nodalThicknessField='', idealization=NO_IDEALIZATION,
                          poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)
p = m.parts['BIANZHU']
region = p.sets['Set-face-BIANZHU']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# ==============================================================================
# 参考点与约束边
# ==============================================================================
p = m.parts['BIANZHU']
z720_points = [point for point in ALL_EDGE_Point if point[0][2] == 0.0]
if z720_points:
    edges_720 = p.edges.findAt(*z720_points)
    p.Set(edges=edges_720, name='Set-deges1')
else:
    print("未找到Z坐标为720.0的边")

z0_points = [point for point in ALL_EDGE_Point if point[0][2] == BZC]
if z0_points:
    edges_0 = p.edges.findAt(*z0_points)
    p.Set(edges=edges_0, name='Set-deges2')
else:
    print("未找到Z坐标为0.0的边")



r4 = a.ReferencePoint(point=(0, 0, -BZC * 0.07))
r5 = a.ReferencePoint(point=(0, 0,  BZC * 1.07))

myID4 = r4.id
myID5 = r5.id

r1 = a.referencePoints
refPoints1=(r1[myID4], )
region1=a.Set(referencePoints=refPoints1, name='m_Set-1')
a = m.rootAssembly
region2=a.instances['ZHU'].sets['Set-deges1']
m.Coupling(name='Constraint-1', controlPoint=region1,
    surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
    localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

r1 = a.referencePoints
refPoints1=(r1[myID5], )
region1=a.Set(referencePoints=refPoints1, name='m_Set-2')
a = m.rootAssembly
region2=a.instances['ZHU'].sets['Set-deges2']
m.Coupling(name='Constraint-5', controlPoint=region1,
    surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
    localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

# ==============================================================================
# 分析步与边界条件（修改部分：添加场输出以保存模态向量）
# ==============================================================================
a = m.rootAssembly
m.BuckleStep(name='Step-1', previous='Initial', numEigen=4, vectors=8, maxIterations=800)
m.FieldOutputRequest(name='F-Output-1',createStepName='Step-1', variables=('U',), modes=(1, 2, 3, 4))

region = a.sets['m_Set-2']
m.ConcentratedForce(name='Load-1', createStepName='Step-1', region=region, cf3=-1, distributionType=UNIFORM, field='', localCsys=None)

region = a.sets['m_Set-1']
m.DisplacementBC(name='BC-1', createStepName='Step-1',
    region=region, u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=UNSET, ur3=0.0,
    amplitude=UNSET, buckleCase=PERTURBATION_AND_BUCKLING, fixed=OFF,
    distributionType=UNIFORM, fieldName='', localCsys=None)

region = a.sets['m_Set-2']
m.DisplacementBC(name='BC-2', createStepName='Step-1',
    region=region, u1=0.0, u2=0.0, u3=UNSET, ur1=0.0, ur2=UNSET, ur3=0.0,
    amplitude=UNSET, buckleCase=PERTURBATION_AND_BUCKLING, fixed=OFF,
    distributionType=UNIFORM, fieldName='', localCsys=None)

# ==============================================================================
# 网格与求解
# ==============================================================================
p = m.parts['BIANZHU']
p.seedPart(size=Me, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

mdb.Job(name=qqmtname, model='DQL', description='', type=ANALYSIS, atTime=None,
    waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE,
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
    scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN,
    numDomains=Nc, activateLoadBalancing=False, multiprocessingMode=DEFAULT,
    numCpus=Nc)

mdb.jobs[qqmtname].submit(consistencyChecking=OFF)
mdb.jobs[qqmtname].waitForCompletion()


# ==============================================================================
# 2. 打开ODB文件并提取模态数据（修正后：基于BZC/750计算放大系数）
# ==============================================================================
try:
    odb = openOdb(path=odb_path, readOnly=True)
    print
    "成功打开ODB文件：%s" % odb_path
    buckle_step = odb.steps["Step-1"]
    mode_frame = buckle_step.frames[1]
    disp_field = mode_frame.fieldOutputs["U"]

    mode_data = {}
    max_magnitude = 0.0
    for data in disp_field.values:
        node_id = data.nodeLabel
        u1 = data.data[0]
        u2 = data.data[1]
        u3 = data.data[2]
        mode_data[node_id] = (u1, u2, u3)
        magnitude = math.sqrt(u1 ** 2 + u2 ** 2 + u3 ** 2)
        if magnitude > max_magnitude:
            max_magnitude = magnitude

    modal_reference = 750.0

    scale_factor = BZC * 1.2 / modal_reference if modal_reference != 0 else 1.0
    print
    "缺陷放大系数：%.6f（柱子长度BZC=%.1f / 基准值750）" % (scale_factor, BZC)

    # 保存数据（保留必要参数，删除无用的target_max_defect）
    save_data = {
        "mode_data": mode_data,
        "max_magnitude": max_magnitude,
        "modal_reference": modal_reference,  # 记录基准值750
        "scale_factor": scale_factor,  # 修正后的系数
        "BZC": BZC  # 记录当前柱子长度（便于追溯）
    }
    with open(output_file, "wb") as f:
        pickle.dump(save_data, f)
    odb.close()
    print
    "后处理完成！"

except Exception as e:
    print
    "后处理失败：%s" % str(e)


# ==============================================================================
# 2. 直接读取缺陷数据
# ==============================================================================
with open(output_file, "rb") as f:
    defect_data = pickle.load(f)

mode_data = defect_data["mode_data"]
scale_factor = defect_data["scale_factor"]

# ==============================================================================
# 3. 复制源模型并创建带缺陷的静力模型（新增幅值曲线+修改分析步）
# ==============================================================================
if source_model_name not in mdb.models:
    raise Exception("源模型 '%s' 不存在，请先运行第一部分建模代码" % source_model_name)

source_model = mdb.models[source_model_name]
mdb.Model(name=new_model_name, objectToCopy=source_model)
new_model = mdb.models[new_model_name]
steps_to_delete = [s.name for s in new_model.steps.values() if s.name != "Initial"]
for step_name in steps_to_delete:
    del new_model.steps[step_name]

# 1. 创建150步加载至15mm的幅值曲线
new_model.TabularAmplitude(
    name='Force_Displacement_15mm_150Steps',
    timeSpan=STEP,
    smooth=SOLVER_DEFAULT,
    data=((0.0, 0.0), (1.0, 1.0))  # 0步→0mm，150步→15mm（比例控制）
)


# 2. 静力分析步（强制150步完成加载）
new_model.StaticStep(
    name="Static_Compression_Defect",
    previous="Initial",
    nlgeom=ON,  # 大变形开关必须开启
    maxNumInc=150,  # 核心：强制150步
    initialInc=0.01,  # 初始步长比例（150×0.01=1.0，覆盖全程）
    minInc=1e-8,      # 允许极小步长保证收敛
    maxInc=0.01,      # 固定最大步长，确保150步加载
    timePeriod=1.0    # 时间周期与步长比例匹配
)

# ==============================================================================
# 5. 施加约束与荷载（修改：位移加载关联幅值曲线）
# ==============================================================================
assembly = new_model.rootAssembly
required_sets = ["m_Set-1", "m_Set-2"]
for set_name in required_sets:
    if set_name not in assembly.sets:
        raise Exception("集合 %s 不存在，请检查源模型" % set_name)


# 1. 底部球铰约束（平动固定，转动释放）
new_model.DisplacementBC(
    name="BC_Base_Hinge",
    createStepName="Static_Compression_Defect",
    region=assembly.sets["m_Set-1"],  # 底部端点集合
    u1=0.0, u2=0.0, u3=0.0,          # 固定3个平动自由度
    ur1=UNSET, ur2=UNSET, ur3=UNSET, # 释放3个转动自由度
    fixed=ON
)

# 2. 顶部球铰约束+轴向位移加载（15mm）
new_model.DisplacementBC(
    name="BC_Top_Hinge_Load",
    createStepName="Static_Compression_Defect",
    region=assembly.sets["m_Set-2"],
    u1=0, u2=0,                  # 固定径向平动
    u3=-15.0,                     # 轴向位移加载目标改为15mm
    ur1=UNSET, ur2=UNSET, ur3=UNSET,
    amplitude='Force_Displacement_15mm_150Steps',  # 关联新幅值曲线
    fixed=OFF
)

# ==============================================================================
# 6. 提交带缺陷的静力分析并保存结果
# ==============================================================================
mdb.Job(name=wyjzname, model='Static_Load_Model_Defect', description='',
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None,
    memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=Nc,
    numDomains=Nc, numGPUs=0)

mdb.jobs[wyjzname].submit(consistencyChecking=OFF)
mdb.jobs[wyjzname].waitForCompletion()



if JZ == 1:
    odb_path = os.path.join(target_dir, "%s.odb" % wyjzname)
    my_odb = openOdb(odb_path)
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('wendunaodu')
    sheet.write(0, 0, 'Analysis_Step')
    sheet.write(0, 1, 'Step')
    sheet.write(0, 2, 'Time')
    sheet.write(0, 3, 'Weiyi_mm')
    sheet.write(0, 4, 'Fanli_kN')
    sheet.write(0, 5, 'Qiangdu_MPa')
    row_index = 1
    for step_name, step in my_odb.steps.items():
        # 处理步骤名称特殊字符
        safe_step_name = step_name.encode('utf-8', errors='replace').decode('utf-8')
        for frame in step.frames:
            # 获取反力数据
            rf_field = frame.fieldOutputs['RF']
            NodeSet0 = my_odb.rootAssembly.nodeSets['M_SET-2']
            local_rf_values0 = rf_field.getSubset(region=NodeSet0, position=NODAL)
            # 获取位移数据
            dis_field1 = frame.fieldOutputs['U']
            NodeSet1 = my_odb.rootAssembly.nodeSets['M_SET-2']
            local_rf_values1 = dis_field1.getSubset(region=NodeSet1, position=NODAL)
            for value0, value1 in zip(local_rf_values0.values, local_rf_values1.values):
                frame_id = frame.frameId
                frame_time = float(frame.frameValue)
                rf3_value = float(value0.data[2] / -1000)
                gudingkua = float(-1 * value1.data[2])
                rf3_div_1737 = round(rf3_value / 1.737, 2)
                sheet.write(row_index, 0, safe_step_name)
                sheet.write(row_index, 1, frame_id)
                sheet.write(row_index, 2, frame_time)
                sheet.write(row_index, 3, gudingkua)
                sheet.write(row_index, 4, rf3_value)
                sheet.write(row_index, 5, rf3_div_1737)
                row_index += 1
    excel_path = os.path.join(target_dir, "%s.xls" % wyjzname)
    try:
        workbook.save(excel_path)
        print("结果已保存至Excel文件：{}".format(excel_path))
    except Exception as e:
        print("Excel保存失败：{}".format(str(e)))
    finally:
        my_odb.close()

# 保存模型
mdb.saveAs(pathName=os.path.join(target_dir, "%s.cae" % wyjzname))
session.graphicsOptions.setValues(backgroundStyle=SOLID, backgroundColor='#FFFFFF')










