from flask import Flask, request, redirect, url_for, render_template, send_file, jsonify
import sqlite3
import os
import io
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            # Log the received username and password for debugging purposes
            print(f"Received username: {username}")
            print(f"Received password: {password}")

            # Connect to the SQLite database
            db_path = os.path.join(os.path.dirname(__file__), 'login.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Parameterized query to avoid SQL injections
            cursor.execute("SELECT * FROM Logincredentials WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                # If user exists, redirect to home page
                return redirect(url_for('home'))

            cursor.execute("SELECT * FROM adminlogin WHERE username = ? AND password = ?", (username, password))
            admin = cursor.fetchone()
            conn.close()
            if admin:
                return redirect(url_for('homeadmin'))
            else:
                # If credentials are invalid, show an error or stay on the login page
                error = 'Invalid credentials. Please try again.'
        else:
            print("Received GET request")
    except Exception as e:
        error = f"An error occurred: {str(e)}"
        print(error)

    # For a GET request, simply render a login form
    return render_template('login.html', error=error)


@app.route('/homeadmin')
def homeadmin():
    return render_template('homeadmin.html')
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/homeadmin/historical_data')
def historical_data():
    # Fetch employee data
    df = fetch_employee_data()
    # Calculate summary statistics
    summary_stats = calculate_summary_statistics(df)
    # Pass summary statistics to the template
    return render_template('historical_data.html', summary_stats=summary_stats)

def fetch_employee_details():
    try:
        conn = sqlite3.connect('employee.db')
        cursor = conn.cursor()
        cursor.execute("SELECT NAME, email FROM employeedetails")
        employees = cursor.fetchall()
        conn.close()
        return employees
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
def fetch_employee_attendance():
    try:
        conn = sqlite3.connect('employee.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Time FROM employeedetails")
        employees = cursor.fetchall()
        conn.close()
        return employees
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
# Route to render the notifications page
@app.route('/homeadmin/notifications')
def notifications():
    employees = fetch_employee_details()
    return render_template('notifications.html', employees=employees)

@app.route('/homeadmin/reporting')
def reporting():
    # Logic for automated reporting
    return "Automated Reporting Page"

@app.route('/homeadmin/camera_feeds')
def camera_feeds():
    # Logic for monitoring camera feeds
    return render_template('camera_feeds.html')

@app.route('/shift_notifications')
def shift_notifications():
    # Logic for displaying shift notifications
    return "Shift Notifications Page"

@app.route('/admin')
def admin():
    # Logic for accessing admin functionalities
    return "Admin Page"

@app.route('/self_service', methods=['GET', 'POST'])
def self_service():
    if request.method == 'POST':
        try:
            # Fetch form data
            emp_id = request.form.get('emp_id')
            phone_no = request.form.get('phone_no')
            address = request.form.get('address')
            email = request.form.get('email')
            dob = request.form.get('dob')

            # Debugging: Print the fetched form data
            print(f"Received form data - Employee ID: {emp_id}, Phone No: {phone_no}, Address: {address}, Email: {email}, DOB: {dob}")

            # Connect to the SQLite database
            db_path = os.path.join(os.path.dirname(__file__), 'employee.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Update employee details
            cursor.execute("""
                UPDATE employeedetails 
                SET PhoneNo = ?, address = ?, email = ?, dob = ? 
                WHERE employeeid = ?
            """, (phone_no, address, email, dob, emp_id))

            # Debugging: Check the number of rows affected
            print(f"Rows updated: {cursor.rowcount}")

            conn.commit()
            conn.close()

            if cursor.rowcount > 0:
                success_message = "Details updated successfully!"
            else:
                success_message = "No details were updated. Please check the Employee ID."

            employee_ids = fetch_employee_ids()  # Fetch employee IDs for the dropdown
            return render_template('self_service.html', success_message=success_message, employee_ids=employee_ids)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  # Debugging: Print the error message
            employee_ids = fetch_employee_ids()  # Fetch employee IDs for the dropdown
            return render_template('self_service.html', error_message=error_message, employee_ids=employee_ids)
    else:
        employee_ids = fetch_employee_ids()  # Fetch employee IDs for the dropdown
        return render_template('self_service.html', employee_ids=employee_ids)
def fetch_employee_ids():
    try:
        conn = sqlite3.connect('employee.db')
        cursor = conn.cursor()
        cursor.execute("SELECT employeeid FROM employeedetails")
        employee_ids = cursor.fetchall()
        conn.close()
        return [employeeid[0] for employeeid in employee_ids]
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
def fetch_employee_data(db_path='employee.db'):
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM employeedetails"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Log the fetched data for debugging
        print(df.head())

        return df
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

# Function to plot monthly attendance analysis
def plot_monthly_attendance(df):
    df['JAN'] = pd.to_numeric(df['JAN'], errors='coerce')
    df['FEB'] = pd.to_numeric(df['FEB'], errors='coerce')
    df['MAR'] = pd.to_numeric(df['MAR'], errors='coerce')
    attendance = df[['JAN', 'FEB', 'MAR']].sum()
    fig, ax = plt.subplots(figsize=(8, 6))
    attendance.plot(kind='bar', color=['skyblue', 'lightgreen', 'salmon'], ax=ax)
    ax.set_title('Monthly Attendance Analysis')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Attendance')
    return fig

def calculate_summary_statistics(df):
    total_employees = len(df)
    gender_counts = df['GENDER'].value_counts().to_dict() if 'GENDER' in df.columns else {}
    return {
        'total_employees': total_employees,
        'gender_counts': gender_counts
    }

# Function to plot gender distribution analysis
def plot_gender_distribution(df):
    if 'GENDER' in df.columns:
        df['GENDER'] = df['GENDER'].str.upper()
        df['GENDER'] = df['GENDER'].fillna('UNKNOWN')
        gender_distribution = df['GENDER'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 6))
        gender_distribution.plot(kind='pie', autopct='%1.1f%%', colors=['lightblue', 'lightpink'], ax=ax)
        ax.set_title('Gender Distribution Analysis')
        ax.set_ylabel('')  # Hide the y-label
        return fig
    else:
        return None

# Function to plot age distribution analysis
def plot_age_distribution(df):
    if 'AGE' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df['AGE'], bins=10, edgecolor='black', color='lightcoral')
        ax.set_title('Age Distribution Analysis')
        ax.set_xlabel('AGE')
        ax.set_ylabel('Number of Employees')
        return fig
    else:
        return None

@app.route('/plot/attendance')
def plot_attendance():
    df = fetch_employee_data()
    fig = plot_monthly_attendance(df)
    output = io.BytesIO()
    fig.savefig(output, format='png')
    output.seek(0)
    return send_file(output, mimetype='image/png')

@app.route('/plot/gender')
def plot_gender():
    df = fetch_employee_data()
    fig = plot_gender_distribution(df)
    if fig:
        output = io.BytesIO()
        fig.savefig(output, format='png')
        output.seek(0)
        return send_file(output, mimetype='image/png')
    else:
        return "No gender data available"

@app.route('/plot/age')
def plot_age():
    df = fetch_employee_data()
    fig = plot_age_distribution(df)
    if fig:
        output = io.BytesIO()
        fig.savefig(output, format='png')
        output.seek(0)
        return send_file(output, mimetype='image/png')
    else:
        return "No age data available"
@app.route("/table")
def table():
    df = fetch_employee_data()
    # Convert DataFrame to a list of dictionaries
    employees = df.to_dict(orient='records')
    return render_template('table.html', employees=employees)
@app.route('/data')
def data():
    df = fetch_employee_data()
    return df.to_json(orient='records')
def save_fig_to_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    return img
@app.route('/generate_pdf')
def generate_pdf():
    try:
        df = fetch_employee_data()
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        # Add title
        c.setFont("Helvetica", 16)
        c.drawString(30, height - 30, "Employee Data Visualization")

        # Add attendance graph
        fig = plot_monthly_attendance(df)
        img = save_fig_to_image(fig)
        img_path = 'attendance.png'
        img.save(img_path)
        c.drawImage(img_path, 30, height - 300, width=500, height=250)
        os.remove(img_path)
        plt.close(fig)

        # Add gender distribution graph
        fig = plot_gender_distribution(df)
        if fig:
            img = save_fig_to_image(fig)
            img_path = 'gender_distribution.png'
            img.save(img_path)
            c.drawImage(img_path, 30, height - 600, width=500, height=250)
            os.remove(img_path)
            plt.close(fig)
        else:
            print("Gender distribution graph not generated")

        # Add age distribution graph
        fig = plot_age_distribution(df)
        if fig:
            img = save_fig_to_image(fig)
            img_path = 'age_distribution.png'
            img.save(img_path)
            c.drawImage(img_path, 30, height - 900, width=500, height=250)
            os.remove(img_path)
            plt.close(fig)
        else:
            print("Age distribution graph not generated")

        c.showPage()
        c.save()
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name='employee_data.pdf', mimetype='application/pdf')
    except Exception as e:
        print(f"An error occurred during PDF generation: {e}")
        return jsonify({"error": "Failed to generate PDF"}), 500
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Route to handle form submission and send email
@app.route('/send_notification', methods=['POST'])
def send_notification():
    try:
        email = request.form['email']
        email_type = request.form['email_type']

        # Set up the SMTP server
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "miniprojectxxxx@gmail.com"  
        sender_password = "xxxxxxxx"

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email

        if email_type == 'shift_change':
            shift_number = request.form['shift_number']
            shift_time = request.form['shift_time']
            subject = f"Shift Change Notification for Shift {shift_number}"
            message_body = f"Dear Employee,\n\nYour shift has been changed to Shift {shift_number} at {shift_time}.\n\n"
        else:
            subject = request.form['custom_subject']
            message_body = request.form['custom_message']

        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))

        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()

        return "Notification sent successfully!"

    except Exception as e:
        return f"An error occurred: {e}"
