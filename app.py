from flask import Flask, render_template, request, redirect, url_for, session
import csv
import pyrebase
import firebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import storage
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  

#authentication 

firebaseConfig = {
    'apiKey': "AIzaSyC5IgBXaslXo7Y_wl2LZVDyPY9_1muA8V0",
    'authDomain': "edutransform-33efe.firebaseapp.com",
    'projectId': "edutransform-33efe",
    'storageBucket': "edutransform-33efe.appspot.com",
    'messagingSenderId': "714003630570",
    'appId': "1:714003630570:web:0239ee658c18e9f6224a93",
    'measurementId': "G-93VTMCF22Q",
    'databaseURL': ''
  };

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Firestore database 
cred = credentials.Certificate('credentials.json')
application = firebase_admin.initialize_app(cred)
db = firestore.client()
docs = db.collections()

# creating an empty session
session = []
user = {
    'collection': '',
    'docid': '',
    
}
userdetails = {}

# path for saving the files 
current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funtions 
def reset():
    global userdetails, user
    userdetails= {}
    user = {
    'collection': '',
    'docid': '',
    
}

def createaccount(name, email, password, organization):
    data = {
        'name': name,
        'email': email,
        'password': password,
        'role':'admin'
        
    }
    
    try: 
        auth.create_user_with_email_and_password(email, password)
        db.collection(organization).document('admin1').set(data)
        return "created"
    except Exception as e:
        print(f"error {e}")
        return "error"
    
def createstudentaccount(file_path):
    print("entered")
        # Open the CSV file for reading
    with open(file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.DictReader(csvfile)
        
        # Loop over each row in the CSV file
        print("started")
        for row in csv_reader:
            # Extract details from the row
            name = row['Name']
            email = row['Email']
            class_name = row['Class']
            section = row['Section']
            
            # Create a dictionary to store the details
            data = {
                'name': name,
                'email': email,
                'class': class_name,
                'section': section,
                'role': 'student'
            }
            
            # Add the details to the Firestore database
            # Replace 'students' with the name of your Firestore collection
            studentpassword=123456
            auth.create_user_with_email_and_password(email,studentpassword)
            db.collection(user['collection']).add(data)
            print(f"added {name}")
            
    print("added succesfully")

def get_profile(collection,docid):
    global userdetails
    print(collection,docid)
    doc_ref = db.collection(user['collection']).document(user['docid'])
    doc = doc_ref.get()
    if doc.exists:
        userdetails = doc.to_dict()
    # print(userdetails)
        
        
    
def get_docid(email):
    for collection in docs:
        query = collection.where('email', '==', email).limit(1).stream()
        for doc in query:
            user['docid']=doc.id
            user['collection']=collection.id
            
            
            

    

@app.route('/', methods=['GET', 'POST'])
def home():
    # if user in session:
    #     return render_template('home/logged.html')
    # else:
    #     return render_template('home/notlogged.html')
    return render_template('home/notlogged.html')

@app.route('/notlogged', methods=['GET', 'POST'])
def notlogged():
    return render_template('home/notlogged.html')

@app.route('/logged', methods=['GET', 'POST'])
def logged():
    return render_template('home/logged.html')


@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # print(request.form)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        organization = request.form['Organization']
        
        if createaccount(name, email, password, organization)== 'created':
            get_docid(email)
            get_profile(user['collection'],user['docid'])
            session.append(email)
            return render_template('home/logged.html')
    return render_template('auth/signin.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        # print(request.form)
        email = request.form['email']
        password = request.form['password']
        try:
            auth.sign_in_with_email_and_password(email, password)
            session.append(email)
            get_docid( email)
            get_profile(user['collection'],user['docid'])
            # print(userdetails)
            return render_template('home/logged.html')
        except Exception as e:
            print(f"error:- {e}")
            pass
    return render_template('auth/login.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    reset()
    if session:
        session.pop()
    return redirect(url_for('notlogged'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    user_details = userdetails
    print(user_details)
    return render_template('components/profile.html',user_details=user_details)

@app.route('/workflow', methods=['GET','POST'])
def workflow():
    if request.method == 'POST':
        if 'student_csv' in request.files:
            student_csv = request.files['student_csv']
            if student_csv.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'student.csv')
                student_csv.save(file_path)
                print(file_path)
                createstudentaccount(file_path)
                
            else:
                print("No file selected!")
                return 'No file selected!'
            
    return render_template('components/workflow.html')
        
        




         
        
        
    
    

if __name__ == '__main__':
    app.run(debug=True)