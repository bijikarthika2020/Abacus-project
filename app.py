from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = '99a1bcdf63193e62a3e0cb9b312147bb526d4120618bf2b655651002bde24050'

# MySQL config for user auth
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tinybeads_db'

mysql = MySQL(app)

# MongoDB client for student data
client = MongoClient('mongodb://localhost:27017/')
db = client['tinybeads_db']
students_collection = db['students']


@app.route('/')
def home():
    return render_template("base.html")


# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form.get('user_type')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['email'] = user['email']
            session['user_type'] = user_type

            # Redirect based on user type
            if user_type == 'student':
                return redirect(url_for('dashboard'))
            elif user_type == 'teacher':
                return redirect(url_for('teacher'))
            else:
                flash('User type is invalid', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

    return render_template("login.html")



# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if password != confirm:
            flash("Passwords don't match", 'danger')
            return redirect(url_for('register'))
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            flash('Account already exists!', 'danger')
            cursor.close()
            return redirect(url_for('register'))
        cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, password))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html")


# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Student registration route using MongoDB

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
            print("Inserting student:", student)
            result = students_collection.insert_one(student)
            print("Inserted with id:", result.inserted_id)
            flash('Student added successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            print("Error inserting student:", e)
            flash(f'Error occurred: {e}', 'danger')
            return redirect(url_for('studentreg'))
    return render_template('studentreg.html')



# List students from MongoDB
@app.route('/students')
def students():
    students = list(students_collection.find())
    return render_template('students.html', students=students)


# Other routes...
@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

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


if __name__ == "__main__":
    app.run(debug=True, port=5050)
