import os
import pickle
import cv2
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-2754d-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-2754d.appspot.com"
})

bucket = storage.bucket()

#find default webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("C:\\Users\\User\\PycharmProjects\\fyp\\Resources\\background.png")

#Importing the node images into a list
folderModePath = "C:\\Users\\User\\PycharmProjects\\fyp\\Resources\\Modes"
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
#print(len(imgModeList))


# Load the encoding file
print("Loading Encoding File...")
file = open('EncodeFile.p' , 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown,attendeeID = encodeListKnownWithIds
#print(studentIds)
print("Encode File Loaded")
modeType = 0
counter = 0
id = -1
imgAttendee = []
while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0,0) , None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162+480 , 55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print("matches", matches)
        print("faceDis", faceDis)

        matchIndex = np.argmin(faceDis)
        print("Match Index", matchIndex)

        if matches[matchIndex]:
            #print("Known Face Detected")
            #print(studentIds[matchIndex])
            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55+x1, 162+y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = attendeeID[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1

        if counter != 0:

            if counter == 1:
                #Get Data
                print(f"Fetching info for attendee ID: {id}")
                attendeeInfo = db.reference(f'Attendees/{id}').get()
                print(attendeeInfo)
                #Get Image From DB
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgAttendee = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

            # Function to draw label and value side by side
            def draw_label_and_value(img, label, value, font, scale, color, thickness, box_x, box_y, label_offset,
                                     box_w, box_h):
                # Draw the label part (e.g., "ID:", "Company:")
                cv2.putText(img, label, (box_x + label_offset, box_y + (box_h + 10) // 2), font, scale, color,
                            thickness)
                # Get text size for the label to calculate where the value starts
                label_size = cv2.getTextSize(label, font, scale, thickness)[0]
                # Draw the value part (aligned next to the label)
                cv2.putText(img, value, (box_x + label_size[0] + label_offset + 5, box_y + (box_h + 10) // 2), font,
                            scale, color, thickness)

            # Set font parameters
            font = cv2.FONT_HERSHEY_COMPLEX
            scale = 0.5
            color = (128, 128, 128)
            thickness = 1

            # ID Box values and position
            draw_label_and_value(imgBackground, "ID:", str(id), font, scale, color, thickness,
                                 808, 473, 10, 243, 39)

            # Company Box values and position
            draw_label_and_value(imgBackground, "Company:", str(attendeeInfo['Company']), font, scale, color, thickness,
                                 808, 536, 10, 243, 39)

            # Position Box values and position
            draw_label_and_value(imgBackground, "Position:", str(attendeeInfo['Position']), font, scale, color,
                                 thickness,
                                 808, 599, 10, 243, 39)

            (w, h), _ = cv2.getTextSize(attendeeInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1,1)
            offset = (414-w)//2
            cv2.putText(imgBackground, str(attendeeInfo['name']), (808+offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,50), 1)

            imgBackground[175:175 + 216, 909:909 + 216] = imgAttendee
            counter += 1

    #cv2.imshow('Webcam', img)
    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break