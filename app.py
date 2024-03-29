from flask import Flask, render_template, request, redirect, url_for, session
import csv
import pyrebase
import firebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import storage
import os
from questiongeneration import get_pdf_text, get_text_chunks, get_vector_store, get_conversational_chain, user_input
import json

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
        print(f" create account error {e}")
        return "error"
    
    
def createquestions(path):
    raw_text = get_pdf_text(path)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)
    response = user_input()
    return response
    
def createstudentaccount(file_path):
    print("entered createstudentaccount function")
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            name = row['Name']
            email = row['Email']
            class_name = row['Class']
            section = row['Section']
            
            data = {
                'name': name,
                'email': email,
                'class': class_name,
                'section': section,
                'role': 'student'
            }
            studentpassword=123456
            auth.create_user_with_email_and_password(email,studentpassword)
            db.collection(user['collection']).add(data)
            print(f"added student {name}")
            
    print("added all students succesfully")
    

def createteacheraccount(file_path):    
    print("entered createteacheraccount function")
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            name = row['Name']
            email = row['Email']
            subject_name = row['subject_name']
            data = {
                'name': name,
                'email': email,
                'subject_name': subject_name,
                'role': 'teacher'
            }
            teacherpassword=123456
            auth.create_user_with_email_and_password(email,teacherpassword)
            db.collection(user['collection']).add(data)
            print(f"added teacher {name}")
            
    print("added teacher succesfully")
    
    
def createadminaccount(file_path):    
    print("entered createadminaccount function ")
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        print("started")
        for row in csv_reader:
            name = row['Name']
            email = row['Email']
            data = {
                'name': name,
                'email': email,
                
                'role': 'admin'
            }
            adminpassword=123456
            auth.create_user_with_email_and_password(email,adminpassword)
            db.collection(user['collection']).add(data)
            print(f"added admin {name}")
            
    print("added admin succesfully")
    

# def adddetails(file_path):    
#     print("entered")
#         # Open the CSV file for reading
#     with open(file_path, 'r') as csvfile:
#         # Create a CSV reader object
#         csv_reader = csv.DictReader(csvfile)
        
#         # Loop over each row in the CSV file
#         print("started")
#         for row in csv_reader:
#             # Extract details from the row
#             name = row['Name']
#             email = row['Email']
            

            
#             # Create a dictionary to store the details
#             data = {
#                 'name': name,
#                 'email': email,
#                 'role': 'admin'
#             }
            
#             # Add the details to the Firestore database
#             # Replace 'students' with the name of your Firestore collection
#             adminpassword=123456
#             auth.create_user_with_email_and_password(email,adminpassword)
#             db.collection(user['collection']).add(data)
#             print(f"added {name}")
            
#     print("added succesfully")
  

    
def get_profile(collection,docid):
    global userdetails
    userdetails = {}
    print(f"get profile function {collection},{docid}")
    doc_ref = db.collection(collection).document(docid)
    doc = doc_ref.get()
    if doc.exists:
        userdetails = doc.to_dict()
    print(f"get profile function {userdetails}")
        
        
    
def get_docid(email):
    global user
    user['docid']=''
    user['collection']=''
    print(f"geting docid of {email}")
    doc_found = False
    docs = db.collections()
    for collection in docs:
        print("entered1")
        query = collection.where('email', '==', email).limit(1).stream()
        print("entered2")
        for doc in query:
            print("entered 3")
            print(doc.id)
            
            dummy_id = doc.id
            print("checking in get_docid")
            user['docid']=doc.id
            user['collection']=collection.id
            print(f" got docid {user}")
            break
        
    print(f" got docid {user}")
  
    return dummy_id
        
            
            

    

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
            userw = auth.sign_in_with_email_and_password(email, password)
            print("authentication done")
            session.append(email)
            dummyvariable = get_docid( email)
            print("entering in login")
            print(user)
            if user['docid']:
                get_profile(user['collection'],user['docid'])
                print(userdetails)
                if userdetails:
                    if userdetails['role'] == 'teacher':
                        return redirect(url_for('teacher', docid=user['docid']))
                    elif userdetails['role'] == 'student':
                        return redirect(url_for('student', docid = user['docid']))
                    elif userdetails['role'] == 'admin':
                        return redirect(url_for('admin', docid = user['docid']))
        except Exception as e:
            print(f"error:- {e}")
            pass
    return render_template('auth/login.html')
@app.route('/stduent/<docid>', methods=['GET', 'POST'])
def student(docid):
    return render_template('home/student.html')

@app.route('/teacher/<docid>', methods=['GET', 'POST'])
def teacher(docid):
    return render_template('home/teacher.html')

@app.route('/admin/<docid>',methods=['GET', 'POST'])
def admin(docid):
    return render_template('home/logged.html')

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
        if 'student_csv' in request.files and 'teacher_csv' in request.files and 'admin_csv' in request.files :

            print(request.files)
            student_csv = request.files['student_csv']
            teacher_csv = request.files['teacher_csv']
            admin_csv = request.files['admin_csv']
            if student_csv.filename != '' and teacher_csv.filename != '' and admin_csv.filename != '':
                # student data 
                file_path_student = os.path.join(app.config['UPLOAD_FOLDER'], 'student.csv')
                student_csv.save(file_path_student)
                createstudentaccount(file_path_student)

                # teacher data 
                file_path_teacher = os.path.join(app.config['UPLOAD_FOLDER'], 'teacher.csv')
                teacher_csv.save(file_path_teacher)
                print(file_path_teacher)
                createteacheraccount(file_path_teacher)
                
                # admin data
                file_path_admin = os.path.join(app.config['UPLOAD_FOLDER'], 'admin.csv')
                admin_csv.save(file_path_admin)
                createadminaccount(file_path_admin)
                
               # details of the organization 
                # file_path_details = os.path.join(app.config['UPLOAD_FOLDER'], 'details.csv')
                # student_csv.save(file_path_details)
                # adddetails(file_path_details)

                
                
            else:
                print("No file selected!")
                return 'No file selected!'
            
    return render_template('components/workflow.html')


@app.route('/update_lesson', methods=['POST', 'GET'])
def update_lesson():
    response_text = ''
    if request.method == 'POST':
        if 'lesson_pdf' in request.files:
            lesson = request.files['lesson_pdf']
            file_path_lesson = os.path.join(app.config['UPLOAD_FOLDER'], 'lesson.pdf')
            lesson.save(file_path_lesson)
            #response = createquestions(file_path_lesson)
            #response_text = response['output_text']
            
            #response_text = json.loads(response_text)
    return render_template('components/update_lesson.html')


if __name__ == '__main__':
    app.run(debug=True)
