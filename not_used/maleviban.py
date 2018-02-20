#!/usr/bin/python
"""
Erin Brandt - 31/5/2013
This module contains functions specifically to process duration, frequency, and rate data for male H. clypeatus songs.  
TODO: fix up frequency aspects, comment frequency/fft/peakfinding parts.
"""
import scipy
import math
import ctypes
import tkMessageBox
import pylab
import re

import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma

from pylab import*
from scipy.io.wavfile import read,write
from numpy import sin, linspace, pi
from scipy import fft, arange, ifft, signal, fft, arange, ifft
from pypeaks import Data, Intervals

# the file that contains the variables necessary to run this module
import config as cfg

def importanns(wavpath):
	"""
    	description:This function opens a file containing duration information for vibratory song components.  It takes a path name (string),
	and outputs a numpy array that contains the following columns: component labels, component start times, component end times, component
	midpoints(useful for plotting components against total song length), length of component, percent of the total song at which the
	midpoint of a component occurs.
	parameters: wavpath: a string containing the path of the annotation file
	calculations: (1) determines the duration of each feature (2) determines the temporal position of each feature in the song.  
	song length is normalized to 1 based on the distance between the first feature and the last feature. note: scrape-rate information
	needs to be handled elsewwere (the rates function in this module).
	returns: cfg.lengths_output: array containing all duration and temproal information for each feature. 
	"""
	# imports the label file with the specified path/file name
	loadarray = np.array(np.loadtxt(open(wavpath),dtype = "string", delimiter = "\t,", skiprows = 0))

	#variable to count through loop
	readvar = 0
	# defines three arrays, start time and end time for a given vibratory feature
	startarray = []
	endarray = []
	labelarray = []

	# loops through loadarray, converting starts and ents to floats. We end up with startarray (starting times), endarray(ending times), and labelarray (labels (s, t, b, and r)
	while readvar < loadarray.shape[0]:
		# splits a given line of loadarray into a separate string
		readstring = loadarray[readvar].split()	
		# converts all numbers to floats, appends to starting and ending arrays
		startarray.append(float(readstring[0]))
		endarray.append(float(readstring[1]))
		labelarray.append(readstring[2])
		readvar = readvar + 1
	songlength = (max(startarray) - min(startarray))
	# now we need to make three separate arrays, one each for scrapes, thumps, buzzes, and rate regions

	# this array holds the names of all the strings we're interested in iterating (in this case, scrape, thump, buzz, rate)
	strings = ["s", "t", "b", "r"]
	# variable for looping trhough each string we want to test
	stringloop = 0
	
	# loops through each string we want to test
	while stringloop < len(strings):
		readvar = 0
		divlabels = []
		divstart = []
		divlength = []
		divend = []
		divmid = []
		divpercent = []
		songstart = min(startarray)
		songend = max(endarray)
		songlength = songend - songstart
		# loops through entire array
		while readvar < len(labelarray):
			# asks whether a given element matches our string of interest.  If it does, adds information to the relevant arrays
			if strings[stringloop] in labelarray[readvar]:	
				divlabels.append(labelarray[readvar])
				start = (startarray[readvar])
				divstart.append(start)
				end = (endarray[readvar])
				divend.append(end)
				length = (end - start)
				divlength.append(length)
				# note the timepoint we're using is the midpoint of the duration of the feature.  This makes most sense for very long features, such as scrape rate regions.
				mid = (length / 2) + songstart + (start - songstart)
				divmid.append(mid)
				mid_to_start = mid - start
				mid_to_end = songend - mid
				percent = (mid - songstart)/songlength			
				divpercent.append(percent)
			readvar = readvar +1
		# combines all of our separate arrays into one variable
		divarray = np.array([divlabels, divstart, divend, divmid, divlength, divpercent], dtype = 'S20')
		# sets our current divnparray to the relevant portion of the output variable	
		cfg.lengths_output[stringloop] = divarray
		# resets all our arrays so we don't just keep appending them
		stringloop = stringloop + 1
	# returns our output when we're all done	
	return cfg.lengths_output


