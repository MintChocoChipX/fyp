import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-2754d-default-rtdb.firebaseio.com/"
})

ref = db.reference('Attendees')

data = {

    "258025":
        {
            "name": "Jensen",
            "Company": "McDonald's",
            "Position": "CEO",
            "check_in_status": "Absent"
        },
    "321654":
        {
            "name": "Alex",
            "Company": "Google",
            "Position": "CFO",
            "check_in_status": "Absent"
        },
    "852741":
         {
            "name": "Hazel",
            "Company": "APAC",
            "Position": "CEO",
            "check_in_status": "Absent"

         },
    "963852":
        {
            "name": "Elon Musk",
            "Company": "tesla",
            "Position": "CEO",
            "check_in_status": "Absent"
        }

}

for key, value in data.items():
    ref.child(key).set(value)