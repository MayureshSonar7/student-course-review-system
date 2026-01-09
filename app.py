from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yourpassword' 
app.config['MYSQL_DB'] = 'course_reviews'

mysql = MySQL(app)

@app.route('/')
def index():
    if 'logged_in' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        print("Courses from DB:", courses)  # This line is critical
        cursor.close()
        return render_template('index.html', courses=courses)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            error = 'Username already exists!'
        else:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_pw))
            mysql.connection.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
            session['logged_in'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('index'))
        else:
            error = 'Incorrect username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/course/<int:course_id>')
def view_course(course_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get course details
    cursor.execute('SELECT * FROM courses WHERE id = %s', (course_id,))
    course = cursor.fetchone()

    # Get all reviews for the course
    cursor.execute('''
        SELECT r.review, u.username, r.created_at
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.course_id = %s
        ORDER BY r.created_at DESC
    ''', (course_id,))
    reviews = cursor.fetchall()

    return render_template('review.html', course=course, reviews=reviews)

@app.route('/course/<int:course_id>/review', methods=['POST'])
def submit_review(course_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    review_text = request.form['review']
    user_id = session['id']

    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT INTO reviews (user_id, course_id, review) VALUES (%s, %s, %s)',
        (user_id, course_id, review_text)
    )
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('view_course', course_id=course_id))

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        url = request.form['url']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO courses (name, description, url) VALUES (%s, %s, %s)", (name, description, url))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('add_course.html')

if __name__ == '__main__':
    app.run(debug=True)
