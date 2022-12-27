import time
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os
from future.builtins import input
import sys
from stretch_body.dynamixel_XL430 import *
import argparse
import stretch_body.device

d = stretch_body.device.Device(name='dummy_device') # to initialize logging config

parser=argparse.ArgumentParser(description='Jog a Dynamixel servo from the command line')
parser.add_argument("usb", help="The dynamixel USB bus e.g.: /dev/hello-dynamixel-head")
parser.add_argument("id", help="The ID to jog", type=int)
parser.add_argument("--baud", help="Baud rate (57600, 115200, or 1000000) [57600]", type=int,default=57600)
args = parser.parse_args()

yaw = DynamixelXL430(args.id, args.usb,baud=args.baud) # id, usb, baud
pitch = DynamixelXL430(int(args.id+1), args.usb,baud=args.baud) # id, usb, baud

if not yaw.startup() or not yaw.do_ping() or not pitch.startup() or not pitch.do_ping():
    print('Failed to start gimbal')
    exit(0)

yaw.disable_torque()
pitch.disable_torque()

#If servo somehow has wrong drive mode it may appear to not respond to vel/accel profiles
#Can reset it here by uncommenting
#yaw.set_drive_mode(vel_based=True,reverse=False)

yaw.enable_pos()
yaw.enable_torque()

pitch.enable_pos()
pitch.enable_torque()


def move_gimbal(event):
    try:
        x,y = event.data['x'], event.data['y'] if event.data.get('x') and event.data.get('y') else None
        if x and y:
        
            print(x,y)
            
            if x > 0.7:
                yaw.go_to_pos(yaw.get_pos()+25)
                #pitch.go_to_pos(pitch.get_pos()+50)
                        
            if y > 0.7:
                #yaw.go_to_pos(yaw.get_pos()+50)
                pitch.go_to_pos(pitch.get_pos()+50)
                            
            if x < -0.7:
                yaw.go_to_pos(yaw.get_pos()-25)
                #pitch.go_to_pos(pitch.get_pos()-25)
                                    
            if y < -0.7:
                #yaw.go_to_pos(yaw.get_pos()-25)
                pitch.go_to_pos(pitch.get_pos()-50)
                        
    except KeyError as e:
        #       print(e)
        pass

if __name__ == "__main__":

    cred = credentials.Certificate("keys/touri-65f07-firebase-adminsdk-wuv71-3751c21aa8.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://touri-65f07-default-rtdb.firebaseio.com/'})

    db.reference("gimbal").listen(move_gimbal)
