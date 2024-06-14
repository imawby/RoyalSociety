import RPi.GPIO as GPIO
from gpiozero import Button
import time
import random
import matplotlib.pyplot as plt
import math
import board
import busio
import neopixel

####################################
# Config
####################################

# Pins
ND_PIN = 16				# BLUE LED
FD_NUE_PIN = 23		# RED CONNECTION OF RGB LED
FD_NUMU_PIN = 24	# GREEN CONNECTION OF RGB LED 
FD_NUTAU_PIN = 25 # BLUE CONNECTION OF RGB LED 
BUTTON_PIN = 2

pins = [ND_PIN, FD_NUE_PIN, FD_NUMU_PIN, FD_NUTAU_PIN]

# BASELINE LEDS
N_NODES = 6
MAX_BRIGHTNESS = 0.5

nue_baseline_prob = [0.012, 0.022, 0.038, 0.056, 0.071, 0.082] # have added 1% just so light actually comes on...
numu_baseline_prob = [0.961, 0.799, 0.555, 0.298, 0.100, 0.016]
nutau_baseline_prob = [0.037, 0.189, 0.417, 0.656, 0.838, 0.912]

NUE_PROB_RANGE_FD = [0.0, 0.0745]
NUMU_PROB_RANGE_FD = [0.0745, 0.098]
NUTAU_PROB_RANGE_FD = [0.098, 1.0]

# GRAPH CONFIG
names = [r'$\nu_{e}$', r'$\nu_{\mu}$', r'$\nu_{\tau}$']
edgecolours = ['red', 'green', 'blue']
colours = [[1, 0, 0, 0.5], [0, 1, 0, 0.5], [0, 0, 1, 0.5]]
plt.rcParams['toolbar'] = 'None' # Get rid of the toolbar for better visualisation
Y_MAX = 1000										 # Max y-axis of graph
COUNT_MAX = 950									 # Max counts before reset

####################################
# Some functions
####################################

def turn_on_light(pin) :
	GPIO.output(pin, GPIO.HIGH) # turn the pin on
	time.sleep(1) # pauses progam for a second
	GPIO.output(pin, GPIO.LOW) # turns the pin off, will no longer supply power

####################################
# Let's get this show on the road!
####################################

def main() :
	GPIO.setmode(GPIO.BCM)	# set naming convention for pins
	GPIO.setwarnings(False)

	# Setup pins
	for pin in pins :
		GPIO.setup(pin, GPIO.OUT)

	# Setup button
	button = Button(BUTTON_PIN)
				
	# Setup pixels
	pixels_nue = neopixel.NeoPixel(board.D18, N_NODES, brightness=MAX_BRIGHTNESS)
	pixels_numu = neopixel.NeoPixel(board.D18, N_NODES, brightness=MAX_BRIGHTNESS)
	pixels_nutau = neopixel.NeoPixel(board.D18, N_NODES, brightness=MAX_BRIGHTNESS)		 

	nue_baseline_intensity = [math.floor(prob * 255) for prob in nue_baseline_prob]		 
	numu_baseline_intensity = [math.floor(prob * 255) for prob in numu_baseline_prob]
	nutau_baseline_intensity = [math.floor(prob * 255) for prob in nutau_baseline_prob]		 

	# Turn everything off
	for pin in pins :
		GPIO.output(pin, GPIO.LOW)
		
	# Set event counters...
	n_nue_fd = 0
	n_numu_fd = 0
	n_nutau_fd = 0

	print("Press CTRL-C to exit.")
		
	while (True) :
		# Only proceed if button pressed
		button.wait_for_press()
		
		for count in [n_nue_fd, n_numu_fd, n_nutau_fd] :
			if count > COUNT_MAX :
				n_nue_fd = 0
				n_numu_fd = 0
				n_nutau_fd = 0

		# At the ND
		turn_on_light(ND_PIN)
			
		# Pixel things
		for node in range(N_NODES) :
			pixels_nue[node] = (int(nue_baseline_intensity[node]), 0, 0)
			time.sleep(0.5)						 
			pixels_nue[node] = (0,0,0)
			pixels_numu[node] = (0,0,0)
			pixels_nutau[node] = (0,0,0)

		# Pixel things
		for node in range(N_NODES) :
			pixels_numu[node] = (0, int(numu_baseline_intensity[node]), 0)
			time.sleep(0.5)						 
			pixels_nue[node] = (0,0,0)
			pixels_numu[node] = (0,0,0)
			pixels_nutau[node] = (0,0,0)

		# Pixel things
		for node in range(N_NODES) :
			pixels_nutau[node] = (0, 0, int(nutau_baseline_intensity[node]))						
			time.sleep(0.5)
			pixels_nue[node] = (0,0,0)
			pixels_numu[node] = (0,0,0)
			pixels_nutau[node] = (0,0,0)												

		# At the FD
		random_number = random.uniform(0, 1)				
		if ((random_number > NUE_PROB_RANGE_FD[0]) and (random_number < NUE_PROB_RANGE_FD[1])) : 
			n_nue_fd += 1
			turn_on_light(FD_NUE_PIN)
		elif ((random_number > NUMU_PROB_RANGE_FD[0]) and (random_number < NUMU_PROB_RANGE_FD[1])) : 
			turn_on_light(FD_NUMU_PIN)
			n_numu_fd += 1
		else :
			n_nutau_fd += 1
			turn_on_light(FD_NUTAU_PIN)

		# Draw the graph!		 
		plt.clf()
		plt.xticks(fontsize=12)				 
		plt.xlabel('Type of Neutrino', fontsize=11)
		plt.ylabel('Total Count', fontsize=11)
		plt.ylim((0, Y_MAX))
		plt.tight_layout()
		plt.grid()
			
		bars = plt.bar(names, [n_nue_fd, n_numu_fd, n_nutau_fd], color = colours, edgecolor=edgecolours, width=0.4, lw = 1)

		# Connect the names to the bars so we can get a legend...
		for bar, name in zip(bars, names) :
			bar.set_label(name)
						
		ax=plt.gca()
		ax.legend(loc='upper left', fontsize=12)
				
		# This is to add the counts to the bars
		for p in ax.patches :
			ax.annotate(str(p.get_height()), (p.get_x() + (p.get_width() * 0.5), p.get_height() + 10), ha = 'center', fontsize=12)

		# Draw and pause for a bit..
		plt.draw()
		plt.pause(1)						

if __name__ == '__main__':
	plt.ion()
	plt.show(block=False)
	main()
