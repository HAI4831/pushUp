import os
import subprocess
import sys
import shutil
import venv

script_dir = os.path.dirname(os.path.realpath(__file__))
setup_file = os.path.join(script_dir, "setup.txt")

# Set up the virtual environment directory
venv_dir = os.path.join(script_dir , "venv")
# os.makedirs(venv_dir, exist_ok=True)

# Create the virtual environment
venv.create(venv_dir, with_pip=True)
# Activate the virtual environment
if sys.platform == "win32":
    activate_script = os.path.join(venv_dir, "Scripts", "activate.bat")
else:
    activate_script = os.path.join(venv_dir, "bin", "activate")
subprocess.call(activate_script, shell=True)

print(f"setup:{setup_file}")
# Install PyTorch within the virtual environment
subprocess.call([sys.executable, "-m", "pip", "install", "-r", setup_file])

# Verify the installation by importing torch
import torch

# Print the PyTorch version
print("PyTorch version:", torch.__version__)



# script_path = os.path.abspath(__file__)
# script_dir = os.path.dirname(script_path)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
clear()

import cv2
import mediapipe as mp
import numpy as np
import PoseModulePy as pm

cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
count = 0
direction = 0
form = 0
feedback = "Fix Form"

#cap.get(x) x=
#1.cv2.CAP_PROP_POS_MSEC: Current position of the video file in milliseconds.
#2.cv2.CAP_PROP_POS_FRAMES: Index of the next frame to be captured.
#3.cv2.CAP_PROP_FRAME_WIDTH: Width of the frames in the video stream.
#4.cv2.CAP_PROP_FRAME_HEIGHT: Height of the frames in the video stream.
#5.cv2.CAP_PROP_FPS: Frame rate of the video stream.
#6.cv2.CAP_PROP_FRAME_COUNT: Total number of frames in the video file.

while cap.isOpened():

    ret, img = cap.read() #640 x 480
    cv2.imshow('Pushup counter', img)
    #Determine dimensions of video - Help with creation of box in Line 43
    width  = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    print(f"""Current position of the video file in milliseconds:{cap.get(1)}
          Index of the next frame to be captured:{cap.get(2)}
          Width of the frames in the video stream:{cap.get(3)}
          Height of the frames in the video stream:{cap.get(4)}
          Frame rate of the video stream:{cap.get(5)}
          Total number of frames in the video file:{cap.get(6)}\n""")
    
    img = detector.findPose(img, True)
    lmList = detector.findPosition(img, True)
    # print(lmList)
    if len(lmList) != 0:
        elbow = detector.findAngle(img, 11, 13, 15)#góc khuỷu tay 
        shoulder = detector.findAngle(img, 13, 11, 23)#góc vai
        hip = detector.findAngle(img, 11, 23,25)# góc hông
        
        #Percentage of success of pushup
        per = np.interp(elbow, (90, 160), (0, 100))#quy dổi giá trị của khuỷu tay từ dải giá trị 90-160 đến dải 0-100 ct (x-min)/(max-min)*width + min new
        # nếu tay góc tay 90 tỉ lệ thành công là đẩy là 0 ,160 tỉ lệ là đẩy là 100
        #Bar to show Pushup progress
        bar = np.interp(elbow, (90, 160), (380, 50))

        #Check to ensure right form before starting the program
        if elbow > 160 :
            form = 1
    
        #Check for full range of motion for the pushup
        if form == 1:
            if per == 0:
                if elbow <= 45 :
                    feedback = "Up"
                    if direction == 0:
                        count += 0.5
                        direction = 1
                else:
                    feedback = "Fix Form"
                    
            if per == 100:
                if elbow > 160 :
                    feedback = "Down"
                    if direction == 1:
                        count += 0.5
                        direction = 0
                else:
                    feedback = "Fix Form"
                        # form = 0
                
                    
    
        print(count)
        
        #Draw Bar
        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 0), 2)


        #Pushup counter
        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)
        
        #Feedback 
        cv2.rectangle(img, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, feedback, (500, 40 ), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)

        
    cv2.imshow('Pushup counter', img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
os.system("deactivate")