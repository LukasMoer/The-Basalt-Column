import os
import csv
import numpy
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def read_image(filename):
  """reads  jpeg file and turns it into a numpy matrix"""
  img = Image.open(filename)
  img_bw = img.convert("L")
  data = np.array(img_bw)
  return data

    
def center(A):
    """ Weighted mean of the matrix"""
    median=np.median(A)
    A[A<=median]=0
    res=np.array([0,0])
    for i in range(len(A)):
        for j in range(len(A[0])):
            res=res+np.array([i,j])*A[i][j]
    res=res/np.sum(A)
    return res[0], res[1]


def timedelta(t1,t2):
    """Difference between 2 times, in seconds. t1 is the earlier point of time.
    Takes 2 tuples with 3 integers e.g. (17,30,45) representing hour,minute,second"""
    dh=(t2[0]-t1[0])*60*60
    dm=(t2[1]-t1[1])*60   
    ds=(t2[2]-t1[2])
    return dh+dm+ds


#Get the positions from the images
filelist=os.listdir()
jpegs=[]
for file in filelist:
    if ".jpg" in file:
        jpegs.append(file)

X,Y=[],[]
for imagename in jpegs:
   i,j=center(read_image(imagename))
   X.append(j)
   Y.append(i)

#Get the timestamps from the image filenames.
#Requirement: webcam saves images with filename scheme YYYYMMDD_HH_MM_SS.jpg
time_pos=[]
for imagename in jpegs:
    timestamp=imagename.replace(".jpg","")
    [date,hour,minute,second]=timestamp.split("_")
    time_pos.append((int(hour),int(minute),int(second)))

#Read the csv file from the magnetic field sensor
time_mag_raw=[]
B_raw,Bx_raw,By_raw,Bz_raw=[],[],[],[]
filename="magnet.csv"
fobj=open(filename)
for line in fobj:
    line=line.split(";")
    [hour,minute,second,milli]=line[0].split(":")
    time_mag_raw.append((int(hour),int(minute),int(second)))
    B_raw.append(float(line[-1].replace("\n","")))
    Bx_raw.append(float(line[-4].replace("\n","")))
    By_raw.append(float(line[-3].replace("\n","")))
    Bz_raw.append(float(line[-2].replace("\n","")))

#Average all measurements taken within the interval of a second
time_mag=[]
B,Bx,By,Bz=[],[],[],[]
n=0
tref=time_mag_raw[0]
count=0
Bsum,Bxsum,Bysum,Bzsum=0,0,0,0
while n<len(time_mag_raw):
    if time_mag_raw[n][0]==tref[0] and time_mag_raw[n][1]==tref[1] and time_mag_raw[n][2]==tref[2]:
        Bsum+=B_raw[n]
        Bxsum+=Bx_raw[n]
        Bysum+=By_raw[n]
        Bzsum+=Bz_raw[n]
        count+=1
    else:
        time_mag.append((tref[0],tref[1],tref[2]))
        B.append(Bsum/count)
        Bx.append(Bxsum/count)
        By.append(Bysum/count)
        Bz.append(Bzsum/count)
        tref=time_mag_raw[n]
        count=0
        Bsum,Bxsum,Bysum,Bzsum=0,0,0,0
    n+=1


#Match the position data with the magnetic field sensor data
B_match,Bx_match,By_match,Bz_match=[],[],[],[]
for t in time_pos:
    n=0
    while timedelta(t,time_mag[n])<0 and n<len(time_mag):
        n+=1
    B_match.append(B[n])
    Bx_match.append(Bx[n])
    By_match.append(By[n])
    Bz_match.append(Bz[n])


#Output as csv file and plot
plt.scatter(X,Y,c=B_match)

output = np.column_stack((X, Y, B_match,Bx_match,By_match,Bz_match))
np.savetxt("output.csv", output, delimiter=";", header="X,Y,Btotal,Bx,By,Bz")
