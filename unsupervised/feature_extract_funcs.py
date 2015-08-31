from pyESig.analysis.mu_drop_funcs import *

def extract_power(signal, f_lo, f_hi, samp_rate):
    """ Extracts power from signal at the samp_rate for
        specified frequencies using fft"""
    window_size = signal.shape[0]
    f_lo_adj = int(f_lo*window_size/samp_rate)
    f_hi_adj = int(f_hi*window_size/samp_rate)
    power = np.sum((np.abs(np.fft.fft(signal))**2)[f_lo_adj:f_hi_adj])
    return power


