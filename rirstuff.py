# Imports required for the class methods
from math import pi as pi
from numpy import log as log
from numpy import exp as exp
from numpy import sin as sin
from numpy import cos as cos
from scipy.signal import fftconvolve
from scipy import signal
import numpy as np



# Imports for testing the module. Remove when test phase is over
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftfreq, fftshift
from scipy.signal import spectrogram
import soundfile as sf

class stimulus:

    # Constructor
    def __init__(self,stimulusType, samplingRate):

        self.type = stimulusType
        self.fs = samplingRate
        self.repetitions = 0
        self.Lp = []
        self.excitation = []
        self.invfilter = []

    # Generate the stimulus and populate the required attributes (stimulus-dependent)
    def generateStimulus(self, fs, duration, amplitude, repetitions, silenceAtStart, silenceAtEnd):

        if self.type == 'sinesweep':

            f1 = 0.1            # start of sweep in Hz. Used to be 0.01
            f2 = 20000           # end of sweep in Hz. Used to be fs/2

            w1 = 2*pi*f1/fs     # start of sweep in rad/sample
            w2 = 2*pi*f2/fs     # end of sweep in rad/sample

            numSamples = duration*fs
            sinsweep = np.zeros(shape = (numSamples,1))
            taxis = np.arange(0,numSamples,1)/(numSamples-1)

            # EXPONENTIAL SINE SWEEP PROPOSED BY FARINA
            lw = log(w2/w1)

            # tapering window (currently no tapering as sides are 0)
            taperStart = signal.tukey(numSamples,0)
            taperEnd = signal.tukey(numSamples,0.01)
            taperWindow = np.ones(shape = (numSamples,))
            taperWindow[0:int(numSamples/2)] = taperStart[0:int(numSamples/2)]
            taperWindow[int(numSamples/2):numSamples] = taperEnd[int(numSamples/2):numSamples]

            sinsweep = taperWindow*amplitude * sin(w1*(numSamples-1)/lw * (exp(taxis*lw)-1));

            # CREATE THE INVERSE FILTER
            envelope = (w2/w1)**(-taxis); # Holters2009, Eq.(9)
            # Note: this envelope is used to compensate for the non-white spectrum. Derivation?
            invfilter = np.flipud(sinsweep)*envelope

            # Final excitation including repetition and pauses
            sinsweep = np.expand_dims(sinsweep,axis = 1)
            zerostart = np.zeros(shape = (silenceAtStart*fs,1))
            zeroend = np.zeros(shape = (silenceAtEnd*fs,1))
            sinsweep = np.concatenate((np.concatenate((zerostart, sinsweep), axis = 0), zeroend), axis=0)
            sinsweep = np.transpose(np.tile(np.transpose(sinsweep),repetitions))

            scaling = pi*numSamples*(w1/w2-1)/(2*(w2-w1)*log(w1/w2))*(w2-w1)/pi; # Holters2009, Eq.10

            # Populate the class attributes
            self.Lp = (silenceAtStart + silenceAtEnd + duration)*fs;
            #self.scaling = pi*numSamples*(w1/w2-1)/(2*(w2-w1)*log(w1/w2))*(w2-w1)/pi; # Holters2009, Eq.10
            self.invfilter = invfilter/amplitude**2/scaling
            self.repetitions = repetitions
            self.excitation = sinsweep


        else:

            print("Excitation type not implemented")
            return


    # Deconvolution: different method should be implemented for each stimulus type
    # Currently only sinesweep supported

    def deconvolve(self,systemOutput):

        if self.type == 'sinesweep':

            numChans = systemOutput.shape[1]
            tmplen = self.invfilter.shape[0] + self.Lp-1;
            RIRs = np.zeros(shape = (tmplen,numChans))

            for idx in range(0,numChans):

                currentChannel = systemOutput[0:self.repetitions*self.Lp,idx]

                # Average over the repetitions
                sig_reshaped = currentChannel.reshape((self.repetitions,self.Lp))
                sig_avg = np.mean(sig_reshaped,axis = 0)

                # Deconvolution
                RIRs[:,idx] = fftconvolve(self.invfilter,sig_avg);

            return RIRs

        else:

            print("Excitation type not implemented")
            return


