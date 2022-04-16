import logging
from imutils import paths
import face_recognition
import pickle
import cv2
import os
import time
# initialize the log settings
from functions import if_dir_not_exists

logging.basicConfig(filename='error_face_encoding.log', level=logging.INFO, filemode='w')
try:
	# check directory
	def if_dir_not_exists(directory):
		# Check directory exist or not
		if not os.path.exists(directory):
			os.mkdir(directory)

	# grab the paths to the input images in our dataset
	print("[INFO] quantifying faces...")

	imagePaths = list(paths.list_images("all_employees"))

	# initialize the list of known encodings and known names
	knownEncodings = []
	knownNames = []

	# loop over the image paths
	for (i, imagePath) in enumerate(imagePaths):
		# extract the person name from the image path
		print("[INFO] processing image {}/{}".format(i + 1,
			len(imagePaths)))
		name = imagePath.split(os.path.sep)[-2]

		# load the input image and convert it from RGB (OpenCV ordering)
		# to dlib ordering (RGB)
		image = cv2.imread(imagePath)
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		# detect the (x, y)-coordinates of the bounding boxes
		# corresponding to each face in the input image
		boxes = face_recognition.face_locations(rgb,
			model=["cnn"])

		# compute the facial embedding for the face
		encodings = face_recognition.face_encodings(rgb, boxes, num_jitters=100)

		# loop over the encodings
		for encoding in encodings:
			# add each encoding + name to our set of known names and
			# encodings
			knownEncodings.append(encoding)
			knownNames.append(name)
	# time
	local_time = time.localtime()  # get struct_time
	c_date = time.strftime("%Y-%m-%d", local_time)
	c_time = time.strftime("%I:%M", local_time)
	file_date_time = "encodings_" + c_date + "_" + c_time
	# dump the facial encodings + names to disk
	print("[INFO] serializing encodings...")
	data = {"encodings": knownEncodings, "names": knownNames}

	# check directory
	encoded_output_dir = "Encoded_data"
	if_dir_not_exists(encoded_output_dir)

	# Save data
	f = open(encoded_output_dir+"/"+file_date_time, "wb")
	f.write(pickle.dumps(data))
	f.close()

	print("Successfully trained!")

except Exception as e:
    logging.exception(str(e))


def encode_faces(name):
	# grab the paths to the input images in our dataset
	print("[INFO] quantifying faces...")

	imagePaths = list(paths.list_images("New_face/"+name))

	# initialize the list of known encodings and known names
	knownEncodings = []
	knownNames = []

	# loop over the image paths
	for (i, imagePath) in enumerate(imagePaths):
		# extract the person name from the image path
		print("[INFO] processing image {}/{}".format(i + 1,
			len(imagePaths)))
		#name = imagePath.split(os.path.sep)[-2]

		# load the input image and convert it from RGB (OpenCV ordering)
		# to dlib ordering (RGB)
		image = cv2.imread(imagePath)
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		# detect the (x, y)-coordinates of the bounding boxes
		# corresponding to each face in the input image
		#boxes = face_recognition.face_locations(rgb, model=["cnn"])
		boxes = face_recognition.face_locations(rgb, model=["cnn"])

		# compute the facial embedding for the face
		#encodings = face_recognition.face_encodings(rgb, boxes, num_jitters=100)
		encodings = face_recognition.face_encodings(rgb, boxes, num_jitters=100)

		# loop over the encodings
		for encoding in encodings:
			# add each encoding + name to our set of known names and
			# encodings
			knownEncodings.append(encoding)
			knownNames.append(name)

	# dump the facial encodings + names to disk
	print("[INFO] serializing encodings...")
	data = {"encodings": knownEncodings, "names": knownNames}

	# check directory
	encoded_output_dir = "Encoded_faces"
	if_dir_not_exists(encoded_output_dir)

	# Save data
	f = open(encoded_output_dir+"/"+name, "wb")
	f.write(pickle.dumps(data))
	f.close()
	print("Successfully trained and saved!")


def add_new_with_existing(name):
	new_encoding = pickle.loads(open("Encoded_faces" + "/" + name, "rb").read())

	if os.path.exists("encodings"):
		encoding = pickle.loads(open("encodings", "rb").read())

		# New encoded face added with existing
		for key in encoding.keys():
			for item in new_encoding[key]:
				encoding[key].append(item)
	else:
		encoding = new_encoding

	# Save data
	f = open("encodings", "wb")
	f.write(pickle.dumps(encoding))
	f.close()
	print("Successfully added new encoding with existing!")