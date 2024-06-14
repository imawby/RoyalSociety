########################################################################
# This is the script for the RSSE LED oscillation poster!
# 
# Need to run in a virtual environment,
# and with sudo (because of neopixel)
#
# source /home/isobel/NuOsc/.pixelenv/bin/activate
# sudo -E env PATH=$PATH python3 /home/isobel/NuOsc/Pixels.py
#
# Press button to send a neutrino on its way!
# On the very first time, the graph won't actually show -.-    (my python effort expired)
# On the second time the graph will recalibrate its position   (my python effort expired)
# On the third time, and onwards everything should be fine! :D (good enough?) 
#
# Contact: Isobel Mawby (i.mawby1@lancaster.ac.uk)
########################################################################

from gpiozero import Button
import time
import random
import matplotlib.pyplot as plt
import math
import board
import neopixel

####################################
# Config
####################################

# Pins
NUE_STRIP = board.D18	# rPi GIPO pin for nue strip/red strip (THIS WILL NEED TO BE SET)
NUMU_STRIP = board.D18  # rPi GIPO pin for numu strip/green strip (THIS WILL NEED TO BE SET)
NUTAU_STRIP = board.D18	# rPi GIPO pin for nutau strip/blue strip (THIS WILL NEED TO BE SET)
BUTTON_PIN = 2          # rPi GIPO pin for the button (THIS WILL NEED TO BE SET) 

# LED pixel config
# LED strip is a set of pixels with indices [0, 1, etc...]
# 'visible' ignores any pixels hidden by the board
# 'ND pixel' is the strip pixel inside the ND
# 'FD pixel' is the strip pixel inside the FD
# 'Baseline pixels' are the visible pixels that are inbetween the ND and FD
MAX_BRIGHTNESS = 0.5             # Can be adjusted between [0,1], 0.5 isn't blinding but feel free to adjust
TIME_INTERVAL = 0.5              # The time interval of each step (s)
ND_STRIP = 1                     # Which strip is the ND pixel on (0-nue, 1-numu, 2-nutau), i'm guessing it's numu
ND_PIXEL = 0                     # The index of the ND pixel
N_BASELINE_PIXELS = 4            # How many VISIBLE BASELINE pixels do we have in a single strip? (IsobelsBreadboard = 4, RSSE = 21)  
BASELINE_START_PIXEL = [1, 1, 1] # The index of the first visible pixel on the [nue, numu, nutau] strip (YOU'LL HAVE TO CHANGE THIS)
BASELINE_PIXELS = [range(BASELINE_START_PIXEL[i], BASELINE_START_PIXEL[i] + N_BASELINE_PIXELS) for i in range(3)] # YOU MIGHT HAVE TO CHANGE THIS
FD_STRIP = 1                     # Which strip is the FD pixel on (0-nue, 1-numu, 2-nutau), i'm guessing it's numu
FD_PIXEL = 5                     # The index of the FD pixel

# Isobel's breadboard (4 baseline pixels)
# Added 1% to nue so we pass the threshold for the light to come on
nue_baseline_prob = [0.022, 0.038, 0.056, 0.071] 
numu_baseline_prob = [0.799, 0.555, 0.298, 0.100]
nutau_baseline_prob = [0.189, 0.417, 0.656, 0.838]

# RSSE (Assuming 21 visible baseline pixels corresponding to [156km -> 1196km] of the baseline i.e. 52km separation)
# Added 1% to nue so we pass the threshold for the light to come on
#nue_baseline_prob   = [0.012, 0.014, 0.016, 0.019, 0.022, 0.026, 0.030, 0.034, 0.038, 0.042, 0.047, 0.051, 0.056, 0.060, 0.064, 0.068, 0.071, 0.075, 0.078, 0.080, 0.082]
#numu_baseline_prob  = [0.961, 0.931, 0.894, 0.849, 0.799, 0.743, 0.683, 0.620, 0.555, 0.489, 0.424, 0.360, 0.298, 0.241, 0.188, 0.141, 0.100, 0.067, 0.041, 0.024, 0.016]
#nutau_baseline_prob = [0.037, 0.065, 0.100, 0.142, 0.189, 0.241, 0.297, 0.356, 0.417, 0.478, 0.539, 0.599, 0.656, 0.709, 0.758, 0.801, 0.838, 0.868, 0.891, 0.906, 0.912]

# Measurement at 1300km
NUE_PROB_RANGE_FD = [0.0, 0.0745]
NUMU_PROB_RANGE_FD = [0.0745, 0.098]
NUTAU_PROB_RANGE_FD = [0.098, 1.0]

# Graph config
names = [r'$\nu_{e}$', r'$\nu_{\mu}$', r'$\nu_{\tau}$']    # Bar labels
edgecolours = ['red', 'green', 'blue']                     # Bar edge colour
colours = [[1, 0, 0, 0.5], [0, 1, 0, 0.5], [0, 0, 1, 0.5]] # Bar fill colour - 0.5 alpha
plt.rcParams['toolbar'] = 'None'                           # Get rid of the toolbar for better visualisation
Y_MAX = 1000										       # Max y-axis of graph (if you change this, you'll need to faff with the count number offset)
COUNT_MAX = 950									           # Max counts before reset

####################################
# Let's get this show on the road!
####################################