# End of class definition
# ===========================================================================

# Functions outside of the class
def computeEnergyDecayCurve(h, integrationStart):

    idmax = np.argmax(np.absolute(h))
    echogram = h[idmax:h.shape[0]]**2

    intSchroeder_full = np.flipud(np.cumsum(np.flipud(echogram)))
    intSchroeder = np.flipud(np.cumsum(np.flipud(echogram[0:integrationStart])))

    EDC = 10*np.log10(intSchroeder/np.amax(intSchroeder))
    EDC_full = 10*np.log10(intSchroeder_full/np.amax(intSchroeder_full))

    return EDC, EDC_full



def analyseRIR(h,fs):

    startOfEDCIntegral = 0.5 # in seconds
    endSample = int(startOfEDCIntegral*fs)
    endidx = np.min([h.shape[0],endSample])

    EDC, EDC_full = computeEnergyDecayCurve(h,endidx)

    # Get the relevant points for early decay time (EDT), T30, and T60
    idxs = np.nonzero(EDC < 0)
    idxs = idxs[0]
    index_0dB = idxs[0]
    #---
    idxs = np.nonzero(EDC < -5)
    idxs = idxs[0]
    index_5dB = idxs[0]
    #---
    idxs = np.nonzero(EDC < -10)
    idxs = idxs[0]
    index_10dB = idxs[0]
    #---
    idxs = np.nonzero(EDC < -35)
    idxs = idxs[0]
    index_35dB = idxs[0]
    #---
    idxs = np.nonzero(EDC < -65)
    idxs = idxs[0]
    index_65dB = idxs[0]

    # Get the slopes and biases of the relevant lines
    slope60 = (EDC[index_65dB] - EDC[index_5dB])/(index_65dB-index_5dB)
    slope30 = (EDC[index_35dB] - EDC[index_5dB])/(index_35dB-index_5dB)
    slopeEDT = (EDC[index_10dB] - EDC[index_0dB])/(index_10dB-index_0dB)

    bias60 = EDC[index_5dB] - slope60* index_5dB
    bias30 = EDC[index_5dB] - slope30* index_5dB
    biasEDT = EDC[index_0dB] - slopeEDT* index_0dB

    xx = np.arange(0,30000,1)
    yy60 = slope60*xx + bias60
    yy30 = slope30*xx + bias30
    yyEDT = slopeEDT*xx + biasEDT

    # Get the reverberation time in seconds and format strings for the legend
    T30 = -60/slope30/fs
    T60 = -60/slope60/fs
    EDT = -60/slopeEDT/fs
    str60 = str(T60)
    str30 = str(T30)
    strEDT = str(EDT)
    str60 = str60[0:5]
    str30 = str30[0:5]
    strEDT = strEDT[0:5]


    # PLOTTING THE RESULTS
    fig, axes = plt.subplots(2,1, figsize = (16,10))
    axes[0].plot(h)
    axes[0].set_xlim([0,fs*1])
    axes[1].plot(EDC,color = "black")
    axes[1].plot(EDC_full)
    axes[1].grid(color='r', linestyle=':')
    axes[1].plot(xx[0:index_35dB],yy30[0:index_35dB],  "--", color = "red",linewidth = 2)
    axes[1].plot(xx[0:index_65dB],yy60[0:index_65dB], "--",  color = "blue",linewidth = 2)
    h3, = axes[1].plot(index_0dB,EDC[index_0dB],'p', color = "black",markersize = 7, label = 'Early decay time = ' + strEDT+ ' sec')
    axes[1].plot(index_10dB,EDC[index_10dB],'p', color = "black",markersize = 7)
    axes[1].plot(index_5dB,EDC[index_5dB],'o', color = "grey",markersize = 9)
    h2,=axes[1].plot(index_35dB,EDC[index_35dB],'o', color = "red",markersize = 9, label = '$T_{30} = $' + str30+ ' sec')
    h1, = axes[1].plot(index_65dB,EDC[index_65dB],'o', color = "blue",markersize = 9, label = '$T_{60} = $'+ str60 + ' sec')
    axes[1].legend(handles = [h1,h2,h3])
    axes[1].set_ylim([-100,0])
    axes[1].set_xlim([-1000,fs*1])
    plt.show()


