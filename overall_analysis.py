#!/usr/bin/python

"""
Erin Brandt - 31/5/2013
This function does several things.
Input: (1) animal_info csv file that contains information not related to sound file itself (ie: animal size, weight, treatment, temperature, etc)
(2) annotation files from each trial
Process: (1) calculates the duration of each feature 
(2)separates out scrape numbers from annotation file (see documentation for more detail)
(3)gets peak frequency from each buzz
Output: 1 csv file per individual with all features and feature durations, scrape number (for scrape rate regions), buzz peak frequencies and trial information
This file is written into the folder that contains annotation information.  Use all_inds.py to compile these files for comparision across trials and individuals
"""

# to process annotation files, and wav data once it's enabled
import maleviban as vib
# holds variables that will be shared with maleviban
import config as cfg
# for displaying file/folder choosers and message boxes to user
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
# lets us do file and folder operations within the operating system of the user
import os
# lets us make plots
import matplotlib.pyplot as plt
# for numerical operations and numpy arrays
import numpy as np
# for reading/writing csv files
import csv
# lets us transpose arrays
import itertools as it
# gets current date and time for timestamp
import datetime

from itertools import chain

# get timestamp for files we'll save
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
startime = datetime.datetime.now()
startstring = startime.strftime("%H:%M:%S")
startime_str = "starting at " + startstring
print startime_str

# ask for file that contains general animal info. (treatment, temp., size & weight, etc.)
animal_information_file = tkFileDialog.askopenfilename(initialdir = "/home/eebrandt/projects/temp_trials/male_only/data/", title = "Choose the file that contains animal information")    
if animal_information_file == "":
	tkMessageBox.showerror(
            "Open file",
            "You need to choose a file with animal information." )
	raise SystemExit

# opens animal_info file and puts it in numpy array NOTE: "names" and "missing values" needs to change if you add or subtract columns to this file

kwargs = dict(delimiter=",",
               dtype="S10, S10, S10, S10, S10, S10, f20, f20, f20, S20, S200",
               names= "tape, video_number, individual, date, treatment, rank, temp, weight, ceph_width, comments, complete",
               missing_values={0:"N/A", 1:"N/A", 2:"",3:"N/A", 4:" ", 5:"N/A", 6:"N/A", 7:"N/A", 8:"N/A", 9: " ", 10: " "},)
try:
	animal_info = np.genfromtxt(animal_information_file, **kwargs)
except:
	tkMessageBox.showerror(
        "Open file",
        "Something is wrong with your animal information file.  Check documentation to fix your file.")
	raise SystemExit

# gets the folder that contains all the annotation files.  Should be a directory (such as "data") that contains each individual, then trial underneath it.
annotation_folder = tkFileDialog.askdirectory(initialdir= "/home/eebrandt/projects/temp_trials/male_only/data/", title = "Choose the folder that contains annotations")

# asks the user if they want to see duration and rate plots
duration_plots =  tkMessageBox.askyesno("Duration Plots", "Do you want to view duration plots?")
rate_plots = tkMessageBox.askyesno("Rate Plots", "Do you want to view scrape rate plots?")

#gets spectral data from user
wav_folder = tkFileDialog.askdirectory(initialdir = "/media/eebrandt/Erin1/Erin_Berkeley/male_temp_vids/", title = "Choose the folder that contains .wav files")
plotwav = tkMessageBox.askyesno("Peak Graphs", "Do you want to see plots showing spectra and peaks?")
if wav_folder == "":
	tkMessageBox.showerror(
	"Fatal Error",
	"You need to give the folder that contains your wav data.")
	raise SystemExit

# sets up an array so we can search through animal_info to find the individuals we're analyzing in our annotation files
trialname = []
readvar = 1
trialname.append("trial")
while readvar < animal_info.shape[0]:
	trialname.append(animal_info["video_number"][readvar] + "-" + animal_info["individual"][readvar])
	readvar = readvar + 1
ndtrialname = np.array(trialname)



