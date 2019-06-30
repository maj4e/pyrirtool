# ================================================================
# Room impulse response measurement with an exponential sine sweep
# ----------------------------------------------------------------
# Author:                    Maja Taseska, ESAT-STADIUS, KU LEUVEN
# ================================================================
import os
import sounddevice as sd
import numpy as np
from matplotlib import pyplot as plt

# modules from this software
import stimulus as stim
import _parseargs as parse
import utils as utils

# --- Parse command line arguments and check defaults
flag_defaultsInitialized = parse._checkdefaults()
args = parse._parse()
parse._defaults(args)
# -------------------------------

if flag_defaultsInitialized == True:

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
        parse._defaults(args)

    elif args.test == True:

        deltapeak = stim.test_deconvolution(args)
        plt.plot(deltapeak)
        plt.show()

    else:

        # Create a test signal object, and generate the excitation
        testStimulus = stim.stimulus('sinesweep', args.fs);
        testStimulus.generate(args.fs, args.duration, args.amplitude,args.reps,args.startsilence, args.endsilence, args.sweeprange)

        # Record
        recorded = utils.record(testStimulus.signal,args.fs,args.inputChannelMap,args.outputChannelMap)

        # Deconvolve
        RIR = testStimulus.deconvolve(recorded)

        # Truncate
        lenRIR = 1.2;
        startId = testStimulus.signal.shape[0] - args.endsilence*args.fs -1
        endId = startId + int(lenRIR*args.fs)
        # save some more samples before linear part to check for nonlinearities
        startIdToSave = startId - int(args.fs/2)
        RIRtoSave = RIR[startIdToSave:endId,:]
        RIR = RIR[startId:endId,:]

        # Save recordings and RIRs
        utils.saverecording(RIR, RIRtoSave, testStimulus.signal, recorded, args.fs)
