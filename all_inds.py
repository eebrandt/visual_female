#!/usr/bin/python

"""
Erin Brandt - 31/5/2013
This function does several things.
Input: .csv files of all individuals' duration information
Process: (1) calculates average durations for each quartile of the song for each feature
(2) Calculates scrape rates for each quartile of the song and overall
Output: 1 csv file with information about each individual.  This only includes averages, so the source files should be retained
for more detailed analysis of individual features
"""

# for moving around in folders
import os
# for making file and folder dialog boxes and  boxes
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
# for getting the contents of a directory
from os import listdir
# for doing numerical calcuations and for making numpy arrays
import numpy as np
# for reading and writing csv files
import csv
# for getting current date and time for timestamp
import datetime

# gets a timestamp to identify data files
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# function to gather a list of the names of all csv files in the folder.
def find_csv_filenames(path_to_dir, suffix=".csv"):
	filenames = listdir(path_to_dir)
	return [ filename for filename in filenames if filename.endswith(suffix)]

# Asks user for data folder.  Should be the same as "annotation_folder" for overall_analysis.py
data_folder = tkFileDialog.askdirectory(initialdir= "/home/eebrandt/projects/temp_trials/male_only/data", title = "Choose the folder that contains data files.")

# Defines the header for the .csv file we're going to make
durations_output_header = ["tape_video", "complete", "individual", "treatment" , "rank", "date", "temperature", "weight", "ct_width", "scrape_q1", "scrape_q2", "scrape_q3", "scrape_q4", "scrape_avg", "srms_q1", "srms_q2", "srms_q3", "srms_q4", "srms_avg", "thump_q1", "thump_q2", "thump_q3", "thump_q4", "thump_avg", "trms_q1", "trms_q2","trms_q3","trms_q4","trms_avg","buzz_q1", "buzz_q2", "buzz_q3", "buzz_q4","buzz_avg", "brms_q1", "brms_q2", "brms_q3", "brms_q4", "brms_avg", "srates_q1", "srates_q2", "srates_q3", "srates_q4", "srates_avg", "sfreq_q1", "sfreq_q2", "sfreq_q3", "sfreq_q4", "sfreq_avg", "tfreq_q1", "tfreq_q2", "tfreq_q3", "tfreq_q4", "tfreq_avg", "bfreq_q1", "bfreq_q2", "bfreq_q3", "bfreq_q4", "bfreq_avg", "comments"]

# Defines and opens a .csv file that we'll write our file to
fl = open(data_folder + "/" + "temp_vibration_data" + "_" + timestamp + '.csv', 'w')
writer = csv.writer(fl)
# writes header to csv file
writer.writerow(durations_output_header)

