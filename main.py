import cv2
import numpy as np
import pickle
import face_recognition
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db,storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-8628c-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-8628c.appspot.com"
})

bucket=storage.bucket()

cap=cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
image=np.zeros((1440,2440,3),dtype=np.uint8)
modes=["Active","Marked","Already Marked"]

#load the encoding file
print("Loading face Encodings")
file=open("Face_Encoding.p","rb")
encodeListKnownWithIds=pickle.load(file)
encodeListKnown,studentIds=encodeListKnownWithIds
print("Enoding file Loaded")


modeType=0
counter=0
id=-1
imgstudent=[]

while True:
    succes,img=cap.read()
    # scaling down the image to reduce computational power
    imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    #converting bgr to rgb for face-recognition library
    imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
    #faces in current frame
    faceCurrFrame=face_recognition.face_locations(imgS)
    #find the current frame face encodings 
    encodeCurrFrame=face_recognition.face_encodings(imgS,faceCurrFrame)

    for encodeFace,faceLoc in zip(encodeCurrFrame,faceCurrFrame):
        matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)
        # print("matches",matches)
        # print("dis",faceDis)

        matchIndex=np.argmin(faceDis)
        if matches[matchIndex]:
            print("Known face detected. Student Id is: ",studentIds[matchIndex])
            y1,x1,y2,x2=faceLoc #coordinates of bounding box
            x1,y1,x2,y2=x1*4,y1*4,x2*4,y2*4
            #plotting the bounding box
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            id=studentIds[matchIndex]
            if counter==0:
                cv2.putText(image,"Loading",(275,400),2,2,(0,0,255),2)
                cv2.imshow("image",image)
                if cv2.waitKey(1)==ord('q'):
                    break
                counter=1

                
    if counter!=0:
        if counter==1:
            #get the data
            studentInfo=db.reference(f'Students/{id}').get()
            print(studentInfo)
            #get the image
            blob=bucket.get_blob(f'student_images/{id}.jpg')
            array=np.frombuffer(blob.download_as_string(),np.uint8)
            imgstudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
            imgstudent=cv2.resize(imgstudent,(300,300))
            # print(len(imgstudent))
            # cv2.imshow("i",imgstudent)

            #update the data of attendence
            datetimeObject=datetime.strptime(studentInfo['last_attendence_time'],"%Y-%m-%d %H:%M:%S")
            secondsElapsed=(datetime.now()-datetimeObject).total_seconds()
            if secondsElapsed>30:
                    
                ref=db.reference(f'Students/{id}')
                studentInfo['total_attendence']+=1
                ref.child('total_attendence').set(studentInfo['total_attendence'])
                ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                modeType=2
                counter=0
                image2=np.zeros((1000,840,3),dtype=np.uint8)
                cv2.putText(image2,modes[modeType],(200,300),2,2,(255,255,255),2)
                image[100:100+1000,1450:1450+840]=image2
           
        if modeType!=2: 
            if 10<counter<=20:
                modeType=1
                image2=np.zeros((1000,840,3),dtype=np.uint8)
                cv2.putText(image2,modes[modeType],(200,300),2,2,(255,255,255),2)
                image[100:100+1000,1450:1450+840]=image2
                counter+=1

                
            if counter<=10:
                cv2.putText(image,modes[modeType],(1500,180),2,2,(255,255,255),2)
                cv2.putText(image,'Total Attendence'+str(studentInfo['total_attendence']),(1500,580),cv2.FONT_HERSHEY_COMPLEX,2,(255,255,255),2)
                cv2.putText(image,'name: '+str(studentInfo['name']),(1500,640),cv2.FONT_HERSHEY_COMPLEX,2,(255,255,255),2)
                cv2.putText(image,'id:'+str(id),(1500,700),cv2.FONT_HERSHEY_COMPLEX,2,(255,255,255),2)
                cv2.putText(image,'starting_year'+str(studentInfo['starting_year']),(1500,760),cv2.FONT_HERSHEY_COMPLEX,2,(255,255,255),2)
                cv2.putText(image,'course'+str(studentInfo['course']),(1500,820),cv2.FONT_HERSHEY_COMPLEX,2,(255,255,255),2)
                image[200:200+300,1600:1600+300]=imgstudent
                modeType=0
            counter+=1

            if counter>=20:
                modeType=0
                counter=0
                studentInfo=[]
                imgstudent=[]

    image[150:150+720,75:75+1280]=img
    cv2.putText(image,"Face Attendance System",(75,65),2,2,(255,255,255),2)
    
    cv2.imshow("image",image)
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()
