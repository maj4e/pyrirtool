import soundfile as sf
from scipy.signal import blackman, hamming, hann, cosine, blackmanharris, tukey
from scipy.fftpack import fft, fftfreq, fftshift
from scipy import signal
import matplotlib.pyplot as plt
from importlib import reload
import sounddevice as sd
from scipy.io.wavfile import write as wavwrite
import numpy as np

from math import pi as pi
from numpy import log as log
from numpy import exp as exp
from numpy import sin as sin
from numpy import cos as cos

flag_plot = True

fs = 44100
sd.default.samplerate = fs
sd.default.dtype = 'float32'


# Get a few sine waves for Testing
lengths = 1
breaks = 0.5
taxis = np.arange(0,lengths,1/fs)
amplitude = 0.4

freqcs = [500,1000,4000]
pauses = np.zeros(shape = (int(breaks*fs),))


for idx in range(len(freqcs)):
    ff = freqcs[idx]
    sinwave = amplitude*np.sin(2*pi*taxis*ff)
    sinwave*signal.tukey(sinwave.shape[0],0.1)

    if idx == 0:
        sinsig = np.concatenate((pauses,sinwave,pauses),0)
    else:
        sinsig = np.concatenate((sinsig, sinwave,pauses),0)


myrec = sd.playrec(sinsig, samplerate=fs, channels = 2)
sd.wait()

# save recording
wavwrite('tone_rec.wav',fs,myrec)


if flag_plot:
    plt.plot(sinsig)
    plt.plot(myrec)
    plt.show()
