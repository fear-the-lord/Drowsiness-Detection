# Import the necessary packages 
from EAR_calculator import *
from imutils import face_utils 
from imutils.video import VideoStream 
import imutils 
import dlib
import time 
import argparse 
import cv2 
from playsound import playsound
from scipy.spatial import distance as dist

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

# Now, loop over all the frames and detect the faces
while True: 
	# Extract a frame 
	frame = vs.read() 
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

		# Compute the convex hull for both the eyes and then visualize it
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		# Draw the contours 
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [mouth], -1, (0, 255, 0), 1)

		MAR = mouth_aspect_ratio(mouth)

		# Check if EAR < EAR_THRESHOLD, if so then it indicates that a blink is taking place 
		# Thus, count the number of frames for which the eye remains closed 
		if EAR < EAR_THRESHOLD: 
			FRAME_COUNT += 1

			cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)

			if FRAME_COUNT >= CONSECUTIVE_FRAMES: 
				playsound('sound files/alarm.mp3')
				cv2.putText(frame, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		else: 
			if FRAME_COUNT >= CONSECUTIVE_FRAMES: 
				playsound('sound files/warning.mp3')
			FRAME_COUNT = 0
		cv2.putText(frame, "EAR: {:.2f}".format(EAR), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

		# Check if the person is yawning
		if MAR > MAR_THRESHOLD:
			cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1) 
			cv2.putText(frame, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			playsound('sound files/alarm.mp3')
			playsound('sound files/warning_yawn.mp3')
			
	#Display the frame 
	cv2.imshow("Output", frame)
	key = cv2.waitKey(1) & 0xFF 

	if key == ord('q'):
		break

cv2.destroyAllWindows()
vs.stop()