from abaqus import *
from abaqusConstants import *
import numpy as np
import matplotlib.pyplot as plt
import os
import csv

class MultiCellAluminumSection:
    """
    Class for defining the multi-cell aluminum cross-section
    Includes geometric parameters, material properties, and centerline generation
    """
    def __init__(self, b, h, t, b1, b2, b3, b4, h1, h2, h3, h4, l,
                 density=2.7e-9, young=70000.0, poisson=0.3, yield_stress=90,
                 plastic_table=None, working_dir = None):
        # Cross-section geometric parameters
        self.b = b
        self.h = h
        self.t = t
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.b4 = b4
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3
        self.h4 = h4
        # Material properties
        self.density = density
        self.young = young
        self.poisson = poisson
        self.yield_stress = yield_stress
        self.plastic_table = plastic_table if plastic_table is not None else ((90, 0.0),)
        # Offset parameter calculated from wall thickness
        self.c = 0.207 * t
        # Store all independent closed polygons (centerlines)
        self.centerline_polygons = None
        # Initial geometric imperfection
        self.d = 0.001 * l
        # Component length (extrusion depth)
        self.l = l
        # Working directory
        self.working_dir = working_dir
    
    def generate_centerline(self):
        """
        Generate closed centerline polygons for all chambers
        Each corner chamber is closed independently (1→2→3→4→5→1)
        """
        # Quarter 1 points (top-right corner)
        q1_points = [
            (self.b3/2 + self.c, self.h/2 - self.h4 - self.t/2),
            (self.b3/2 + self.b2 + self.c, self.h/2 - self.t/2),
            (self.b/2 - self.t/2, self.h/2 - self.t/2),
            (self.b/2 - self.t/2, self.h/2 - self.h1 + self.c),
            (self.b/2 - self.b4 - self.t/2, self.h3/2 + self.c),
        ]
        # Generate symmetric points for other quadrants
        q2_points = [(-x, y) for x, y in q1_points]
        q3_points = [(-x, -y) for x, y in q1_points]
        q4_points = [(x, -y) for x, y in q1_points]
        # Close each corner chamber independently
        q1_closed = q1_points + [q1_points[0]]
        q2_closed = q2_points + [q2_points[0]]
        q3_closed = q3_points + [q3_points[0]]
        q4_closed = q4_points + [q4_points[0]]
        # Closed loop for middle web and flange
        middle_closed = [
            q1_points[0],
            q2_points[0],
            q2_points[4],
            q3_points[4],
            q3_points[0],
            q4_points[0],
            q4_points[4],
            q1_points[4],
            q1_points[0],
        ]
        # Store all centerline polygons
        self.centerline_polygons = [
            np.array(q1_closed),
            np.array(q2_closed),
            np.array(q3_closed),
            np.array(q4_closed),
            np.array(middle_closed),
        ]
        return self.centerline_polygons
    
    def plot_centerline(self, save_path):
        """
        Plot the cross-section centerlines for verification
        """
        if self.centerline_polygons is None:
            self.generate_centerline()
        plt.figure(figsize=(8, 10))
        # Plot all independent closed polygons (centerlines)
        for poly in self.centerline_polygons:
            plt.plot(poly[:, 0], poly[:, 1], 'r-', linewidth=2, marker='o', markersize=4)
        plt.axhline(0, color='k', linestyle='--', alpha=0.3)
        plt.axvline(0, color='k', linestyle='--', alpha=0.3)
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.title('Multi-Cell Aluminum Section Centerline')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.savefig(os.path.join(save_path, "Section_Centerline.png"), dpi=1200, bbox_inches='tight')
        plt.close()
        print("Section plot saved successfully!")


