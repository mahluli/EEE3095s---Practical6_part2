import socket
import sys
import time
import busio
import digitalio
import board
import RPi.GPIO as GPIO
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import datetime
import os
import spidev
from flask import Flask
################TCP SEND SETUP###########################

#TODO Add code to setup the tcp connection with the correct IP and same port as the tcp_server on the other pi
    #Test this locally before trying to deploy via balena using test messages instead of ADC values
    #Use localmode when deploying to balena and use the advertised local address (using public IPs is possible but more complicated to configure due to the security measures BalenaOS imposes by default.  These are a good thing for real world deployment but over complicate the prac for the immediate purposes

HOST = "192.168.209.124"  # The server's hostname or IP address
PORT = 65432        # The port used by the server
#message = "Hellow dee"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

#the actual data sending is happpening in the main function

##################ADC Setup##############################

#TODO using the adafruit circuit python SPI and MCP libraries setup the ADC interface
#Google will supply easy to follow instructions 
# Open SPI bus

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7

count = 1 # global 

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(7,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(7,GPIO.FALLING,callback = general ,bouncetime = 300)


def general(channel):
    fun_10()

def fun_10():
    global count 
    count +=1 
    print_time_thread(10)

def fun_5(): 
    global count
    count +=1 
    print_time_thread(5)

def fun_1():
    global count
    count +=1
    print_time_thread(1)
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
    volts = (data * 3.3) / float(1023)
    volts = round(volts,places)
    return volts
 
# Function to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data,places):
    # ADC Value
    # (approx)  Temp  Volts
    #    0      -50    0.00
    #   78      -25    0.25
    #  155        0    0.50
    #  233       25    0.75
    #  310       50    1.00
    #  465      100    1.50
    #  775      200    2.50
    # 1023      280    3.30
    temp = ((data * 330)/float(1023))-50
    temp = round(temp,places)
    return temp
 
# Define sensor channels
light_channel = 0
temp_channel  = 1 
# Define delay between readings
delay = 5

print("Runtime\t\tTemp Reading\t\tTemp\t\tLight Reading")

record = [] # for storing the run times
lap = [] # for storing the durations

Duration = [] # for storing time objects
def print_time_thread(length=10):
    """
    This functions prints the time to the screen every 10 seconds 
    """


    t_start =datetime.datetime.now()
    Duration.append(t_start)
  
    #print(Duration)
  
    thread = threading.Timer(length,print_time_thread,args = (length,) )
    thread.daemon = True # Daemon thread exit when the program does 
    
    thread.start()
    output  = ""
    if(len(Duration)==1):
        output = "Os"
        record.append(output)
    else:
        for i in range(len(Duration)-1):
            diff = Duration[i+1] - Duration[0] 
            output  = str(round(diff.total_seconds()))
            output = output+"s"
        #output = output[:output.index('.')]+"s"
        record.append(output) 


    #print(record)
    # read the light sensor data 
    light_level = ReadChannel(light_channel)
    light_volts = ConvertVolts(light_level,2)

    # Read the temperature sensor data 
    temp_level = ReadChannel(temp_channel)
    temp_volts = ConvertVolts(temp_level,2)
    temp = ConvertTemp(temp_level,2)

    # print out the results
    print(record[-1]+"\t\t"+str(temp_level)+"\t\t\t"+str(temp)+" C\t\t"+str(light_level))
    return record[-1]+"\t\t"+str(temp_level)+"\t\t\t"+str(temp)+" C\t\t"+str(light_level)

#########################################################

print("Sensor Node it awake\n")     #Print statements to see what's happening in balena logs
#f.write("Sensor Node it awake\n")   #Write to file statements to see what's happening if you ssh into the device and open the file locally using nano
#f.flush()
#s.send(b'Sensor Node it awake\n')   #send to transmit an obvious message to show up in the balena logs of the server pi

#while(True):
#TODO add code to read the ADC values and print them, write them, and send them
if __name__ == "__main__":
    try:
        setup()
        # the program to run indefinitely
        sample = print_time_thread(10)
        print(sample)
        s.sendall(sample.encode())
        while true:
            reading = print_time_thread(10)
            # sending the sensor readings
            s.sendall(reading.encode())
            print(reading)
            time.sleep(10)
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
    


