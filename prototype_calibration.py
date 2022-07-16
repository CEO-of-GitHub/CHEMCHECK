import RPi.GPIO as GPIO
import time

s0 = 27
s1 = 22
s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10

nRED = 0
nGREEN = 1
nBLUE = 2

def setup():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(s0,GPIO.OUT)
  GPIO.setup(s1,GPIO.OUT)
  GPIO.setup(s2,GPIO.OUT)
  GPIO.setup(s3,GPIO.OUT)
  
  GPIO.output(s0,GPIO.LOW)
  GPIO.output(s1,GPIO.HIGH)
  
  print("\n")

def loop():
  temp = 1
  while(1): 
       
    print("Start...")
    time.sleep(5)
    
    
    # Calibrate for (255,0,0), (0,255,0), and (0,0,255)
    print("Provide RGB model for RED (255,0,0)")
    red_high = colorCalibrate(GPIO.LOW,GPIO.LOW,'R',255)
    print("Provide RGB model for GREEN (0,255,0)")
    green_high = colorCalibrate(GPIO.HIGH,GPIO.HIGH,'G',255)
    print("Provide RGB model for BLUE (0,0,255)")
    blue_high = colorCalibrate(GPIO.LOW,GPIO.HIGH,'B',255)
    calibration_high = [red_high, green_high, blue_high]
    
    # Calibrate for (0,0,0)
    print("Provide RGB model for BLACK (0,0,0)")
    red_low = colorCalibrate(GPIO.LOW,GPIO.LOW,'R',0)
    green_low = colorCalibrate(GPIO.HIGH,GPIO.HIGH,'G',0)
    blue_low = colorCalibrate(GPIO.LOW,GPIO.HIGH,'B',0)
    calibration_low = [red_low, green_low, blue_low]
    
    # Find RAW color values of sample
    print("Provide sample:")
    time.sleep(5)
    RAWval = colorReadRAW_FULL()
    
    RGB_1 = [0,0,0]
    RGB_2 = [255,255,255]
    
    # Determine each of the RGB (all red, green, and blue) values of sample based on previous calibration
    print("Processing...")
    time.sleep(5)
    print(str(colorRead_FULL(RAWval, calibration_low, calibration_high, RGB_1, RGB_2)))
    # Needs revision
    
    # RED
    #print("Red value - " + str(colorReadRAW(GPIO.LOW,GPIO.LOW)))
    # BLUE
    #print("Blue value - ", colorReadRAW(GPIO.LOW,GPIO.HIGH))
    # GREEN
    #print("Green value - ", colorReadRAW(GPIO.HIGH,GPIO.HIGH))
    print("\n")
    #time.sleep(5)

def map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def colorCalibrate(s2val,s3val,color,intensity):
    if intensity not in range(256):
        print("Invalid intensity value. Please try again.")
        time.sleep(5)
        return -1
    print("Provide a color model for " + color + " with intensity " + str(intensity) + " in 5 seconds:")
    time.sleep(5)
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
    time.sleep(0.3)
    
    #print("Provide sample:")
    #time.sleep(5) 
    
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start
    result_value = NUM_CYCLES / duration
    return result_value    
    
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
