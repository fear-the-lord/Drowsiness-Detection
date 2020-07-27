# Import the necessary packages 
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from EAR_calculator import *
from imutils import face_utils 
from imutils.video import VideoStream
import matplotlib.pyplot as plt
import matplotlib.animation as animate
from matplotlib import style 
import imutils 
import dlib
import time 
import argparse 
import cv2 
from playsound import playsound
from scipy.spatial import distance as dist
import os 
import csv
import numpy as np
import pandas as pd
from datetime import datetime

style.use('fivethirtyeight')
# Creating the dataset 
def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


#all eye  and mouth aspect ratio with time
ear_list=[]
total_ear=[]
mar_list=[]
total_mar=[]
ts=[]
total_ts=[]
# Construct the argument parser and parse the arguments 
ap = argparse.ArgumentParser() 
ap.add_argument("-p", "--shape_predictor", required = True, help = "path to dlib's facial landmark predictor")
ap.add_argument("-r", "--picamera", type = int, default = -1, help = "whether raspberry pi camera shall be used or not")
args = vars(ap.parse_args())

# Declare a constant which will work as the threshold for EAR value, below which it will be regared as a blink 
EAR_THRESHOLD = 0.3
# Declare another costant to hold the consecutive number of frames to consider for a blink 
CONSECUTIVE_FRAMES = 20 
# Another constant which will work as a threshold for MAR value
MAR_THRESHOLD = 14

# Initialize two counters 
BLINK_COUNT = 0 
FRAME_COUNT = 0 

# Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print("[INFO]Loading the predictor.....")
detector = dlib.get_frontal_face_detector() 
predictor = dlib.shape_predictor(args["shape_predictor"])

# Grab the indexes of the facial landamarks for the left and right eye respectively 
(lstart, lend) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rstart, rend) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mstart, mend) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# Now start the video stream and allow the camera to warm-up
print("[INFO]Loading Camera.....")
vs = VideoStream(usePiCamera = args["picamera"] > 0).start()
time.sleep(2) 

assure_path_exists("dataset/")
count_sleep = 0
count_yawn = 0 

 
# Now, loop over all the frames and detect the faces
while True: 
	# Extract a frame 
	frame = vs.read()
	cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3) 
	# Resize the frame 
	frame = imutils.resize(frame, width = 500)
	# Convert the frame to grayscale 
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# Detect faces 
	rects = detector(frame, 1)

	# Now loop over all the face detections and apply the predictor 
	for (i, rect) in enumerate(rects): 
		shape = predictor(gray, rect)
		# Convert it to a (68, 2) size numpy array 
		shape = face_utils.shape_to_np(shape)

		# Draw a rectangle over the detected face 
		(x, y, w, h) = face_utils.rect_to_bb(rect) 
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)	
		# Put a number 
		cv2.putText(frame, "Driver", (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

		leftEye = shape[lstart:lend]
		rightEye = shape[rstart:rend] 
		mouth = shape[mstart:mend]
		# Compute the EAR for both the eyes 
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)

		# Take the average of both the EAR
		EAR = (leftEAR + rightEAR) / 2.0
		#live datawrite in csv
		ear_list.append(EAR)
		#print(ear_list)
		

		ts.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
		# Compute the convex hull for both the eyes and then visualize it
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		# Draw the contours 
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [mouth], -1, (0, 255, 0), 1)

		MAR = mouth_aspect_ratio(mouth)
		mar_list.append(MAR/10)
		# Check if EAR < EAR_THRESHOLD, if so then it indicates that a blink is taking place 
		# Thus, count the number of frames for which the eye remains closed 
		if EAR < EAR_THRESHOLD: 
			FRAME_COUNT += 1

			cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)

			if FRAME_COUNT >= CONSECUTIVE_FRAMES: 
				count_sleep += 1
				# Add the frame to the dataset ar a proof of drowsy driving
				cv2.imwrite("dataset/frame_sleep%d.jpg" % count_sleep, frame)
				playsound('sound files/alarm.mp3')
				cv2.putText(frame, "DROWSINESS ALERT!", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		else: 
			if FRAME_COUNT >= CONSECUTIVE_FRAMES: 
				playsound('sound files/warning.mp3')
			FRAME_COUNT = 0
		#cv2.putText(frame, "EAR: {:.2f}".format(EAR), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

		# Check if the person is yawning
		if MAR > MAR_THRESHOLD:
			count_yawn += 1
			cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1) 
			cv2.putText(frame, "DROWSINESS ALERT!", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			# Add the frame to the dataset ar a proof of drowsy driving
			cv2.imwrite("dataset/frame_yawn%d.jpg" % count_yawn, frame)
			playsound('sound files/alarm.mp3')
			playsound('sound files/warning_yawn.mp3')
	#total data collection for plotting
	for i in ear_list:
		total_ear.append(i)
	for i in mar_list:
		total_mar.append(i)			
	for i in ts:
		total_ts.append(i)
	#display the frame 
	cv2.imshow("Output", frame)
	key = cv2.waitKey(1) & 0xFF 
	
	

	if key == ord('q'):
		break

a = total_ear
b=total_mar
c = total_ts

df = pd.DataFrame({"EAR" : a, "MAR":b,"TIME" : c})
df.to_csv("op_webcam.csv", index=False)
df=pd.read_csv("op_webcam.csv")

df.plot(x='TIME',y=['EAR','MAR'])
#plt.xticks(rotation=45, ha='right')

plt.subplots_adjust(bottom=0.30)
plt.title('EAR & MAR calculation over time of webcam')
plt.ylabel('EAR & MAR')
plt.gca().axes.get_xaxis().set_visible(False)
plt.show()
cv2.destroyAllWindows()
vs.stop()
