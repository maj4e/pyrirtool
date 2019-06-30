# ================================================================
# Parsing command line arguments
# ----------------------------------------------------------------
# Author:                    Maja Taseska, ESAT-STADIUS, KU LEUVEN
# ================================================================
import argparse
import numpy as np
import os


# === FUNCTION: Parsing command line arguments
def _parse():

    # Load the defaults
    defaults = np.load('_data/defaults.npy', allow_pickle = True).item()

    parser = argparse.ArgumentParser(description='Setting the parameters for RIR measurement using exponential sine sweep \n ----------------------------------------------------------------------')
    #---
    parser.add_argument("-f", "--fs", type = int, help=" The sampling rate (make sure it matches that of your audio interface). Default: 44100 Hz.", default = defaults['fs'])
    #---
    parser.add_argument("-dur", "--duration", type = int, help=" The duration of a single sweep. Default: 15 seconds.", default = defaults['duration'])
    #---
    parser.add_argument("-r", "--reps", type = int, help = "Number of repetitions of the sinesweep. Default: 1.", default = defaults['reps'])
    #---
    # parser.add_argument("-fr", "--frange", type =  tuple, help = "Frequency range of the sweep (f_min, f_max). Default: (0.01,20000) Hz.", default = (0.01,20000))
    #---
    parser.add_argument("-a", "--amplitude", type = float, help = "Amplitude of the sine. Default: 0.7",default = defaults['amplitude'])
    #---
    parser.add_argument("-ss", "--startsilence", type = int, help = "Duration of silence at the start of a sweep, in seconds. Default: 1.", default = defaults['startsilence'])

    parser.add_argument("-frange", "--sweeprange", nargs='+', type=int, help = "Frequency range of the sweep", default = defaults['sweeprange'])
    #---
    parser.add_argument("-es", "--endsilence", type = int, help = "Duration of silence at the end of a sweep, in seconds. Default: 1.", default = defaults['endsilence'])
    #---
    parser.add_argument("-chin", "--inputChannelMap", nargs='+', type=int, help = "Input channel mapping", default = defaults['inputChannelMap'])

    parser.add_argument("-chou", "--outputChannelMap", nargs='+', type=int, help = "Output channel mapping", default = defaults['outputChannelMap'])


    #--- arguments for checking and selecting audio interface
    parser.add_argument("-outdev", "--outputdevice", type = int, help = "Output device ID.", default = defaults['outputdevice'])

    parser.add_argument("-indev", "--inputdevice", type = int, help = "Input device ID.",default = defaults['inputdevice'])

    parser.add_argument('--listdev', help='List the available devices, indicating the default one',action='store_true')

    parser.add_argument('--defaults', help = 'List the default measurement parameters (devices, channels, and signal properties)', action = 'store_true')

    parser.add_argument('--setdev', help='Use this keyword in order to change the default audio interface.',action='store_true')

    parser.add_argument('--test', help = 'Just for debugging: check the output of deconvolution applied directly to the computer-generated sinesweep', action='store_true')


    args = parser.parse_args()

    return args


#------------------------------------------------
# === FUNCTION: Update defaults

def _defaults(args):

    if (args.listdev == False and  args.defaults == False):
        defaults = {
            "amplitude": args.amplitude,
            "duration" : args.duration,
            "startsilence": args.startsilence,
            "endsilence" : args.endsilence,
            "reps" : args.reps,

            "fs" : args.fs,
            "inputChannelMap" : args.inputChannelMap,
            "outputChannelMap": args.outputChannelMap,
            "inputdevice": args.inputdevice,
            "outputdevice": args.outputdevice,
            "sweeprange": args.sweeprange
        }
        np.save('_data/defaults.npy', defaults)


#-------------------------------------------------------------
# === FUNCTION: Check if a file with defaults exists. If not, make one

def _checkdefaults():

    flag_defaultsInitialized = True

    if not os.path.exists('_data'):
        os.makedirs('_data')

    if not os.path.exists('_data/defaults.npy'):
        print("Default settings not detected. Creating a defaults file in _data")
        defaults = {
            "amplitude": 0.2,
            "duration" : 10,
            "startsilence": 1,
            "endsilence" : 1,
            "reps" : 1,

            "fs" : 44100,
            "inputChannelMap" : [1],
            "outputChannelMap": [1],
            "inputdevice": 0,
            "outputdevice": 1,
            "sweeprange": [0 , 0]
        }
        np.save('_data/defaults.npy', defaults)
        flag_defaultsInitialized = False

    return flag_defaultsInitialized
