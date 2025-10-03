from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from datetime import datetime
import bcrypt
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '99a1bcdf63193e62a3e0cb9b312147bb526d4120618bf2b655651002bde24050'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['tinybeads_db']
users_collection = db['users']
lessons_collection = db['lessons']
students_collection = db['students']

# File upload config
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'mkv'}
ALLOWED_NOTES = {'pdf', 'doc', 'docx', 'txt'}
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
NOTES_FOLDER = os.path.join(UPLOAD_FOLDER, 'notes')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

# Create upload directories if they don't exist
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(NOTES_FOLDER, exist_ok=True)

def allowed_file(filename, file_type='video'):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'video':
        return ext in ALLOWED_EXTENSIONS
    elif file_type == 'notes':
        return ext in ALLOWED_NOTES
    return False

@app.route('/')
def home():
    return render_template("base.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['userType']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        if users_collection.find_one({'email': email}):
            flash("Email already registered!", "danger")
            return redirect(url_for('register'))

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw,
            "user_type": user_type,
            "created_at": datetime.utcnow()
        })

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form.get('user_type')

        user = users_collection.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            if user_type == user['user_type']:
                session['loggedin'] = True
                session['email'] = user['email']
                session['user_type'] = user['user_type']

                if user['user_type'] == 'student':
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('teacher'))
            else:
                flash("Incorrect user type!", "danger")
        else:
            flash('Invalid email or password', 'danger')

        return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if session.get('loggedin') and session.get('user_type') == 'student':
        total_students = users_collection.count_documents({'user_type': 'student'})
        active_courses = lessons_collection.distinct('course')
        avg_progress = 78
        achievements = 156
        return render_template(
            'dashboard.html',
            total_students=total_students,
            active_courses=len(active_courses),
            avg_progress=avg_progress,
            achievements=achievements
        )
    return redirect(url_for('login'))

@app.route('/teacher')
def teacher():
    if session.get('loggedin') and session.get('user_type') == 'teacher':
        # Get teacher's uploaded materials
        teacher_materials = list(lessons_collection.find({
            'teacher_email': session.get('email')
        }).sort('uploaded_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for material in teacher_materials:
            material['_id'] = str(material['_id'])
            
        return render_template('teacher.html', materials=teacher_materials)
    return redirect(url_for('login'))

@app.route('/teacher/lesson', methods=['GET', 'POST'])
def upload_lesson():
    if session.get('loggedin') and session.get('user_type') == 'teacher':
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            course = request.form.get('course', '').strip()
            video = request.files.get('video')
            notes = request.files.get('notes')

            if not title or not video or video.filename == '':
                flash('Please provide a title and video file.', 'danger')
                return redirect(url_for('upload_lesson'))

            if not allowed_file(video.filename, 'video'):
                flash('Invalid video file type! Allowed: ' + ', '.join(ALLOWED_EXTENSIONS), 'danger')
                return redirect(url_for('upload_lesson'))

            # Save video file
            video_filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{video.filename}")
            video_path = os.path.join(VIDEO_FOLDER, video_filename)
            video.save(video_path)
            video_url = f"/static/uploads/videos/{video_filename}"

            # Save notes file if provided
            notes_filename = None
            notes_url = None
            if notes and notes.filename:
                if allowed_file(notes.filename, 'notes'):
                    notes_filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{notes.filename}")
                    notes_path = os.path.join(NOTES_FOLDER, notes_filename)
                    notes.save(notes_path)
                    notes_url = f"/static/uploads/notes/{notes_filename}"
                else:
                    flash('Invalid notes file type! Allowed: PDF, DOC, DOCX, TXT', 'warning')

            # Save to database
            lesson_data = {
                'title': title,
                'description': description,
                'course': course,
                'video_filename': video_filename,
                'video_url': video_url,
                'notes_filename': notes_filename,
                'notes_url': notes_url,
                'teacher_email': session.get('email'),
                'uploaded_at': datetime.utcnow(),
                'published': True
            }
            
            result = lessons_collection.insert_one(lesson_data)
            flash('Lesson uploaded successfully!', 'success')
            return redirect(url_for('teacher'))

        return render_template('lesson.html')
    
    flash('Please login as a teacher to upload lessons.', 'danger')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/course')
def courses():
    if not session.get('loggedin') or session.get('user_type') != 'student':
        flash('Please login as a student to view courses.', 'danger')
        return redirect(url_for('login'))

    course_filter = request.args.get('course')
    query = {'published': True}
    if course_filter:
        query['course'] = course_filter

    lessons = list(lessons_collection.find(query).sort('uploaded_at', -1))
    # Convert _id to string for templates
    for lesson in lessons:
        lesson['_id'] = str(lesson['_id'])

    return render_template('course.html', lessons=lessons, course=course_filter)

@app.route("/api/materials")
def get_materials():
    if not session.get("loggedin") or session.get("user_type") != "student":
        return jsonify([])

    lessons = list(lessons_collection.find({"published": True}).sort("uploaded_at", -1))
    results = []
    for lesson in lessons:
        results.append({
            "title": lesson["title"],
            "description": lesson["description"],
            "course": lesson["course"],
            "teacher_email": lesson["teacher_email"],
            "video_url": lesson["video_url"],
            "notes_url": lesson.get("notes_url"),
            "uploaded_at": lesson["uploaded_at"].strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(results)

@app.route('/studentreg', methods=['GET', 'POST'])
def studentreg():
    if request.method == 'POST':
        try:
            student = {
                'name': request.form['name'],
                'parent': request.form['parent'],
                'address': request.form['address'],
                'dob': request.form['dob'],
                'age': int(request.form['age']),
                'standard': request.form['standard'],
                'mobile': request.form['mobile'],
                'whatsapp': request.form['whatsapp'],
                'gender': request.form['gender'],
                'location': request.form['location']
            }
            result = students_collection.insert_one(student)
            flash('Student added successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            flash(f'Error occurred: {e}', 'danger')
            return redirect(url_for('studentreg'))
    return render_template('studentreg.html')

@app.route('/students')
def students():
    students = list(students_collection.find())
    return render_template('students.html', students=students)

@app.route('/lesson')
def lesson():
    return render_template('lesson.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/p_report')
def p_report():
    return render_template('p_report.html')

@app.route('/activities')
def activities():
    return render_template('activities.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/order')
def order():
    return render_template('order.html')

if __name__ == "__main__":
    app.run(debug=True, port=5050)