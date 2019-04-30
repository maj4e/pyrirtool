#!/Users/mtaseska/.envs/PyPlayrec/bin/python

# temporary
import imp
import os

# required
import argparse
import sounddevice as sd
import numpy as np
from matplotlib import pyplot as plt
from scipy.io.wavfile import write as wavwrite
import soundfile as sf

# module with the main code
import stimulus as stim


# load the file from Randy
yy, fs = sf.read('Stimuli/measurement_file.wav')

amplitudes = [0.2,0.4,0.6,0.8]
durations = [5,10,15]

ampstring = ['02','04', '06', '08']
durstring = ['05', '10', '15']

# set the sine sweep parameters
type = 'sinesweep'
repetitions = 2
silenceAtStart = 1
silenceAtEnd = 3


for aidx in range(len(amplitudes)):
    for didx in range(len(durations)):

        duration = durations[didx]
        amplitude = amplitudes[aidx]
        testStimulus = stim.stimulus(type,fs);
        testStimulus.generate(fs, duration, amplitude,repetitions,silenceAtStart, silenceAtEnd)
        final = np.concatenate((testStimulus.signal[:,0],yy))

        filename = 'stimuli/measurement_file/stimulus_amp' + ampstring[aidx] + '_dur' + durstring[didx] + '.wav'
        filename_s = 'stimuli/sweep/sweep_amp' + ampstring[aidx] + '_dur' + durstring[didx] + '.wav'
        wavwrite(filename,fs,final)
        wavwrite(filename_s,fs,testStimulus.signal[:,0])



#
