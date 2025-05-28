from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import config

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.secret_key = "supersecretkey"

mysql = MySQL(app)

# ========= Database Connection Test =========
def check_db_connection():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1")
            cur.close()
            return True
        except Exception as e:
            print("Database connection error:", str(e))
            return False

# ========= Public Routes =========

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/events')
def events():
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, date, description FROM events ORDER BY date DESC")
    events = cur.fetchall()
    cur.close()
    return render_template('events.html', events=events)

@app.route('/what-we-do')
def what_we_do():
    return render_template('what-we-do.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        amount = request.form.get('amount', '').strip()

        if not name or not amount.replace('.', '', 1).isdigit():
            flash("Invalid input. Please enter a valid name and amount.", "danger")
            return redirect(url_for('donate'))

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO donations (name, amount) VALUES (%s, %s)", (name, float(amount)))
            mysql.connection.commit()
            cur.close()
            flash("Thank you for your donation!", "success")
        except Exception as e:
            flash("Database error: " + str(e), "danger")

        return redirect(url_for('donate'))

    return render_template('donate.html')


@app.route('/donation_history')
def donation_history():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, amount, timestamp FROM donations ORDER BY timestamp DESC")
        donations = cur.fetchall()
        cur.close()
    except Exception as e:
        flash("Error fetching donation history: " + str(e), "danger")
        donations = []
    return render_template('donation_history.html', donations=donations)

@app.route('/emergency-contact')
def emergency():
    return render_template('emergency.html')

@app.route('/food-donations')
def food_donations():
    return render_template('food-donations.html')

@app.route('/shelters-found')
def shelters_found():
    return render_template('shelters-found.html')

@app.route('/medical-emergencies')
def medical_emergencies():
    return render_template('medical-emergencies.html')

@app.route('/get-involved')
def get_involved():
    return render_template('get-involved.html')

@app.route('/volunteer')
def volunteer():
    return render_template('volunteer.html')

# ========= Admin Routes =========

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'aditya' and password == '1234':
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Please log in first", "warning")
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()

    # Fetch Donations
    cur.execute("SELECT id, name, amount, timestamp FROM donations ORDER BY timestamp DESC")
    donations = cur.fetchall()  # This returns a list of tuples (id, name, amount, timestamp)

    # Fetch Events
    cur.execute("SELECT id, title, date, description FROM events ORDER BY date DESC")
    events = cur.fetchall()  # This returns a list of tuples (id, title, date, description)

    cur.close()
    return render_template('admin_dashboard.html', donations=donations, events=events)


@app.route('/admin/add-event', methods=['POST'])
def add_event():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    title = request.form['title']
    date = request.form['date']
    description = request.form['description']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO events (title, date, description) VALUES (%s, %s, %s)", (title, date, description))
    mysql.connection.commit()
    cur.close()
    flash("Event added successfully", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-event/<int:event_id>')
def delete_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
    mysql.connection.commit()
    cur.close()
    flash("Event deleted", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out", "info")
    return redirect(url_for('admin_login'))

# ========= Start App =========

if __name__ == '__main__':
    with app.app_context():
        if check_db_connection():
            print("✅ Database connected successfully!")
        else:
            print("❌ Database connection failed. Please check your config.")
    app.run(debug=True)
