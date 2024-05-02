import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-8628c-default-rtdb.firebaseio.com/"
})
ref=db.reference('Students')
data={
    "12":{
        "name":"Rahul Kumar",
        "course":"Btech",
        "starting_year":2021,
        "total_attendence":6,
        "last_attendence_time":"2022-12-11 00:54:34"
    },
    "23":{
        "name":"RDJ",
        "course":"Filmtech",
        "starting_year":2021,
        "total_attendence":1,
        "last_attendence_time":"2022-12-11 00:54:34"

    },
    "34":{
        "name":"tom holland",
        "course":"Filmtech",
        "starting_year":2021,
        "total_attendence":4,
        "last_attendence_time":"2022-12-11 00:54:34"

    }
}
for key,value in data.items():
    ref.child(key).set(value)