def plotlengths (scrapedur, thumpdur, buzzdur, plot_durs_title):
	""" 
	description:This function takes three arrays that contain duration info for scrapes, thumps, and buzzes.  It generates a scatterplot
	that plots the duration of a component over the total length of the song (length given in percent length)  This is a good quick visual
	check to make sure everything's working well.  It also gives a good indication of how song elements are distributed temporally.
	parameters: scrapedur: scrape duration and occurence data, thump duration and occurence data, buzz duration and occurence data, title 
	for plot.
	returns: doesn't return anything, but generates plots
	"""

	figlengths = plt.figure(figsize=(5, 4))
	ax1 = figlengths.add_subplot(1,1,1)
	# we're just looking at scrapes, thumps, and buzzes here.  Keep in mind that the x, y axes are backwards.
	p1 = ax1.plot(scrapedur[5], scrapedur[4], color = "red", label = "scrapes", marker='o', linestyle = 'None')
	p2 = ax1.plot(thumpdur[5], thumpdur[4], color = "green", label = "thumps", marker='o', linestyle = 'None')
	p3 = ax1.plot(buzzdur[5], buzzdur[4], color = "blue", label = "buzzes", marker='o', linestyle = 'None')
	# sets labels on plot axes
	ax1.set_xlabel('% of song at which feature begins')
	ax1.set_ylabel('Length of feature (s)')
	# sets up legend
	plt.legend(loc='upper left', shadow=True, numpoints = 1)
	# sets axis limits
	plt.xlim(0, 1)
	plt.ylim(0, 10)
	plt.title(plot_durs_title)
	# show plot
	plt.show()

def rates(readarray):
	"""
	description: This function separates the rate count the annotation file and puts it in an array for later calculation
	parameters: readarray: array that is output from importanns containing all duration information
	calculations: splits out rate count and puts in its own column
	returns: cfg.srtot: contains all duration and rate information for scrape_rate data
	"""
	labelarray = []	
	countarray=[]
	lengtharray = []
	ratearray = []
	midarray = []
	percentarray = []
	readvar = 0

	# loops through readarray to strip count information from the label
	while readvar < readarray.shape[1]:
		r_count_string = readarray[0, readvar]
		try:
			labelarray.append(r_count_string.split('_')[0])
			counts = int(r_count_string.split('_')[1])
		# if the rate information isn't encoded properly (ie: b2_25), we get an error.
		except:
			tkMessageBox.showerror(
			"Rates Function Error",
			"There's a problem with generating rates from your annotation file.  Check documentation to fix.")
			raise SystemExit	

		countarray.append(counts)
		# length of component
		lengtharray.append(float(readarray[4, readvar]))
		# counts/second
		rate = counts/float(readarray[4, readvar])
		ratearray.append(float(rate))
		# midpoint of component
		mid = readarray[3, readvar]
		midarray.append(float(mid))
		# percent of song at which midpoint of component happens
		percent = readarray[5, readvar]
		percentarray.append(float(percent))
		readvar = readvar + 1
	# makes the final array that gets returned to whoever called the function
	cfg.srtot = [labelarray, countarray, lengtharray, ratearray, midarray, percentarray]
	ndsrtot = np.array(cfg.srtot)	
	return cfg.srtot