def create_buckling_model(section, model_name='Buckling_Model', part_name='MultiCell_Part',
                          seed_size=5.0, job_name='Buckling_Analysis', num_eigen=4, step_name='BuckleStep'):
    """
    Create and submit buckling modal analysis for multi-cell aluminum component
    :param section: Instance of MultiCellAluminumSection
    """
    # Initialize model
    if model_name not in mdb.models.keys():
        model = mdb.Model(name=model_name)
    else:
        model = mdb.models[model_name]
    # ===================== save files =====================
    root_path = section.working_dir
    import datetime
    timestamp = datetime.datetime.now().strftime("%m%d_%H%M")
    folder_name = f"{timestamp}_{section.b}_{section.h}_{section.yield_stress}_{seed_size}".replace(".0", "")
    save_path = os.path.join(root_path, folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    os.chdir(save_path)
    mdb.saveAs(os.path.join(save_path, model_name+'.cae'))
    section.plot_centerline(save_path)
    print(f"All files will be saved to: {save_path}")
    # ========================================================================
    # Generate cross-section centerlines
    section.generate_centerline()
    # ------------------- Sketch Creation -------------------
    # Create sketch for cross-section profile
    sketch = model.ConstrainedSketch(name='CrossSection_Profile', sheetSize=2000.0)
    sketch.setPrimaryObject(option=STANDALONE)
    # Draw all closed polygons from centerlines
    for poly in section.centerline_polygons:
        num_points = len(poly)
        for i in range(num_points - 1):
            pt1 = (float(poly[i][0]), float(poly[i][1]))
            pt2 = (float(poly[i+1][0]), float(poly[i+1][1]))
            sketch.Line(point1=pt1, point2=pt2)
    # ------------------- Part Creation -------------------
    # Create 3D deformable shell part by extrusion
    part = model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    part.BaseShellExtrude(sketch=sketch, depth=section.l)
    sketch.unsetPrimaryObject()
    del model.sketches['CrossSection_Profile']
    print("part creation finished")
    # ------------------- Material Definition -------------------
    material_name = 'Aluminum_Alloy'
    model.Material(name=material_name)
    model.materials[material_name].Density(table=((section.density,),))
    model.materials[material_name].Elastic(table=((section.young, section.poisson),))
    if section.plastic_table:
        model.materials[material_name].Plastic(
            scaleStress=None,
            table=section.plastic_table
        )
    print("material definition finished")
    # ------------------- Shell Section Assignment -------------------
    model.HomogeneousShellSection(
        name='Shell_Section',
        preIntegrate=OFF,
        material=material_name,
        thicknessType=UNIFORM,
        thickness=section.t,
        idealization=NO_IDEALIZATION,
        poissonDefinition=DEFAULT,
        temperature=GRADIENT,
        useDensity=OFF,
        integrationRule=SIMPSON,
        numIntPts=5
    )
    # Assign shell section to all part faces
    all_faces = part.faces[:]  
    face_region = part.Set(faces=all_faces, name='All_Faces')
    part.SectionAssignment(
        region=face_region,
        sectionName='Shell_Section',
        offset=0.0,
        offsetType=MIDDLE_SURFACE,
        thicknessAssignment=FROM_SECTION
    )
    print("assign section finished")
    # ------------------- Assembly -------------------
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)
    instance = assembly.Instance(name=part_name + '-1', part=part, dependent=ON)
    # Create reference points at top and bottom
    rp_bottom = assembly.ReferencePoint(point=(20.0, 0.0, -50.0))
    rp_top = assembly.ReferencePoint(point=(20.0, 0.0, section.l + 50.0))
    rp_bottom_obj = assembly.referencePoints[rp_bottom.id]
    rp_top_obj = assembly.referencePoints[rp_top.id]
    print("assembly finished")
    # ------------------- Buckling Step -------------------
    model.BuckleStep(
        name=step_name,
        previous='Initial',
        numEigen=num_eigen,
        vectors=8,
        maxIterations=500
    )
    # Set field output requests
    model.fieldOutputRequests['F-Output-1'].setValues(
        variables=('U', 'UT', 'UR', 'RBANG', 'RBROT')
    )
    print("step finished")
    # --------------- Select Edges Using  Mask ----------------
    a = assembly
    # Get instance edges
    s1 = instance.edges
    # Select TOP edges with fixed mask (from your code)
    side1Edges1 = s1.getSequenceFromMask(mask=('[#22522491 #24a92549 #5 ]', ), ) # 硬编码，怎么改？
    # Select BOTTOM edges with fixed mask (from your code)
    side1Edges2 = s1.getSequenceFromMask(mask=('[#89249244 #925492a4 #a ]', ), )
    # Create Surfaces for coupling
    region2 = a.Surface(side1Edges=side1Edges1, name='s_Surf-1')
    region3 = a.Surface(side1Edges=side1Edges2, name='s_Surf-2')
    # Reference Point Sets
    rp_bottom_set = assembly.Set(referencePoints=(rp_bottom_obj,), name='m_Set-1')
    rp_top_set = assembly.Set(referencePoints=(rp_top_obj,), name='m_Set-2')
    # ------------------- Kinematic Coupling Constraints -------------------
    model.Coupling(name='Constraint-1',  
        controlPoint=rp_top_set, surface=region2, influenceRadius=WHOLE_SURFACE, 
        couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, 
        ur2=ON, ur3=ON)
    model.Coupling(name='Constraint-2', 
        controlPoint=rp_bottom_set, surface=region3, influenceRadius=WHOLE_SURFACE, 
        couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, 
        ur2=ON, ur3=ON)
    print("interaction finished")
    # ------------------- Boundary Conditions -------------------
    model.DisplacementBC(
        name='BC_Bottom_Fixed',
        createStepName='Initial',
        region=rp_bottom_set,
        u1=SET, u2=SET, u3=SET,
        ur1=SET, ur2=UNSET, ur3=SET
    )
    print("boundary condition finished")
    model.DisplacementBC(
        name='BC_Top_Guided',
        createStepName='Initial',
        region=rp_top_set,
        u1=SET, u2=SET, u3=UNSET,
        ur1=SET, ur2=UNSET, ur3=SET
    )
    # ------------------- Axial Compressive Load -------------------
    model.ConcentratedForce(
        name='Axial_Compressive_Force',
        createStepName=step_name,
        region=rp_top_set,
        cf3=-1.0
    )
    # ------------------- Meshing -------------------
    part.seedPart(size=seed_size, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()
    assembly.regenerate()
    # ------------------- Submit Linear Buckling Job -------------------
    job = mdb.Job(
        name=job_name,
        model=model_name,
        memory=90,
        memoryUnits=PERCENTAGE,
        getMemoryFromAnalysis=True,
        resultsFormat=ODB, numDomains=8, numCpus=4,
    )
    job.submit(consistencyChecking=OFF)
    job.waitForCompletion()
    print(f"Job '{job_name}' completed successfully.")
# ------------------- Integrated Nonlinear Local Buckling (Riks) Analysis -------------------
    # Write restart file for imperfection import
    mdb.models[model_name].keywordBlock.synchVersions(storeNodesAndElements=False)
    mdb.models[model_name].keywordBlock.replace(51,"*Restart, write, frequency=0\n*node file, global=yes, last mode=1\nu")
    # Copy model for nonlinear analysis
    mdb.Model(name=model_name+'-Copy', objectToCopy=mdb.models[model_name])
    mdb.models[model_name+'-Copy'].keywordBlock.synchVersions(storeNodesAndElements=False)
    imp_line = f"*Imperfection, file={job_name}, Step=1\n1, {section.d}"
    mdb.models[model_name+'-Copy'].keywordBlock.replace(38, imp_line)
    # Create Static Riks step
    mdb.models[model_name+'-Copy'].StaticRiksStep(name='BuckleStep', previous='Initial', maintainAttributes=True, minArcInc=1e-09, nlgeom=ON, maxNumInc=50)
    # Set output requests
    mdb.models[model_name+'-Copy'].fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'MISES', 'TSHR', 'ALPHA', 'TRIAX', 'E', 'PE', 'U', 'UR', 'RF', 'CF'))
    regionDef=mdb.models[model_name+'-Copy'].rootAssembly.sets['m_Set-2']
    mdb.models[model_name+'-Copy'].historyOutputRequests['H-Output-1'].setValues(variables=('U3','RF3','ALLIE'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    # Modify load and boundary
    mdb.models[model_name+'-Copy'].loads['Axial_Compressive_Force'].suppress()
    mdb.models[model_name+'-Copy'].boundaryConditions['BC_Top_Guided'].setValuesInStep(stepName='BuckleStep', u3=-20.0)
    # Submit nonlinear Riks job
    job2 = mdb.Job(name=job_name+'_Local', model=model_name+'-Copy', type=ANALYSIS, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, resultsFormat=ODB, numDomains=4, numCpus=4,)
    job2.submit(consistencyChecking=OFF)
    job2.waitForCompletion()
    print("Nonlinear local buckling job completed successfully!")
    final_odb_path = os.path.join(save_path, job_name + "_Local.odb")
    extract_load_displacement(final_odb_path, save_path)
    print("Data extraction and curve plotting completed successfully!")

def extract_load_displacement(odb_file_path, save_folder):
    if not os.path.exists(odb_file_path):
        print(f"Error: ODB file not found: {odb_file_path}")
        return
    base_name = os.path.splitext(os.path.basename(odb_file_path))[0]
    csv_path = os.path.join(save_folder, f"{base_name}_Load_Displacement.csv")
    img_path = os.path.join(save_folder, f"{base_name}_Load_Displacement_Curve.png")
    print(f"Processing ODB file: {os.path.basename(odb_file_path)}")
    try:
        odb = session.openOdb(odb_file_path)
    except Exception as e:
        print(f"Error: Failed to open ODB: {str(e)}")
        return
    try:
        step = odb.steps['BuckleStep']
    except KeyError:
        print("Error: Step 'BuckleStep' not found")
        odb.close()
        return
    target_region = None
    for region in step.historyRegions.values():
        if 'U3' in region.historyOutputs and 'RF3' in region.historyOutputs:
            target_region = region
            break
    if not target_region:
        print("Error: U3 / RF3 history output not found")
        odb.close()
        return
    u3_data = target_region.historyOutputs['U3'].data
    rf3_data = target_region.historyOutputs['RF3'].data
    try:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time(s)','Displacement_U3(mm)','Reaction_RF3(N)','Abs_Load(N)'])
            disp_list = []
            load_list = []
            for i in range(len(u3_data)):
                time = u3_data[i][0]
                disp = u3_data[i][1]
                rf = rf3_data[i][1]
                abs_load = abs(rf)
                disp_list.append(-disp)
                load_list.append(abs_load)
                writer.writerow([time, -disp, rf, abs_load])
        max_load = max(load_list) if load_list else 0
        plt.figure(figsize=(10,6))
        plt.plot(disp_list, load_list, 'b-', linewidth=2, label='Load-Displacement Curve')
        plt.xlabel('Displacement (mm)')
        plt.ylabel('Axial Load (N)')
        plt.title(f"Maximum Load = {max_load:.2f} N")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig(img_path, dpi=300, bbox_inches='tight')
        plt.close()
        print("="*50)
        print(f"Maximum Axial Load: {max_load:.2f} N")
        print(f"Data saved: {os.path.basename(csv_path)}")
        print(f"Curve saved: {os.path.basename(img_path)}")
        print("="*50)
    except Exception as e:
        print(f"Error: Failed to write output file: {str(e)}")
    odb.close()

ALUMINUM_MATERIALS = {
    80: [[240, 0], [250, 0.01], [260, 0.02], [270, 0.04], [282, 0.1]], #6082-T6-4mm-test
    81: [[217, 0], [230, 0.01], [240, 0.02], [250, 0.04], [262, 0.11]], #6082-T6-6mm-test
    82: [[230, 0], [240, 0.01], [250, 0.02], [260, 0.04], [270, 0.1]], #6082-T6-5mm-test
    90: [[90, 0.0], [100, 0.006590921], [110, 0.013743979], [120, 0.028350876], [130, 0.056601276], [140, 0.108659546], [150, 0.200600917]],  # 6063A-T4
    110: [[110, 0.0], [120, 0.006922684], [130, 0.014419969], [140, 0.030386958], [150, 0.06277659], [160, 0.125604792], [170, 0.242670383], [180, 0.453085142], [190, 0.819296788], [200, 1.438480155], [205, 1.886590371]],  # 6082-T4
    111: [[110, 0], [120, 0.006922684], [130, 0.014419969], [140, 0.030386958], [150, 0.06277659], [160, 0.125604792]], #6063-T5
    150: [[150, 0.0], [160, 0.007551472], [170, 0.015502164], [180, 0.033385472], [190, 0.072051298]],  # 6063A-T5
    180: [[180, 0.0], [185, 0.005917893], [190, 0.008007137], [195, 0.011233598], [200, 0.016182069], [205, 0.023710909]],  # 6063-T6
    181: [[180, 0], [190, 0.008007137], [200, 0.016182069], [210, 0.035068025], [220, 0.077228347]], #6063A-T6
    182: [[180, 0], [190, 0.006300414], [200, 0.009097521], [210, 0.013569521], [220, 0.020611207]], #6063A-T6 n=10.8
    183: [[180, 0], [190, 0.016721425], [200, 0.091633977], [210, 0.517179103], [220, 2.747472784]], #6063A-T6 n=36
    240: [[240, 0.0], [245, 0.006780547], [250, 0.008898891], [255, 0.012211746], [260, 0.017370193], [265, 0.025356262]],  # 6061-T6
    260: [[260, 0.0], [270, 0.009192713], [280, 0.017735098], [290, 0.038346384], [300, 0.086865846], [310, 0.198127397]],  # 6082-T6
}
L_list1 = [519.0097889, 1038.019578, 1557.029367, 2076.039155, 2335.54405, 2595.048944, 2854.553839, 3114.058733, 3633.068522, 4152.078311, 4671.0881, 5190.097889, 5709.107678, 6228.117466, 6747.127255, 7266.137044, 7785.146833,] #120x120x6  1557.029367, 2076.039155, 2335.54405, 2595.048944, 2854.553839, 3114.058733, 3633.068522, 4152.078311, 4671.0881, 5190.097889, 5709.107678, 6228.117466, 6747.127255, 7266.137044, 7785.146833,
L_list2 = [259.5047595, 519.009519, 778.5142785, 1038.019038, 1167.771418, 1297.523797, 1427.276177, 1557.028557, 1816.533316, 2076.038076, 2335.542835, 2595.047595, 2854.552354, 3114.057114, 3373.561873, 3633.066633, 3892.571392,] #60x60x3
L_list3 = [1038.053472, 2076.106944, 3114.160415, 4152.213887, 4671.240623, 5190.267359, 5709.294095, 6228.320831, 7266.374303, 8304.427774, 9342.481246, 10380.53472, 11418.58819, 12456.64166, 13494.69513, 14532.74861, 15570.80208,] #240x240x12
L_list4 = [1080, 2160, 3241, 4321, 4861, 5401, 5941, 6481, 7561, 8642, 9722, 10802, 11882, 12963, 14043, 15123, 16203,] #240x120x6-x
L_list5 = [537, 1074, 1612, 2149, 2417, 2686, 2955, 3223, 3760, 4298, 4835, 5372, 5909, 6447, 6984, 7521, 8058,] #240x120x6-y
L_list6 = [848, 1273, 1697, 2121, 2545, 2969, 3393,] #120x120x4 test
L_list7 = [834, 1251, 1669, 2086, 2503, 2920, 3337,] #120x120x6 test
L_list8 = [765, 1148, 1530, 1913,] #2296, 2678, 3061,] #120x120x5 test
L_list9 = [529, 1059, 1588, 2117, 2382, 2647, 2911, 3176, 3705, 4235, 4764, 5293, 5823, 6352, 6882, 7411, 7940 ] #120x120x3

Section_list1 = [120, 120, 6, 35, 10, 30, 10, 35, 10, 30, 10] # (b, h, t, h1, h2, h3, h4, b1, b2, b3, b4) 120x120x6
Section_list2 = [60, 60, 3, 17.5, 5, 15, 5, 17.5, 5, 15, 5] # 60x60x3
Section_list3 = [240, 240, 12, 70, 20, 60, 20, 70, 20, 60, 20] # 240x240x12
Section_list4 = [120, 240, 6, 35, 10, 150, 10, 35, 10, 30, 10] # 240x120x6
Section_list5 = [120, 120, 4, 35, 10, 30, 10, 35, 10, 30, 10] # 120x120x4-test
Section_list6 = [120, 120, 6, 35, 10, 30, 10, 35, 10, 30, 10] # 120x120x6-test
Section_list7 = [120, 200, 5, 35, 20, 90, 10, 35, 10, 30, 20] # 200x120x5-test
Section_list8 = [120, 120, 3, 35, 10, 30, 10, 35, 10, 30, 10] # 120x120x3

TASKS = [
    {"section": Section_list5, "lengths": L_list6, "yield_stress_list": [80]}, #[181, 182, 183, 111, 260, ]}
    # {"section": Section_list2, "lengths": L_list2, "yield_stress_list": [90, 110, 111]},
    # {"section": Section_list3, "lengths": L_list3, "yield_stress_list": [90, 110, 111]},
    # {"section": Section_list4, "lengths": L_list4, "yield_stress_list": [90, 110, 111]},
]

if __name__ == "__main__":
    for task in TASKS:
        sec = task["section"]
        ls = task["lengths"]
        ys = task["yield_stress_list"]
        for y in ys:
            plastic_data = ALUMINUM_MATERIALS[y]
            for li in ls:
                mdb.close()
                mdb.Model(name='Temp_Model')
                li_int = int(li)
                try:
                    cross_section = MultiCellAluminumSection(
                        b=sec[0],
                        h=sec[1],
                        t=sec[2],
                        b1=sec[7],
                        b2=sec[8],
                        b3=sec[9],
                        b4=sec[10],
                        h1=sec[3],
                        h2=sec[4],
                        h3=sec[5],
                        h4=sec[6],
                        l = li,
                        density=2.7e-9,
                        young=70000,
                        poisson=0.3,
                        plastic_table=plastic_data,
                        yield_stress=y,
                        working_dir=rf"D:\abaqus_working_directory\Abaqus_All_Buckling_Results\{sec[2]}_{li_int}",
                    )
                    job_suffix = f"Y{y}_b{sec[0]}_h{sec[1]}".replace(".0", "")
                    create_buckling_model(
                        section=cross_section,
                        model_name=f'MultiCell_Buckling{job_suffix}',
                        part_name='Aluminum_Component',
                        seed_size=5,
                        job_name=f'Buckling_Job{job_suffix}',
                    )
                    print(f"yield_stress = {y} compute finished")
                except Exception as e:
                    print(f"compute failed, {str(e)}")
                    continue
    print("all computations finished!")
