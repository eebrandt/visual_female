#!/usr/bin/env python

"""
Erin Brandt, 11/1/2016
This program is used to calculate durations and percent durations of various visual behaviors during H. clypeatus courtship interactions.
It outputs an array that can be converted to a .csv by overall_female.py. Scroll to the bottom to see exactly what is calculated and output.
"""

# For generating user dialog and warning boxes
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
# for making and using numpy arrays
import numpy as np
# the list of variables needed for this program
import femvars as fv

# this function takes in the data from the trial info file, the .tsv  times trial file, and the name of the trial, respectively 
def trial_behaviors(info, masterarray, trial_name):
	
	# splits trial_name into two parts: the tape, and the trial
	trial_list = trial_name.split('-')
	
	# defines the tape
	tape = info[info[:,0] == float(trial_list[0])]
	

	# Looks for the section of the trial info array that pertains to this specific trial, and then adds it to an array
	tape_trial = tape[tape[:,1] == float(trial_list[1])]

	#calculates temperatures
	temperatures = tape_trial[0][12:15]
	temperatureF = np.mean(temperatures)
	temperatureC = (temperatureF-32)*5/9

	# makes sub-arrays of time data for males and females
	males = masterarray[masterarray[:,1] == 'male']
	#print males
	females = masterarray[masterarray[:,1] == "female"]

	#figures out where waves, sidles, and moves occur for males
	
	wavearray = males[males[:,2] =="wave"]
	#print wavearray
	# calculates total time that the male is waving (note: assumes that this time is from the beginning of the first wave to the end of the last, does not take "lost" times into account). This is a proxy for "trial time"
	wavetime = float(wavearray[-1,0]) - float(wavearray[0,0])

	# makes array for sidles
	sidlearray = males[males[:,2]=="sidle"]

	# makes two arrays: one for the beginning of sidles, and one for the ending
	# this makes it a little easier to step through the array
	sidlestart = sidlearray[sidlearray[:,5] =="START"]
	sidlestop = sidlearray[sidlearray[:,5] =="STOP"]
	
	# sidlenumber is the total number of sidles(half of the values in the full array)
	sidlenumber = len(sidlestart)

	# array to hold the total time of each sidle
	sidlelength = np.zeros([sidlenumber])

	#iterators for populating the sidlelength array
	sidletime = 0

	# loop to populate sidle array - note the two iterators, one for the total number of sidles, and one that includes both beginnings and endings
	while sidletime < sidlenumber:
		sidlelength[sidletime] = float(sidlestop[sidletime,0]) - float(sidlestart[sidletime,0])
		sidletime = sidletime + 1	

	# need to do the same thing with movement, but iterated over each sidling display
	# make an array of all of the movement values
	movearray = males[males[:,2] =="move"]
	
	# this makes an empty array to contain summary and average information about movement
	mastermove = np.zeros([sidlenumber,4])

	# loop through sidles here
	sidleint = 0
	
	#again, we're making two arrays, one for the beginning of each sidle and one for the end
	movestart = movearray[movearray[:,5] == "START"]
	movestop = movearray[movearray[:,5] == "STOP"]

	# this is a dumb way to convert the "movestart" and "movestop" arrays to float values -- was causing problems before
	floatstart = np.array(movestart[:,0], dtype = float)
	floatstop = np.array(movestop[:,0], dtype = float)

	# checks to make sure there are equal  numbers of start and stop moves. If they are not equal, that means that either the movement is unpaired, or it either starts or stops outside of a sidling period.
	if len(floatstart) != len(floatstop):
		tkMessageBox.showerror(
       	    		"File Error",
       	    		"For trial " + str(trial_name) + ", sidle number " + str(sidleint+1) + " there is a movement start or stop outside of the sidle. Check your file and rerun the analysis.")
		print "For trial " + str(trial_name) + ", sidle number " + str(sidleint+1) + " there is a movement start or stop outside of the sidle. Check your file and rerun the analysis."
		exit() 


	# loop to evaluate movement bouts for each sidle
	while sidleint < sidlenumber:
		
		# finds the timecode for the start and stop of the given sidle, respectively
		# this needs to be converted to float to avoid weird problems
		sidstart = float(sidlestart[sidleint,0])
		sidstop = float(sidlestop[sidleint,0])
		
		#this makes a sub array of all "start" movements between the beginning and ending of the sidle bout
		subfloatstart =  floatstart[np.all([floatstart >= sidstart, floatstart <= sidstop], axis=0)]
		# this makes a sub array of all "stop" movements between teh beginning and ending of the sidle bout
		subfloatstop =  floatstop[np.all([floatstop >= sidstart, floatstop <= sidstop], axis=0)]

		# total number of movements. calculated based on the "stop" array, but it could be done with either
		submovenumber = len(subfloatstop)
		# array that will calculate the length of each movement bout
		movelength = np.zeros([submovenumber])
		movetime = 0
		# loop that steps through each movement bout
		while movetime < submovenumber:
			#calculates the length of a given movement bout
			movelength[movetime] = float(subfloatstop[movetime]) - float(subfloatstart[movetime])
			movetime = movetime + 1
		# these values will be put into the final fv.output file
		# number of movement bouts for this sidle
		mastermove[sidleint,0] = submovenumber
		# amount of time spent moving for this sidle
		mastermove[sidleint,1] = sum(movelength)
		# average length of a movement bout for this sidle
		mastermove[sidleint,2] = np.mean(movelength) 
		# percent of time spent moving in this sidle
		mastermove[sidleint,3] = sum(movelength)/(sidlelength[sidleint])
		sidleint += 1
	
	#score aggression
	# note:aggression is scored after the male begins to wave the first time. 
	# Aggressive behaviors before then cannot be distinguished from mistaken predatory responses
	# get sub array for female after first wave 
	femag = females[(females[:,0] >= wavearray[0,0]) & (females[:,0] <= females[-1,0])]
	# gets number of female escapes
	escapes = femag[femag[:,2] == "escape"]
	# gets number of female attack jumps
	attacks = femag[femag[:,3] == "attack"]
	# gets number of female jumps toward male
	jumpt = femag[(femag[:,2] == "jump") & (femag[:,3] == "toward")]
	# gets number of female walks toward 
	walkt = femag[(femag[:,2] == "walk") & (femag[:,3] == "toward")]

	# tests to see whether the female grappled with the male; simple boolean true/false but expressed as a number for later calculations
	grapplearr = femag[femag[:,2] == "grapple"]
	if "grapple" in femag[:,2]:
		grapple = 1
	else: 
		grapple = 0
	
	# this block writes to the output array that will be output by the function. 
	# If overall_female program is used, this array will be included as one line of the output .csv file
	# general info.
	# assigns trial number to fv.output
	fv.output[0] = trial_name
	# assigns date to fv.output
	fv.output[1] = tape_trial[0,3]
	# assigns round number to fv.output
	fv.output[2] = tape_trial[0,5]
	# assigns treatment to fv.output
	fv.output[3] = tape_trial[0,4]
	#assigns temperature to fv.output
	fv.output[4] = temperatureC
	# assigns female number to fv.output
	fv.output[5] = tape_trial[0,6]
	# assigns female weight to fv.output
	fv.output[6] = tape_trial[0,7]
	# assigns male number to fv.output
	fv.output[7] = tape_trial[0,8]
	# assigns male weight to fv.output
	fv.output[8] = tape_trial[0,9]
	# assigns outcome to fv.output
	fv.output[9] = tape_trial[0,10]

	# male displays

	# assigns length of display to fv.output
	fv.output[10] = str(wavetime)

	# sidling
	# assigns number of sidles to fv.output
	fv.output[11] = str(sidlenumber)
	# assigns total time spent sidling to fv.output
	fv.output[12] = str(sum(sidlelength))
	# assigns percent of trial spent sidling
	fv.output[13] = str(sum(sidlelength/wavetime))
	# assigns average length of sidling bout to fv.output
	fv.output[14] = str(sum(sidlelength)/sidlenumber)

	#movement
	# assigns number of total movement bouts
	fv.output[15] = str(int((sum(mastermove[:,0]))))
	# assigns number of movement bouts/sidle
	fv.output[16] = str(np.mean(mastermove[:,0]))

	# assigns average length of movement bout
	fv.output[17] = str(np.mean(mastermove[:,2]))
	# assigns total time of movement
	fv.output[18] = str(sum(mastermove[:,1]))
	# assigns % of movement time per sidle
	fv.output[19] = str(np.mean(mastermove[:,1]))
	# assigns % of movement time per display (wave)
	fv.output[20] = str(sum(mastermove[:,1]/wavetime))
	
	# females
	# assigns number of escapes
	fv.output[21] = str(len(escapes))
	# assigns number of attack jumps
	fv.output[22] = str(len(attacks))
	# assigns number of walks toward
	fv.output[23] = str(len(jumpt))
	# assigns number of jumps toward
	fv.output[24] = str(len(walkt)/2)
	# assigns grappling yes/no
	fv.output[25] = str(grapple)
	
	# assigns comments
	fv.output[26] = tape_trial[0,11]
	
	# returns array that can later be added to a .csv
	return fv.output

# this is used for debugging mostly. Can use it to figure out what is calculated where and troubleshoot any issues
'''
print "Male"
print "Number of sidling displays: " + str(sidlenumber)
print "Total time spent sidling: " + str(sum(sidlelength))
print "Percent time spent sidling: " + str(sum(sidlelength/wavetime))
print "Average time per sidling display: "+ str(sum(sidlelength)/sidlenumber)

print "Total movement bouts: " + str(int((sum(mastermove[:,0]))))
print "Movement bouts/sidle (average)" + str(np.mean(mastermove[:,0]))
print "Time spent moving per sidle (average): " + str(np.mean(mastermove[:,1]))
print "Percent time moving per sidle: "
print "Total time spent moving: " + str(sum(mastermove[:,1]))
print "Time spent moving as fraction of total: " + str(sum(mastermove[:,1]/wavetime))
print "Average length of movement bout: " + str(np.mean(mastermove[:,2]))
print "---"
print "Female"
print "Number of escapes during courtship: " + str(len(escapes))
print "Number of attacks during courtship: " + str(len(attacks))
print "Number of jumps toward during courtship " + str(len(jumpt))
print "Number of walks toward during courtship " + str(len(walkt)/2)
print "Was there grappling? " + str(grapple)
'''	