def plot_rates(durarray, plot_rates_title = "Your plot, fine sir/madam."):
	"""
	description: This function plots the average rate of scrapes over time (time being length of the song normalized to one).  It also
	adds a linear fit line, just for funsies.
	parameters: duararray: array containing the scrape rates, and positions of each of these, plot_rates_title: name of the individual for 
	display on the plot's title.
	returns: doesn't return anything, but generates plot.
	"""
	figrates = plt.figure(figsize=(5, 4))
	ax1 = figrates.add_subplot(1,1,1)
	ax1.set_xlabel('% of song at which feature begins')
	ax1.set_ylabel("Scrape Rate (scrapes/second)")
	x = durarray[5]
	y = durarray[3]
	ratefit = np.polyfit(x, y, 1)
	# makes a linear fit line
	yfit = np.polyval(ratefit, x)
	p1 = plt.plot(x, y, color = "red", marker='o', linestyle = 'None', label = 'scrape rates')
	p2 = plt.plot(x, yfit, label = 'linear fit line')
	plt.xlim(0, 1)
	plt.ylim(min(y) - (.05 * min(y)), max(y) + (.10 * max(y)))
	plt.legend(loc='upper center', shadow=True, numpoints = 1)
	plt.title(plot_rates_title)
	plt.legend(loc='upper left', shadow=True, numpoints = 1)
	plt.show()
		
def importwav(wavpath, normalize = False, plot = False):
	""" 
	description: this function reads in a wav file existing at a give path and converts it into an x/y series of points by dividing each
	number by the sampling rate.  Also, it optionally normalizes the y values (amplitude) based on the bitrate of the file (see description 	in that part of the function).
	parameters: wavpath: the path name of the .wav file, normalize: variable
	returns: cfg.wavdata, which is an x, y list of all the points in the .wav file, with y being amplitude and x being time. 
	Also optionally shows a graph of the entire file (time-varying signal).
	"""
	# actually loads the file, saving the bitrate, and data of the file, respectively
	cfg.rate,cfg.y = scipy.io.wavfile.read(wavpath, mmap=False)
	
	# this figures out the bit depth of the file (not sure if the io.wavfile function can handle anything other than 16-bit, but if it can, 	we will record it.  This bitrate number allows us to normalize the resulting output to the maximum/minimum possible values for a given 		bit depth (audio gui programs do this automatically, so this can be good for sanity-checking our data).  You will want to use the"real" 	numbers if you want to make direct measurements of amplitude (such as when recording location is standardized).

	bitdepth = float(re.findall('\d+', str(cfg.y.dtype))[0])
	# it's important for the frame rate to be a float, otherwise it will give a divide by 0 error as int.
	cfg.rate = float(cfg.rate)
	cfg.y.astype(float)
	# this normalizes the array containing the .wav data if requested by the user
	if normalize:
		#finds the normalization constant, which is 2** bitrate, divided by 2 (max. in each direction, positive and negative)
		norm_constant = (2 ** bitdepth)/2
		cfg.y = cfg.y/norm_constant

	# gets total length of "y" array, which amounts to the total number of samples in the clip
	lungime=len(cfg.y)
	timp=len(cfg.y)/cfg.rate
	# generates equally-spaced units along the time domain, starting with zero and ending with the previously generated total time
	cfg.t=linspace(0,timp,len(cfg.y))

	# plots the time-varying signal if the user reqests it
	if plot:
		p1 = plt.plot(cfg.t,cfg.y)
		plt.xlim(0, timp)
		show()	
	cfg.wavdata = [cfg.t, cfg.y, cfg.rate]	
	return cfg.wavdata

