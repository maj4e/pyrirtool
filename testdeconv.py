# temporary
import imp

# required
import argparse
import sounddevice as sd
import numpy as np
from matplotlib import pyplot as plt

from math import pi as pi
from numpy import log as log
from numpy import exp as exp
from numpy import sin as sin
from numpy import cos as cos
from scipy import signal
from scipy.signal import fftconvolve

# module with the main code
import stimulus as stim

parser = argparse.ArgumentParser(description='Testing deconvolution')
parser.add_argument('--fadein', default = 0, type = float)
parser.add_argument('--fadeout', default = 0, type = float)
parser.add_argument('--crop', action='store_true', default = True)
args = parser.parse_args()


#=======================================
fs  = 44100
f1 = 0.1       # start of sweep in Hz.
f2 = fs/2         # end of sweep in Hz.

duration = 40
A = 0.7
rep = 1
silenceAtStart = 2
silenceAtEnd = 1

w1 = 2*pi*f1/fs     # start of sweep in rad/sample
w2 = 2*pi*f2/fs     # end of sweep in rad/sample
lw = log(w2/w1)

numSamples = duration*fs
taxis = np.arange(0,numSamples,1)/(numSamples-1)
sinsweep = A * sin(w1*(numSamples-1)/lw * (exp(taxis*lw)-1));


plt.plot(sinsweep)

# Get the inverse filter
envelope = (w2/w1)**(-taxis);
scaling = pi*numSamples*(w1/w2-1)/(2*(w2-w1)*log(w1/w2))*(w2-w1)/pi;
invfilter = np.flipud(sinsweep)*envelope
invfilter = invfilter/A**2/scaling
Lp = (silenceAtStart + silenceAtEnd)*fs + numSamples;


if args.crop == True:
    k = np.flipud(sinsweep)
    error = 1
    counter = 0
    while error > 0.005:
        error = np.abs(k[counter])
        counter = counter+1

    k = k[counter::]
    sinsweep_hat = np.flipud(k)
    sinsweep = np.zeros(shape = (numSamples,))
    sinsweep[0:sinsweep_hat.shape[0]] = sinsweep_hat
    print(counter)


# Adjust the tapering of the sinesweep
taperStart = signal.tukey(numSamples,args.fadein)
taperEnd = signal.tukey(numSamples,args.fadeout)
taperWindow = np.ones(shape = (numSamples,))
taperWindow[0:int(numSamples/2)] = taperStart[0:int(numSamples/2)]
taperWindow[int(numSamples/2):numSamples] = taperEnd[int(numSamples/2):numSamples]
sinsweep = taperWindow*sinsweep



zerostart = np.zeros(shape = (silenceAtStart*fs,))
zeroend = np.zeros(shape = (silenceAtEnd*fs,))
sinsweep = np.concatenate((np.concatenate((zerostart, sinsweep), axis = 0), zeroend), axis=0)
res = fftconvolve(invfilter,sinsweep)


#plt.plot(k[0:100])

# hat = True
# # The convolutional inverse
# if hat == False:
#
#     envelope = (w2/w1)**(-taxis);
#     scaling = pi*numSamples*(w1/w2-1)/(2*(w2-w1)*log(w1/w2))*(w2-w1)/pi;
#     invfilter = np.flipud(sinsweep)*envelope
#     invfilter = invfilter/A**2/scaling
#     Lp = (silenceAtStart + silenceAtEnd)*fs + numSamples;
#
#     # fade-in window. Fade out removed because causes ringing
#     taperStart = signal.tukey(sinsweep.shape[0],0.1)
#     taperWindow = np.ones(shape = (sinsweep.shape[0],))
#     taperWindow[0:int(sinsweep.shape[0]/2)] = taperStart[0:int(sinsweep.shape[0]/2)]
#     sinsweep = taperWindow*sinsweep
#
#     zerostart = np.zeros(shape = (silenceAtStart*fs,))
#     zeroend = np.zeros(shape = (silenceAtEnd*fs,))
#     sinsweep = np.concatenate((np.concatenate((zerostart, sinsweep), axis = 0), zeroend), axis=0)
#     res = fftconvolve(invfilter,sinsweep)
#
# else:
#     envelope = (w2/w1)**(-taxis_hat);
#     scaling = pi*numSamples_hat*(w1/w2-1)/(2*(w2-w1)*log(w1/w2))*(w2-w1)/pi;
#     invfilter = np.flipud(sinsweep_hat)*envelope
#     invfilter = invfilter/A**2/scaling
#     Lp = (silenceAtStart + silenceAtEnd)*fs + numSamples_hat;
#
#     # fade-in window. Fade out removed because causes ringing
#     taperStart = signal.tukey(sinsweep_hat.shape[0],0.1)
#     taperWindow = np.ones(shape = (sinsweep_hat.shape[0],))
#     taperWindow[0:int(sinsweep_hat.shape[0]/2)] = taperStart[0:int(sinsweep_hat.shape[0]/2)]
#     sinsweep_hat = taperWindow*sinsweep_hat
#
#     zerostart = np.zeros(shape = (silenceAtStart*fs,))
#     zeroend = np.zeros(shape = (silenceAtEnd*fs,))
#     sinsweep_hat = np.concatenate((np.concatenate((zerostart, sinsweep_hat), axis = 0), zeroend), axis=0)
#     res = fftconvolve(invfilter,sinsweep_hat)
#

# Add silences and tapering to the sinesweep
# The shape of the result has len(invfilter) + len(sinsweep)-1
#startid = (sinsweep_hat.shape[0]-(silenceAtEnd)*fs-1) - 120000

kk = np.argmax(res)

startid = kk - 100
#endid = sinsweep.shape[0]-(silenceAtEnd)*fs + invfilter.shape[0]
endid = kk + 100

plt.figure(figsize = (15,5))
plt.plot(res)
plt.xlim([startid,endid])
plt.show()
