from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("base.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # TODO: Add your user authentication logic here

        # On successful login, redirect to dashboard page
        return redirect(url_for('dashboard'))

    # For GET requests, render the login page
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # TODO: save user data
        return redirect(url_for('home'))
    return render_template("register.html")

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/studentreg')
def studentreg():
    return render_template('studentreg.html')

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