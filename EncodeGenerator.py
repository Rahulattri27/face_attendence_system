import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db,storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-8628c-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-8628c.appspot.com"
})


folder_path="/Users/rahulkumarair/Documents/rahul_vsCode/face recognition sytem/student_images"
PathList=os.listdir(folder_path)
img_List=[]
studentsIds=[]
for path in PathList:
    img_List.append(cv2.imread(os.path.join(folder_path,path)))
    studentsIds.append(os.path.splitext(path)[0])
    #upploading the images to bucket
    filename=f'student_images/{path}'
    bucket=storage.bucket()
    blob=bucket.blob(filename)
    blob.upload_from_filename(filename)

print(len(img_List))
print(studentsIds)

def findEncodings(imageList):
    encodelist=[]
    for image in imageList:
        #converting the colorScale from bgr to rgb as from opencv to face-recognition
        image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        encodings=face_recognition.face_encodings(image)[0]
        encodelist.append(encodings)
    return encodelist
print("enocding Started...")
encodeListKnown=findEncodings(img_List)
print("Encoding Complete...")

#save the encoding and ids in pickle file
encodeListKnownWithIds=[encodeListKnown,studentsIds]


file =open("Face_Encoding.p","wb")
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("file saved")



