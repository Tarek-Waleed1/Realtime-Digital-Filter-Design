import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt

# Parameters
order = 4
cutoff_freq = 1000.0  # Example cutoff frequency
fs = 10000.0  # Example sampling frequency

# Design a lowpass filter
b, a = sig.butter(order, cutoff_freq / (fs / 2), btype='low')

# Generate a sample signal
t = np.linspace(0, 1, num=1000, endpoint=False)
x = np.sin(2 * np.pi * 500 * t)  # Example signal with a frequency of 500 Hz

# Apply the filter
filtered_signal = sig.lfilter(b, a, x)

# Design an allpass filter for phase correction
allpass_order = 2  # Choose an appropriate order
allpass_freq = 1000.0  # Choose the frequency for phase correction

# Design the allpass filter frequency response
b_allpass = np.zeros(allpass_order + 1)
a_allpass = np.zeros(allpass_order + 1)
b_allpass[0] = 1
a_allpass[0] = 1
a_allpass[1] = -np.cos(2 * np.pi * allpass_freq / fs)

# Apply the allpass filter for phase correction
filtered_signal_corrected = sig.lfilter(b_allpass, a_allpass, filtered_signal)

# Plot the original and corrected signals
plt.figure(figsize=(10, 6))
plt.plot(t, x, label='Original Signal')
plt.plot(t, filtered_signal, label='Filtered Signal')
plt.plot(t, filtered_signal_corrected, label='Corrected Signal')
plt.legend()
plt.title('Original, Filtered, and Corrected Signals')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.show()