# gets the indivudals based on everything that's in the top-level folder (folders and files)
individuals =  os.listdir(annotation_folder)
#loop to go through each "individual"
indnum = 1
individual_count = sum(1 for i in individuals if os.path.isdir(annotation_folder + "/" + i))
for individual in individuals:
	# checks to see which "individuals" are actually folders
	if os.path.isdir(annotation_folder + "/" + individual):
		print individual + " number " + str(indnum) + "/" + str(individual_count) + " total"
		indnum = indnum + 1
		# make sure each "individual" is a folder
		trials = os.listdir(annotation_folder + "/" + individual)
		# loop to go through each individual
		for trial in trials:
			labelfilename =  annotation_folder +"/"+ individual + "/" + trial + "/" + trial + ".labels.txt"
			# makes sure our "trial" is  a folder and that the folder contains a "labels.txt" file that we can load
			if os.path.isdir(annotation_folder + "/" + individual + "/" + trial) and os.path.isfile(labelfilename):
				trialindex = trialname.index(trial)
				outputarray = []
				# list to hold animal information (from the animal information file)
				an_info = []
				# adding data from the animal_info file to the array that will be written to the csv file eventually.
				an_info.append(animal_info[trialindex]["tape"] + "-" + animal_info[trialindex][1])
				an_info.append(animal_info[trialindex]["complete"])
				an_info.append(animal_info[trialindex]["individual"])
				an_info.append(animal_info[trialindex]["treatment"])
				an_info.append(animal_info[trialindex]["rank"])
				an_info.append(animal_info[trialindex]["date"])
				# calculates temperature in celsius from the given temperature in farenheit
				tempf = (float(animal_info[trialindex]["temp"]))
				tempc = (tempf - 32) * 5.0/9.0
				an_info.append(tempc)
				an_info.append(animal_info[trialindex]["weight"])
				an_info.append(animal_info[trialindex]["ceph_width"])
				
				# error checking mechanism to make sure the .labels.txt file is in the expected format
				try:
					vib.importanns(labelfilename)
				except:
					tkMessageBox.showerror(
           				"Annotation File Error",
            				labelfilename + " doesn't look right, formatting-wise. Look through the documentation to fix your file.")
					raise SystemExit

				# runs the rate analysis.  Gives the user an error if there's something wrong with the file
				try:
					vib.rates(cfg.lengths_output[3])
				except:
					tkMessageBox.showerror(
					"Rate Error",
					"Something about " + labelfilename + " is making rates not work.  See documentation to fix.")
					print "Something about " + labelfilename + " is making rates not work.  See documentation to fix."
					break
				# at this point, we figure out how many scrapes, thumps, and buzzes there are, so we only 
				# assign that number of rows in the npoutput column.  This will result in most cases in many
				# empty rows per column.

				lenscrape = len(cfg.lengths_output[0][5]) 
				lenthump = len(cfg.lengths_output[1][5])
				lenbuzz = len(cfg.lengths_output[2][5])
				lensr = len(cfg.srtot[0])
				
				wavpath = wav_folder + "/" + individual + "/" + trial + ".wav"
				print wavpath
				# opens wav file, puts it in array.  Add a "normalize = False" to the arguments of vib.importwav if you want to normalize the data.  Default is to use raw numbers.
				vib.importwav(wavpath)
				#rms loop similar to the duration stuff.
				rms_array = np.zeros((3, max(lenscrape, lenthump, lenbuzz)))
				readvar = 0
				# loops through each feature type
				features = ["scrape", "thump", "buzz"]				
				while readvar < len(features):
					# loops through each feature
					featurenum = 0
					for feature in cfg.lengths_output[readvar][featurenum]:
						vib.featurefinder(cfg.lengths_output, features[readvar], featurenum, cfg.wavdata, .25)
						rms = vib.rms_feature(cfg.feature[0][1]) 
						rms_array[readvar][featurenum] = rms
						featurenum = featurenum +1
					readvar = readvar + 1
						
				
				
				# runs peak frequency analysis if the user requests (for now we're just looking for fundamental peaks in buzzes peaks)				
				
				featuretype = 0
				nonbuzz_frq = []
				nonbuzz_peak = []
				while featuretype < 2:
					nonbuzz_temp_frq = []	
					nonbuzz_temp_peaks = []
					readvar = 0			
					while readvar < len(cfg.lengths_output[featuretype][5]):
						print str(trial) + " " + features[featuretype] + " " + str(readvar + 1)
						try:
							vib.featurefinder(cfg.lengths_output, features[featuretype], readvar, cfg.wavdata, .25)	
							print "featurefinder complete"	
							# performs fft on a given feature (thump or scrape)
							vib.getfreq(cfg.feature[0][1], cfg.rate, False, 10000000)
							print "getfreq complete"
							vib.simplepeaks(cfg.fft_dat[0], cfg.fft_dat[1], 1, plot_title = str(trial) + " " + features[featuretype] + " " + str(readvar + 1))
							print "simple peaks complete"
							print "simple peaks complete"
						except:
							print "Woops.  Looks like there's a problem with " + str(trial) + ".wav.  Possibly an issue with your particular .wav file."
							print "\a"
						nonbuzz_temp_frq.append(cfg.peaks[0][0])
						nonbuzz_temp_peaks.append(cfg.peaks[1][0])
						readvar = readvar + 1
					
					nonbuzz_frq.append(nonbuzz_temp_frq)
					nonbuzz_peak.append(nonbuzz_temp_peaks)
					featuretype = featuretype + 1
				np_nonbuzz_frq = np.array((nonbuzz_frq))
				np_nonbuzz_peak = np.array((nonbuzz_peak))
				# variable to loop through buzzes
				readvar = 0
				peakarray = np.zeros((2, lenbuzz))
				fundarray = np.zeros((2, lenbuzz))
				while readvar < lenbuzz:
					print str(trial) + " buzz " + str(readvar + 1)
					# picks out each feature from the wav array and loads it so we can analyze that part of the song
					try:
						vib.featurefinder(cfg.lengths_output, "buzz", readvar, cfg.wavdata, .25)
						print "featurefinder complete"
						# performs fft on a given buzz
						vib.getfreq(cfg.feature[1][1], cfg.rate, False, 10000000)
						print "getfreq complete"
						# performs peak analysis
						vib.getpeaks(cfg.fft_dat[0], cfg.fft_dat[1], .10, plotwav, smooth = 10, plot_title = str(trial) + " buzz " + str(readvar + 1))
						
						print "getpeaks complete"
					except:
						print "Woops.  Looks like there's a problem with " + str(trial) + ".wav.  Possibly an issue with your particular .wav file."
						print "\a"
						
					# if there's only one peak, we don't have to find the max or the fundamental; just write it to the array as-is
					if cfg.final_peaks.shape[1] == 1:
						peakarray[0][readvar] = cfg.final_peaks[0]
						peakarray[1][readvar] = cfg.final_peaks[1]
						fundarray[0][readvar] = cfg.final_peaks[0]
						fundarray[1][readvar] = cfg.final_peaks[1]
					else:
						fundarray[0][readvar] = cfg.final_peaks[0][0] 
						fundarray[1][readvar] = cfg.final_peaks[1][0]

						maxpeak = max(cfg.final_peaks[1])
						peakarray[1][readvar] = maxpeak
						maxindex = np.nonzero(cfg.final_peaks[1] == maxpeak)
						peakarray[0][readvar] = cfg.final_peaks[0][maxindex]
				
					readvar = readvar + 1

				if duration_plots:
					vib.plotlengths(cfg.lengths_output[0], cfg.lengths_output[1], cfg.lengths_output[2], trial)
				if rate_plots:
					vib.plot_rates(cfg.srtot, trial)
						
				# compiling info. to put into a csv.
				# makes an nparray the size and shape we need to eventually write the csv.  Note that this will make many empty spaces, since most of the data only have 1 row.
				Maxlen = max(len(cfg.lengths_output[0][0]), len(cfg.lengths_output[1][0]), len(cfg.lengths_output[2][0]), len(cfg.lengths_output[3][0]),)
				# this array is the key to this whole thing working properly.  It is an array with a pre-set number of columns,
				# but the rows are pre-determined by the *longest* row that exists in the lengths_output array.
				npoutput = np.zeros((32, Maxlen), dtype="S20")

				readvar = 0
				while readvar < 9:
					npoutput[readvar][0] = str(an_info[readvar])
					readvar = readvar + 1
				readvar = 0
				
				# this is where we actually assign all of our scrape, thump, and buzz values to the output array, based on how
				# many of each there are.  We are specifically using the percent of song length of the midpoint of each feature,
				# and its duration.  TODO: possibly clean this up with a loop?
				npoutput[9][0:lenscrape] = cfg.lengths_output[0][5]
				npoutput[10][0:lenscrape] = cfg.lengths_output[0][4]
				npoutput[11][0:lenscrape] = rms_array[0][0:lenscrape]
				npoutput[12][0:lenthump] = cfg.lengths_output[1][5]
				npoutput[13][0:lenthump] = cfg.lengths_output[1][4]
				npoutput[14][0:lenthump] = rms_array[1][0:lenthump]
				npoutput[15][0:lenbuzz]	 = cfg.lengths_output[2][5]
				npoutput[16][0:lenbuzz]  = cfg.lengths_output[2][4]
				npoutput[17][0:lenbuzz] = rms_array[2][0:lenbuzz]
				# writes the rate data.  This writes the number of scrapes, duration of scrape region, and number of scrapes
				npoutput[18][0:lensr]  = cfg.srtot[5]
				npoutput[19][0:lensr] = cfg.srtot[2]
				npoutput[20][0:lensr] = cfg.srtot[1]
				# writes the frequency data (peaks for scrape and thump, fundamental and peaks for buzzes)
				npoutput[21][0:lenscrape] = nonbuzz_frq[0]
				npoutput[22][0:lenscrape] = nonbuzz_peak[0]
				npoutput[23][0:lenthump] = nonbuzz_frq[1]
				npoutput[24][0:lenthump] = nonbuzz_peak[1]
				npoutput[25][0:lenbuzz] = fundarray[0]
				npoutput[26][0:lenbuzz] = fundarray[1]
				npoutput[27][0:lenbuzz] = peakarray[0]
				npoutput[28][0:lenbuzz] = peakarray[1]
				npoutput[29][0] = animal_info[trialindex]["comments"]

				# this will be the header for the csv file.  If something looks screwy with the resulting file, check here first
				durations_output_header = ["tape-video", "complete?", "individual", "treatment", "rank", "date", "temperature (C)", "weight", "ct_width", "scrape_pos", "scrape_dur", "scrape_rms", "thump_pos", "thump_dur", "thump_rms", "buzz_pos", "buzz_dur", "buzz_rms", "srate_pos", "srate_dur", "srate_num", "scrape_freq", "scrape_peak", "thump_freq", "thump_peak", "buzz_freq", "buzz_peak", "fund_freq", "fund_peak", "comments"]
				# this transposes our previous mess of an array so that we can have columns of unequal length written into our csv	
				zipoutput = list(it.izip_longest(*npoutput, fillvalue=''))
				
				# this bit writes the file. Comment it out if you want to check the functionality of this program without making csvs.
				fl = open(annotation_folder +"/"+ individual + "/" + trial + "/" + trial +"_" + "duration_data" + "_" + timestamp + '.csv', 'w')
				writer = csv.writer(fl)
				writer.writerow(durations_output_header)
				writer.writerows(zipoutput) 
				fl.close() 
 
#beeps, and gives user info about how long the run went for
print "All done!"
print "\a"
endtime = datetime.datetime.now()
#gives user info about how long it took to do the run
print "ending at " + datetime.datetime.now().strftime("%H:%M:%S")
print "run went for " +  str(endtime - startime)