def main() :
	# Setup button
	button = Button(BUTTON_PIN)
				
	# Setup LED strip (we need to tell it the total number of physical pixels we have on the strip)
	# I'm sorry this isn't a function
	if (FD_STRIP == 0) :
		pixels_nue = neopixel.NeoPixel(NUE_STRIP, FD_PIXEL + 1, brightness=MAX_BRIGHTNESS)
		pixels_numu = neopixel.NeoPixel(NUMU_STRIP, BASELINE_PIXELS[1][-1] + 1, brightness=MAX_BRIGHTNESS)
		pixels_nutau = neopixel.NeoPixel(NUTAU_STRIP, BASELINE_PIXELS[2][-1] + 1, brightness=MAX_BRIGHTNESS)		 
	elif (FD_STRIP == 1) :
		pixels_nue = neopixel.NeoPixel(NUE_STRIP, BASELINE_PIXELS[0][-1] + 1, brightness=MAX_BRIGHTNESS)
		pixels_numu = neopixel.NeoPixel(NUMU_STRIP, FD_PIXEL + 1, brightness=MAX_BRIGHTNESS)
		pixels_nutau = neopixel.NeoPixel(NUTAU_STRIP, BASELINE_PIXELS[2][-1] + 1, brightness=MAX_BRIGHTNESS)		 
	else :
		pixels_nue = neopixel.NeoPixel(NUE_STRIP, BASELINE_PIXELS[0][-1] + 1, brightness=MAX_BRIGHTNESS)
		pixels_numu = neopixel.NeoPixel(NUMU_STRIP, BASELINE_PIXELS[1][-1] + 1, brightness=MAX_BRIGHTNESS)
		pixels_nutau = neopixel.NeoPixel(NUTAU_STRIP, FD_PIXEL + 1, brightness=MAX_BRIGHTNESS)		 

	# Convert probability to intensity
	nue_baseline_intensity = [math.floor(prob * 255) for prob in nue_baseline_prob]		 
	numu_baseline_intensity = [math.floor(prob * 255) for prob in numu_baseline_prob]
	nutau_baseline_intensity = [math.floor(prob * 255) for prob in nutau_baseline_prob]		 

	# Set event counters...
	n_nue_fd = 0
	n_numu_fd = 0
	n_nutau_fd = 0

	print("Press CTRL-C to exit.")
		
	while (True) :
		# Only proceed if button pressed
		button.wait_for_press()

		# If we've exceeded the max count, reset
		for count in [n_nue_fd, n_numu_fd, n_nutau_fd] :
			if count > COUNT_MAX :
				n_nue_fd = 0
				n_numu_fd = 0
				n_nutau_fd = 0

		# At the ND
		if (ND_STRIP == 0) :
			pixels_nue[ND_PIXEL] = (0, 0, 255) # always see a numu (green)
			time.sleep(TIME_INTERVAL)          # wait for a bit...
			pixels_nue[ND_PIXEL] = (0, 0, 0)   # turn off
		elif (ND_STRIP == 1) :
			pixels_numu[ND_PIXEL] = (0, 0, 255)
			time.sleep(TIME_INTERVAL)
			pixels_numu[ND_PIXEL] = (0, 0, 0)						
		else :
			pixels_nutau[ND_PIXEL] = (0, 0, 255)
			time.sleep(TIME_INTERVAL)
			pixels_nutau[ND_PIXEL] = (0, 0, 0) 				
			
		# Baseline
		for baseline_step in range(N_BASELINE_PIXELS) :
			pixels_nue[BASELINE_PIXELS[0][baseline_step]] = (int(nue_baseline_intensity[baseline_step]), 0, 0)
			pixels_numu[BASELINE_PIXELS[1][baseline_step]] = (0, int(numu_baseline_intensity[baseline_step]), 0)
			pixels_nutau[BASELINE_PIXELS[2][baseline_step]] = (0, 0, int(nutau_baseline_intensity[baseline_step]))			
			time.sleep(TIME_INTERVAL)						 
			pixels_nue[BASELINE_PIXELS[0][baseline_step]] = (0, 0, 0)
			pixels_numu[BASELINE_PIXELS[1][baseline_step]] = (0, 0, 0)
			pixels_nutau[BASELINE_PIXELS[2][baseline_step]] = (0, 0, 0)

		# At the FD
		# Work out what we 'see'
		random_number = random.uniform(0, 1)
		detection_colour = (0, 0, 0)
		
		if ((random_number > NUE_PROB_RANGE_FD[0]) and (random_number < NUE_PROB_RANGE_FD[1])) : 
			n_nue_fd += 1
			detection_colour = (255, 0, 0)
		elif ((random_number > NUMU_PROB_RANGE_FD[0]) and (random_number < NUMU_PROB_RANGE_FD[1])) : 
			n_numu_fd += 1
			detection_colour = (0, 255, 0)			
		else :
			n_nutau_fd += 1
			detection_colour = (0, 0, 255)

		# Turn on the corect pixel
		if (FD_STRIP == 0) :
			pixels_nue[FD_PIXEL] = detection_colour
			time.sleep(TIME_INTERVAL)
			pixels_nue[FD_PIXEL] = (0, 0, 0)
		elif (FD_STRIP == 1) :
			pixels_numu[FD_PIXEL] = detection_colour
			time.sleep(TIME_INTERVAL)
			pixels_numu[FD_PIXEL] = (0, 0, 0)
		else :
			pixels_nutau[FD_PIXEL] = detection_colour
			time.sleep(TIME_INTERVAL)
			pixels_nutau[FD_PIXEL] = (0, 0, 0)

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
