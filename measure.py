# ================================================================
# Room impulse response measurement with an exponential sine sweep
# ----------------------------------------------------------------
# Author:                    Maja Taseska, ESAT-STADIUS, KU LEUVEN
# ================================================================
import os
import sounddevice as sd
import numpy as np
from matplotlib import pyplot as plt
from scipy.io.wavfile import write as wavwrite
#import imp

import stimulus as stim
import _parseargs as parse


# --- Parse command line arguments
args = parse._parse()
parse._defaults(args)
# -------------------------------

if args.listdev == True:

    print(sd.query_devices())
    sd.check_input_settings()
    sd.check_output_settings()
    print("Default input and output device: ", sd.default.device )

elif args.defaults == True:
    aa = np.load('_data/defaults.npy', allow_pickle = True).item()
    for i in aa:
        print (i + " => " + str(aa[i]))

elif args.setdev == True:

    sd.default.device[0] = args.inputdevice
    sd.default.device[1] = args.outputdevice

    sd.check_input_settings()
    sd.check_output_settings()
    print(sd.query_devices())
    print("Default input and output device: ", sd.default.device )
    print("Sucessfully selected audio devices. Ready to record.")

elif args.test == True:

    deltapeak = stim.test_deconvolution(args)
    plt.plot(deltapeak)
    plt.show()

else:

    # sounddevice parameters
    sd.default.samplerate = args.fs
    sd.default.dtype = 'float32'
    channels_in = args.inputChannelMap
    print("Input channels:",  channels_in)
    channels_out = args.outputChannelMap
    print("Output channels:",channels_out)

    # test signal parameters
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
    dirname = 'recorded/newrir1'
    while dirflag == False:
        if os.path.exists(dirname):
            print('Directory exists. Trying another name...')
            counter = counter + 1
            dirname = 'recorded/newrir' + str(counter)
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

    # Save in the lastRecording for a quick check
    np.save('recorded/lastRecording/RIR.npy',RIR)
    np.save( 'recorded/lastRecording/RIRac.npy',RIRtoSave)
    wavwrite( 'recorded/lastRecording/sigtest.wav',fs,testStimulus.signal)
    for idx in range(recorded.shape[1]):
        wavwrite('sigrec' + str(idx+1) + '.wav',fs,recorded[:,idx])
