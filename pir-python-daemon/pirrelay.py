#!/usr/bin/python
import RPi.GPIO as GPIO
import time

PIR = 27
RELAY = 17
DETECTIONTIMEOUT = 2*60

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR, GPIO.IN)            #Read output from PIR motion sensor
GPIO.setup(RELAY, GPIO.OUT)         #LED Relay output pin


while True:
    i=GPIO.input(PIR)
    if i==0:                 #When output from motion sensor is LOW
       GPIO.output(RELAY, GPIO.LOW)  #Turn OFF LED
       time.sleep(0.5)
    elif i==1:               #When output from motion sensor is HIGH
       while GPIO.input(PIR) == 1:
           GPIO.output(RELAY, GPIO.HIGH)  #Turn ON SCREEN
           time.sleep(DETECTIONTIMEOUT)
       
        
 
