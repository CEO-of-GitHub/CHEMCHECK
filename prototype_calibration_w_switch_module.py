import RPi.GPIO as GPIO
import time
import os.path

# Pins for TCS3200 Color Sensor

s0 = 27
s1 = 22
s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10

# Pins for Keypad 

KP_ROW = [5,6,13,19]
KP_COL = [12,16,20,21]

# Keypad Matrix

MATRIX = [ [1,2,3,'A'],
           [4,5,6,'B'],
           [7,8,9,'C'],
           ['*',0,'#','D'] ]

# Placeholders

nRED = 0
nGREEN = 1
nBLUE = 2

calibrationValues = []

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s0,GPIO.OUT)
    GPIO.setup(s1,GPIO.OUT)
    GPIO.setup(s2,GPIO.OUT)
    GPIO.setup(s3,GPIO.OUT)
  
    GPIO.output(s0,GPIO.LOW)
    GPIO.output(s1,GPIO.HIGH)
  
    for j in range(4):
        GPIO.setup(KP_COL[j],GPIO.OUT)
        GPIO.output(KP_COL[j],GPIO.HIGH)
    
    for i in range(4):
        GPIO.setup(KP_ROW[i],GPIO.IN,pull_up_down=GPIO.PUD_UP)
  
    print("\n")

def loop():
    global calibrationValues
    temp = 1
    print("CHOOSE OPERATION\nPress A: Color Calibration\nPress B: Color Sensing\nPress C: SAVE Current Calibration Config\nPress D: LOAD Latest Calibration Config")
    while(1): 
        pick = selectMODE()
        if pick == 'A':
            calibrationValues = calibrationMODE()
        elif pick == 'B':
            if not calibrationValues:
                print("There are no calibration values set for color sensing. Please perform the color calibration process first.\n\n")
            elif calibrationValues:
                RGBval = sensingMODE()
                print("R: " + str(RGBval[nRED]) + "     G: " + str(RGBval[nGREEN]) + "     B: " + str(RGBval[nBLUE]))
                print("\n\n")
        elif pick == 'C':
            if not calibrationValues:
                print("There are no calibration values set for saving. Please perform the color calibration process first.\n\n")
            elif calibrationValues:
                if checkConfig() == 1:
                    print("Saving current calibration config will override the previous one. Do you wish to continue? (0-no,1-yes)")
                    while(True):
                        pick2 = selectMODE()
                        if pick2 == 0:
                            print("Attempt to save calibration config cancelled.\n\n")
                            break
                        if pick2 == 1:
                            saveConfig()
                            print("Saved current calibration config!\n\n")
                            break
                elif checkConfig() == 0:
                    saveConfig()
                    print("Saved current calibration config!\n\n")
        elif pick == 'D':
            if checkConfig() == 1:
                if calibrationValues:
                    print("Loading latest calibration config will override the current one. Do you wish to continue? (0-no,1-yes)")
                    while(True):
                        pick3 = selectMODE()
                        if pick3 == 0:
                            print("Attempt to load \"config.txt\" cancelled.\n\n")
                            break
                        if pick3 == 1:
                            saveConfig()
                            print("Loaded \"config.txt\" successfully!\n\n")
                            break
                elif not calibrationValues:
                    loadConfig()
            elif checkConfig() == 0:
                print("Config file \"config.txt\" does not exist!\n\n")
        else:
            print("Invalid option. Try again.\n\n")
       
def selectMODE():
    while(True):
        for j in range(4):
            GPIO.output(KP_COL[j],GPIO.LOW)
            for i in range(4):
                if GPIO.input(KP_ROW[i]) == 0:
                    returnVal = MATRIX[i][j]
                    while(GPIO.input(KP_ROW[i]) == 0):
                        pass
                    return returnVal
            GPIO.output(KP_COL[j],GPIO.HIGH)

def calibrationMODE():
    global calibrationValues
    print("Start...")
    time.sleep(5)
    
    # Calibrate for (255,0,0), (0,255,0), and (0,0,255)
    print("Provide RGB model for RED (255,0,0) in 5 seconds")
    time.sleep(5)
    red_high = colorCalibrate(GPIO.LOW,GPIO.LOW,'R',255)
    print("Provide RGB model for GREEN (0,255,0) in 5 seconds")
    time.sleep(5)
    green_high = colorCalibrate(GPIO.HIGH,GPIO.HIGH,'G',255)
    print("Provide RGB model for BLUE (0,0,255) in 5 seconds")
    time.sleep(5)
    blue_high = colorCalibrate(GPIO.LOW,GPIO.HIGH,'B',255)
    
    # Calibrate for (0,0,0)
    print("Provide RGB model for BLACK (0,0,0) in 5 seconds")
    time.sleep(5)
    red_low = colorCalibrate(GPIO.LOW,GPIO.LOW,'R',0)
    green_low = colorCalibrate(GPIO.HIGH,GPIO.HIGH,'G',0)
    blue_low = colorCalibrate(GPIO.LOW,GPIO.HIGH,'B',0)
    
    calibrationValues = [[red_low, green_low, blue_low], [red_high, green_high, blue_high]]
    print("\nCalibration done!\n\n")
    
    return calibrationValues

