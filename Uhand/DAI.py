import time
import serial
import struct
import math as m

import DAN

#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = 'uhand' #if None, Reg_addr = MAC address

DAN.profile['dm_name']='U-Hand'
DAN.profile['df_list']=['Thumb-O', 'Index-O','Middle-O', 'Ring-O','Pinky-O', 'Wrist-O']
DAN.profile['d_name']= '00.uHand'

DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line

Baudrate = 9600
COM = 'COM3'            # using in windows
#COM = '/dev/ttyUSB0'   # using in linux
Timeout = 3

try:
    ser = serial.Serial(COM, Baudrate, timeout=3)
except Exception as e:
    print(e)

Servo1_min = 800
Servo1_max = 2400
Servo2_min = 750
Servo2_max = 2100
Servo3_min = 700
Servo3_max = 2000
Servo4_min = 800
Servo4_max = 2050
Servo5_min = 900
Servo5_max = 2200
Servo6_min = 500
Servo6_max = 2500

Servo1_low = Servo1_max
Servo1_high = Servo1_min
Servo2_low = Servo2_min
Servo2_high = Servo2_max
Servo3_low = Servo3_min
Servo3_high = Servo3_max
Servo4_low = Servo4_min
Servo4_high = Servo4_max
Servo5_low = Servo5_max
Servo5_high = Servo5_min
Servo6_left = Servo6_min
Servo6_right = Servo6_max

def PercentToLevel(no, percent):
    val = 0
    if no == 1:
        val = (int) (Servo1_max-(percent*((Servo1_max-Servo1_min)/100)))
    if no == 2:
        val = (int) (Servo2_min+percent*((Servo2_max-Servo2_min)/100))
    if no == 3:
        val = (int) (Servo3_min+percent*((Servo3_max-Servo3_min)/100))
    if no == 4:
        val = (int) (Servo4_min+percent*((Servo4_max-Servo4_min)/100))
    if no == 5:
        val = (int) (Servo5_max-(percent*((Servo5_max-Servo5_min)/100)))
    if no == 6:
        val = (int) (Servo6_min+percent*((Servo6_max-Servo6_min)/100))
    return val

def SingleServoCtrl(no,speed,percent):
        val_byte = struct.pack('<H',PercentToLevel(no,percent))
        speed_byte = struct.pack('<H',speed)
        val_bytearray = bytearray([85,85,8,3,1,speed_byte[0],speed_byte[1],no,val_byte[0],val_byte[1]])
        ser.write(val_bytearray)

def DegreeToPercent(degree):
    input_degree = degree
    result_percent = None
    max_degree = 175
    min_degree = 95
    max_percent= 100
    min_percent = 0

    degree_map = [95, 125, 175]
    percent_map = [0, 50, 100]

    if input_degree >= max_degree:
        result_percent = max_percent
    elif input_degree <= min_degree:
        result_percent = min_percent
    else:
        for n in range(len(degree_map)-1):
            if input_degree >= degree_map[n] and input_degree <= degree_map[n+1]:
                result_percent = percent_map[n]+((input_degree-degree_map[n])/(degree_map[n+1] - degree_map[n])*(percent_map[n+1]-percent_map[n]))
        if input_degree == 0 or input_degree == None:
            print("Calculte finger value error!")
    return result_percent

def SingleServoCtrlWithAngle(servo_no,angle):
    servo_percent = DegreeToPercent(angle)
    SingleServoCtrl(servo_no,0,servo_percent)

def initial_low():
    SingleServoCtrl(1,0,0)
    SingleServoCtrl(2,0,0)
    SingleServoCtrl(3,0,0)
    SingleServoCtrl(4,0,0)
    SingleServoCtrl(5,0,0)
    time.sleep(0.5)

def initial_high():
    SingleServoCtrl(1,0,100)
    SingleServoCtrl(2,0,100)
    SingleServoCtrl(3,0,100)
    SingleServoCtrl(4,0,100)
    SingleServoCtrl(5,0,100)
    time.sleep(0.5)

def initial():
    initial_high()
    time.sleep(0.5)
    initial_low()
    time.sleep(0.5)
    SingleServoCtrl(6,0,50)
    time.sleep(1)

initial()
print('Initial done')


while True:
    try:
        Servo_O1_data = DAN.pull('Thumb-O')
        Servo_O2_data = DAN.pull('Index-O')
        Servo_O3_data = DAN.pull('Middle-O')
        Servo_O4_data = DAN.pull('Ring-O')
        Servo_O5_data = DAN.pull('Pinky-O')
        Servo_O6_data = DAN.pull('Wrist-O')
        if Servo_O1_data != None:
            servo1_data = Servo_O1_data[1]
            SingleServoCtrlWithAngle(1,servo1_data)
            #print('Servo1 data:'+ str(servo1_data))
        if Servo_O2_data != None:
            servo2_data = Servo_O2_data[1]
            SingleServoCtrlWithAngle(2,servo2_data)
            #print('Servo2 data:'+ str(servo2_data))
        if Servo_O3_data != None:
            servo3_data = Servo_O3_data[1]
            SingleServoCtrlWithAngle(3,servo3_data)
            #print('Servo3 data:'+ str(servo3_data))
        if Servo_O4_data != None:
            servo4_data = Servo_O4_data[1]
            SingleServoCtrlWithAngle(4,servo4_data)
            #print('Servo4 data:'+ str(servo4_data))
        if Servo_O5_data != None:
            servo5_data = Servo_O5_data[1]
            SingleServoCtrlWithAngle(5,servo5_data)
            #print('Servo5 data:'+ str(servo5_data))
        if Servo_O6_data != None:
            servo6_data = Servo_O6_data[1]
            SingleServoCtrlWithAngle(6,servo6_data)
            #print('Servo6 data:'+ str(servo6_data))

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(0.05)