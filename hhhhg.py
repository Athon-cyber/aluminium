from abaqus import *
from abaqusConstants import *




#function
def create_plate_hole(ba,bb,bc,bd,ha,hb,hc,hd,ganchang,midu,yangshi,bosong,qufu,qufuyb,houdu,zhouli,part,model):
	s1 = mdb.models[model].ConstrainedSketch(name='__profile__',sheetSize=1000.0)
	g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
	s1.setPrimaryObject(option=STANDALONE)
	s1.Spot(point=(-(ba/2+bb+bd), ha/2+hb+hc))
	s1.Spot(point=(ba/2+bb+bd, ha/2+hb+hc))
	s1.Spot(point=(-(ba/2+bb+bd), -(ha/2+hb+hc)))
	s1.Spot(point=(ba/2+bb+bd, -(ha/2+hb+hc)))
	s1.Spot(point=(-(ba/2), ha/2+hc+hb-hd))
	s1.Spot(point=(ba/2, ha/2+hc+hb-hd))
	s1.Spot(point=(-(ba/2), -(ha/2+hc+hb-hd)))
	s1.Spot(point=(ba/2, -(ha/2+hc+hb-hd)))
	s1.Spot(point=(ba/2+bd, -(ha/2+hb+hc)))
	s1.Spot(point=(-(ba/2+bd), -(ha/2+hb+hc)))
	s1.Spot(point=(-(ba/2+bd), ha/2+hb+hc))
	s1.Spot(point=(ba/2+bd, ha/2+hb+hc))
	s1.Spot(point=(-(ba/2+bc), ha/2))
	s1.Spot(point=(ba/2+bc, ha/2))
	s1.Spot(point=(-(ba/2+bc), -ha/2))
	s1.Spot(point=(ba/2+bc, -ha/2))
	s1.Spot(point=(-(ba/2+bb+bd), ha/2+hc))
	s1.Spot(point=(ba/2+bb+bd, ha/2+hc))
	s1.Spot(point=(-(ba/2+bb+bd), -(ha/2+hc)))
	s1.Spot(point=(ba/2+bb+bd, -(ha/2+hc)))
	s1.Line(point1=(-(ba/2+bb+bd), ha/2+hb+hc), point2=(-(ba/2+bd), ha/2+hb+hc))
	s1.HorizontalConstraint(entity=g[2], addUndoState=False)
	s1.Line(point1=(-(ba/2+bd), ha/2+hb+hc), point2=(-ba/2, ha/2+hc+hb-hd))
	s1.Line(point1=(-ba/2, ha/2+hc+hb-hd), point2=(ba/2, ha/2+hc+hb-hd))
	s1.HorizontalConstraint(entity=g[4], addUndoState=False)
	s1.Line(point1=(ba/2, ha/2+hc+hb-hd), point2=(ba/2+bd, ha/2+hb+hc))
	s1.Line(point1=(ba/2+bd, ha/2+hb+hc), point2=(ba/2+bb+bd, ha/2+hb+hc))
	s1.HorizontalConstraint(entity=g[6], addUndoState=False)
	s1.Line(point1=(ba/2+bb+bd, ha/2+hb+hc), point2=(ba/2+bb+bd, ha/2+hc))
	s1.VerticalConstraint(entity=g[7], addUndoState=False)
	s1.PerpendicularConstraint(entity1=g[6], entity2=g[7], addUndoState=False)
	s1.Line(point1=(ba/2+bb+bd, ha/2+hc), point2=(ba/2+bc, ha/2))
	s1.Line(point1=(ba/2+bc, ha/2), point2=(ba/2+bc, -ha/2))
	s1.VerticalConstraint(entity=g[9], addUndoState=False)
	s1.Line(point1=(ba/2+bc, -ha/2), point2=(ba/2+bb+bd, -(ha/2+hc)))
	s1.Line(point1=(ba/2+bb+bd, -(ha/2+hc)), point2=(ba/2+bb+bd, -(ha/2+hb+hc)))
	s1.VerticalConstraint(entity=g[11], addUndoState=False)
	s1.Line(point1=(ba/2+bb+bd, -(ha/2+hb+hc)), point2=(ba/2+bd, -(ha/2+hb+hc)))
	s1.HorizontalConstraint(entity=g[12], addUndoState=False)
	s1.PerpendicularConstraint(entity1=g[11], entity2=g[12], addUndoState=False)
	s1.Line(point1=(ba/2+bd, -(ha/2+hb+hc)), point2=(ba/2, -(ha/2+hc+hb-hd)))
	s1.Line(point1=(ba/2, -(ha/2+hc+hb-hd)), point2=(-ba/2, -(ha/2+hc+hb-hd)))
	s1.HorizontalConstraint(entity=g[14], addUndoState=False)
	s1.Line(point1=(-ba/2, -(ha/2+hc+hb-hd)), point2=(-(ba/2+bd), -(ha/2+hb+hc)))
	s1.Line(point1=(-(ba/2+bd), -(ha/2+hb+hc)), point2=(-(ba/2+bb+bd), -(ha/2+hb+hc)))
	s1.HorizontalConstraint(entity=g[16], addUndoState=False)
	s1.Line(point1=(-(ba/2+bb+bd), -(ha/2+hb+hc)), point2=(-(ba/2+bb+bd), -(ha/2+hc)))
	s1.VerticalConstraint(entity=g[17], addUndoState=False)
	s1.PerpendicularConstraint(entity1=g[16], entity2=g[17], addUndoState=False)
	s1.Line(point1=(-(ba/2+bb+bd), -(ha/2+hc)), point2=(-(ba/2+bc), -ha/2))
	s1.Line(point1=(-(ba/2+bc), -ha/2), point2=(-(ba/2+bc), ha/2))
	s1.VerticalConstraint(entity=g[19], addUndoState=False)
	s1.Line(point1=(-(ba/2+bc), ha/2), point2=(-(ba/2+bb+bd), ha/2+hc))
	s1.Line(point1=(-(ba/2+bb+bd), ha/2+hc), point2=(-(ba/2+bb+bd), ha/2+hb+hc))
	s1.VerticalConstraint(entity=g[21], addUndoState=False)
	s1.Line(point1=(-ba/2, ha/2+hc+hb-hd), point2=(-(ba/2+bc), ha/2))
	s1.Line(point1=(ba/2, ha/2+hc+hb-hd), point2=(ba/2+bc, ha/2))
	s1.Line(point1=(-ba/2, -(ha/2+hc+hb-hd)), point2=(-(ba/2+bc), -ha/2))
	s1.Line(point1=(ba/2, -(ha/2+hc+hb-hd)), point2=(ba/2+bc, -ha/2))
	p = mdb.models[model].Part(name=part, dimensionality=THREE_D, 
	    type=DEFORMABLE_BODY)
	p = mdb.models[model].parts[part]
	p.BaseShellExtrude(sketch=s1, depth=ganchang)
	s1.unsetPrimaryObject()
	p = mdb.models[model].parts[part]
	del mdb.models[model].sketches['__profile__']
	mdb.models[model].Material(name='al')
	mdb.models[model].materials['al'].Density(table=((midu, ), ))
	mdb.models[model].materials['al'].Elastic(table=((yangshi, bosong), ))
	mdb.models[model].materials['al'].Plastic(scaleStress=None, table=(
	    (qufu, qufuyb), ))
	mdb.models[model].HomogeneousShellSection(name='Section-1', 
	    preIntegrate=OFF, material='al', thicknessType=UNIFORM, thickness=houdu, 
	    thicknessField='', nodalThicknessField='', idealization=NO_IDEALIZATION, 
	    poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
	    useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)
	p = mdb.models[model].parts['plate_hole']
	f = p.faces
	faces = f.getSequenceFromMask(mask=('[#ffffff ]', ), )
	region = p.Set(faces=faces, name='Set-1')
	p = mdb.models[model].parts['plate_hole']
	p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
	    offsetType=MIDDLE_SURFACE, offsetField='', 
	    thicknessAssignment=FROM_SECTION)
	a = mdb.models[model].rootAssembly
	a = mdb.models[model].rootAssembly
	a.DatumCsysByDefault(CARTESIAN)
	p = mdb.models[model].parts['plate_hole']
	a.Instance(name='plate_hole-1', part=p, dependent=ON)
	mdb.models[model].BuckleStep(name='Step-1', previous='Initial', 
	    numEigen=4, vectors=8,maxIterations=500)
	mdb.models['stress_analysis'].fieldOutputRequests['F-Output-1'].setValues(
    variables=('U', 'UT', 'UR', 'RBANG', 'RBROT'))
	a = mdb.models[model].rootAssembly
	a.ReferencePoint(point=(0.0, 0.0, -50.0))
	a = mdb.models[model].rootAssembly
	a.ReferencePoint(point=(0.0,  0.0, ganchang+50))
	a = mdb.models[model].rootAssembly
	r1 = a.referencePoints
	refPoints1=(r1[5], )
	region1=a.Set(referencePoints=refPoints1, name='m_Set-1')
	a = mdb.models[model].rootAssembly
	s1 = a.instances['plate_hole-1'].edges
	side1Edges1 = s1.getSequenceFromMask(mask=('[#5248a491 #4922a924 #5 ]', ), )
	region2=a.Surface(side1Edges=side1Edges1, name='s_Surf-1')
	mdb.models[model].Coupling(name='Constraint-1',  
	    controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
	    couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, 
	    ur2=ON, ur3=ON)
	a = mdb.models[model].rootAssembly
	r1 = a.referencePoints
	refPoints1=(r1[4], )
	region1=a.Set(referencePoints=refPoints1, name='m_Set-2')
	a = mdb.models[model].rootAssembly
	s1 = a.instances['plate_hole-1'].edges
	side1Edges1 = s1.getSequenceFromMask(mask=('[#29225244 #a4895491 #a ]', ), )
	region2=a.Surface(side1Edges=side1Edges1, name='s_Surf-2')
	mdb.models[model].Coupling(name='Constraint-2', 
	    controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
	    couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, 
	    ur2=ON, ur3=ON)
	a = mdb.models[model].rootAssembly
	r1 = a.referencePoints
	refPoints1=(r1[4], )
	region = a.Set(referencePoints=refPoints1, name='yueshud')
	mdb.models[model].DisplacementBC(name='BC-1', createStepName='Initial', 
    region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
    amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
	a = mdb.models['stress_analysis'].rootAssembly
	r1 = a.referencePoints
	refPoints1=(r1[5], )
	region = a.Set(referencePoints=refPoints1, name='yueshuu')
	mdb.models['stress_analysis'].DisplacementBC(name='BC-2', createStepName='Initial', 
    region=region, u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=SET, 
    amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
	a = mdb.models[model].rootAssembly
	r1 = a.referencePoints
	refPoints1=(r1[5], )
	region = a.Set(referencePoints=refPoints1, name='hezai')
	mdb.models[model].ConcentratedForce(name='Load-1', 
	    createStepName='Step-1', region=region, cf3=zhouli, 
	    distributionType=UNIFORM, field='', localCsys=None)
	p = mdb.models[model].parts['plate_hole']
	p = mdb.models[model].parts['plate_hole']
	p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
	p = mdb.models[model].parts['plate_hole']
	p.generateMesh()
	a1 = mdb.models[model].rootAssembly
	a1.regenerate()
	a = mdb.models[model].rootAssembly
	mdb.Job(name='ppp', model=model, description='', type=ANALYSIS, 
	    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
	    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,  
		explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
	    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
	    scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1, multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
	mdb.jobs['ppp'].submit(consistencyChecking=OFF)




mdb.models['stress_analysis'].keywordBlock.synchVersions(
    storeNodesAndElements=False)

mdb.models['stress_analysis'].keywordBlock.replace(51, """
*Restart, write, frequency=0
*node file,  global=yes,  last mode=1
U""")


mdb.Model(name='stress_analysis-Copy', 
    objectToCopy=mdb.models['stress_analysis'])
#: The model "stress_analysis-Copy" has been created.
p = mdb.models['stress_analysis-Copy'].parts['plate_hole']
session.viewports['Viewport: 1'].setValues(displayedObject=p)

mdb.models['stress_analysis-Copy'].keywordBlock.synchVersions(
    storeNodesAndElements=False)
mdb.models['stress_analysis-Copy'].keywordBlock.replace(38, """
*Boundary
RP_Top, 1, 1
RP_Top, 2, 2
RP_Top, 6, 6
*imperfection,  file=Analysis_Job,  Step=1
1,  0.84""")

a = mdb.models['stress_analysis-Copy'].rootAssembly
mdb.models['stress_analysis-Copy'].StaticRiksStep(name='BuckleStep', 
    previous='Initial', maintainAttributes=True, nlgeom=ON)

mdb.models['stress_analysis-Copy'].fieldOutputRequests['F-Output-1'].setValues(
    variables=('S', 'MISES', 'MISESMAX', 'TSHR', 'CTSHR', 'ALPHA', 'TRIAX', 
    'LODE', 'VS', 'PS', 'CS11', 'ALPHAN', 'SSAVG', 'MISESONLY', 'PRESSONLY', 
    'SEQUT', 'YIELDPOT', 'E', 'VE', 'PE', 'VEEQ', 'PEEQ', 'PEEQT', 'PEEQMAX', 
    'PEMAG', 'PEQC', 'EE', 'IE', 'THE', 'NE', 'LE', 'TE', 'TEEQ', 'TEVOL', 
    'EEQUT', 'ER', 'SE', 'SPE', 'SEPE', 'SEE', 'SEP', 'SALPHA', 'U', 'UT', 
    'UR', 'RBANG', 'RBROT', 'RF', 'RT', 'RM', 'CF', 'SF', 'SQEQ', 'TF', 'VF', 
	'ESF1', 'NFORC', 'NFORCSO', 'RBFOR', 'P'))

regionDef=mdb.models['stress_analysis-Copy'].rootAssembly.sets['RP_Top']
mdb.models['stress_analysis-Copy'].historyOutputRequests['H-Output-1'].setValues(
    variables=('U3', 'RF3', 'ALLAE', 'ALLCD', 'ALLDMD', 'ALLEE', 'ALLFD', 
    'ALLIE', 'ALLJD', 'ALLKE', 'ALLKL', 'ALLPD', 'ALLQB', 'ALLSE', 'ALLSD', 
    'ALLVD', 'ALLWK', 'ETOTAL'), region=regionDef, sectionPoints=DEFAULT, 
    rebar=EXCLUDE)

mdb.models['stress_analysis-Copy'].loads['AxialForce'].suppress()


mdb.models['stress_analysis-Copy'].boundaryConditions['BC_Top'].setValuesInStep(
    stepName='BuckleStep', u3=-20.0)

mdb.Job(name='Job-2', model='stress_analysis-Copy', description='', 
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
    memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1, 
    multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
mdb.jobs['Job-2'].submit(consistencyChecking=OFF)



#variables

myname="stress_analysis"
myba=60.0
mybb=44.0
mybc=44.0
mybd=12.0
myha=60.0
myhb=44.0
myhc=12.0
myhd=12.0
myganchang=1258.8
mymidu=2.8e-9
myyangshi=67000
mybosong=0.3
myqufu=197
myqufuyb=0
myhoudu=2
myzhouli=-1
mymodel=mdb.Model(name=myname)
mypart="plate_hole"
create_plate_hole(myba,mybb,mybc,mybd,myha,myhb,myhc,myhd,myganchang,mymidu,myyangshi,mybosong,myqufu,myqufuyb,myhoudu,myzhouli,mypart,myname)