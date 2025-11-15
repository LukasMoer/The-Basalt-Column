import matplotlib.pyplot as plt
import statistics
import math
import numpy as np
from PIL import Image, ImageOps
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.tri as mtri
from scipy.interpolate import interp1d
from scipy.interpolate import UnivariateSpline



def center_of_gravty(A):
    j0=0
    for i in range(len(A)):
        for j in range(len(A[0])):
            j0+=A[i][j]*j
    return int(round(j0/np.sum(A),0))

def find_poleheight(X,Y,Z):
    min_distance=999999
    min_n=0
    for n in range(len(X)):
        distance=(X[n]*X[n]+Y[n]*Y[n])**0.5
        if distance<min_distance:
            min_n=n
            min_distance=distance
    return Z[min_n]


def check(i,j,data,occupied):
  #print("check ",i,j)
  if occupied[i][j]:
    answer=False
    #print("..occupied!")
  else:
    if data[i][j]!=0:
      #print("its in the volume")
      if 0 in [data[i-1][j],data[i][j-1],data[i][j],data[i][j+1],data[i+1][j]]:
        #print("Its ok!")
        answer=True
      else:
        #print("buts in the bulk", [data[i+1][j],data[i][j-1],data[i][j],data[i][j+1],data[i+1][j]])
        answer=False
    else:
      #print("no part of volume")
      answer=False
  return answer

def smooth_polygon(X):
    smoothing_factor = 40
    
    #introduce some redundancy to prevent shootover of the spline
    # Number of entries to move from the end to the start and from the start to the end
    X = np.concatenate([X,X,X])


    t = np.linspace(0, 1, len(X))  # Create a parameter vector from 0 to 1
    new_t = np.linspace(0, 1, int(len(X)*0.5))  # Define a finer parameter vector for a smoother curve
    spline = UnivariateSpline(t, X, s=smoothing_factor)
    new_X = spline(new_t)
    num_entries = int(len(new_X)/3)
    return new_X[num_entries:-num_entries]
    

mm_per_pixel=0.172
stepsize=9
stepnumber=20
X,Y=[],[]
faces=[] # [  [0°, [x1,x2,..], [y1,y2,..] ]  ,   ]

for step in range(stepnumber): #19
    X,Y=[],[]
    
    a=stepsize*step
    image = Image.open(f"{step:03d}"+".png")
    print("opening", f"{step:03d}"+".png")
    image=ImageOps.grayscale(image)
    data=np.asarray(image)
    data=data/255
    axis=center_of_gravty(data)
    

    #Find starting point
    indices = np.argwhere(data > 0)
    i,j=indices[0]
    print("start at",i,j)
    
    occupied  = np.zeros((len(data), len(data[0])), dtype=bool)
            
    istart,jstart=i,j
    while (not(i==istart and j==jstart)) or len(X)==0:
        for didj in [[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1]]:
            if check(i+didj[0],j+didj[1],data,occupied):
                i=i+didj[0]
                j=j+didj[1]
                occupied[i][j]=True
                X.append(j-axis)
                Y.append(len(data)-i)
                break
    
    X,Y=np.array(X),np.array(Y)      
    X,Y=smooth_polygon(X),smooth_polygon(Y)   
    X,Y=X*mm_per_pixel, Y*mm_per_pixel
    plt.plot(X,Y)
    faces.append([a,X,Y])
    
   


#Generate open scad code
EL=len(data[0])*2 #extrusion lenght

cmd="intersection(){\n"

for n in range(stepnumber):
  points = [[faces[n][1][k], faces[n][2][k]] for k in range(len(faces[n][1]))] 
  cmd=cmd+"rotate(a="+str(faces[n][0])+",v=[0,0,1]){ rotate(a=90,v=[1,0,0]){\n"
  cmd=cmd+"linear_extrude(height = "+str(EL)+", center = true){\n"
  cmd=cmd+"polygon(points="+str(points)+");}}}\n"

cmd=cmd+"}"  
    
    


with open('readme.txt', 'w') as f:
    f.write(cmd)