@app.route('/generate_csv')
def generate_csv():
    df = fetch_employee_data()
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return send_file(io.BytesIO(csv_buffer.getvalue().encode()), as_attachment=True, download_name='employee_data.csv', mimetype='text/csv')
@app.route('/performance_reviews', methods=['GET', 'POST'])
def performance_reviews():
    employee_ids = fetch_employee_ids()
    if request.method == 'POST':
        try:
            emp_id = request.form.get('emp_id')

            # Connect to the SQLite database and fetch performance reviews
            db_path = os.path.join(os.path.dirname(__file__), 'employee.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT performance, feedbacks FROM performancereview WHERE employeeid = ?", (emp_id,))
            reviews = cursor.fetchall()
            conn.close()

            return render_template('performance_reviews.html', reviews=reviews, emp_id=emp_id, employee_ids=employee_ids)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render_template('performance_reviews.html', error_message=error_message, employee_ids=employee_ids)
    else:
        return render_template('performance_reviews.html', employee_ids=employee_ids)
@app.route('/leave_application', methods=['GET', 'POST'])
def leave_application():
    employee_ids = fetch_employee_ids()
    if request.method == 'POST':
        try:
            emp_id = request.form.get('emp_id')
            leave_type = request.form.get('leave_type')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            reason = request.form.get('reason')

            # Connect to the SQLite database and save the leave application
            db_path = os.path.join(os.path.dirname(__file__), 'employee.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leaveapplications (employeeid, leave_type, start_date, end_date, reason) 
                VALUES (?, ?, ?, ?, ?)
            """, (emp_id, leave_type, start_date, end_date, reason))
            conn.commit()
            conn.close()

            success_message = "Leave application submitted successfully!"
            return render_template('leave_application.html', success_message=success_message, employee_ids=employee_ids)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render_template('leave_application.html', error_message=error_message, employee_ids=employee_ids)
    else:
        return render_template('leave_application.html', employee_ids=employee_ids)

def fetch_employee_attendance():
    try:
        conn = sqlite3.connect('employee.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Time FROM attendance")  # Query the attendance table
        attendance_data = cursor.fetchall()
        conn.close()
        return pd.DataFrame(attendance_data, columns=['Name', 'Time'])
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def plot_name_time_graph(df):
    try:
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')  # Ensure Time is numeric
        fig, ax = plt.subplots(figsize=(10, 6))
        df.plot(x='Name', y='Time', kind='bar', color='skyblue', ax=ax)
        ax.set_title('Attendance Analysis')
        ax.set_xlabel('Name')
        ax.set_ylabel('Time')
        ax.legend(['Time'])
        plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
        return fig
    except Exception as e:
        print(f"An error occurred while plotting: {e}")
        return None

@app.route('/plot/attendanceagain')
def plot_attendanceagain():
    df = fetch_employee_attendance()  # Fetch attendance data
    fig = plot_name_time_graph(df)  # Plot graph
    if fig:
        output = io.BytesIO()
        fig.savefig(output, format='png')
        output.seek(0)
        return send_file(output, mimetype='image/png')
    else:
        return "Error generating attendance graph"

if __name__ == '__main__':
    app.run(debug=True)