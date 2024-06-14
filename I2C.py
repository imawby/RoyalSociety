import RPi.GPIO as GPIO
#from gpiozero import Button
import time
import random
import matplotlib.pyplot as plt

from adafruit_mcp230xx.mcp23017 import MCP23017
import board
import busio

####################################
# Config
####################################

NUE_PROB_RANGE_FD = [0.0, 0.0745]
NUMU_PROB_RANGE_FD = [0.0745, 0.098]
NUTAU_PROB_RANGE_FD = [0.098, 1.0]

# FD pins
ND_PIN = 18
FD_NUE_PIN = 14
FD_NUMU_PIN = 15
FD_NUTAU_PIN = 16

pins = [ND_PIN, FD_NUE_PIN, FD_NUMU_PIN, FD_NUTAU_PIN]

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

####################################
# Let's get this show on the road!
####################################

def main() :
    GPIO.setmode(GPIO.BCM)  # set naming convention for pins
    GPIO.setwarnings(False)

    # Setup pins
    for pin in pins :
        GPIO.setup(pin, GPIO.OUT)

    # Turn everything off
    for pin in pins :
        GPIO.output(pin, GPIO.LOW)
    
    # Initialise the I2C bus:
    i2c_a = busio.I2C(board.SCL, board.SDA)
    i2c_b = busio.I2C(board.SCL, board.SDA)
    
    # Create MCP23017 instances
    mcp_a = MCP23017(i2c_a)
    mcp_b = MCP23017(i2c_b, address=0x24)
   
    pin_7a = mcp_a.get_pin(7)
    pin_8b = mcp_b.get_pin(8)

    pin_7a.switch_to_output(value=False)    
    pin_8b.switch_to_output(value=False)
    
    # Set event counters...
    n_nue_fd = 0
    n_numu_fd = 0
    n_nutau_fd = 0

    while (True) :

        turn_on_light(ND_PIN)
        
        pin_8b.switch_to_output(value=True)
        time.sleep(1)
        
        pin_8b.switch_to_output(value=False)
        pin_7a.switch_to_output(value=True)
        time.sleep(1)
        pin_7a.switch_to_output(value=False)        


        # What have we detected?
        random_number = random.uniform(0, 1)

        if ((random_number > NUE_PROB_RANGE_FD[0]) and (random_number < NUE_PROB_RANGE_FD[1])) : 
            n_nue_fd += 1
            turn_on_light(FD_NUE_PIN)
            #print("We have a nue!")
        elif ((random_number > NUMU_PROB_RANGE_FD[0]) and (random_number < NUMU_PROB_RANGE_FD[1])) : 
            turn_on_light(FD_NUMU_PIN)
            n_numu_fd += 1
            #print("We have a numu!")
        else :
            n_nutau_fd += 1
            turn_on_light(FD_NUTAU_PIN)
            #print("We have a nutau!")

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





'''
    # LEDs
    # Baseline 0m
    nue_0 = mcp_a.get_pin(0)
    numu_0 = mcp_a.get_pin(1)
    nutau_0 = mcp_a.get_pin(2)
    baseline_0 = [nue_0, numu_0, nutau_0]

    # Baseline 130m
    nue_1 = mcp_a.get_pin(3)
    numu_1 = mcp_a.get_pin(4)
    nutau_1 = mcp_a.get_pin(5)
    baseline_1 = [nue_1, numu_1, nutau_1]

    # Baseline 260m
    nue_2 = mcp_a.get_pin(6)
    numu_2 = mcp_a.get_pin(7)
    nutau_2 = mcp_a.get_pin(8)
    baseline_2 = [nue_2, numu_2, nutau_2]

    # Baseline 390m
    nue_3 = mcp_a.get_pin(9)
    numu_3 = mcp_a.get_pin(10)
    nutau_3 = mcp_a.get_pin(11)
    baseline_3 = [nue_3, numu_3, nutau_3]

    # Baseline 520m
    nue_4 = mcp_a.get_pin(12)
    numu_4 = mcp_a.get_pin(13)
    nutau_4 = mcp_a.get_pin(14)
    baseline_4 = [nue_4, numu_4, nutau_4]

    # Baseline 650m
    nue_5 = mcp_a.get_pin(15)
    numu_5 = mcp_b.get_pin(0)
    nutau_5 = mcp_b.get_pin(1)
    baseline_5 = [nue_5, numu_5, nutau_5]

    # Baseline 780m
    nue_6 = mcp_b.get_pin(2)
    numu_6 = mcp_b.get_pin(3)
    nutau_6 = mcp_b.get_pin(4)
    baseline_6 = [nue_6, numu_6, nutau_6]

    # Baseline 910m
    nue_7 = mcp_b.get_pin(5)
    numu_7 = mcp_b.get_pin(6)
    nutau_7 = mcp_b.get_pin(7)
    baseline_7 = [nue_7, numu_7, nutau_7]

    # Baseline 1040m
    nue_8 = mcp_b.get_pin(8)
    numu_8 = mcp_b.get_pin(9)
    nutau_8 = mcp_b.get_pin(10)
    baseline_8 = [nue_8, numu_8, nutau_8]

    # Baseline 1170m
    nue_9 = mcp_b.get_pin(11)
    numu_9 = mcp_b.get_pin(12)
    nutau_9 = mcp_b.get_pin(13)
    baseline_9 = [nue_9, numu_9, nutau_9]

    # All baseline
    baseline = [baseline_0, baseline_1, baseline_2, baseline_3, baseline_4, baseline_5, baseline_6, baseline_7, baseline_8, baseline_9]
''' 
