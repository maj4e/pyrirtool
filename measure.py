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

# module with the main code
import stimulus as stim
imp.reload(stim)


# --- parse command line arguments
parser = argparse.ArgumentParser(description='Setting the parameters for RIR measurement using exponential sine sweep')
#---
parser.add_argument("-f", "--fs", type = int, help=" The sampling rate (make sure it matches that of your audio interface). Default: 44100 Hz.", default = 44100)
#---
parser.add_argument("-dur", "--duration", type = int, help=" The duration of a single sweep. Default: 15 seconds.", default = 20)
#---
parser.add_argument("-r", "--reps", type = int, help = "Number of repetitions of the sinesweep. Default: 1.", default = 1)
#---
# parser.add_argument("-fr", "--frange", type =  tuple, help = "Frequency range of the sweep (f_min, f_max). Default: (0.01,20000) Hz.", default = (0.01,20000))
#---
parser.add_argument("-a", "--amplitude", type = float, help = "Amplitude of the sine. Default: 0.7",default = 0.5)
#---
parser.add_argument("-ss", "--startsilence", type = int, help = "Duration of silence at the start of a sweep, in seconds. Default: 1.", default = 1)
#---
parser.add_argument("-es", "--endsilence", type = int, help = "Duration of silence at the end of a sweep, in seconds. Default: 1.", default = 2)
#---
#parser.add_argument('--chin', nargs='+', type=int)
#parser.add_argument('--chou', nargs='+', type=int)

parser.add_argument("-chin", "--inputChannelMap", nargs='+', type=int, help = "Input channel mapping")
parser.add_argument("-chou", "--outputChannelMap", nargs='+', type=int, help = "Output channel mapping")
#---
#nargs='+', type=int

#--- arguments for checking and selecting audio interface
#parser.add_argument("-outdev", "--outputdevice", type = int, help = "Output device ID.")
#parser.add_argument("-indev", "--inputdevice", type = int, help = "Input device ID.")
parser.add_argument('--listdev', help='List the available devices, indicating the default one',
    action='store_true')
#parser.add_argument('--setdev', help='Use this keyword in order to change the default audio interface.',action='store_true')
parser.add_argument('--test', help = 'Just for debugging: check the output of deconvolution applied directly to the computer-generated sinesweep', action='store_true')

args = parser.parse_args()
# -------------------------------

sd.default.device = [2,2]


if args.listdev == True:

    print(sd.query_devices())
    sd.check_input_settings()
    sd.check_output_settings()
    print("Default input and output device: ", sd.default.device )

# elif args.setdev == True:
#
#     if args.inputdevice is not None:
#         sd.default.device[0] = args.inputdevice
#
#     if args.outputdevice is not None:
#         sd.default.device[1] = args.outputdevice
#
#     sd.check_input_settings()
#     sd.check_output_settings()
#
#     print(sd.query_devices())
#     print("Default input and output device: ", sd.default.device )
#     print("Sucessfully selected audio devices. Ready to record.")

elif args.test == True:

    type = 'sinesweep'
    fs = args.fs
    duration = args.duration
    amplitude = args.amplitude
    repetitions = args.reps
    silenceAtStart = args.startsilence
    silenceAtEnd = args.endsilence

    if repetitions > 1:
        raise NameError('Synchronous time averaging is not recommended for exponential sweeps. A good averaging method is not implemented. Please use a single long sine sweep (e.g. 15 sec.)')


    # Create a test signal object, and generate the excitation
    testStimulus = stim.stimulus(type,fs);
    testStimulus.generate(fs, duration, amplitude,repetitions,silenceAtStart, silenceAtEnd)

    deltapeak = testStimulus.deconvolve(testStimulus.signal)
    startid = duration*fs + silenceAtStart*fs -1
    endid = deltapeak.shape[0]
    plt.plot(deltapeak[startid::],'o-', markersize = 5)
    plt.xlim([-1,20])
    plt.show()

else:

    # sound device parameters, input and output channels

    sd.default.samplerate = args.fs
    sd.default.dtype = 'float32'

    if args.inputChannelMap is not None:
        channels_in = args.inputChannelMap
        print("Input channels:",  channels_in)
    else:
        channels_in= [1]

    if args.outputChannelMap is not None:
        channels_out = args.outputChannelMap
        print("Output channels:",channels_out)
    else:
        channels_out = [1]


    # Set excitation parameters
    type = 'sinesweep'
    fs = args.fs
    duration = args.duration
    amplitude = args.amplitude
    repetitions = args.reps
    silenceAtStart = args.startsilence
    silenceAtEnd = args.endsilence

    # Create a test signal object, and generate the excitation
    testStimulus = stim.stimulus(type,fs);
    testStimulus.generate(fs, duration, amplitude,repetitions,silenceAtStart, silenceAtEnd)

    # Start the recording
    recorded = sd.playrec(testStimulus.signal, samplerate=fs, input_mapping = channels_in,output_mapping = channels_out)
    sd.wait()

    # Get the room impulse response
    RIR = testStimulus.deconvolve(recorded)
    # length after truncation
    lenRIR = 1.2;
    startId = testStimulus.signal.shape[0] - silenceAtEnd*fs -1
    endId = startId + int(lenRIR*fs)

    # save some more samples before linear part to check for nonlinearities
    startIdToSave = startId - int(fs/2)
    RIRtoSave = RIR[startIdToSave:endId,:]
    RIR = RIR[startId:endId,:]


    # Create a directory for the new recording
    dirflag = False
    counter = 1
    dirname = 'newrir1'
    while dirflag == False:
        if os.path.exists(dirname):
            print('Directory exists. Trying another name...')
            counter = counter + 1
            dirname = 'newrir' + str(counter)
        else:
            os.mkdir(dirname)
            print('Success! Recording saved in directory ' + dirname)
            dirflag = True


    # Saving the RIRs and the captured signals
    np.save(dirname+ '/RIR.npy',RIR)
    np.save(dirname+ '/RIRac.npy',RIRtoSave)
    wavwrite(dirname+ '/sigtest.wav',fs,testStimulus.signal)
    #wavwrite(dirname+ '/RIR.wav',fs,RIR)
    for idx in range(recorded.shape[1]):
        wavwrite(dirname+ '/sigrec' + str(idx+1) + '.wav',fs,recorded[:,idx])
        wavwrite(dirname+ '/RIR' + str(idx+1) + '.wav',fs,RIR[:,idx])

    # Save them in root for a quick check
    np.save('RIR.npy',RIR)
    np.save( 'RIRac.npy',RIRtoSave)
    wavwrite( 'sigtest.wav',fs,testStimulus.signal)
    for idx in range(recorded.shape[1]):
        #wavwrite('RIR' + str(idx+1) + '.wav',fs,RIR[:,idx])
        wavwrite('sigrec' + str(idx+1) + '.wav',fs,recorded[:,idx])
