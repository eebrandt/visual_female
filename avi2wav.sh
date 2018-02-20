#!/bin/bash
#Script to batch-convert .avis (from male signal video) to .wavs (just the vibratory component)
#3/8/14 Erin Brandt

# makes the welcome message red so it stands out when you need to scroll up later
tput setaf 1
# welcome message
echo "Welcome to avi2wav."

#asks if you want to actually run the script.  Any output from this script is in green so you can find it easier in terminal if there are errors.

#sets user input and script output to green so you can see it later.
tput setaf 2 

#asks the user whether they want to run the script
echo -e "This will extract a mono .wav file from each .avi in this folder. 
Do you wish to do this (y/n)?"
read "entire"

# if user chooses "y", run the script
if [ "$entire" = "y" ]; then
	# variables to hold date/time information for the log file
	fixdate=$(date +"%m-%d-%y"_"%T")
	presentdate=$(date +"%m-%d-%y at %T") 
	
	# file name for the logfile
	logfile="avi2wavlog_$fixdate.txt"
	#goes into the folder with all the videos(can't run this script from a USB device).  It will go into each subfolder and make a .wav from each .avi.
	cd /media/eebrandt/Erin1/Erin_Berkeley/male_temp_vids
	# output color in purple to alert the user about the location of the log file
	tput setaf 5

	# location and name information for the user regarding the log file
	echo "A log file is being written with output and time stamp information at /media/eebrandt/Erin1/Erin_Berkeley/male_temp_vids/$logfile"

	#color back to green
	tput setaf 2
	
	# writes header information to logfile
	echo  "Logfile for avi2wav.sh" >> "$logfile"
	echo  "Run was completed on $presentdate" >> "$logfile"
	
	# sets up a loop that for each subdirectory in current directory, go into the subdirectory
	for D in /media/eebrandt/Erin1/Erin_Berkeley/male_temp_vids/*
	do	
		# color back to green
		tput setaf 2
		
		# checks to make sure a given item in the directory is actually a subdirectory, and not just a file
		if [ -d "$D" ]; then

			#set time for timestamp info in logfile (hours, minutes, seconds, milliseconds)
			timenow=$(date +"%T.%3N")
			
			#alert user that we're moving to a subdirectory
			echo "Moving to directory $D"
			echo  "$timenow Moving to directory $D" >> "$logfile"
			
			#actually moves us to the subdirectory
			cd "$D"

			# uses ls to count the number of *avi files that are present this is stored as an integer
			files=$(ls *.avi 2> /dev/null | wc -l)

			# if there are more than 0 *.avi files, we can proceed to converting them to .wav
			if [ ! $files -eq 0 ]; then
				
				#loop that cycles through all *.avi files in the subdirectory sequentially to convert them to .wav
				for i in *.avi
				do
					# color back to green  
					tput setaf 2

       					# set the immediate time and alert the user that we are considering converting a given .avi file
					timenow=$(date +"%T.%3N") 	
					echo "Inspecting file $i..."
					echo "$timenow Processing file $i..." >> ../"$logfile"

					# determine the filename of the avi that we're going to be looking at	
					filename=`basename "$i" .avi`
				
					#check to see if there's already a .wav file by the same name as the .avi file we're inspecting
					if [ ! -e "$filename".wav ]; then
						
						# assign the file name
						filename=`basename "$i" .avi`
					
						#this actually does the conversion here.  Specifically, this outputs a mono .wav from the .avi
						ffmpeg -i "$filename".avi -acodec pcm_s16le -ac 1 "$filename".wav
					
						#color back to green (ffmpeg likes to switch it back to white)
						tput setaf 2
			
						# gets time stamp info and alerts user that a .wav file has been generated
						echo "$timenow File $i.wav has been generated." >> ../"$logfile"
						echo "File $i.wav has been generated."

					# if there is already a .wav file for a given .avi...
					else
						#tells user if a file already exists
						timenow=$(date +"%T.%3N")
						echo "$i.wav already exists, moving to next one."
						echo "$timenow $i.wav already exists, moving to next one." >> ../"$logfile"

					# end of if statement checking for .wavs already in the folder
    					fi
	
				#end of for loop converting all .avis in a subdirectory to .wavs
				done

				# move up a directory so we can go into the next subdirectory
				cd ..

			# if there are no .avi files in a given subdirectory...
			else

				# alert the user that there aren't any files in this subdirectory
				timenow=$(date +"%T.%3N")
				echo "No .avi files in this directory."
				echo "$timenow No .avi files in this directory." >> ../"$logfile"
				
				# move to the next subdirectory
				continue	

			# end of statement checking for .avis in a given folder
			fi

		# if the supposed subdirectory turns out to just be a file...
		else

			# move to the next one
			continue

		# end of statement checking to see if a subdirectory is really a directory or just a file	
		fi

	# end of loop to go through all subdirectories			
	done

#if user chooses "n", exit script without doing anything
fi	

#changes color in terminal back to white
tput setaf 7

#exit script
exit 0
