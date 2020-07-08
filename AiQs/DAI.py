import time
import socket
import threading
import math as m

from datetime import datetime

import DAN

#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = 'A-Glove' #if None, Reg_addr = MAC address

DAN.profile['dm_name']='A-Glove'
DAN.profile['df_list']=['Thumb-I', 'Index-I', 'Middle-I', 'Ring-I', 'Pinky-I','Wrist-I']
#DAN.profile['d_name']= 'Assign a Device Name' 

DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line

landmarks = [0]*28
dof27 = [0]*27
last_data_timestamp = datetime.now()
last_push_timestamp = last_data_timestamp

def LMtoADegreeUsingLawOfCosines(LandMark_data):      # degree = arcccos( (a^2 + b^2 - c^2) / 2ab )
    results_dof27 = [0]*27
    lm_xyz = LandMark_data
    offset_list = [3,4,5,8,9,10,13,14,15,18,19,20,23,24,25]
    dof_list = [6,8,10,11,13,14,15,17,18,19,21,22,23,25,26]

    for i in range(len(offset_list)):
        offset = offset_list[i]
        ab_x = float(lm_xyz[1+offset][0])-float(lm_xyz[0+offset][0])
        ab_y = float(lm_xyz[1+offset][1])-float(lm_xyz[0+offset][1])
        ab_z = float(lm_xyz[1+offset][2])-float(lm_xyz[0+offset][2])
        bc_x = float(lm_xyz[2+offset][0])-float(lm_xyz[1+offset][0])
        bc_y = float(lm_xyz[2+offset][1])-float(lm_xyz[1+offset][1])
        bc_z = float(lm_xyz[2+offset][2])-float(lm_xyz[1+offset][2])
        ac_x = float(lm_xyz[2+offset][0])-float(lm_xyz[0+offset][0])
        ac_y = float(lm_xyz[2+offset][1])-float(lm_xyz[0+offset][1])
        ac_z = float(lm_xyz[2+offset][2])-float(lm_xyz[0+offset][2])
        a = m.sqrt(m.pow(ab_x,2)+m.pow(ab_y,2)+m.pow(ab_z,2))    # AB = a
        b  = m.sqrt(m.pow(bc_x,2)+m.pow(bc_y,2)+m.pow(bc_z,2))   # BC = b
        c = m.sqrt(m.pow(ac_x,2)+m.pow(ac_y,2)+m.pow(ac_z,2))    # AC = c
        cos = (m.pow(a,2)+m.pow(b,2)-m.pow(c,2))/(2*a*b)         # cos = (a^2 + b^2 - c^2) / 2ab 
        degree = m.degrees(m.acos(cos))                          # degree = arcccos( cos )
        results_dof27[dof_list[i]] = degree

    return results_dof27

def ReceiveAiqsDataSocket():
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = 11011              # Arbitrary non-privileged port
    global landmarks, dof27, last_data_timestamp
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            print("Waiting client connect")
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                print('Connected with', addr)
                while True:
                    try:
                        data = conn.recv(1024)
                        if not data:
                           break

                        data = data.decode('utf-8')
                        str_temp = data.replace("\n",", ").split(', ')
                        landmarks = [0]*28
                        for i in range (len(landmarks)):
                            offset = i*3
                            landmarks[i] = [str_temp[offset], str_temp[offset+1], str_temp[offset+2]]
                        fingers_degree = LMtoADegreeUsingLawOfCosines(landmarks)
                        print(data)
                        print(fingers_degree)
                        landmarks = data
                        dof27 = fingers_degree
                        last_data_timestamp = datetime.now()
                    except Exception as e:
                        print("Socket disconnect because", str(e))
                        break
                conn.close()

threaad_socket = threading.Thread(target=ReceiveAiqsDataSocket)
threaad_socket.daemon = True 
threaad_socket.start()

while True:
    try:
        
        if last_data_timestamp > last_push_timestamp:
            last_push_timestamp = last_data_timestamp

            thumb = [dof27[6],dof27[8],dof27[10]]   
            index = [dof27[11],dof27[13],dof27[14]]
            middle = [dof27[15],dof27[17],dof27[18]]
            ring = [dof27[19],dof27[21],dof27[22]]
            pinky = [dof27[23],dof27[25],dof27[26]]

            DAN.push('Thumb-I', thumb[0],thumb[1],thumb[2])
            DAN.push('Index-I', index[0],index[1],index[2])
            DAN.push('Middle-I', middle[0],middle[1],middle[2])
            DAN.push('Ring-I', ring[0],ring[1],ring[2])
            DAN.push('Pinky-I', pinky[0],pinky[1],pinky[2])

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(0.05)