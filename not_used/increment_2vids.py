#!/usr/bin/env python

#for copying to clipboard
import pyperclip

#Loop continuously
while True: 
	# takes data from user
    	timecode = str(raw_input('Enter your timecode: '))
	#if user types "exit, then exit the program
	
	#if user types a number, increments it as described
	try:
		float(timecode)
		newcode = float(timecode) + 1762
		print str(newcode)
		#copies new incremented number to clipboard for easy pasting
		pyperclip.copy(str(newcode)) 
	except ValueError:
		if timecode == 'exit':
			print "Ok. Exiting."
			break
    		else:
			#if user does not type a number, ask the user to enter a number
			print "You need to enter a number. Try again or type exit to exit."	
	
				
	
	
		
		
 

       
		
