import os
from scipy.io.wavfile import write as wavwrite
import numpy as np
import sounddevice as sd


#--------------------------
def record(testsignal,fs,inputChannels,outputChannels):

    sd.default.samplerate = fs
    sd.default.dtype = 'float32'
    print("Input channels:",  inputChannels)
    print("Output channels:", outputChannels)

    # Start the recording
    recorded = sd.playrec(testsignal, samplerate=fs, input_mapping = inputChannels,output_mapping = outputChannels)
    sd.wait()

    return recorded


#--------------------------
def saverecording(RIR, RIRtoSave, testsignal, recorded, fs):

        dirflag = False
        counter = 1
        dirname = 'recorded/newrir1'
        while dirflag == False:
            if os.path.exists(dirname):
                counter = counter + 1
                dirname = 'recorded/newrir' + str(counter)
            else:
                os.mkdir(dirname)
                dirflag = True

        # Saving the RIRs and the captured signals
        np.save(dirname+ '/RIR.npy',RIR)
        np.save(dirname+ '/RIRac.npy',RIRtoSave)
        wavwrite(dirname+ '/sigtest.wav',fs,testsignal)

        for idx in range(recorded.shape[1]):
            wavwrite(dirname+ '/sigrec' + str(idx+1) + '.wav',fs,recorded[:,idx])
            wavwrite(dirname+ '/RIR' + str(idx+1) + '.wav',fs,RIR[:,idx])

        # Save in the recorded/lastRecording for a quick check
        np.save('recorded/lastRecording/RIR.npy',RIR)
        np.save( 'recorded/lastRecording/RIRac.npy',RIRtoSave)
        wavwrite( 'recorded/lastRecording/sigtest.wav',fs,testsignal)
        for idx in range(recorded.shape[1]):
            wavwrite('sigrec' + str(idx+1) + '.wav',fs,recorded[:,idx])
            wavwrite(dirname+ '/RIR' + str(idx+1) + '.wav',fs,RIR[:,idx])


        print('Success! Recording saved in directory ' + dirname)
