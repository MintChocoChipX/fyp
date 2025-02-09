import os
from fileinput import filename

import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
#import images

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-2754d-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-2754d.appspot.com"
})

folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
attendeeIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    attendeeIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

    #print(path)
    #print(os.path.splitext(path)[0])
print(attendeeIds)

def findEncodings(imgaesList):
    encodeList = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown,attendeeIds]
print("Encoding Complete")

file = open("EncodeFile.p" , 'wb')
pickle.dump(encodeListKnownWithIds , file)
file.close()
print("File Saved")