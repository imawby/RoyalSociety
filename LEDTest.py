import RPi.GPIO as GPIO
from gpiozero import Button
import time
import random
import matplotlib.pyplot as plt 

####################################
# Config
####################################

N_ITERATIONS = 10
NUE_PROB_RANGE_FD = [0.0, 0.0745]
NUMU_PROB_RANGE_FD = [0.0745, 0.098]
NUTAU_PROB_RANGE_FD = [0.098, 1.0]

# FD pins
ND_PIN = 18
FD_NUE_PIN = 14
FD_NUMU_PIN = 15
FD_NUTAU_PIN = 16
BUTTON_PIN = 2

# Baseline pins
# Order from ND -> FD
RED_PIN_1 = 23
GREEN_PIN_1 = 24
BLUE_PIN_1 = 25

RED_PIN_2 = 17
GREEN_PIN_2 = 27
BLUE_PIN_2 = 22

pins = [ND_PIN, FD_NUE_PIN, FD_NUMU_PIN, FD_NUTAU_PIN, RED_PIN_1, GREEN_PIN_1, BLUE_PIN_1, RED_PIN_2, GREEN_PIN_2, BLUE_PIN_2]

# Drawing config - nue, numu, nutau
edgecolours = ['red', 'blue', 'green']
colours = [[1, 0, 0, 0.5], [0, 0, 1, 0.5], [0, 1, 0, 0.5]]

####################################
# Some functions
####################################

def turn_on_light(pin) :
	GPIO.output(pin, GPIO.HIGH) # turn the pin on
	time.sleep(1) # pauses progam for a second
	GPIO.output(pin, GPIO.LOW) # turns the pin off, will no longer supply power

def turn_on_rgb(red_pin, green_pin, blue_pin) :
	GPIO.output(red_pin, GPIO.HIGH)
	GPIO.output(green_pin, GPIO.HIGH)
	GPIO.output(blue_pin, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(red_pin, GPIO.LOW)
	GPIO.output(green_pin, GPIO.LOW)
	GPIO.output(blue_pin, GPIO.LOW)

def turn_on_gb(green_pin, blue_pin) :
        GPIO.output(green_pin, GPIO.HIGH)
        GPIO.output(blue_pin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(green_pin, GPIO.LOW)
        GPIO.output(blue_pin, GPIO.LOW)

####################################
# Let's get this show on the road!
####################################

def main() :
        GPIO.setmode(GPIO.BCM)  # set naming convention for pins
        GPIO.setwarnings(False)

        # Setup pins
        for pin in pins :
                GPIO.setup(pin, GPIO.OUT)

        # Setup button
        button = Button(BUTTON_PIN)
        
        # Turn everything off
        for pin in pins :
                GPIO.output(pin, GPIO.LOW)

        
        print("Press CTRL-C to exit.")

        try :
                # Set event counters...
                n_nue_fd = 0
                n_numu_fd = 0
                n_nutau_fd = 0

                while True :
                        button.wait_for_press()
                        # Turn ND pin on
                        #print("ND LED on")
                        turn_on_light(ND_PIN)
                        #print("ND LED off")

                        # Turn baseline on
                        #print("Baseline LED on")
                        turn_on_gb(GREEN_PIN_1, BLUE_PIN_1)
                        turn_on_rgb(RED_PIN_2, GREEN_PIN_2, BLUE_PIN_2)
                        #print("Baseline off")

                        # Turn FD pin on
                        #print("FD LED on")
                        #print("FD LED off")

                        # What have we detected?
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

                        #print("---------------------------")
                        #print("Total counts: ")
                        #print("---------------------------")
                        #print(n_nue_fd, "nues")
                        #print(n_numu_fd, "numus")
                        #print(n_nutau_fd, "nutaus")

                        plt.clf()
                        plt.xlabel('Type of Neutrino')
                        plt.ylabel('Total')
                        plt.ylim((0,105))                        
                        plt.bar([r'$\nu_{e}$', r'$\nu_{\mu}$', r'$\nu_{\tau}$'], [n_nue_fd, n_numu_fd, n_nutau_fd], color = colours, edgecolor=edgecolours, width=0.4, lw = 1)
                        ax=plt.gca()
                        for p in ax.patches :
                                ax.annotate(str(p.get_height()), (p.get_x() + (p.get_width() * 0.5), p.get_height() + 1), ha = 'center')
                        
                        plt.draw()
                        plt.pause(1)
        finally :
                GPIO.cleanup()

if __name__ == '__main__':
        plt.ion()
        plt.show(block=False)
        main()





