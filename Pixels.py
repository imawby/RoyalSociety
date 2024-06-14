import RPi.GPIO as GPIO
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

NUE_PROB_RANGE_FD = [0.0, 0.0745]
NUMU_PROB_RANGE_FD = [0.0745, 0.098]
NUTAU_PROB_RANGE_FD = [0.098, 1.0]

# Pins
ND_PIN = 16       # BLUE LED
FD_NUE_PIN = 23   # RED CONNECTION OF RGB LED
FD_NUMU_PIN = 24  # GREEN CONNECTION OF RGB LED 
FD_NUTAU_PIN = 25 # BLUE CONNECTION OF RGB LED 

# LED
N_NODES = 6
MAX_BRIGHTNESS = 0.5

# Nue brightness
nue_baseline_prob = [0.012, 0.022, 0.038, 0.056, 0.071, 0.082] # have added 1% just so light actually comes on...
numu_baseline_prob = [0.961, 0.799, 0.555, 0.298, 0.100, 0.016]
nutau_baseline_prob = [0.037, 0.189, 0.417, 0.656, 0.838, 0.912]

pins = [ND_PIN, FD_NUE_PIN, FD_NUMU_PIN, FD_NUTAU_PIN]

# Drawing config - nue, numu, nutau
edgecolours = ['red', 'green', 'blue']
colours = [[1, 0, 0, 0.5], [0, 1, 0, 0.5], [0, 0, 1, 0.5]]

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
    GPIO.setmode(GPIO.BCM)  # set naming convention for pins
    GPIO.setwarnings(False)

    # Setup pins
    for pin in pins :
        GPIO.setup(pin, GPIO.OUT)

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

    while (True) :

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
            print("We have a nue!")
        elif ((random_number > NUMU_PROB_RANGE_FD[0]) and (random_number < NUMU_PROB_RANGE_FD[1])) : 
            turn_on_light(FD_NUMU_PIN)
            n_numu_fd += 1
            print("We have a numu!")
        else :
            n_nutau_fd += 1
            turn_on_light(FD_NUTAU_PIN)
            print("We have a nutau!")

        plt.clf()
        plt.xlabel('Type of Neutrino')
        plt.ylabel('Total')
        plt.ylim((0,1000))                        
        plt.bar([r'$\nu_{e}$', r'$\nu_{\mu}$', r'$\nu_{\tau}$'], [n_nue_fd, n_numu_fd, n_nutau_fd], color = colours, edgecolor=edgecolours, width=0.4, lw = 1)
        ax=plt.gca()
        for p in ax.patches :
            ax.annotate(str(p.get_height()), (p.get_x() + (p.get_width() * 0.5), p.get_height() + 1), ha = 'center')
                        
        plt.draw()
        plt.pause(1)            

if __name__ == '__main__':
        plt.ion()
        plt.show(block=False)
        main()