def featurefinder(lengths_output, featuretypestr, featureindex, wavdata, crop = 1):
	"""
	Description:This function is used to define a particular region of a .wav file for further analysis (usually fft and peak-finding).
	Parameters: lengths_output: numpy array that contains all of the information from the annotation file, featuretypestr, string
	indicating what type of feature we're dealing with (scrape, thump, buzz), featureindex: index of the particul (eg: buzz1, "1" is the
	featureindex), wavdata: numpy array containing x-y (time-varying) information for the wav file, crop: the factor by which we want to
	crop the beginning and end of the feature.  This is mostly useful for when we want the fft of a feature, but don't want the beginnings 		and ends because they're messier.
	Returns: feature: contains the subset of the wav file (in numpy array) for both uncropped [0] and cropped [1] versions of the feature.
	"""
	
	# looks to the featurekey dict to figure out what index of the feature_lengths array we need to refer to for our feature type.
	featuretype = cfg.featurekey[featuretypestr]
	#finds the start of the feature.  This will just be the number listed in lengths+output
	start = float(lengths_output[featuretype][1][featureindex])
	# the end of the feature listed in lengths_output
	end = float(lengths_output[featuretype][2][featureindex])
	# figures out where the "start" value is in the time domain of the wav data file is.
	indexstart = np.searchsorted(wavdata[0],[start,],side='left')[0]
	# finds the end of the time domain portion
	indexend = np.searchsorted(wavdata[0],[end,],side='right')[0]
	#figures out the amount by which we will need to crop the feature for the cropped portion
	cropamount = (end - start) * crop
	# crops the beginning of the array
	start_cr = start + cropamount
	# crops the end
	end_cr = end - cropamount
	# figures out where the crops should actually start in the wav data
	indexstart_cr = np.searchsorted(wavdata[0],[start_cr,],side='left')[0]
	# finds the end
	indexend_cr = np.searchsorted(wavdata[0],[end_cr,],side='right')[0]
	# actually gets the numbers from the array (uncropped)
	feature_whole = [wavdata[0][indexstart:indexend], wavdata[1][indexstart:indexend]]
	# gets the numbers for the cropped portion
	feature_buzz = [wavdata[0][indexstart_cr:indexend_cr], wavdata[1][indexstart_cr:indexend_cr]]
	# sets the variable we'll return
	cfg.feature = [feature_whole, feature_buzz]
	return cfg.feature	

def getfreq(y, Fs, plot, normal = -1):
	"""
	Description: Performs an fft of an array that has been broken down into x, y domains by the importwav function.
	Parameters: y: y-values of a wav file, Fs: sampling rate of wav file, normal: normaliziation number.  This sets the number you'll use
	to set the db for the fft.
	Returns: cfg.fft_dat: a 2-column array that contains the frequency and amplitude (fft plot) to feed into the find_peaks def. 
	"""
	# number of samples
	n = len(y) 
	k = arange(n)
	T = n/Fs
	#two-sided frequency range
	cfg.frq = k/T
	# one side frequency range	
	cfg.frq = cfg.frq[range(n/2)] 
	
	# fft computation and normalization
	cfg.Y = fft(y)
	# extract the real component of the fft array only
	cfg.Y = cfg.Y.real
	# don't know what this does
	cfg.Y = cfg.Y[range(n/2)]
	# normalizes it
	#The default normalization if the user doesn't specify one
	if normal == -1:
		normal = max(Y)
	cfg.Y = (cfg.Y/normal) * 100
	cfg.Y = abs(cfg.Y)
	
	#Plots the fft if the user requests it
	if plot:
		p1 = plt.plot(cfg.frq,abs(cfg.Y),'r')
		#pylab.xscale('log')
		pylab.xlim([0,4000])
		pylab.ylim([0,max(abs(cfg.Y))])
		show()	

	# sets the return variable, which contains frequency and amplitude information
	cfg.fft_dat = [cfg.frq, cfg.Y]
	return cfg.fft_dat