# looks in each individual folder for trial folders
individuals =  os.listdir(data_folder)
for individual in individuals:
	# make sure each "individual" is a folder
	if os.path.isdir(data_folder + "/" + individual):
		trials = os.listdir(data_folder + "/" + individual)
		# loop to go through each individual
		for trial in trials:
			# defines the folders that we'll be looking in for csvs.
			trial_folder = data_folder + "/" + individual + "/" + trial
			# makes sure each trial is a folder
			if os.path.isdir(trial_folder):
				# looks for all the csvs. in a trial folder
				csvs = find_csv_filenames(trial_folder, suffix = ".csv")
				# checks to make sure there is at least one csv file in the folder.  If not, moves to next one and alerts the user to this
				if not csvs:
					tkMessageBox.showinfo(
					"Missing .csv file",
					"Duration file for " + trial + " was not found.  Moving to next one")
					print "Duration file for " + trial + " was not found.  Moving to next one"
					break
				creation_time = []
				# gets creation time for each file, so we only use the most recent one				
				for csv in csvs:
					creation_time.append(os.path.getmtime(trial_folder + "/" +  csv))
				recent_time = max(creation_time)
				max_index = creation_time.index(recent_time)
				# csv file that we'll actually load
				use_file = csvs[max_index]
				# arguments that we'll use to open the folder.  Specifically: we're setting the data type for each column and naming each column.
				kwargs = dict(delimiter=",",
               				dtype= "S10, S10, S10, S10, S10, S10, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, f20, S200",
              				names= "video, complete, individual, treatment, rank, date, temperature, weight, ct_width, scrape_pos, scrape_dur, scrape_rms, thump_pos, thump_dur, thump_rms, buzz_pos, buzz_dur, buzz_rms, srate_pos, srate_dur, srate_num, scrape_freq, scrape_peak, thump_freq, thump_peak, buzz_freq, buzz_peak, fund_freq, fund_peak, comments",
					skip_header=1)
				# load the data file once we know which is the proper one 
				data_file = np.genfromtxt(trial_folder + "/" + use_file, **kwargs)
				#print data_file
				# list of feature types
				feature_type = ["scrape", "thump", "buzz"]
				# counts which feature we're on (could probably technically do this by finding index of feature_type)
				feature_counter = 0
				# gets overall averages for the entire song
				allmeanfeatures = []
				allmeanrms = []
				# this loop goes through each "feature type" (scrape, thump, and buzz) and figures out average duration of features and rms values for each quarter of the song plus and overall average
				
				for feature in feature_type:
					# holds average for the entire song
					average_count = []
					average_rms = []
					#holds durations for each quartile
					mean_quartile = []
					mean_qrms = []
					# keeps track of which quartile we're on
					quartile_count = 1
					
					while quartile_count < 5:
						# holds the mean for each quartile
						quartile_durs = []
						quartile_rms = []
						readvar = 0
						for item in data_file[feature + "_pos"]:
							# check to make sure that there is a number here (not nan) and within quartile range.
							if not np.isnan(item) and  (quartile_count * .25) > float(item) > ((quartile_count * .25) - .25):
								average_count.append(data_file[feature + "_dur"][readvar])
								quartile_durs.append(data_file[feature +"_dur"][readvar])
								average_rms.append(data_file[feature + "_rms"][readvar])
								quartile_rms.append(data_file[feature + "_rms"][readvar])
							readvar = readvar + 1
						# makes sure there's something in the quartile_durs array.  It will throw an error (but not abort the program) if this isn't included
						if quartile_durs:
							mean_quartile.append(np.mean(quartile_durs))
							mean_qrms.append(np.mean(quartile_rms))
						else:
							mean_quartile.append(" ")
							mean_qrms.append(" ")
						quartile_count = quartile_count + 1
					# also makes sure there's something in average_count, so we don't get weird errors.  Note that we add empty string if it doesn't have a number so things don't get appended over necessary blanks.
					if average_count:
						mean_quartile.append(np.mean(average_count))
						mean_qrms.append(np.mean(average_rms))
					else:
						mean_quartile.append(" ")
						mean_qrms.append(" ")
					allmeanfeatures.append(mean_quartile)
					allmeanrms.append(mean_qrms)
					feature_counter = feature_counter + 1	
				# this loop gets scrape rates for 1st, 2nd, 3rd, and 4th quartiles of the song.  It does this by creating a running total of time, and a running total of scrape number to get those averages (ie: it doesn't calculate each rate independently and then average them).
				# variable to hold running total of time (durations)
				overall_dur = 0.0
				# variable to hold running total of scrape counts
				overall_count = 0.0
				# this makes a list that will hold all of the rate data (each quartile plus an overall average).  It is a fixed size (5) so that if one of them is empty (as often happens with buzzes), subsequent rates won't get appended over intended empty slots.
				rates = [0.0] * 5
				# counts the number of quartiles we go through (4)
				quartile_count = 0
				# this loop actually gets the rates for each quartile
				while quartile_count < 5:
					readvar = 0.0
					sdur = 0.0
					scount = 0.0
					for item in data_file["srate_pos"]:
						# this checks each "srate_pos" item to see if it's within the quartile range and also exists (not nan). If it's nan, it will throw an error but not break the program.  If everything looks ok, it adds to the scount and sdur running totals
						if not np.isnan(item) and  (quartile_count * .25) > float(item) > ((quartile_count * .25) - .25):
							sdur = sdur + data_file["srate_dur"][readvar]
							scount = scount + data_file["srate_num"][readvar]
						readvar = readvar + 1
					# this calculates the average.  First it makes sure neither scount or sdur are zero (to avoid division by zero errors) and then figures out the averages, which are then added to the rates list. Note that the overall_count and overall_dur variables get appended throughout all quartiles to give an overall average.
					savg = 0.0
					if float(scount) != 0 and float(sdur) != 0:
						savg = round(float(scount)/float(sdur),7)
						rates[quartile_count -1] = savg
						overall_dur = float(overall_dur + sdur)
						overall_count = float(overall_count + scount)
					else:
						rates[quartile_count -1] = ""

					quartile_count = quartile_count + 1
					
				#calculates the overall average, again checking for /0 errors and
				if overall_count != 0 and overall_dur != 0:
					overall_avg = overall_count/overall_dur
					rates[4] = round(overall_avg, 7)
				else:
					rates[4] = ""

				# handles frequency stuff.  for now, this just handles peak and fundamental frequencies, and not amplitude data.  Eventually, we'll have the peak based on real values gotten from the vibrometer
				
				#holds frequencies for each quartile
				mean_quartile = []
				# keeps track of which quartile we're on
				quartile_count = 1
				quartile_peak = [0.0] * 5
				quartile_fund = [0.0] * 5
				allpeak = []
				allfund = []
				
				while quartile_count < 5:
					# holds the mean for each quartile	
					readvar = 0
					peak_count = []
					fund_count = []
					for item in data_file["buzz_pos"]:
				
						# this was a first pass at functionality to reject any buzzes that have a peak amplitude smaller than 1% of the average of all buzzes.  This didn't work well because in some individuals, many of the buzzes had tiny peak amplitudes.  Instead, I went for an absolute threshold of "1", which seems to work ok.  NOTE: this absolute threshold will need to be changed if you decide to use normalized amplitudes (selected from the import_wav function).						
						#checkmean = data_file["fund_peak"][~np.isnan(data_file["fund_peak"])].mean()
						# check to make sure that there is a number here (not nan), within quartile range, and larger than a certain threshold (filters out buzzes where the peakfinding algorithm failed).
						if data_file["buzz_freq"][readvar] > 0 and  (quartile_count * .25) > float(item) > ((quartile_count * .25) - .25) and data_file["fund_peak"][readvar] > 1:				
							peak_count.append(data_file["buzz_freq"][readvar])
							fund_count.append(data_file["fund_freq"][readvar])
							allpeak.append(data_file["buzz_freq"][readvar])
							allfund.append(data_file["fund_freq"][readvar])
						# makes sure there's something in the quartile_freq array.  It will throw an error (but not abort the program) if this isn't included	
						readvar = readvar + 1	
					if peak_count:
						quartile_peak[quartile_count - 1] = np.mean(peak_count)
					else:
						quartile_peak[quartile_count - 1] = " "
					if fund_count:
						quartile_fund[quartile_count -1] = np.mean(fund_count)
					else:
						quartile_fund[quartile_count - 1] = " "
	
					quartile_count = quartile_count + 1
				
				# also makes sure there's something in peak_count, so we don't get weird errors.  Note that we add empty string if it doesn't have a number so things don't get appended over necessary blanks.
				if allfund:
					quartile_fund[4] = np.mean(allfund)
				else:
					quartile_fund[4] = (" ")
				# now we're going to handle peak frequency data for non-buzz (ie: scrape and thump) data
				nonbuzzfreq = []
				nonbuzzpeak = []
				nonzero_freq = np.zeros((3,5))
				nonzero_peak = np.zeros((3,5))
				featurecount = 0
				# we have to loop through each feature (scrape and thump) in addition to looping through quartiles like we do for buzzes
				while featurecount < 2:
					#holds frequencies for each quartile
					mean_quartile = []
					# keeps track of which quartile we're on
					allfreq = []
					allpeak = []
					quartile_count = 1
					quartile_peak = [0.0] * 5
					quartile_freq = [0.0] * 5
					while quartile_count < 5:	
						readvar = 0
						peak_count = []
						freq_count = []
						colfreq = feature_type[featurecount] + "_freq"
						colpeak = feature_type[featurecount] + "_peak"
						colpos = feature_type[featurecount] + "_pos"
						for item in data_file[colpos]:
							if data_file[colpos][readvar] > 0 and  (quartile_count * .25) > float(item) > ((quartile_count * .25) - .25):
