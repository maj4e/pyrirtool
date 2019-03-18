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


#=======================================
fs  = 44100
f1 = 0.01            # start of sweep in Hz.
f2 = fs/2         # end of sweep in Hz.

duration = 12
A = 0.7
rep = 2
silenceAtStart = 2
silenceAtEnd = 1

w1 = 2*pi*f1/fs     # start of sweep in rad/sample
w2 = 2*pi*f2/fs     # end of sweep in rad/sample
lw = log(w2/w1)

numSamples = duration*fs
taxis = np.arange(0,numSamples,1)/(numSamples-1)
sinsweep = A * sin(w1*(numSamples-1)/lw * (exp(taxis*lw)-1));


# Find zero crossing to avoid the need for fadeout
k = np.flipud(sinsweep)
error = 1
counter = 0
while error > 0.01:
    error = np.abs(k[counter])
    counter = counter+1


k = k[counter::]
sinsweep_hat = np.flipud(k)
numSamples_hat = sinsweep_hat.shape[0]
taxis_hat = taxis[0:numSamples_hat]


#plt.plot(k[0:100])

hat = True
# The convolutional inverse
if hat == False:
    envelope = (w2/w1)**(-taxis);
    scaling = pi*numSamples*(w1/w2-1)/(2*(w2-w1)*log(w1/w2))*(w2-w1)/pi;
    invfilter = np.flipud(sinsweep)*envelope
    invfilter = invfilter/A**2/scaling
    Lp = (silenceAtStart + silenceAtEnd)*fs + numSamples;
    zerostart = np.zeros(shape = (silenceAtStart*fs,))
    zeroend = np.zeros(shape = (silenceAtEnd*fs,))
    sinsweep = np.concatenate((np.concatenate((zerostart, sinsweep), axis = 0), zeroend), axis=0)
    res = fftconvolve(invfilter,sinsweep)

else:
    envelope = (w2/w1)**(-taxis_hat);
    scaling = pi*numSamples_hat*(w1/w2-1)/(2*(w2-w1)*log(w1/w2))*(w2-w1)/pi;
    invfilter = np.flipud(sinsweep_hat)*envelope
    invfilter = invfilter/A**2/scaling
    Lp = (silenceAtStart + silenceAtEnd)*fs + numSamples_hat;
    zerostart = np.zeros(shape = (silenceAtStart*fs,))
    zeroend = np.zeros(shape = (silenceAtEnd*fs,))
    sinsweep_hat = np.concatenate((np.concatenate((zerostart, sinsweep_hat), axis = 0), zeroend), axis=0)
    res = fftconvolve(invfilter,sinsweep_hat)


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
