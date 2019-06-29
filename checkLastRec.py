# @Author:Maja Taseska, ESAT-STADIUS, KU LEUVEN

# Vizualizing the results from the last recording

import numpy as np
from matplotlib import pyplot as plt
import soundfile as sf   # for loading wavfiles
from scipy.signal import spectrogram
import os

fs = 44100

# THE ROOM IMPULSE RESPONSES
RIR = np.load('RIR.npy')
maxval = np.max(RIR)
minval = np.min(RIR)
taxis = np.arange(0,RIR.shape[0]/fs,1/fs)

# Plot all on a single figure
# plt.figure(figsize = (10,6))
# plt.plot(taxis,RIR)
# plt.ylim((minval+0.05*minval,maxval+0.05*maxval))

# Plot them as subplots
numplots = RIR.shape[1]
#height = numplots*3
#fig = plt.figure(figsize = (10,height))
for idx in range(numplots):
    fig = plt.figure(figsize = (9,3))
    plt.plot(RIR[:,idx])
    plt.ylim((minval+0.05*minval,maxval+0.05*maxval))
    plt.title('RIR Microphone '+ str(idx + 1))
    #ax = fig.add_subplot(numplots,1,idx+1)
    #plt.plot(taxis,RIR[:,idx])


# The emitted and recorded signals
sigtest, ff = sf.read('sigtest.wav')

sigrec = np.zeros(shape = (sigtest.shape[0],RIR.shape[1]))
for idx in range(RIR.shape[1]):
    tmp, ff = sf.read('sigrec' + str(idx+1)+ '.wav')
    sigrec[:,idx] = tmp

fig = plt.figure(figsize = (9,3))
plt.plot(sigtest, color = 'r')
plt.plot('Computer-generated test signal')

for idx in range(numplots):
    fig = plt.figure(figsize = (9,3))
    plt.plot(sigrec[:,idx], color = 'k')
    plt.title('Recording at Microphone '+ str(idx + 1))

# fig = plt.figure(figsize = (14,7))
# fig.subplots_adjust(left=0.09, bottom=0.1, right=0.99, top=0.99, wspace=0.2, hspace = 0.35)
# ax = fig.add_subplot(2,1,1)
# plt.plot(sigtest,color = 'r')
# plt.title('Test signal', fontsize = 14)
# ax = fig.add_subplot(2,1,2)
# plt.plot(sigrec, color = 'k')
# plt.title('Recorded signals', fontsize = 14)


# Spectrograms of the emitted and the recorded signals
# add a tiny amount of noise to avoid zeros
tmp = np.random.rand(sigtest.shape[0],)
sigtest = sigtest + 0.00001*tmp

nperseg = 2**11
sweepnfft = nperseg
faxis = np.linspace(0,fs,sweepnfft)
faxis = faxis[0:int(sweepnfft/2)]

ff,tt,spectest = spectrogram(sigtest, nperseg = nperseg, nfft = sweepnfft, noverlap = int(0.5*nperseg) , scaling = 'spectrum' )
spectest = spectest[1::,:]

for idx in range(sigrec.shape[1]):

    ff,tt,specrec = spectrogram(sigrec[:,idx], nperseg = nperseg, nfft = sweepnfft, noverlap = int(0.5*nperseg) , scaling = 'spectrum' )

    specrec = specrec[1::,:]

    taxis = np.arange(0,spectest.shape[1],1)

    fig = plt.figure(figsize = (13,6))
    ax = fig.add_subplot(1,2,1)
    #p = ax.pcolormesh(taxis,faxis,20*np.log10(spectest), cmap = 'hot',vmin = -100, vmax = -10)
    p = ax.pcolormesh(taxis,faxis,20*np.log10(spectest), cmap = 'hot' ,vmin = -130)
    ax.set_yscale('log')
    ax.set_ylim((20,20000))
    cb = fig.colorbar(p, ax=ax,orientation = 'horizontal', fraction = 0.06)
    ax = fig.add_subplot(1,2,2)
    #p = ax.pcolormesh(taxis,faxis,20*np.log10(specrec), cmap = 'hot',vmin = -100, vmax = -10)
    p = ax.pcolormesh(taxis,faxis,20*np.log10(specrec), cmap = 'hot',vmin = -130)
    ax.set_yscale('log')
    ax.set_ylim((20,20000))
    cb = fig.colorbar(p, ax=ax,orientation = 'horizontal', fraction = 0.06)
    fig.suptitle('Microphone '+ str(idx + 1))

plt.show()