#and data_file[colfreq][readvar] < 5000:	
								peak_count.append(data_file[colpeak][readvar])
								freq_count.append(data_file[colfreq][readvar])
								allpeak.append(data_file[colpeak][readvar])
								allfreq.append(data_file[colfreq][readvar])	
							readvar = readvar + 1
						# makes sure there's something in the quartile_freq array.  It will throw an error (but not abort the program) if this isn't included
						if peak_count:
							quartile_peak[quartile_count - 1] = np.mean(peak_count)
						else:
							quartile_peak[quartile_count - 1] = " "
						if freq_count:
							quartile_freq[quartile_count - 1] = np.mean(freq_count)
						else:
							quartile_freq[quartile_count - 1] = " "	
						quartile_count = quartile_count + 1
					featurecount = featurecount + 1
					
				
					# also makes sure there's something in peak_count, so we don't get weird errors.  Note that we add empty string if it doesn't have a number so things don't get appended over necessary blanks.
					if allfreq:
						quartile_freq[4] = np.mean(allfreq)
						quartile_peak[4] = np.mean(allpeak)
					else:
						quartile_freq[4] = (" ")
						quartile_peak[4] = (" ")
					nonbuzzfreq.append(quartile_freq) 
					nonbuzzpeak.append(quartile_peak)
			
				if data_file["weight"][0] == False:
					weight = ""
				else:
					weight = data_file["weight"][0]
					

				# these two conditionals put empty string instead of nan if weight or ct is missing.  Easier for later import	
				if data_file["ct_width"][0] == False:
					ct = ""
				else:
					ct = data_file["ct_width"][0]
				
				# defines the row that we're going to write to the csv.  
				row = [data_file["video"][0], data_file["complete"][0], data_file["individual"][0], data_file["treatment"][0] ,data_file["rank"][0], data_file["date"][0], data_file["temperature"][0], weight, ct, allmeanfeatures[0][0], allmeanfeatures[0][1], allmeanfeatures[0][2], allmeanfeatures[0][3], allmeanfeatures[0][4], allmeanrms[0][0], allmeanrms[0][1], allmeanrms[0][2],allmeanrms[0][3], allmeanrms[0][4], allmeanfeatures[1][0], allmeanfeatures[1][1], allmeanfeatures[1][2], allmeanfeatures[1][3], allmeanfeatures[1][4],allmeanrms[1][0],allmeanrms[1][1],allmeanrms[1][2],allmeanrms[1][3],allmeanrms[1][4], allmeanfeatures[2][0], allmeanfeatures[2][1], allmeanfeatures[2][2], allmeanfeatures[2][3], allmeanfeatures[2][4], allmeanrms[2][0],allmeanrms[2][1],allmeanrms[2][2],allmeanrms[2][3],allmeanrms[2][4], rates[0], rates[1], rates[2], rates[3], rates[4], nonbuzzfreq[0][0], nonbuzzfreq[0][1], nonbuzzfreq[0][2],  nonbuzzfreq[0][3], nonbuzzfreq[0][4], nonbuzzfreq[1][0], nonbuzzfreq[1][1], nonbuzzfreq[1][2], nonbuzzfreq[1][3], nonbuzzfreq[1][4], quartile_fund[0], quartile_fund[1], quartile_fund[2], quartile_fund[3], quartile_fund[4], data_file["comments"]]
				# writes the row, for each trial
				writer.writerow(row) 
# closes the csv writer
fl.close() 