def sensingMODE():
    global calibrationValues
    print("Detecting color...")
    RAWval = colorReadRAW_FULL()
    print("Processing detected color...")
    RGB_1 = [0,0,0]
    RGB_2 = [255,255,255]
    time.sleep(5)
    RGBval = colorRead_FULL(RAWval, calibrationValues[0], calibrationValues[1], RGB_1, RGB_2)
    return RGBval

def map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def colorCalibrate(s2val,s3val,color,intensity):
    #if intensity not in range(256):
    #    print("Invalid intensity value. Please try again.")
    #    time.sleep(5)
    #    return -1
    #print("Provide a color model for " + color + " with intensity " + str(intensity) + " in 5 seconds:")
    #time.sleep(5)
    calibration_value = colorReadRAW(s2val,s3val)
    #print("Calibration for " + color + " complete, resulting equality is (" + color + ")" + str(intensity) + " = " + str(calibration_value))
    # 'intensity' refers to intensity value of R, G, or B hue, which falls in the range of 0-255 
    return calibration_value
    # 'calibration_value' refers to RAW intensity value

def colorCalibrate_FULL():
    time.sleep(5)
    print("Calibrating the RED value:")
    time.sleep(1)
    red = colorReadRAW(GPIO.LOW,GPIO.LOW)
    print("Calibrating the GREEN value:")
    time.sleep(1)
    green = colorReadRAW(GPIO.HIGH,GPIO.HIGH)
    print("Calibrating the BLUE value:")
    time.sleep(1)
    blue = colorReadRAW(GPIO.LOW,GPIO.HIGH)
    calibration_value = [red, green, blue]
    return calibration_value
    
def colorReadRAW(s2val,s3val):
    GPIO.output(s2,s2val)
    GPIO.output(s3,s3val)
    
    reps = 10
    result_values
    for i in range(reps):
           start = time.time()
           for impulse_count in range(NUM_CYCLES):
                      GPIO.wait_for_edge(signal, GPIO.FALLING)
           duration = time.time() - start
           result_value = NUM_CYCLES / duration
           result_values += result_value
    return result_values / reps
    
def colorReadRAW_FULL():
    red = colorReadRAW(GPIO.LOW,GPIO.LOW)
    green = colorReadRAW(GPIO.HIGH,GPIO.HIGH)
    blue = colorReadRAW(GPIO.LOW,GPIO.HIGH)
    RAWlist = [red, green, blue]
    return RAWlist
    
def colorRead(RAWval, RAW_1, RAW_2, RGB_1, RGB_2):
    return int((RAWval) * ((RGB_2 - RGB_1) / (RAW_2 - RAW_1)))
    # above equation is just a Python version of Arduino's map() function

def colorRead_FULL(RAWval, RAW_1, RAW_2, RGB_1, RGB_2):
    red = int((RAWval[nRED]) * ((RGB_2[nRED] - RGB_1[nRED]) / (RAW_2[nRED] - RAW_1[nRED])))
    green = int((RAWval[nGREEN]) * ((RGB_2[nGREEN] - RGB_1[nGREEN]) / (RAW_2[nGREEN] - RAW_1[nGREEN])))
    blue = int((RAWval[nBLUE]) * ((RGB_2[nBLUE] - RGB_1[nBLUE]) / (RAW_2[nBLUE] - RAW_1[nBLUE])))
    RGBlist = [red, green, blue]
    return RGBlist

def checkConfig():
    if os.path.exists("config.txt") == True:
      return 1
    elif os.path.exists("config.txt") == False:
      return 0

def saveConfig():
    global calibrationValues
    f = open("config.txt","a")
    f.seek(0)
    for group in calibrationValues:
           for item in calibrationValues[group]:
                      f.write(str(calibrationValues[group][item]) + " ")
           f.write("\n")
    f.close()

def loadConfig():
    global calibrationValues
    f = open("config.txt","r")
    calibrationValues = f.splitlines()
    for i in calibrationValues:
           calibrationValues[i] = f.split()
    f.close()

def endprogram():
    GPIO.cleanup()

if __name__=='__main__':
    
    setup()

    try:
        loop()

    except KeyboardInterrupt:
        endprogram()








# For CHEMCHECK's sample detection, 3D print a "sample module". Similar sa IMAHE stackable sample holder so that non-reflective material can be locked in place (instead of nylon mesh kay this time it's the transparent material)

# Unify calibration for R, G, and B tomorrow

# Order of functions in calibration process: (colorCalibrate && colorReadRAW >> colorRead) or (colorCalibrate_FULL && colorReadRAW_FULL >> colorRead_FULL)

# Membrane Switch Code is based on https://www.youtube.com/watch?v=yYnX5QodqQ4