def getpeaks(frq, Y, cutoff,  showplot, smooth = 10, plot_title = "Your plot, fine sir/madam: ", plotraw = False):
	"""
	Description: This is used to find peaks in an fft. 
	Parameters: frq: frequency data from an fft, Y: amplitude data from an fft, cutoff: percent of highest peak at which we'll consider
	other peaks.  (eg: .10 means we'll save all peaks that are 10% or more of the highest peak in amplitude. plot_title: title for the
	plot, if the user wants a plot, 
	showplot: boolean to either show or not show a completed peaks plot, plotraw: boolean to either show or not show the canned plot the 
	pypeaks package makes.
	Calculations: (1) uses pypeaks to get peaks.  This is a rough measure, because it smooths the fft so much.  (2) first filtering step:
	removes peaks that are smaller than the cutoff * highest peak. (3) second filtering step: compares the x,y data for the found peaks to
	the actual values on the fft.  In particular, pypeaks smooths the data, so the real peaks are a bit off.  This filtering step finds the
	real local maximum on the fft.
	Returns: cfg.final_peaks: 2-d array that contains x and y values of the peaks.
	  
	"""
	
	# first step of getting peaks - smooths the fft
	# smoothness value can be changed to make the peak-detection more or less sensitive depending on your needs.
	peaks_obj = Data(frq, Y, smoothness=smooth)
	#second part of getting peaks
	peaks_obj.get_peaks(method='slope')
	# gives a raw, built-in plot of the peak data.  Axes aren't particularly meaningful, but can be a useful sanity check.
	if plotraw:
		peaks_obj.plot()

	#pull data out of peaks data object for filtering
	peaks = peaks_obj.peaks["peaks"]
	
	peaksnp = np.zeros((2, len(peaks[0])))
	peaksnp[0] = peaks[0]
	peaksnp[1] = peaks[1] 
	maxpeaks = max(peaks_obj.peaks["peaks"][1])
	

	# first filtering function: removes peaks that are shorter than the cutoff specified in function
	filteredypeaks = []
	filteredxpeaks = []
	filter_thresh = cutoff * maxpeaks
	readvar = 0
	while readvar < len(peaks_obj.peaks["peaks"][1]):
		if peaks_obj.peaks["peaks"][1][readvar] > filter_thresh:
			filteredxpeaks.append(peaks_obj.peaks["peaks"][0][readvar])
			filteredypeaks.append(peaks_obj.peaks["peaks"][1][readvar])
		readvar = readvar +1
	filteredpeaks = [filteredxpeaks, filteredypeaks]
	
	#puts filteredpeaks into a numpy array for the second filtering step
	filter1_peaks = np.array(filteredpeaks)
	filter1_peaksy = []
	# gets the absolute value of the Y array so we don't get weird errors.
	absY = abs(Y)
	
	# superimposes the found peaks onto our array from the wav file
	readvar = 0
	while readvar < len(filter1_peaks[1]):
		ypeak = np.searchsorted(frq,[filter1_peaks[0][readvar,]],side='left')[0]
		filter1_peaksy.append(absY[ypeak])
		readvar = readvar + 1
	
	# now we have to get the peaks in order, so that each peak is relative to his nearest neighbor.  Important for optimizing peaks in the next step.  this is very important if you don't want innapropriate peaks!
	indexarray = np.argsort(filter1_peaks[0])
	indexed_array=filter1_peaks[:,indexarray]	
	
	# second filtering step.  Judders peaks back and forth along the x-axis of the frequency plot until they reach the true local max (y)
	rangeleft_arr = []
	rangeright_arr = []
	finalpeaksx = []
	finalpeaksy = []
	cfg.final_peaks = np.zeros((2, len(filter1_peaks[1])))
	
	# if we only have one peak, we just write that one to the final_peaks array
	if len(filter1_peaks[0]) == 1:
		finalpeaky = max(abs(Y))
		# filtering step to remove freqencies outside of a reasonable range.  This probably isn't the best option, but since we have
		# A good idea of what the frequencies should be, this is a reasonable cutoff and we will just remove the feature outright rather 
		# than trying to fix it.  

		indexy = np.where(abs(Y) == finalpeaky)
		finalpeakx = frq[indexy]
		cfg.final_peaks[0] = finalpeakx
		finalpeaksy.append(finalpeaky)
		cfg.final_peaks[1] = finalpeaky
		maxpeak = round(finalpeakx,0)
	else:
		readvar = 0
		while readvar < len(indexed_array[0]):
			# figure out the x-distance to the next closest peak, then 
			if readvar == 0:
				xdist =  abs(indexed_array[0][readvar +1] - indexed_array[0][readvar])
			 
			elif readvar == len(indexed_array[0]) - 1:
				xdist = abs(indexed_array[0][readvar - 1] - indexed_array[0][readvar])
			else:
				distright = abs(indexed_array[0][readvar +1] - indexed_array[0][readvar])
				distleft = abs(indexed_array[0][readvar - 1] - indexed_array[0][readvar])
				xdist = min(distright, distleft)

			# we want to search the half the distance to the next closest peak.  Calculates this distance and finds it on the wav file.
			xdist2 = xdist/2
			rangeleft = max(0, indexed_array[0][readvar] - xdist2)
			rangeright = min(indexed_array[0][readvar] + xdist2, max(frq))
			rangeright_arr.append(rangeright)
			rangeleft_arr.append(rangeleft)
			readvar = readvar + 1

		readvar = 0
		while readvar < len(rangeright_arr):
			# actually gets the local maximum and matches it to an x value
			xmin = np.searchsorted(frq,[rangeleft_arr[readvar]],side='left')[0]
			xmax = np.searchsorted(frq,[rangeright_arr[readvar]],side ='right')[0]
			finalpeaky = max(abs(Y)[xmin:xmax])
			indexy = np.where(abs(Y)==finalpeaky)
			finalpeakx = frq[indexy]
			cfg.final_peaks[0][readvar] = finalpeakx
			cfg.final_peaks[1][readvar] = finalpeaky
			maxarray =  max([frq[xmin:xmax]])
			readvar = readvar + 1
		maxpeak = round(max(cfg.final_peaks[1]),0)
	maxpeakstr = str(maxpeak) + " Hz"
	if showplot:
		# shows plot if user requests it
		# plotting the spectrum
		p1 = plt.plot(frq,abs(Y),'r') 
		# plotting the original (non-filtered) peaks
		p2 = plt.plot(filter1_peaks[0], filter1_peaksy, linestyle = "none", marker = "o", color = "black")
		# plotting the filtered peaks
		p3 = plt.plot(cfg.final_peaks[0], cfg.final_peaks[1], linestyle = "none", marker = "o", color = "green")
		# defines the title based on the string that the user put in
		plt.title(plot_title + " - max peak at: " + maxpeakstr)
		pylab.xlim([0,500])
		xlabel('Freq (Hz)')
		ylabel('|Y(freq)|')
		plt.show()
	
	return cfg.final_peaks
