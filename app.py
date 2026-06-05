from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "change_this_to_any_random_string_123"
DB = "billing.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')

    # Reseller table
    c.execute('''CREATE TABLE IF NOT EXISTS reseller
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, balance REAL DEFAULT 0)''')

    # History table
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY, reseller_id INTEGER, type TEXT, amount REAL,
                  note TEXT, date TEXT, FOREIGN KEY(reseller_id) REFERENCES reseller(id))''')

    # Create default admin if not exists
    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        hashed_pw = generate_password_hash("admin123")
        c.execute("INSERT INTO admin (username, password) VALUES (?,?)", ("admin", hashed_pw))

    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'admin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        admin = conn.execute("SELECT * FROM admin WHERE username=?", (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("ভুল ইউজারনেম বা পাসওয়ার্ড")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    resellers = conn.execute("SELECT * FROM reseller").fetchall()
    history = conn.execute("SELECT h.*, r.username FROM history h JOIN reseller r ON h.reseller_id=r.id ORDER BY h.id DESC LIMIT 20").fetchall()
    conn.close()
    return render_template('dashboard.html', resellers=resellers, history=history)

@app.route('/add_reseller', methods=['POST'])
def add_reseller():
    if 'admin' not in session:
        return redirect(url_for('login'))
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    balance = float(request.form['balance'])
    conn = get_db()
    try:
        conn.execute("INSERT INTO reseller (username, password, balance) VALUES (?,?,?)",
                     (username, password, balance))
        conn.commit()
        flash("রিচার্জার অ্যাড হয়েছে")
    except:
        flash("এই ইউজারনেম আগেই আছে")
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_balance', methods=['POST'])
def add_balance():
    if 'admin' not in session:
        return redirect(url_for('login'))
    reseller_id = request.form['reseller_id']
    amount = float(request.form['amount'])
    conn = get_db()
    conn.execute("UPDATE reseller SET balance = balance + ? WHERE id=?", (amount, reseller_id))
    conn.execute("INSERT INTO history (reseller_id, type, amount, note, date) VALUES (?, 'Credit', ?, 'Admin Balance Add', ?)",
                 (reseller_id, amount, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    flash("ব্যালেন্স অ্যাড হয়েছে")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)