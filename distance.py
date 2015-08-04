import numpy as np
import math

import matplotlib.pyplot as plt
from matplotlib import lines
from mpl_toolkits.mplot3d import Axes3D

#--------------------------------------------------
class TargetPoint():  # define by (R,A,S)
    def __init__(self, R = 0, A = 0, S = 0):
        self.R = R
        self.A = A
        self.S = S

    def pointArray(self):
        return np.array([self.R, self.A, self.S])


class TemplatePlane():  # define by (A,B,C,D) and Ax+By+Cz+D = 0
    def __init__(self, A = 1, B = 1, C = 1, D = 1):
        if (A == 0) & (B == 0) & (C == 0):
            print "A, B, C shouldn't all == 0!!"
            exit()
        else:
            self.A = A
            self.B = B
            self.C = C
            self.D = D

    def planeArray(self):
        return np.array([self.A, self.B, self.C, self.D])

    def planeNormalArray(self):
        return np.array([self.A, self.B, self.C])


class ProjectionPoint():
    def projectPointArray(self, pointArray, planeArray):
        #pointOnPlane = planeNormalArray    
        #projectPointOnPlane = pointArray - np.dot(pointArray-pointOnPlane, planeNormalArray)*planeNormalArray

        ## k = -(ax+by+cz+d)/(aa+bb+cc)
        ## x' = x+ka
        k = -float((planeArray[0]*pointArray[0] + planeArray[1]*pointArray[1] + planeArray[2]*pointArray[2] + planeArray[3]))/float((planeArray[0]**2 + planeArray[1]**2 + planeArray[2]**2))

        print "k: ", k

        proj_x = pointArray[0] + k*planeArray[0]
        proj_y = pointArray[1] + k*planeArray[1]
        proj_z = pointArray[2] + k*planeArray[2]

        projectPointOnPlane = [proj_x, proj_y, proj_z]

        return projectPointOnPlane  # in format np.array([x,y,z])

    def nearestHole(self, targetPoint, templatePlane):  # point=TargetPoint(r,a,s), plane=TemplatePlane(a,b,c,d) 
        # project point on the plane
        pointProject = self.projectPointArray(targetPoint.pointArray(), templatePlane.planeArray())




class GeneratePaths():
    def disPoint2Plane(self, TargetPoint, TemplatePlane):
        numer = math.fabs(TemplatePlane.A*TargetPoint.R + TemplatePlane.B*TargetPoint.A + TemplatePlane.C*TargetPoint.S + TemplatePlane.D)
        denom = math.sqrt(pow(TemplatePlane.A,2) + pow(TemplatePlane.B,2) + pow(TemplatePlane.C,2))
        self.depthNeedleBase = float(numer)/float(denom)
        return self.depthNeedleBase


    def disPointLimit(self, TargetPoint, TemplatePlane):
        self.disVLimit = self.depthNeedleBase
        self.disHLimit = math.tan((15*math.pi)/180)*self.disVLimit
        disSLimit = float(self.disVLimit)/float(math.cos((15*math.pi)/180))
	
        return round(self.disVLimit,3), round(self.disHLimit,3), round(disSLimit,3)
	

    def insertionPathsDistance(self, numOfPath):
        x_disH_list = []
        x_disS_list = []
        gap = float(15)/(numOfPath-1) 
        
        print "gap: ", gap

        for x in range(0, 15, gap):
            x_disH = round(math.tan((x*math.pi)/180)*self.disVLimit, 3)
            x_disS = round(float(self.disVLimit)/math.cos((x*math.pi)/180), 3)
            x_disH_list.append(x_disH)
            x_disS_list.append(x_disS)

        
        # the limitation -- 15 degree 
        x_disH_15 = round(math.tan((15*math.pi)/180)*self.disVLimit, 3)
        x_disS_15 = round(float(self.disVLimit)/math.cos((15*math.pi)/180), 3)
        x_disH_list.append(x_disH_15)
        x_disS_list.append(x_disS_15)

        return x_disH_list, x_disS_list


    def circlePath(self, projectPoint, radius):  # radius define the angulation degree of the needle
        x_list = []
        y_list = []

        for d in range (0, 360, 15):
            x = round(projectPoint[0] + radius*math.sin((d*math.pi)/180), 3)
            y = round(projectPoint[1] + radius*math.cos((d*math.pi)/180), 3)
            x_list.append(x)
            y_list.append(y)
            
        x_list_length = len(x_list)
        z = [round(projectPoint[2],2)]*x_list_length

        return x_list, y_list, z



#--------------------------------------------------
# test
#-------------------------------------------------- 
p = TargetPoint(5, -5, 3)
q = TemplatePlane(1.5, -2, 1, 0)

pjt = ProjectionPoint()
nH = pjt.nearestHole(p,q)
project_point = pjt.projectPointArray(p.pointArray(), q.planeArray())


path = GeneratePaths()
disV = path.disPoint2Plane(p, q) 
disL = path.disPointLimit(p, q)
fourPaths = path.insertionPathsDistance(4)


print "point: ", p.pointArray()
print "plane: ", q.planeArray()
print "planeNormalArray: ", q.planeNormalArray()
print ""
print "project point on plane: ", project_point
print ""
print "disPoint2Plane: ", disV
print "disLimit: ", disL
print "4paths_disH: ", fourPaths[0]
print "4paths_disS: ", fourPaths[1]    
print ""


radH = fourPaths[0]
newCir_x_list = []
newCir_y_list = []
newCir_z_list = []
for i in radH:
    print i
    newCir = path.circlePath(project_point, i)
    newCir_x_list.append(newCir[0])
    newCir_y_list.append(newCir[1])
    newCir_z_list.append(newCir[2])
#print newCir_x_list, newCir_y_list, newCir_z_list
    

point = np.array([q.A, q.B, q.C])
normal = np.array([q.A, q.B, q.C])
d = -point.dot(normal)
xx, yy = np.meshgrid(range(10), range(10))
z = (-normal[0]*xx - normal[1]*yy - d) * 1./normal[2]

#fig = plt.figure().gca(projection='3d')
#fig.plot_surface(xx,yy,z)
#fig.scatter(p.R, p.A, p.S, c='r', marker='o')
#fig.scatter(project_point[0], project_point[1], project_point[2], c='r', marker='*')
#plt.show()


fig = plt.figure().gca(projection='3d')
fig.plot_surface(xx,yy,z)
fig.scatter(p.R, p.A, p.S, c='r', marker='*')
fig.scatter(project_point[0], project_point[1], project_point[2], c='r', marker='^')
fig.scatter(newCir_x_list, newCir_y_list, newCir_z_list, marker='o')
plt.show()