def simplepeaks(frq, Y, peaknum, showplot = False, plot_title = "Your plot, fine sir/madam: "):
	cfg.peaks = []
	readvar = 0
	maxpeak = []
	maxfrq = []
	while readvar < peaknum:
		maxpeak.append(float(max(abs(Y))))
		peakindex = np.where(abs(Y)==max(abs(Y)))
		maxfrq.append(float(frq[peakindex]))
		readvar = readvar + 1
	cfg.peaks.append(maxfrq)
	cfg.peaks.append(maxpeak)
	
	if showplot:
		p1 = plt.plot(frq,abs(Y),'r') 
		p3 = plt.plot(peaks[0], peaks[1], linestyle = "none", marker = "o", color = "green")
		plt.title(plot_title + " - max peak at: " + str(peaks[0][0]) + "Hz")
		plt.show()
	#print cfg.peaks
	return cfg.peaks

def rms_feature(amp):
	"""
	Description: gets the root-mean-square of a given feature, which is a measure of the energy within a signal.
	Parameters: amp: array that contains amplitude data from a file.
	Calculations: calculates root-mean-squares
	Returns: cfg.rms: float containing the root-mean-square
	"""
	# need to get the absolute value of all the amplitudes.  If we don't, we'll get negatives that cause the sqrt function to choke.
	abs_square =  abs(mean(amp**2))
	
	# actualloy takes RMS
	cfg.rms = sqrt(abs_square)

	# returns rms
	return cfg.rms	
