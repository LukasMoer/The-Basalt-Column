import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def DiscreteFourier(f):
    """Computes the Fourier coefficients c (complex 1D array) 
    for a  given 1D-signal f"""
    N=len(f)
    c=[]
    for k in range(0,N-1):
        Sum=0
        for l in range(N-1):
            Sum+=f[l]*np.exp((-2)*np.pi*(1j)*k*l/N)
        c.append(Sum/N)
    return np.array(c)

def InverseFourier(F):
    """Computes the signal from a given spectrum"""
    N=len(F)
    f=[]
    for k in range(0,N-1):
        Sum=0
        for l in range(N-1):
            Sum+=F[l]*np.exp((2)*np.pi*(1j)*k*l/N)
        f.append(Sum/N)
    return np.array(f).real/np.pi

#MAIN
#User Inputs
fn=input("Filename:")
scale=float(input("Length of the image (mm):"))

#Read image
raw_image = Image.open("./"+fn)
image = raw_image.convert('L')
data=np.asarray(image)

#Calculate the spectrum for every row and average the spectra
PSDFs=[]
for row in data:
  row=row-np.mean(row)
  F=DiscreteFourier(row)
  PSDFs.append(F*np.conjugate(F))
PSDF_avg=np.sum(PSDFs,axis=0)/len(PSDFs)
ACF=InverseFourier(PSDF_avg)


#Corellation length
#..is the length at which the ACF decreased to 1/e=0.3678 of its starting value
i=0
while ACF[i]>ACF[0]*0.3679:
    i+=1
Lcorrel_px=(i-1)+(ACF[0]*0.3679-ACF[i-1])/(ACF[i]-ACF[i-1])
Lcorrel_mm=Lcorrel_px*scale/len(data[0])


#Outputs
print("Correlation length:", round(Lcorrel_mm,1), "mm")
print("Grain size", round(Lcorrel_mm*3.5,1),"+-",round(Lcorrel_mm,1),"mm")
plt.plot(np.linspace(0,scale,len(ACF)),ACF)
plt.plot([0,Lcorrel_mm,Lcorrel_mm],[ACF[0]*0.3679,ACF[0]*0.3679,-ACF[0]],color="gray",linestyle="dashed")
plt.xlabel(u"Shift (mm)")
plt.ylabel("ACF (1)")
plt.ylim([min(ACF),max(ACF)])
plt.xlim([0,scale/2])
plt.show()