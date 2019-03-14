import soundfile as sf
from scipy.signal import blackman, hamming, hann, cosine, blackmanharris, tukey
from scipy.fftpack import fft, fftfreq, fftshift
from scipy import signal
import matplotlib.pyplot as plt
from importlib import reload
import sounddevice as sd
from scipy.io.wavfile import write as wavwrite
import numpy as np

flag_plot = False

fs = 44100
sd.default.samplerate = fs
sd.default.dtype = 'float32'


lenNoise = 5 # in seconds
powNoise = 0.03
wn = np.random.randn(lenNoise*fs)*np.sqrt(powNoise)
#wavwrite('whiteNoise.wav',fs,wn)
#noisesig, fs = sf.read('whiteNoise.wav') # mixture
wn = wn*signal.tukey(wn.shape[0],0.1)

myrec = sd.playrec(wn, samplerate=fs, channels = 2)
sd.wait()

# save recording
wavwrite('wn_rec.wav',fs,myrec)

if flag_plot:
    plt.plot(myrec)
    plt.show()
