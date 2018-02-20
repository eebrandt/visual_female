#!/usr/bin/python
import numpy as np
# array that holds information
lengths_output = [0,0,0,0]
# holds .wav info.
wavdata = [0,0]
y = []
t = []
rate = 0
frq = []
Y = []
srtot = []
wavdata = []
featurekey = {"scrape": 0, "thump": 1, "buzz": 2, "scrape_rates": 3}
feature = []
fft_dat = []
final_peaks = []
rms = 0.0
peaks = [[],[]]