# ==========================END OF MODULE============================



# Testing the module
if (__name__ == '__main__'):

    # #SOUND CARD SETTINGS
     fs = 44100
     sd.default.samplerate = fs
     sd.default.dtype = 'float32'
    #
    # #EXCITATION SETTINGS
     type = 'sinesweep'
     duration = 7
     A = 0.7
     rep = 5
     silenceAtStart = 1
     silenceAtEnd = 1

     systemProbe = stimulus(type,fs);
     systemProbe.generateStimulus(fs,duration,A, rep,silenceAtStart, silenceAtEnd)
     plt.plot(systemProbe.excitation)
     plt.show()


    # myrecording = sd.playrec(systemProbe.excitation, samplerate=fs, channels=2)
    # sd.wait()

    # #RIRs = systemProbe.deconvolve(myrecording)

    # # SETTINGS FOR PLOTTING AND ANALYSIS
    # startId = (duration+silenceAtStart)*fs # keep some non-causal part also to check nonlinearities
    # lenRIR = 1; # in seconds, after desired truncation
    # endId = int(np.ceil((duration+silenceAtStart + lenRIR)*fs))
    #
    # RIRs_truncated = RIRs[startId:endId,:]
    # #taxis = np.arange(0,RIRs_truncated.shape[0],1)/fs
    #
    # plt.plot(RIRs_truncated,linewidth=0.5)
    # #plt.xlabel("time [s]")
    # #plt.plot(RIRs)
    # #
    # plt.show()

    # TIME-FREQUENCY ANALYSIS OF THE STIMULUS
    #-----------------------------------------------------
    # testsig = np.squeeze(systemProbe.excitation[fs*silenceAtStart:fs*(silenceAtStart+duration)])
    #
    # nfft = 1024
    # taxis = np.arange(0,testsig.shape[0],1)
    # faxis = np.linspace(0,fs/2,nfft/2+1)
    # faxis = faxis[1:faxis.shape[0]]
    #
    # magspec = np.abs(fft(testsig,nfft))
    # magspec = magspec[1:int(nfft/2 + 1)]
    #
    # ff,tt,Sxx = spectrogram(testsig, nperseg = nfft, nfft = nfft, noverlap = 1000 , scaling = 'density' )
    #
    # fig, axes  = plt.subplots(3,1,figsize = (8,7))
    # axes[0].plot(taxis,testsig,linewidth = 0.5)
    # # axes[0].set_xlim([0,duration])
    # axes[1].semilogx(faxis,20*np.log10(magspec),linewidth = 1)
    # axes[1].grid(True)
    # plt.subplot(313)
    # plt.pcolormesh(10*np.log10(Sxx), cmap = 'jet',vmin = -100, vmax = -0)
    # plt.colorbar(orientation = 'horizontal', fraction = 0.1)

    # axes[1].set_xlim([0,fs/2])


    # plot spectrogram of the stimulus
    # plt.subplot(311)
    # plt.plot(testsig)
    # plt.subplot(312)
    # nfft = 1024
    # overlap = 900
    # sig = np.squeeze(systemProbe.excitation[fs*silenceAtStart:fs*(silenceAtStart+duration)-1])
    # Pxx, freqs, bins, im = plt.specgram(sig, NFFT=nfft, Fs=fs, noverlap=overlap, cmap = 'jet', vmin = -130, vmax = -60)
    # plt.colorbar(orientation = 'horizontal', fraction = 0.1 )
    #
    # plt.subplot(313)
    # magspec =  np.abs(fft(y,nfft))
    #
    # plt.magnitude_spectrum(systemProbe.excitation[fs*silenceAtStart:fs*(silenceAtStart+duration)-1])

    #plt.show()
