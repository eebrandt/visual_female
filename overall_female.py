#!/usr/bin/python
"""
Erin Brandt, 11/1/2016
This program is used to generate a .csv file containing information from multiple H. clypeatus courtship trials. 
The manipulation of the individual files is done within the video_scoring function
"""
# this is a function written specifically to do the analysis on a csv file containing H. clypeatus visual vibratory information
import video_scoring as vs
# for importing .tsv files
import pandas as pd
# for making and manipulating numpy arrays
import numpy as np
# for user dialog and message boxes
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
# list of variables affiliated with video_scoring
import femvars as fv
# used to root through folders on computer
import os
# used to generate timestamp for output files
import datetime
# for opening, writing, and manipulating .csv (also .tsv) files
import csv
import shutil

# gets timestamp for adding to the filename (keeps files from getting overwritten
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# change this string if you want to change where the gui folder chooser is defaulted to.
trialinfo_folder = "/home/eebrandt/projects/dissertation/chapter_1/female_choice/data/"
# opens a dialog to choose the trial information file, and throws error if you don't choose one
infofile = tkFileDialog.askopenfilename(initialdir = trialinfo_folder, title = "Choose the file that contains overall information")    
if infofile == "":
	tkMessageBox.showerror(
       	    "Open file",
       	    "You need to choose a file with overall information." )
	raise SystemExit
#reads in trial info file
trial_info = pd.read_csv(infofile,sep=',')
# puts trial info into array
info = np.array(trial_info)


# get folder that contains .tsv files for trials
# change this string if you want the folder chooser to default to opening a different place
timedata_folder = "/home/eebrandt/projects/dissertation/chapter_1/female_choice/data/"
trial_folder = tkFileDialog.askdirectory(initialdir= timedata_folder, title = "Choose the folder that contains trial time files.")


# array to hold list of .tsv files in folder
tsvs = []
for file in os.listdir(trial_folder):
	if file.endswith(".tsv"):
		tsvs.append(file)

#makes a .csv file that will compile all of the data
fl = open(trial_folder + "/processed_times/" + "female_time_data" + "_" + timestamp + '.csv', 'w')
writer = csv.writer(fl)
# header row for csv file
headers = ["trial number", "date", "round number", "treatment", "temperature", "female ID", "female weight", "male number", "male weight", "outcome", "trial length", "number of sidles", "time spent sidling", "percent of trial spent sidling", "length of sidling bout", "number of movement bouts", "number of movement bouts per sidle", "length of movement bout", "total time of movement", "percent of movement time per sidle", "percent of movement time per trial", "number of female escapes", "number of female attack jumps", "number of female walks toward", "number of female jumps toward", "grappling present", "comments"]

# writes header row
writer.writerow(headers)

#iterates through all the files
fileint = 0

while fileint < len(tsvs):
	#reads in .tsv file (tab-delimited), skips first 24 rows which is header garbage, and lists the 25th row as a header
	
	# gets current file name
	currentfile = tsvs[fileint]
	# strips .tsv bit out of file name to get trial name
	trial_name = currentfile[:-4]
	# prints the tape and trial number to the console, so you can see how it's progressing and pin down any weird errors to a specific file
	print trial_name

	if int(trial_name[0]) < 8:
		skiprows = 24
	else:
		skiprows = 14

	timesread = pd.read_csv(trial_folder +"/"+ tsvs[fileint],sep='\t', skiprows = skiprows, header = 1, dtype={'time': float, 'subject': str, 'behavior': str, 'modifier': str, 'comment': str, 'status': str})	
	#puts the input data into a numpy array
	masterarray = np.array(timesread)
	#print masterarray[0]
	#runs trial_behaviors from video_scoring for one file
	vs.trial_behaviors(info, masterarray, trial_name)
	#writes output row
	writer.writerow(fv.output)
	#increments fileint
	fileint += 1
			
#close .csv after it has run through all files	
fl.close()

# makes a copy of the file that was just produced and names it "female_time_final.csv". This is the file that will be read by the R programs
shutil.copy2(trial_folder + "/processed_times/" + "female_time_data" + "_" + timestamp + '.csv', trial_folder + "/processed_times/" + "female_time_final.csv")
