import rirstuff as rir
import soundfile as sf
from scipy.signal import blackman, hamming, hann, cosine, blackmanharris, tukey
from scipy.fftpack import fft, fftfreq, fftshift
from scipy import signal
import matplotlib.pyplot as plt
from importlib import reload
import sounddevice as sd
from scipy.io.wavfile import write as wavwrite
import numpy as np
reload(rir)

# Set these to false if only recording desired without RIR computation

flag_getrir = True
flag_plt = True

# PLAYBACK
#============
# sounddevice.play(data, samplerate=None, mapping=None, blocking=False, loop=False)
# mapping: put the output channels as a list

# PLAYBACK AND RECORDING
#==========================
# sounddevice.playrec(data, samplerate=None, channels=None, dtype=None, out=None, input_mapping=None, output_mapping=None, blocking=False, **kwargs)
# channels: number of input channels outputs obtained from data.shape - automatic
# input_mapping and output_mapping - the list of channel numbers to record/play

# Test the hardware and stuff
# sd.query_devices()
# sd.default.device
# sd.check_input_settings()
# sd.check_output_settings()



# SAMPLING RATE AND SOUND CARD SETTINGS
fs = 44100
sd.default.samplerate = fs
sd.default.dtype = 'float32'


#EXCITATION SETTINGS
type = 'sinesweep'
duration = 7
A = 0.7
rep = 2
silenceAtStart = 1
silenceAtEnd = 1


# CALL THE CONSTRUCTOR FOR THE STIMULUS
systemProbe = rir.stimulus(type,fs);
systemProbe.generateStimulus(fs,duration,A, rep,silenceAtStart, silenceAtEnd)

# PLAY THE STIMULUS AND RECORD
myrecording = sd.playrec(systemProbe.excitation, samplerate=fs, channels=2)
sd.wait()
wavwrite('newrecording.wav',fs,myrecording)


if flag_getrir:

    RIRs = systemProbe.deconvolve(myrecording)

    # some truncation
    lenRIR = 1.2; # in seconds, after desired truncation
    startId = (duration+silenceAtStart)*fs # keep some non-causal part also to check nonlinearities
    endId = int(np.ceil((duration+silenceAtStart + lenRIR)*fs))
    RIRs = RIRs[startId:endId,:]

    if flag_plt:
        rir.analyseRIR(RIRs[:,0],fs)





# SAVE AND ANALYZE
#wavwrite('newRIRs.wav',fs,RIRs)
