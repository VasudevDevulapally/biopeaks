# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 11:01:04 2019

@author: John Doe
"""

import os
import glob
import bioread
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from scipy.signal import butter, filtfilt, argrelmax, argrelmin, find_peaks, welch, medfilt, hilbert, peak_prominences
from sklearn.cluster import KMeans, SpectralClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from scipy import stats


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data, method='pad')
    return y


#datasets = glob.glob('C:\Users\John Doe\surfdrive\Beta\gemh_biosignals\Joanneke\*.acq')
#
#for i in range(4):
#
#    data = bioread.read_file(datasets[i])
#    sfreq = data.channels[5].samples_per_second
#    print sfreq
#    ecg_raw = data.channels[5].data
#    np.save(os.path.join('C:\Users\John Doe\surfdrive\Beta\gemh_biosignals\Joanneke', 'subject'+str(i)) , ecg_raw)


datasets = glob.glob('C:\Users\John Doe\surfdrive\Beta\gemh_biosignals\Joanneke\*.npy')
sfreq = 2000.


for t in range(1):
    
    plt.figure()
    
    for subject in range(1):
        
        ecg_raw = np.load(datasets[3])    
        lenidx = 30 * sfreq
        idxrange = np.arange(0, np.size(ecg_raw) - lenidx)
        np.random.seed(66)
        randbeg = int(np.random.choice(idxrange))
        randend = int(randbeg + lenidx)
        ecg_raw = ecg_raw[randbeg:randend]  # select lenidx random samples 
        
        # remove baseline and filter
        lowcut = 1.
        highcut = 100.
        ecg_filt = butter_bandpass_filter(ecg_raw,
                                          lowcut,
                                          highcut,
                                          fs=sfreq,
                                          order=3)
        # amplify peaks
        ecg_sqrd = ecg_filt**2
        
        # remove outliers
        outliers = np.abs(ecg_filt) > np.percentile(np.abs(ecg_filt), 99) * 2
        ecg_filt[outliers] = 0
        
        
        # build features for clustering
        
        pospeaks = argrelmax(ecg_filt)[0]
        negpeaks = argrelmin(ecg_filt)[0]
        all_peaks = np.union1d(pospeaks, negpeaks)
        
        height = ecg_filt[all_peaks]
        
        # for each peak p, get the average slope (absolute value) of the ECGs slope from preceding peaks to p and from p to subsequent peak
        slope = np.zeros(np.size(all_peaks))
        firstdiff = np.abs(np.diff(ecg_filt))
        for p in np.arange(1, np.size(all_peaks)-1):
            leftpeak = all_peaks[p-1]
            rightpeak = all_peaks[p+1]
            slope[p] = np.mean(firstdiff[leftpeak:rightpeak])
        
        prominence = np.empty(np.size(ecg_filt))
        prominence[:] = np.nan
        posprom = peak_prominences(ecg_filt, pospeaks)[0]
        negprom = peak_prominences(ecg_filt * -1, negpeaks)[0]    # all this shananigance is to circumvent the fact that prominence can only be determined for positive peaks
        prominence[pospeaks] = posprom
        prominence[negpeaks] = negprom
        prominence = prominence[~np.isnan(prominence)]    
        
        hilb = hilbert(ecg_filt)
        # extract the phase angle time series
        instphase = np.angle(hilb)
        # frequency sliding is defined as the temporal derivative of the phase angle time series (using the sampling rate s and 2π to scale the result to frequencies in hertz)
        instfreq = (np.diff(np.unwrap(instphase)) / (2.0 * np.pi) * sfreq)
        instfreq = instfreq[all_peaks]
        
        features = np.column_stack((height,
                                    instfreq,
                                    prominence,
                                    slope))
        
        # scale features
        scaler = MinMaxScaler()
        features = scaler.fit_transform(features)
        
        # reduce dimensionality features
        pca = PCA(n_components=.90, svd_solver='full')
        features = pca.fit_transform(features)
        
#        plt.subplot(3,4,subject+5)
        plt.subplot(2,1,1)
        plt.scatter(features[:, 0], features[:, 1])
        
        # get an initial estimate of dominant heart rate (assume BPM ranging from 50 to 150)
        fmin, fmax = .8, 2.5
        f, powden = welch(ecg_sqrd, sfreq, nperseg=np.size(ecg_filt))    # use squared data here to make QRS complex more prominent
        f_range = np.logical_and(f>=fmin, f<=fmax)
        f = f[f_range]
        powden = powden[f_range]
        pow_peaks = find_peaks(powden)[0]
        max_pow = pow_peaks[np.argmax(powden[pow_peaks])]
        freq_est = f[max_pow]
        # calculate expected number of beats over the given signal lenght at the estimated heart rate
        scds = np.size(ecg_filt) / sfreq    
        expNpeaks = scds * freq_est
        print expNpeaks
        
#        plt.subplot(3,4,subject+1)
#        plt.semilogy(f, powden)
#        plt.axvline(x=freq_est, c='r')
#        plt.xlim([fmin, fmax])
#        plt.ylim([min(powden[f < fmax]), max(powden[f < fmax])])
#        plt.xlabel('frequency [Hz]')
        
        
        # use clustering to identify peaks
        clustering = KMeans(n_clusters=4, random_state=42)
        clustering.fit(features)
        labels = clustering.labels_
        
        
        label_counts = np.unique(labels, return_counts=True)
        # make sure these variables are calculated irrespective of number of labels
        diffexpNpeaks = 1 / (np.abs(label_counts[1] - expNpeaks) + 1)   # smaller difference results in larger value, + 1 to avoid potential division by zero
        medheight = []
        for i in label_counts[0]:
            height_i = height[labels == i]
            medheight_i = np.median(height_i)
            medheight = np.append(medheight, medheight_i)
        medheight = np.log10(medheight)    # give less weight to extreme values

        print medheight, diffexpNpeaks
        # diffexpNpeaks will be 1 if the difference is 0 and progressively smaller as the difference grows,
        # therefore, it gives progressively smaller weight to medheight as the difference increase
        criterion = medheight * diffexpNpeaks 
        
        peak_label = np.argmax(criterion)
        peak_label_idcs = np.where(labels == peak_label)[0]
        labeled_peaks = all_peaks[peak_label_idcs]
        plt.subplot(2,1,1)
        plt.scatter(features[peak_label_idcs, 0], features[peak_label_idcs, 1], c='g')
        
        
        # as final criterion (to identify false positives), check if any of the IBIs is smaller than 0.5 * the expected IBI
        ibi_est = int(1. / freq_est * sfreq)
        fp_peak_idcs = np.where(np.diff(labeled_peaks) < ibi_est * .5)    # lives in the same space as peak_label_idcs
        fp_peaks = labeled_peaks[fp_peak_idcs]
        plt.scatter(features[peak_label_idcs[fp_peak_idcs], 0], features[peak_label_idcs[fp_peak_idcs], 1], marker = 'X', c='r', s=150)
        
        # for each pair of peaks that has been flagged as potential false positives ("pair" pertains to those peaks that are used to calculate a given difference in fp_peaks),
        # choose the most likely false positive according to the distance of each peak to the cluster center, such that larger distance pertains to greater likelihood
        # of being the "true" false positive peak
        disttocent = np.ravel(clustering.fit_transform(features)[peak_label_idcs,
                              peak_label])    # clustering.fit_transform returns n_samples x n_clusters dimensional array
#        final_peaks = []
#        for p in fp_peak_idcs[0]:
#            peaka = disttocent[p]
#            peakb = disttocent[p + 1]
#            retain_peak = np.argmin([peaka, peakb])
#            final_peaks = np.append(final_peaks,
#                                    labeled_peaks[p:p + 2][retain_peak])
#        final_peaks = np.unique(final_peaks).astype(int)
        plt.subplot(3,4,subject+9)
        plt.subplot(2,1,2)
        plt.plot(ecg_filt)
        
        final_peaks = labeled_peaks.copy()
        for p in fp_peak_idcs[0]:
            
            peaka = disttocent[p]
            peakb = disttocent[p + 1]
            discard_peak = np.argmax([peaka, peakb])
            plt.scatter(final_peaks[p:p + 2][discard_peak], ecg_filt[final_peaks[p:p + 2][discard_peak]], c='r')
            disttocent[p:p + 2][discard_peak] = np.max(disttocent) + 1    # make sure the discarded peak "looses" in case it is in the next pair of peaks
        final_peaks = np.delete(final_peaks, np.where(final_peaks == 0)[0])
    
        
        
        
#        plt.subplot(3,4,subject+9)
#        plt.subplot(2,1,2)
#        plt.plot(ecg_filt)
#        plt.scatter(labeled_peaks, ecg_filt[labeled_peaks], marker='X', c='m', s=150)
#        plt.scatter(fp_peaks, ecg_filt[fp_peaks] + .1, marker='X', c='r', s=150)
#        plt.scatter(final_peaks, ecg_filt[final_peaks] + .2, marker='X', c='g', s=150)
#       