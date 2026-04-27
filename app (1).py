from flask import Flask, render_template, session, request, redirect, url_for, flash
import mysql.connector
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import io
import base64

app = Flask(__name__)
app.secret_key = 'organ_donation_secret_key_2024'

# ─── DB CONNECTION ───────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='dbms_project'
    )

# ─── HOME ────────────────────────────────────────────────────────
@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    if not session.get('login'):
        return redirect(url_for('login'))
    if session.get('isAdmin'):
        return render_template('home.html', username=session.get('username'))
    return render_template('home_user.html', username=session.get('username'))

# ─── LOGIN ───────────────────────────────────────────────────────
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(buffered=True)
        cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
        res = cursor.fetchall()
        cursor.close()
        db.close()
        if not res or password != res[0][1]:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
        session['login'] = True
        session['username'] = username
        session['password'] = password
        session['isAdmin'] = (username == 'admin')
        return redirect(url_for('home'))
    return render_template('login.html')

# ─── LOGOUT ──────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── USER MANAGEMENT ─────────────────────────────────────────────
@app.route("/user")
def user():
    if not session.get('login'):
        return redirect(url_for('login'))
    return render_template('user.html')

@app.route("/view_user", methods=['POST', 'GET'])
def view_user():
    if not session.get('login'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()
    fields = cursor.column_names
    cursor.close()
    db.close()
    return render_template('view_user.html', users=users, fields=fields)

@app.route("/show_update_detail", methods=['POST', 'GET'])
def show_update_detail():
    if not session.get('login'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        user_id = request.form.get('User_ID', '')
        if user_id == '':
            return render_template("search_detail.html")
        db = get_db()
        cursor = db.cursor(buffered=True)
        not_found = False
        res = ()
        cursor.execute("SELECT * FROM User WHERE User_ID = %s", (user_id,))
        if cursor.rowcount > 0:
            res = cursor.fetchone()
        else:
            not_found = True
        fields = cursor.column_names

        cursor.execute("SELECT * FROM User_phone_no WHERE User_ID = %s", (user_id,))
        phone_no = cursor.fetchall()

        res_pat = ()
        res_dnr = ()
        res_trans = ()
        fields_pat = []
        fields_dnr = []
        fields_trans = []

        cursor.execute(
            "SELECT Patient_ID, organ_req, reason_of_procurement, Doctor_name "
            "FROM Patient INNER JOIN Doctor ON Doctor.Doctor_ID = Patient.Doctor_ID "
            "AND User_ID = %s", (user_id,)
        )
        if cursor.rowcount > 0:
            res_pat = cursor.fetchall()
            fields_pat = cursor.column_names

        cursor.execute(
            "SELECT Donor_ID, organ_donated, reason_of_donation, Organization_name "
            "FROM Donor INNER JOIN Organization ON Organization.Organization_ID = Donor.Organization_ID "
            "AND User_ID = %s", (user_id,)
        )
        if cursor.rowcount > 0:
            res_dnr = cursor.fetchall()
            fields_dnr = cursor.column_names

        cursor.execute(
            "SELECT DISTINCT Transaction.Patient_ID, Transaction.Donor_ID, Organ_ID, "
            "Date_of_transaction, Status FROM Transaction, Patient, Donor "
            "WHERE (Patient.User_ID = %s AND Patient.Patient_ID = Transaction.Patient_ID) "
            "OR (Donor.User_ID = %s AND Donor.Donor_ID = Transaction.Donor_ID)",
            (user_id, user_id)
        )
        if cursor.rowcount > 0:
            res_trans = cursor.fetchall()
            fields_trans = cursor.column_names

        cursor.close()
        db.close()

        if "show" in request.form:
            return render_template('show_detail_2.html',
                                   res=res, fields=fields, not_found=not_found,
                                   phone_no=phone_no, res_dnr=res_dnr, res_pat=res_pat,
                                   res_trans=res_trans, fields_trans=fields_trans,
                                   fields_dnr=fields_dnr, fields_pat=fields_pat)
        if "update" in request.form:
            return render_template('update_detail.html', res=res, fields=fields, not_found=not_found)
        if "delete" in request.form:
            if not not_found:
                db2 = get_db()
                c2 = db2.cursor()
                c2.execute("DELETE FROM User WHERE User_ID = %s", (user_id,))
                db2.commit()
                c2.close()
                db2.close()
                flash('User deleted successfully.', 'success')
            return redirect(url_for('home'))
    return render_template('search_detail.html')

@app.route("/update_user", methods=['POST'])
def update_user():
    if not session.get('login'):
        return redirect(url_for('login'))
    user_id = request.form['User_ID']
    name = request.form['Name']
    dob = request.form['Date_of_Birth']
    insurance = request.form['Medical_insurance']
    history = request.form['Medical_history']
    street = request.form['Street']
    city = request.form['City']
    state = request.form['State']
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE User SET Name=%s, Date_of_Birth=%s, Medical_insurance=%s, "
        "Medical_history=%s, Street=%s, City=%s, State=%s WHERE User_ID=%s",
        (name, dob, insurance, history, street, city, state, user_id)
    )
    db.commit()
    cursor.close()
    db.close()
    flash('User updated successfully.', 'success')
    return redirect(url_for('home'))

# ─── SEARCH ──────────────────────────────────────────────────────
@app.route("/search_detail", methods=['GET', 'POST'])
def search_detail():
    if not session.get('login'):
        return redirect(url_for('home'))
    return render_template('search_detail.html')

@app.route("/search/<table>", methods=['GET', 'POST'])
def search_table(table):
    if not session.get('login'):
        return redirect(url_for('login'))
    allowed = {
        'user': 'User',
        'patient': 'Patient',
        'donor': 'Donor',
        'organ': 'Organ_available',
        'organization': 'Organization',
        'org_head': 'Organization_head',
        'doctor': 'Doctor',
        'transaction': 'Transaction',
        'log': 'log'
    }
    if table not in allowed:
        flash('Invalid table.', 'danger')
        return redirect(url_for('search_detail'))

    db = get_db()
    cursor = db.cursor(buffered=True)
    results = []
    fields = []
    search_term = request.form.get('search_term', '') if request.method == 'POST' else ''

    tbl = allowed[table]
    if search_term:
        cursor.execute(f"SHOW COLUMNS FROM {tbl}")
        cols = [row[0] for row in cursor.fetchall()]
        conditions = " OR ".join([f"{col} LIKE %s" for col in cols])
        vals = [f"%{search_term}%" for _ in cols]
        cursor.execute(f"SELECT * FROM {tbl} WHERE {conditions}", vals)
    else:
        cursor.execute(f"SELECT * FROM {tbl}")

    results = cursor.fetchall()
    fields = cursor.column_names
    cursor.close()
    db.close()
    return render_template('search_result.html', results=results, fields=fields,
                           table=table, search_term=search_term)

# ─── ADD ─────────────────────────────────────────────────────────
@app.route("/add")
def add():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO User VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (request.form['User_ID'], request.form['Name'], request.form['DOB'],
             request.form['Medical_insurance'], request.form['Medical_history'],
             request.form['Street'], request.form['City'], request.form['State'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('User added successfully!', 'success')
        return redirect(url_for('add'))
    return render_template('add_user.html')

@app.route("/add_patient", methods=['GET', 'POST'])
def add_patient():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Patient VALUES (%s,%s,%s,%s,%s)",
            (request.form['Patient_ID'], request.form['organ_req'],
             request.form['reason_of_procurement'], request.form['Doctor_ID'],
             request.form['User_ID'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Patient added successfully!', 'success')
        return redirect(url_for('add'))
    return render_template('add_patient.html')

@app.route("/add_donor", methods=['GET', 'POST'])
def add_donor():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Donor VALUES (%s,%s,%s,%s,%s)",
            (request.form['Donor_ID'], request.form['organ_donated'],
             request.form['reason_of_donation'], request.form['Organization_ID'],
             request.form['User_ID'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Donor added successfully!', 'success')
        return redirect(url_for('add'))
    return render_template('add_donor.html')

@app.route("/add_doctor", methods=['GET', 'POST'])
def add_doctor():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Doctor VALUES (%s,%s,%s,%s)",
            (request.form['Doctor_ID'], request.form['Doctor_Name'],
             request.form['Department_Name'], request.form['organization_ID'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('add'))
    return render_template('add_doctor.html')

@app.route("/add_organization", methods=['GET', 'POST'])
def add_organization():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Organization VALUES (%s,%s,%s,%s)",
            (request.form['Organization_ID'], request.form['Organization_name'],
             request.form['Location'], request.form['Government_approved'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Organization added successfully!', 'success')
        return redirect(url_for('add'))
    return render_template('add_organization.html')

@app.route("/add_org_head", methods=['GET', 'POST'])
def add_org_head():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Organization_head VALUES (%s,%s,%s,%s,%s)",
            (request.form['Organization_ID'], request.form['Employee_ID'],
             request.form['Name'], request.form['Date_of_joining'],
             request.form['Term_length'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Organization Head added successfully!', 'success')
        return redirect(url_for('add'))
    return render_template('add_org_head.html')

@app.route("/add_transaction", methods=['GET', 'POST'])
def add_transaction():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Transaction VALUES (%s,%s,%s,%s,%s)",
            (request.form['Patient_ID'], request.form['Organ_ID'],
             request.form['Donor_ID'], request.form['Date_of_transaction'],
             request.form['Status'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('add'))
    return render_template('add_transaction.html')

@app.route("/add_user_phone", methods=['GET', 'POST'])
def add_user_phone():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO User_phone_no VALUES (%s,%s)",
            (request.form['User_ID'], request.form['phone_no'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Phone number added!', 'success')
        return redirect(url_for('add'))
    return render_template('add_user_phone.html')

@app.route("/add_doctor_phone", methods=['GET', 'POST'])
def add_doctor_phone():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Doctor_phone_no VALUES (%s,%s)",
            (request.form['Doctor_ID'], request.form['Phone_no'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Doctor phone number added!', 'success')
        return redirect(url_for('add'))
    return render_template('add_doctor_phone.html')

@app.route("/add_org_phone", methods=['GET', 'POST'])
def add_org_phone():
    if not session.get('login'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Organization_phone_no VALUES (%s,%s)",
            (request.form['Organization_ID'], request.form['Phone_no'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Organization phone number added!', 'success')
        return redirect(url_for('add'))
    return render_template('add_org_phone.html')

# ─── REMOVE ──────────────────────────────────────────────────────
@app.route("/remove")
def remove():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect(url_for('home'))
    return render_template('remove.html')

@app.route("/remove/<entity>", methods=['GET', 'POST'])
def remove_entity(entity):
    if not session.get('login') or not session.get('isAdmin'):
        return redirect(url_for('login'))
    table_map = {
        'user': ('User', 'User_ID'),
        'patient': ('Patient', 'Patient_ID'),
        'donor': ('Donor', 'Donor_ID'),
        'doctor': ('Doctor', 'Doctor_ID'),
        'organization': ('Organization', 'Organization_ID'),
        'org_head': ('Organization_head', 'Employee_ID'),
    }
    if entity not in table_map:
        flash('Invalid entity.', 'danger')
        return redirect(url_for('remove'))
    tbl, pk = table_map[entity]
    if request.method == 'POST':
        pk_val = request.form.get(pk)
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM {tbl} WHERE {pk} = %s", (pk_val,))
        db.commit()
        cursor.close()
        db.close()
        flash(f'{tbl} with ID {pk_val} removed successfully.', 'success')
        return redirect(url_for('remove'))
    return render_template('remove_entity.html', entity=entity, tbl=tbl, pk=pk)

# ─── STATISTICS ──────────────────────────────────────────────────
@app.route("/statistics")
def statistics():
    if not session.get('login'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(buffered=True)

    # Organs required by patients
    cursor.execute("SELECT organ_req, COUNT(*) FROM Patient GROUP BY organ_req")
    pat_data = cursor.fetchall()
    pat_labels = [r[0] for r in pat_data]
    pat_vals = [r[1] for r in pat_data]

    # Organs available from donors
    cursor.execute("SELECT Organ_name, COUNT(*) FROM Organ_available GROUP BY Organ_name")
    don_data = cursor.fetchall()
    don_labels = [r[0] for r in don_data]
    don_vals = [r[1] for r in don_data]

    # Success vs Failure per organ
    cursor.execute(
        "SELECT oa.Organ_name, "
        "SUM(CASE WHEN t.Status=1 THEN 1 ELSE 0 END) AS success, "
        "SUM(CASE WHEN t.Status=0 THEN 1 ELSE 0 END) AS failure "
        "FROM Transaction t JOIN Organ_available oa ON t.Organ_ID = oa.Organ_ID "
        "GROUP BY oa.Organ_name"
    )
    trans_data = cursor.fetchall()
    cursor.close()
    db.close()

    def make_pie(labels, vals, title):
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(vals, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.set_title(title)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img_b64

    def make_bar(trans_data):
        if not trans_data:
            return None
        organs = [r[0] for r in trans_data]
        success = [r[1] or 0 for r in trans_data]
        failure = [r[2] or 0 for r in trans_data]
        x = np.arange(len(organs))
        width = 0.35
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x - width/2, success, width, label='SUCCESS', color='steelblue')
        ax.bar(x + width/2, failure, width, label='FAILURE', color='orange')
        ax.set_xticks(x)
        ax.set_xticklabels(organs, rotation=15)
        ax.set_ylabel('Number of transplantations')
        ax.set_title('SUCCESS V/S FAILURE IN ORGAN TRANSPLANTATION')
        ax.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img_b64

    pie1 = make_pie(pat_labels, pat_vals, 'Organs Required by Patients') if pat_vals else None
    pie2 = make_pie(don_labels, don_vals, 'Organs Available from Donors') if don_vals else None
    bar = make_bar(trans_data)

    return render_template('statistics.html', pie1=pie1, pie2=pie2, bar=bar)

if __name__ == '__main__':
    app.run(debug=True)
