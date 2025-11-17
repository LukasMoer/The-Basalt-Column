import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

def center_of_gravty(A):
    j0=0
    for i in range(len(A)):
        for j in range(len(A[0])):
            j0+=A[i][j]*j
    return int(round(j0/np.sum(A),0))


def check(i,j,data,occupied):
  #Is this field a boundary?
  if occupied[i][j]:
    answer=False
  else:
    if data[i][j]!=0:
      #if its a pixel within the silhuette..
      if 0 in [data[i-1][j],data[i][j-1],data[i][j],data[i][j+1],data[i+1][j]]:
        #...and at the border, then its valid
        answer=True
      else:
        #..but in the middle of the bulk, then invalid
        answer=False
    else:
      #We are somewhere outside of the volume. Thus invalid.
      answer=False
  return answer


mm_per_pixel=0.172
stepsize=9
stepnumber=20
X,Y=[],[] 
faces=[] # [  [0°, [x1,x2,..], [y1,y2,..] ]  ,   ]

for step in range(stepnumber): #19
    X,Y=[],[] #Lists of Points defining the silhouette
    a=stepsize*step #angle of projection
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
    
    


with open('output.txt', 'w') as f:
    f.write(cmd)

