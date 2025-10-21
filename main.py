# E-Medical Record System For SIH25

import streamlit as st
from dotenv import load_dotenv # for .env file
import mysql.connector
import smtplib, time
import configparser, os # for config ini file
import hashlib, secrets
import uuid, base64
import qrcode, re
from PIL import Image
from datetime import datetime, date, timedelta
import socket, io
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai # using gemini ai
import pandas as pd

# Importing Modules
from Modules import pycss
from Modules import db
from Modules import qrhtml

st.set_page_config(
    page_title="E-Medical Record System",
    page_icon="🏥"
)

# Loading environment variables..
load_dotenv()

config = configparser.ConfigParser()
try:
    config.read("Config.ini")
    if "EMAIL" in config:
        SERVER_SMTP = config["EMAIL"]["smtp_server"]
        PORT_SMTP = int(config["EMAIL"]["smtp_port"])
        OTP_SUBJECT = config["EMAIL"]["subject"]
        OTP_MESSAGE_BODY = config["EMAIL"]["message"]
    else:
        # Default settings
        SERVER_SMTP = "smtp.gmail.com"
        PORT_SMTP = 587
        OTP_SUBJECT = "E-Medical Record System - OTP Verification"
        OTP_MESSAGE_BODY = "Your OTP for E-Medical Record System verification is: {otp}\n\nThis OTP will expire in 5 minutes.\n\nIf you didn't request this OTP, please ignore this email."
except:
    # Default settings
    SERVER_SMTP = "smtp.gmail.com"
    PORT_SMTP = 587
    OTP_SUBJECT = "E-Medical Record System - OTP Verification"
    OTP_MESSAGE_BODY = "Your OTP for E-Medical Record System verification is: {otp}\n\nThis OTP will expire in 5 minutes.\n\nIf you didn't request this OTP, please ignore this email."

# Configuring Gemini ai...
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        AI_AVAILABLE = True

        # model using
        AI_MODEL = genai.GenerativeModel('gemini-2.5-flash-lite')
    else:
        AI_AVAILABLE = False
        print("Google API key not found in environment variables")
except Exception as e:
    AI_AVAILABLE = False
    print(f"AI initialization failed: {e}")

# functions for otp sending
def send_otp_email(receiver_email, otp, sender_email=None, sender_password=None):
    if not sender_email:
        sender_email = os.getenv("SENDER_EMAIL")
    if not sender_password:
        sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        return False, "Email credentials not configured"
    
    body = OTP_MESSAGE_BODY.replace("{otp}", str(otp))
    message = f"Subject: {OTP_SUBJECT}\n\n{body}"
    
    try:
        server = smtplib.SMTP(SERVER_SMTP, PORT_SMTP)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
        return True, "OTP sent successfully"
    except Exception as e:
        return False, f"Failed to send OTP: {str(e)}"

def generate_otp():
    return secrets.randbelow(900000) + 100000  # using secrets module for security..

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'login_error' not in st.session_state:
        st.session_state.login_error = False
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'Login'
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    if 'success_message' not in st.session_state:
        st.session_state.success_message = None
    if 'selected_patients' not in st.session_state:
        st.session_state.selected_patients = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    if 'otp_stage' not in st.session_state:
        st.session_state.otp_stage = None
    if 'otp_code' not in st.session_state:
        st.session_state.otp_code = None
    if 'otp_time' not in st.session_state:
        st.session_state.otp_time = None
    if 'otp_attempts' not in st.session_state:
        st.session_state.otp_attempts = 0
    if 'pending_user_data' not in st.session_state:
        st.session_state.pending_user_data = None
    if 'pending_action' not in st.session_state:
        st.session_state.pending_action = None
    if 'otp_email' not in st.session_state:
        st.session_state.otp_email = None
    if 'show_health_streak_toast' not in st.session_state:
        st.session_state.show_health_streak_toast = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'ai_context' not in st.session_state:
        st.session_state.ai_context = {}
    if 'show_ai_chat' not in st.session_state:
        st.session_state.show_ai_chat = False
    if 'doctor_chat_messages' not in st.session_state:
        st.session_state.doctor_chat_messages = []
    if 'doctor_ai_context' not in st.session_state: 
        st.session_state.doctor_ai_context = {}
    if 'show_batch_instructions' not in st.session_state:
        st.session_state.show_batch_instructions = False

def create_enhanced_tables():
    conn = db.db_connection()
    if not conn: 
        return
    cursor = conn.cursor()
    try:
        # patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id VARCHAR(20) PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                date_of_birth DATE,
                gender ENUM('Male', 'Female', 'Other', 'Prefer not to say'),
                blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'),
                address TEXT,
                emergency_contact VARCHAR(100),
                emergency_phone VARCHAR(20),
                insurance_provider VARCHAR(100),
                insurance_number VARCHAR(100),
                height_cm INT,
                weight_kg DECIMAL(5,2),
                qr_token VARCHAR(255) UNIQUE,
                last_login DATE,
                health_streak INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id VARCHAR(20) PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                license_number VARCHAR(50),
                specialization VARCHAR(100),
                hospital VARCHAR(200),
                experience_years INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # medical records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_records (
                record_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(20),
                doctor_id VARCHAR(20),
                visit_date DATE NOT NULL,
                diagnosis TEXT,
                treatment TEXT,
                prescription TEXT,
                notes TEXT,
                glucose_level DECIMAL(5,2),
                blood_pressure_systolic INT,
                blood_pressure_diastolic INT,
                heart_rate INT,
                temperature DECIMAL(4,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        ''')
        
        # Medical files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_files (
                file_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(20),
                doctor_id VARCHAR(20),
                file_name VARCHAR(200) NOT NULL,
                file_data LONGBLOB NOT NULL,
                file_type VARCHAR(50),
                category ENUM('Lab Report', 'Medical Report', 'Prescription', 'Insurance', 'Other'),
                description TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        ''')
        
        # Medical images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_images (
                image_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(20),
                doctor_id VARCHAR(20),
                image_name VARCHAR(200) NOT NULL,
                image_data LONGBLOB NOT NULL,
                image_type VARCHAR(50),
                description TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        ''')
        
        # Allergies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allergies (
                allergy_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(20),
                allergy_name VARCHAR(100) NOT NULL,
                severity ENUM('Mild', 'Moderate', 'Severe'),
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        ''')
        
        conn.commit()
    except mysql.connector.Error as err:
        st.error(f"Error creating tables: {err}")
    finally:
        cursor.close()
        conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_id(prefix):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

def show_otp_verification():
    pycss.load_css()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🌓 Toggle Theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown('<div class="main-header"><h1>🔐 OTP Verification</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)

        st.markdown(f"#### 📧 OTP sent to: {st.session_state.otp_email}")

        remaining_time = 0
        if st.session_state.otp_time:
            current_time = time.time()
            elapsed_time = current_time - st.session_state.otp_time
            remaining_time = max(0, 300 - elapsed_time)  # means 5 minutes
        
        with st.form("otp_verification_form"):
            user_otp = st.text_input(
                "🔢 Enter 6-digit OTP", 
                max_chars=6, 
                type="password",
                key="otp_input",
                placeholder="000000"
            )
            
            if remaining_time > 0:
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                st.markdown(f"<p style='text-align: center; color: {'#ffffff' if st.session_state.dark_mode else '#2c3e50'}; font-size: 1.1em;'>⏰ Time remaining: <strong>{minutes:02d}:{seconds:02d}</strong></p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='text-align: center; color: red; font-size: 1.1em;'>⏰ <strong>OTP has expired</strong></p>", unsafe_allow_html=True)
            
            verify_button = st.form_submit_button("✅ Verify OTP", use_container_width=True)
            
            if verify_button:
                if not user_otp:
                    st.error("⚠️ Please enter the OTP")
                elif len(user_otp) != 6:
                    st.error("⚠️ OTP must be 6 digits")
                elif not user_otp.isdigit():
                    st.error("⚠️ OTP must contain only numbers")
                else:
                    current_time = time.time()
                    st.session_state.otp_attempts += 1
                    
                    if current_time - st.session_state.otp_time > 300:
                        st.error("⏰ OTP expired. Please request a new one.")
                    elif user_otp == str(st.session_state.otp_code):
                        if st.session_state.pending_action == 'login':
                            st.session_state.user = st.session_state.pending_user_data
                            st.session_state.success_message = f"Welcome back, {st.session_state.user['name']}!"
        
                            # health streak
                            if st.session_state.user.get('role') == 'patient':
                                streak = st.session_state.user.get('health_streak', 0)
                                if streak > 0:
                                    st.session_state.show_health_streak_toast = streak
        
                        elif st.session_state.pending_action == 'register':
                            st.session_state.success_message = "✅ Registration successful! You can now log in."
                            st.session_state.auth_mode = 'Login'

                        st.session_state.otp_stage = None
                        st.session_state.otp_code = None
                        st.session_state.otp_time = None
                        st.session_state.otp_attempts = 0
                        st.session_state.pending_user_data = None
                        st.session_state.pending_action = None
                        st.session_state.otp_email = None
    
                        st.rerun()
                    else:
                        if st.session_state.otp_attempts < 3:
                            st.error(f"❌ Incorrect OTP. Attempts left: {3 - st.session_state.otp_attempts}")
                        else:
                            st.error("❌ Too many failed attempts. Please request a new OTP.")

                            st.session_state.otp_attempts = 0
        
        st.markdown("---")
        

        col_resend, col_back = st.columns([1, 1])
        
        with col_resend:
            if st.button("📧 Resend OTP", use_container_width=True):
                new_otp = generate_otp()
                success, message = send_otp_email(st.session_state.otp_email, new_otp)
                
                if success:
                    st.session_state.otp_code = new_otp
                    st.session_state.otp_time = time.time()
                    st.session_state.otp_attempts = 0
                    st.success("📧 New OTP sent successfully!")
                    time.sleep(2) 
                    st.rerun()
                else:
                    st.error(f"❌ Failed to resend OTP: {message}")
        
        with col_back:
            if st.button("⬅️ Back to Login", use_container_width=True):
                st.session_state.otp_stage = None
                st.session_state.otp_code = None
                st.session_state.otp_time = None
                st.session_state.otp_attempts = 0
                st.session_state.pending_user_data = None
                st.session_state.pending_action = None
                st.session_state.otp_email = None
                st.session_state.auth_mode = 'Login'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if remaining_time > 0:
            time.sleep(1)
            st.rerun()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generate_qr_code(qr_token):
    local_ip = get_local_ip()
    base_url = f"http://{local_ip}:8501"
    emergency_url = f"{base_url}?emergency={qr_token}"
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(emergency_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

# Health streak fxn
def update_health_streak(patient_id):
    conn = db.db_connection()
    if not conn: 
        return 0
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT health_streak, last_login FROM patients WHERE patient_id = %s', (patient_id,))
        result = cursor.fetchone()
        
        if result:
            current_streak = result[0] or 0
            last_login = result[1]
            today = date.today()
            
            if last_login is None:  # streaks logic
                new_streak = 1
            elif last_login == today:
                new_streak = current_streak
            elif last_login == today - timedelta(days=1):
                new_streak = current_streak + 1
            else:
                new_streak = 1
            
            # Updating db for streaks
            cursor.execute('UPDATE patients SET health_streak = %s, last_login = %s WHERE patient_id = %s',
                         (new_streak, today, patient_id))
            conn.commit()
            return new_streak
        
        return 0
    except mysql.connector.Error as e:
        st.error(f"Error updating health streak: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

# authentication functions (logic, register)
def register_patient(patient_data):
    conn = db.db_connection()
    if not conn: 
        return False, "Database connection failed"
    cursor = conn.cursor()
    
    try:
        patient_id = generate_id("PAT")
        qr_token = uuid.uuid4().hex
        password_hash = hash_password(patient_data['password'])
        
        cursor.execute('''
            INSERT INTO patients (patient_id, first_name, last_name, email, password_hash,
                                phone, date_of_birth, gender, blood_group, address, 
                                emergency_contact, emergency_phone, insurance_provider, 
                                insurance_number, height_cm, weight_kg, qr_token)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (patient_id, patient_data['first_name'], patient_data['last_name'],
              patient_data['email'], password_hash, patient_data.get('phone'),
              patient_data.get('date_of_birth'), patient_data.get('gender'),
              patient_data.get('blood_group'), patient_data.get('address'),
              patient_data.get('emergency_contact'), patient_data.get('emergency_phone'),
              patient_data.get('insurance_provider'), patient_data.get('insurance_number'),
              patient_data.get('height_cm'), patient_data.get('weight_kg'), qr_token))
        
        conn.commit()
        return True, patient_id
    except mysql.connector.Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def register_doctor(doctor_data):
    conn = db.db_connection()
    if not conn: 
        return False, "Database connection failed"
    cursor = conn.cursor()
    
    try:
        doctor_id = generate_id("DOC")
        password_hash = hash_password(doctor_data['password'])
        
        cursor.execute('''
            INSERT INTO doctors (doctor_id, first_name, last_name, email, password_hash,
            phone, license_number, specialization, hospital, experience_years)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (doctor_id, doctor_data['first_name'], doctor_data['last_name'],
              doctor_data['email'], password_hash, doctor_data.get('phone'),
              doctor_data['license_number'], doctor_data.get('specialization'),
              doctor_data.get('hospital'), doctor_data.get('experience_years')))
        
        conn.commit()
        return True, doctor_id
    except mysql.connector.Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def login_patient(email_or_id, password):
    conn = db.db_connection()
    if not conn: 
        return False, None
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            SELECT patient_id, first_name, last_name, qr_token, phone, blood_group, email
            FROM patients WHERE (email = %s OR patient_id = %s) AND password_hash = %s
        ''', (email_or_id, email_or_id, password_hash))
        
        result = cursor.fetchone()
        if result:
            patient_id = result[0]
            streak = update_health_streak(patient_id)
            
            return True, {
                'id': result[0], 'name': f"{result[1]} {result[2]}",
                'qr_token': result[3], 'phone': result[4], 'blood_group': result[5],
                'role': 'patient', 'email': result[6], 'health_streak': streak
            }
        return False, None
    except mysql.connector.Error as e:
        st.error(f"Login error: {e}")
        return False, None
    finally:
        cursor.close()
        conn.close()

def login_doctor(email_or_id, password):
    conn = db.db_connection()
    if not conn: 
        return False, None
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            SELECT doctor_id, first_name, last_name, specialization, hospital, email
            FROM doctors WHERE (email = %s OR doctor_id = %s) AND password_hash = %s
        ''', (email_or_id, email_or_id, password_hash))
        
        result = cursor.fetchone()
        if result:
            return True, {
                'id': result[0], 'name': f"Dr. {result[1]} {result[2]}",
                'specialization': result[3], 'hospital': result[4],
                'role': 'doctor', 'email': result[5]
            }
        return False, None
    except mysql.connector.Error as e:
        st.error(f"Login error: {e}")
        return False, None
    finally:
        cursor.close()
        conn.close()

# search fxn

def search_doctors_advanced(search_term="", specialty_filter="", experience_filter="", location_filter=""):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        # Build dynamic query based on filters
        query = '''
            SELECT doctor_id, first_name, last_name, email, phone, specialization, 
                   hospital, experience_years, license_number, created_at
            FROM doctors 
            WHERE 1=1
        '''
        params = []
        
        if search_term:
            query += ''' AND (doctor_id LIKE %s OR first_name LIKE %s OR last_name LIKE %s 
                           OR email LIKE %s OR specialization LIKE %s OR hospital LIKE %s)'''
            search_param = f'%{search_term}%'
            params.extend([search_param] * 6)
        
        if specialty_filter and specialty_filter != "All Specialties":
            query += ' AND specialization LIKE %s'
            params.append(f'%{specialty_filter}%')
        
        if experience_filter and experience_filter != "Any Experience":
            if experience_filter == "0-5 years":
                query += ' AND experience_years BETWEEN 0 AND 5'
            elif experience_filter == "5-10 years":
                query += ' AND experience_years BETWEEN 5 AND 10'
            elif experience_filter == "10-20 years":
                query += ' AND experience_years BETWEEN 10 AND 20'
            elif experience_filter == "20+ years":
                query += ' AND experience_years >= 20'
        
        if location_filter:
            query += ' AND hospital LIKE %s'
            params.append(f'%{location_filter}%')
        
        query += ' ORDER BY experience_years DESC, first_name ASC'
        
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error searching doctors: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def search_patients(search_term):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT patient_id, first_name, last_name, email, phone, blood_group
            FROM patients 
            WHERE patient_id LIKE %s OR first_name LIKE %s OR last_name LIKE %s OR email LIKE %s
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error searching patients: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_medical_file(patient_id, doctor_id, file, category, description):
    conn = db.db_connection()
    if not conn: 
        return False
    cursor = conn.cursor()
    
    try:
        file_data = file.read()
        file_name = file.name
        file_type = file.type
        
        cursor.execute('''
            INSERT INTO medical_files (patient_id, doctor_id, file_name, file_data, file_type, category, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (patient_id, doctor_id, file_name, file_data, file_type, category, description))
        
        conn.commit()
        return True
    except mysql.connector.Error as e:
        st.error(f"Error adding medical file: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def patient_files(patient_id):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT f.file_id, f.file_name, f.file_type, f.category, f.description, f.upload_date,
                   d.first_name, d.last_name, f.file_data
            FROM medical_files f
            LEFT JOIN doctors d ON f.doctor_id = d.doctor_id
            WHERE f.patient_id = %s ORDER BY f.upload_date DESC
        ''', (patient_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error fetching patient files: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_medical_record(record_data):
    conn = db.db_connection()
    if not conn: 
        return False
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment,
                                       prescription, notes, glucose_level, blood_pressure_systolic,
                                       blood_pressure_diastolic, heart_rate, temperature)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (record_data['patient_id'], record_data['doctor_id'], record_data['visit_date'],
              record_data['diagnosis'], record_data['treatment'], record_data['prescription'],
              record_data['notes'], record_data.get('glucose_level'), 
              record_data.get('blood_pressure_systolic'), record_data.get('blood_pressure_diastolic'),
              record_data.get('heart_rate'), record_data.get('temperature')))
        
        conn.commit()
        return True
    except mysql.connector.Error as e:
        st.error(f"Error adding medical record: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_batch_medical_records(records_data, doctor_id):
    """Add multiple medical records from template data"""
    conn = db.db_connection()
    if not conn: 
        return False, "Database connection failed"
    cursor = conn.cursor()
    
    success_count = 0
    failed_records = []
    
    try:
        for i, record_data in enumerate(records_data):
            try:
                cursor.execute('''
                    INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment,
                                               prescription, notes, glucose_level, blood_pressure_systolic,
                                               blood_pressure_diastolic, heart_rate, temperature)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (record_data.get('patient_id'), doctor_id, record_data.get('visit_date'),
                      record_data.get('diagnosis'), record_data.get('treatment'), 
                      record_data.get('prescription'), record_data.get('notes'), 
                      record_data.get('glucose_level'), record_data.get('blood_pressure_systolic'), 
                      record_data.get('blood_pressure_diastolic'), record_data.get('heart_rate'), 
                      record_data.get('temperature')))
                success_count += 1
            except mysql.connector.Error as e:
                failed_records.append(f"Row {i+1}: {str(e)}")
                continue
        
        conn.commit()
        return True, f"Successfully processed {success_count} records. Failed: {len(failed_records)}"
        
    except Exception as e:
        conn.rollback()
        return False, f"Batch processing failed: {str(e)}"
    finally:
        cursor.close()
        conn.close()

def validate_patient_exists(patient_id):
    """Check if patient exists in database"""
    conn = db.db_connection()
    if not conn: 
        return False
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM patients WHERE patient_id = %s', (patient_id,))
        result = cursor.fetchone()
        return result[0] > 0
    except mysql.connector.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def parse_template_file(uploaded_file):
    """Parse uploaded template file (CSV/Excel) and return structured data"""
    try:
        if uploaded_file.type == "text/csv":
            import pandas as pd
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            import pandas as pd
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file format. Please upload CSV or Excel files."
        
        # Clean column names (remove whitespace, standardize)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Required columns mapping
        required_columns = {
            'patient_id': ['patient_id', 'patientid', 'id'],
            'visit_date': ['visit_date', 'date', 'visit_date'],
            'diagnosis': ['diagnosis', 'condition', 'primary_diagnosis'],
            'treatment': ['treatment', 'treatment_plan', 'therapy'],
            'prescription': ['prescription', 'medications', 'drugs'],
            'notes': ['notes', 'comments', 'observations']
        }
        
        # Optional vital signs columns
        optional_columns = {
            'glucose_level': ['glucose', 'glucose_level', 'blood_glucose'],
            'blood_pressure_systolic': ['systolic', 'bp_systolic', 'blood_pressure_systolic'],
            'blood_pressure_diastolic': ['diastolic', 'bp_diastolic', 'blood_pressure_diastolic'],
            'heart_rate': ['heart_rate', 'pulse', 'hr'],
            'temperature': ['temperature', 'temp', 'body_temp']
        }
        
        # Map columns to standard names
        column_mapping = {}
        for standard_name, possible_names in {**required_columns, **optional_columns}.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    column_mapping[possible_name] = standard_name
                    break
        
        # Check for required columns
        missing_required = []
        for required in ['patient_id', 'visit_date']:
            if not any(col in df.columns for col in required_columns[required]):
                missing_required.append(required)
        
        if missing_required:
            return None, f"Missing required columns: {', '.join(missing_required)}"
        
        # Rename columns according to mapping
        df_renamed = df.rename(columns=column_mapping)
        
        # Convert to list of dictionaries
        records_data = []
        for _, row in df_renamed.iterrows():
            # Skip empty rows
            if pd.isna(row.get('patient_id')) or pd.isna(row.get('visit_date')):
                continue
                
            record = {}
            for col in ['patient_id', 'visit_date', 'diagnosis', 'treatment', 'prescription', 'notes',
                       'glucose_level', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                       'heart_rate', 'temperature']:
                if col in df_renamed.columns:
                    value = row[col]
                    if col == 'visit_date':
                        try:
                            if pd.notna(value):
                                # Handle different date formats
                                record[col] = pd.to_datetime(value).date()
                            else:
                                record[col] = date.today()
                        except:
                            record[col] = date.today()
                    elif col in ['glucose_level', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                                'heart_rate', 'temperature']:
                        try:
                            record[col] = float(value) if pd.notna(value) and value != '' else None
                        except:
                            record[col] = None
                    else:
                        record[col] = str(value).strip() if pd.notna(value) and value != '' else None
                else:
                    record[col] = None
            
            records_data.append(record)
        
        return records_data, f"Successfully parsed {len(records_data)} records from template"
        
    except Exception as e:
        return None, f"Error parsing file: {str(e)}"

def generate_template_csv():
    """Generate a sample CSV template for download"""
    import io
    
    template_data = """patient_id,visit_date,diagnosis,treatment,prescription,notes,glucose_level,blood_pressure_systolic,blood_pressure_diastolic,heart_rate,temperature
PAT12345678,2024-01-15,Hypertension,Lifestyle modification and medication,Lisinopril 10mg daily,Patient shows good compliance,95,140,90,72,36.8
PAT87654321,2024-01-16,Type 2 Diabetes,Diet control and medication,Metformin 500mg twice daily,Blood sugar levels improving,180,130,85,68,37.1
PAT11223344,2024-01-17,Common Cold,Rest and symptomatic treatment,Paracetamol as needed,Symptoms should resolve in 7-10 days,,120,80,75,37.2"""
    
    return template_data.encode('utf-8')

def patient_records(patient_id, start_date=None, end_date=None):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT mr.*, d.first_name, d.last_name, d.specialization
            FROM medical_records mr
            LEFT JOIN doctors d ON mr.doctor_id = d.doctor_id
            WHERE mr.patient_id = %s
        '''
        params = [patient_id]
        
        if start_date and end_date:
            query += ' AND mr.visit_date BETWEEN %s AND %s'
            params.extend([start_date, end_date])
            
        query += ' ORDER BY mr.visit_date DESC'
        
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error fetching patient records: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def vital_trends(patient_id):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT visit_date, glucose_level, blood_pressure_systolic, 
                   blood_pressure_diastolic, heart_rate, temperature
            FROM medical_records 
            WHERE patient_id = %s AND visit_date IS NOT NULL
            ORDER BY visit_date ASC
        ''', (patient_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error fetching vital trends: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def add_medical_image(patient_id, doctor_id, image_file, image_type, description):
    conn = db.db_connection()
    if not conn: 
        return False
    cursor = conn.cursor()
    
    try:
        image_data = image_file.read()
        image_name = image_file.name
        
        cursor.execute('''
            INSERT INTO medical_images (patient_id, doctor_id, image_name, image_data, image_type, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (patient_id, doctor_id, image_name, image_data, image_type, description))
        
        conn.commit()
        return True
    except mysql.connector.Error as e:
        st.error(f"Error adding medical image: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def patient_images(patient_id):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT image_id, image_name, image_data, image_type, description, upload_date
            FROM medical_images WHERE patient_id = %s ORDER BY upload_date DESC
        ''', (patient_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error fetching patient images: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_allergy(patient_id, allergy_name, severity, notes):
    conn = db.db_connection()
    if not conn: 
        return False
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO allergies (patient_id, allergy_name, severity, notes)
            VALUES (%s, %s, %s, %s)
        ''', (patient_id, allergy_name, severity, notes))
        
        conn.commit()
        return True
    except mysql.connector.Error as e:
        st.error(f"Error adding allergy: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def patient_allergies(patient_id):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT allergy_name, severity FROM allergies WHERE patient_id = %s
        ''', (patient_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error fetching patient allergies: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def patient_by_qr_token(qr_token):
    conn = db.db_connection()
    if not conn: 
        return None
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT patient_id, first_name, last_name, blood_group, phone, date_of_birth,
                   emergency_contact, emergency_phone
            FROM patients WHERE qr_token = %s
        ''', (qr_token,))
        
        result = cursor.fetchone()
        if result:
            return {
                'patient_id': result[0],
                'first_name': result[1], 
                'last_name': result[2],
                'blood_group': result[3],
                'phone': result[4],
                'date_of_birth': result[5],
                'emergency_contact': result[6],
                'emergency_phone': result[7]
            }
        return None
    except mysql.connector.Error as e:
        st.error(f"Error fetching patient by QR token: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# download records fxn
def create_downloadable_records(records, patient_name):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-Healthcare - {patient_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .record {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; }}
            .record-header {{ background: #f5f5f5; padding: 10px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>E-MEDICAL SYSTEM</h1>
            <h2>{patient_name}</h2>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    """
    
    for record in records:
        doctor_name = f"Dr. {record[13]} {record[14]}" if record[13] and record[14] else "Unknown Doctor"
        html_content += f"""
        <div class="record">
            <div class="record-header">
                Visit Date: {record[3].strftime('%Y-%m-%d')} | Doctor: {doctor_name}
            </div>
            <p><strong>Diagnosis:</strong> {record[4] or 'N/A'}</p>
            <p><strong>Treatment:</strong> {record[5] or 'N/A'}</p>
            <p><strong>Prescription:</strong> {record[6] or 'N/A'}</p>
            <p><strong>Notes:</strong> {record[7] or 'N/A'}</p>
            <div style="margin-top: 10px;">
                <strong>Vital Signs:</strong><br>
                Glucose: {record[8] or 'N/A'} mg/dL | 
                BP: {f"{record[9]}/{record[10]}" if record[9] and record[10] else 'N/A'} mmHg | 
                Heart Rate: {record[11] or 'N/A'} bpm | 
                Temperature: {record[12] or 'N/A'}°C
            </div>
        </div>
        """
    
    html_content += "</body></html>"
    return html_content.encode('utf-8')

# Emergency page..
def show_emergency_page(qr_token):
    pycss.load_css()
    st.markdown('<div class="main-header"><h1>🚨 EMERGENCY MEDICAL INFORMATION</h1></div>', 
                unsafe_allow_html=True)
    
    patient_info = patient_by_qr_token(qr_token)
    
    if not patient_info:
        st.error("⚠️ Invalid QR Code or patient not found.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
        <div class="patient-card">
        <h3>👤 Patient Information</h3>
        <p><strong>Name:</strong> {patient_info['first_name']} {patient_info['last_name']}</p>
        <p><strong>Patient ID:</strong> {patient_info['patient_id']}</p>
        <p><strong>Blood Group:</strong> <span style="color: {'red' if st.session_state.dark_mode else '#d32f2f'}; font-weight: bold;">{patient_info['blood_group'] if patient_info['blood_group'] else 'N/A'}</span></p>
        <p><strong>Phone:</strong> {patient_info['phone'] if patient_info['phone'] else 'N/A'}</p>
        <p><strong>DOB:</strong> {patient_info['date_of_birth'].strftime('%Y-%m-%d') if patient_info['date_of_birth'] else 'N/A'}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="patient-card">
        <h3>📞 Emergency Contact</h3>
        <p><strong>Contact:</strong> {patient_info['emergency_contact'] or 'Not provided'}</p>
        <p><strong>Phone:</strong> {patient_info['emergency_phone'] or 'Not provided'}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    allergies = patient_allergies(patient_info['patient_id'])
    
    if allergies:
        st.markdown('<div class="patient-card"><h3>⚠️ CRITICAL ALLERGIES</h3>', unsafe_allow_html=True)
        for allergy in allergies:
            severity_color = {"Mild": "orange", "Moderate": "red", "Severe": "darkred"}
            st.markdown(f'<p style="color: {severity_color.get(allergy[1], "white" if st.session_state.dark_mode else "black")}; font-weight: bold;">• {allergy[0]} ({allergy[1]})</p>', 
                      unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="patient-card"><p>✅ No known allergies reported.</p></div>', unsafe_allow_html=True)

    recent_records = patient_records(patient_info['patient_id'], start_date=date.today() - timedelta(days=365))
    if recent_records:
        st.markdown('<div class="patient-card"><h3>📋 Recent Medical Notes (Past Year)</h3>', unsafe_allow_html=True)
        for i, record in enumerate(recent_records[:3]):
            st.markdown(f"**Visit Date:** {record[3].strftime('%Y-%m-%d')}")
            if record[4]: 
                st.markdown(f"**Diagnosis:** {record[4]}")
            if record[5]: 
                st.markdown(f"**Treatment:** {record[5]}")
            st.markdown("---")
        st.markdown('<p>⚠️ For full history, access requires authenticated doctor login.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="patient-card"><p>No recent medical records available.</p></div>', unsafe_allow_html=True)

def get_comprehensive_patient_data(patient_id):
    conn = db.db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    
    try:
        # Get patient basic info
        cursor.execute('''
            SELECT patient_id, first_name, last_name, email, phone, date_of_birth, 
                   gender, blood_group, address, emergency_contact, emergency_phone,
                   insurance_provider, insurance_number, height_cm, weight_kg, health_streak
            FROM patients WHERE patient_id = %s
        ''', (patient_id,))
        
        patient_basic = cursor.fetchone()
        if not patient_basic:
            return None
        
        # Calculate age and BMI
        age = None
        bmi = None
        if patient_basic[5]:  # date_of_birth
            age = (date.today() - patient_basic[5]).days // 365
        
        if patient_basic[13] and patient_basic[14]:  # height_cm and weight_kg
            try:
                height_cm = float(patient_basic[13])
                weight_kg = float(patient_basic[14])
                if height_cm > 0:
                    height_m = height_cm / 100.0
                    bmi = round(weight_kg / (height_m * height_m), 1)
                else:
                    bmi = None
            except (TypeError, ValueError, ZeroDivisionError):
                bmi = None

        
        # Get medical records with doctor info
        cursor.execute('''
            SELECT mr.record_id, mr.visit_date, mr.diagnosis, mr.treatment, mr.prescription,
                   mr.notes, mr.glucose_level, mr.blood_pressure_systolic, mr.blood_pressure_diastolic,
                   mr.heart_rate, mr.temperature, mr.created_at,
                   d.first_name, d.last_name, d.specialization
            FROM medical_records mr
            LEFT JOIN doctors d ON mr.doctor_id = d.doctor_id
            WHERE mr.patient_id = %s
            ORDER BY mr.visit_date DESC
        ''', (patient_id,))
        medical_records = cursor.fetchall()
        
        # Get allergies
        cursor.execute('SELECT allergy_name, severity, notes FROM allergies WHERE patient_id = %s', (patient_id,))
        allergies = cursor.fetchall()
        
        # Get medical files
        cursor.execute('''
            SELECT file_name, file_type, category, description, upload_date,
                   d.first_name, d.last_name
            FROM medical_files mf
            LEFT JOIN doctors d ON mf.doctor_id = d.doctor_id
            WHERE mf.patient_id = %s
            ORDER BY mf.upload_date DESC
        ''', (patient_id,))
        medical_files = cursor.fetchall()
        
        # Get medical images
        cursor.execute('''
            SELECT image_name, image_type, description, upload_date
            FROM medical_images
            WHERE patient_id = %s
            ORDER BY upload_date DESC
        ''', (patient_id,))
        medical_images = cursor.fetchall()
        
        # Get recent vital trends
        cursor.execute('''
            SELECT visit_date, glucose_level, blood_pressure_systolic, blood_pressure_diastolic,
                   heart_rate, temperature
            FROM medical_records
            WHERE patient_id = %s AND visit_date >= %s
            ORDER BY visit_date ASC
        ''', (patient_id, date.today() - timedelta(days=180)))
        vital_trends = cursor.fetchall()
        
        return {
            'basic_info': {
                'patient_id': patient_basic[0],
                'name': f"{patient_basic[1]} {patient_basic[2]}",
                'email': patient_basic[3],
                'phone': patient_basic[4],
                'age': age,
                'gender': patient_basic[6],
                'blood_group': patient_basic[7],
                'address': patient_basic[8],
                'emergency_contact': patient_basic[9],
                'emergency_phone': patient_basic[10],
                'insurance_provider': patient_basic[11],
                'insurance_number': patient_basic[12],
                'height_cm': patient_basic[13],
                'weight_kg': patient_basic[14],
                'bmi': bmi,
                'health_streak': patient_basic[15]
            },
            'medical_records': medical_records,
            'allergies': allergies,
            'medical_files': medical_files,
            'medical_images': medical_images,
            'vital_trends': vital_trends
        }
    
    except mysql.connector.Error as e:
        st.error(f"Error fetching patient data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Add this function to show detailed patient history
def show_detailed_patient_history(patient_id):
    st.markdown("---")
    
    # Back button
    if st.button("⬅️ Back to Search", key="back_to_search"):
        if 'selected_patient_for_history' in st.session_state:
            del st.session_state.selected_patient_for_history
        st.rerun()
    
    # Get comprehensive patient data
    patient_data = get_comprehensive_patient_data(patient_id)
    
    if not patient_data:
        st.error("Patient data not found")
        return
    
    basic_info = patient_data['basic_info']
    
    st.markdown(f"## 📋 Complete Medical History - {basic_info['name']}")
    
    # Patient overview cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>👤 Patient Information</h4>
            <p><strong>ID:</strong> {basic_info['patient_id']}</p>
            <p><strong>Age:</strong> {basic_info['age'] if basic_info['age'] else 'Unknown'} years</p>
            <p><strong>Gender:</strong> {basic_info['gender'] if basic_info['gender'] else 'Not specified'}</p>
            <p><strong>Blood Group:</strong> <span style="color: red; font-weight: bold;">{basic_info['blood_group'] if basic_info['blood_group'] else 'Unknown'}</span></p>
            <p><strong>BMI:</strong> {basic_info['bmi'] if basic_info['bmi'] else 'Not calculated'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📞 Contact Information</h4>
            <p><strong>Email:</strong> {basic_info['email']}</p>
            <p><strong>Phone:</strong> {basic_info['phone'] if basic_info['phone'] else 'Not provided'}</p>
            <p><strong>Emergency Contact:</strong> {basic_info['emergency_contact'] if basic_info['emergency_contact'] else 'Not provided'}</p>
            <p><strong>Emergency Phone:</strong> {basic_info['emergency_phone'] if basic_info['emergency_phone'] else 'Not provided'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        insurance_status = "✅ Insured" if basic_info['insurance_provider'] else "❌ No Insurance"
        st.markdown(f"""
        <div class="metric-card">
            <h4>🏥 Medical Summary</h4>
            <p><strong>Total Records:</strong> {len(patient_data['medical_records'])}</p>
            <p><strong>Known Allergies:</strong> {len(patient_data['allergies'])}</p>
            <p><strong>Medical Files:</strong> {len(patient_data['medical_files'])}</p>
            <p><strong>Medical Images:</strong> {len(patient_data['medical_images'])}</p>
            <p><strong>Insurance:</strong> {insurance_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed sections in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Medical Records", "⚠️ Allergies", "📊 Vital Trends", "📁 Files & Images", "👤 Personal Info"])
    
    with tab1:
        st.markdown("### Medical Records History")
        
        if patient_data['medical_records']:
            for record in patient_data['medical_records']:
                doctor_name = f"Dr. {record[12]} {record[13]}" if record[12] and record[13] else "Unknown Doctor"
                specialization = f" ({record[14]})" if record[14] else ""
                
                with st.expander(f"📅 {record[1].strftime('%Y-%m-%d')} - {doctor_name}{specialization}"):
                    col_rec1, col_rec2 = st.columns([2, 1])
                    
                    with col_rec1:
                        if record[2]:  # Diagnosis
                            st.markdown(f"**🔍 Diagnosis:** {record[2]}")
                        if record[3]:  # Treatment
                            st.markdown(f"**💊 Treatment:** {record[3]}")
                        if record[4]:  # Prescription
                            st.markdown(f"**💉 Prescription:** {record[4]}")
                        if record[5]:  # Notes
                            st.markdown(f"**📝 Notes:** {record[5]}")
                    
                    with col_rec2:
                        st.markdown("**Vital Signs:**")
                        if record[6]:  # Glucose
                            glucose_status = "Normal" if 70 <= record[6] <= 140 else "⚠️ Abnormal"
                            st.markdown(f"🩸 Glucose: {record[6]} mg/dL ({glucose_status})")
                        if record[7] and record[8]:  # BP
                            bp_status = "Normal" if record[7] < 140 and record[8] < 90 else "⚠️ High"
                            st.markdown(f"💗 BP: {record[7]}/{record[8]} mmHg ({bp_status})")
                        if record[9]:  # Heart Rate
                            hr_status = "Normal" if 60 <= record[9] <= 100 else "⚠️ Abnormal"
                            st.markdown(f"💓 HR: {record[9]} bpm ({hr_status})")
                        if record[10]:  # Temperature
                            temp_status = "Normal" if 36.1 <= record[10] <= 37.2 else "⚠️ Abnormal"
                            st.markdown(f"🌡️ Temp: {record[10]}°C ({temp_status})")
                        
                        st.markdown(f"**Created:** {record[11].strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No medical records found for this patient.")
    
    with tab2:
        st.markdown("### Known Allergies")
        
        if patient_data['allergies']:
            for allergy in patient_data['allergies']:
                severity_colors = {"Mild": "#ffa500", "Moderate": "#ff6b6b", "Severe": "#d32f2f"}
                severity_color = severity_colors.get(allergy[1], "#666666")
                
                st.markdown(f"""
                <div style="background: {'#1a1a1a' if st.session_state.dark_mode else '#f8f9fa'}; 
                           padding: 12px; border-radius: 8px; margin: 8px 0; 
                           border-left: 4px solid {severity_color};">
                    <strong style="color: {severity_color};">⚠️ {allergy[0]}</strong> - <span style="color: {severity_color};">{allergy[1]} Severity</span><br>
                    {f'<small>{allergy[2]}</small>' if allergy[2] else '<small>No additional notes</small>'}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No known allergies recorded.")
    
    with tab3:
        st.markdown("### Vital Signs Trends (Last 6 Months)")
        
        if patient_data['vital_trends']:
            import pandas as pd
            df_vitals = pd.DataFrame(patient_data['vital_trends'], 
                                   columns=['Date', 'Glucose', 'Systolic', 'Diastolic', 'Heart Rate', 'Temperature'])
            df_vitals['Date'] = pd.to_datetime(df_vitals['Date'])
            
            # Vital signs summary
            col_vital1, col_vital2, col_vital3, col_vital4 = st.columns(4)
            
            with col_vital1:
                if df_vitals['Glucose'].notna().any():
                    avg_glucose = df_vitals['Glucose'].mean()
                    st.metric("Avg Glucose", f"{avg_glucose:.1f} mg/dL")
            
            with col_vital2:
                if df_vitals['Systolic'].notna().any():
                    avg_systolic = df_vitals['Systolic'].mean()
                    st.metric("Avg Systolic", f"{avg_systolic:.0f} mmHg")
            
            with col_vital3:
                if df_vitals['Heart Rate'].notna().any():
                    avg_hr = df_vitals['Heart Rate'].mean()
                    st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm")
            
            with col_vital4:
                if df_vitals['Temperature'].notna().any():
                    avg_temp = df_vitals['Temperature'].mean()
                    st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
            
            # Charts
            if df_vitals['Systolic'].notna().any():
                import plotly.graph_objects as go
                fig_bp = go.Figure()
                fig_bp.add_trace(go.Scatter(x=df_vitals['Date'], y=df_vitals['Systolic'], 
                                          mode='lines+markers', name='Systolic', line=dict(color='red')))
                fig_bp.add_trace(go.Scatter(x=df_vitals['Date'], y=df_vitals['Diastolic'], 
                                          mode='lines+markers', name='Diastolic', line=dict(color='blue')))
                fig_bp.update_layout(title='Blood Pressure Trends', xaxis_title='Date', yaxis_title='mmHg')
                st.plotly_chart(fig_bp, use_container_width=True)
            
            if df_vitals['Glucose'].notna().any():
                import plotly.express as px
                fig_glucose = px.line(df_vitals, x='Date', y='Glucose', title='Blood Glucose Trends', markers=True)
                st.plotly_chart(fig_glucose, use_container_width=True)
        else:
            st.info("No vital signs data available for trend analysis.")
    
    with tab4:
        st.markdown("### Medical Files & Images")
        
        col_files, col_images = st.columns(2)
        
        with col_files:
            st.markdown("#### 📁 Medical Files")
            if patient_data['medical_files']:
                for file in patient_data['medical_files']:
                    uploaded_by = f"Dr. {file[5]} {file[6]}" if file[5] and file[6] else "System"
                    st.markdown(f"""
                    **📄 {file[0]}**
                    - Type: {file[2]} ({file[1]})
                    - Description: {file[3] if file[3] else 'No description'}
                    - Uploaded: {file[4].strftime('%Y-%m-%d')} by {uploaded_by}
                    """)
            else:
                st.info("No medical files uploaded.")
        
        with col_images:
            st.markdown("#### 🖼️ Medical Images")
            if patient_data['medical_images']:
                for image in patient_data['medical_images']:
                    st.markdown(f"""
                    **🖼️ {image[0]}**
                    - Type: {image[1]}
                    - Description: {image[2] if image[2] else 'No description'}
                    - Uploaded: {image[3].strftime('%Y-%m-%d')}
                    """)
            else:
                st.info("No medical images uploaded.")
    
    with tab5:
        st.markdown("### Personal Information")
        
        col_personal1, col_personal2 = st.columns(2)
        
        with col_personal1:
            st.markdown("#### Basic Details")
            st.markdown(f"**Full Name:** {basic_info['name']}")
            st.markdown(f"**Patient ID:** {basic_info['patient_id']}")
            st.markdown(f"**Age:** {basic_info['age'] if basic_info['age'] else 'Unknown'} years")
            st.markdown(f"**Gender:** {basic_info['gender'] if basic_info['gender'] else 'Not specified'}")
            st.markdown(f"**Blood Group:** {basic_info['blood_group'] if basic_info['blood_group'] else 'Unknown'}")
            
            if basic_info['height_cm'] and basic_info['weight_kg']:
                st.markdown(f"**Height:** {basic_info['height_cm']} cm")
                st.markdown(f"**Weight:** {basic_info['weight_kg']} kg")
                st.markdown(f"**BMI:** {basic_info['bmi'] if basic_info['bmi'] else 'Not calculated'}")
        
        with col_personal2:
            st.markdown("#### Contact & Insurance")
            st.markdown(f"**Email:** {basic_info['email']}")
            st.markdown(f"**Phone:** {basic_info['phone'] if basic_info['phone'] else 'Not provided'}")
            st.markdown(f"**Address:** {basic_info['address'] if basic_info['address'] else 'Not provided'}")
            
            st.markdown("#### Emergency Contact")
            st.markdown(f"**Name:** {basic_info['emergency_contact'] if basic_info['emergency_contact'] else 'Not provided'}")
            st.markdown(f"**Phone:** {basic_info['emergency_phone'] if basic_info['emergency_phone'] else 'Not provided'}")
            
            st.markdown("#### Insurance")
            st.markdown(f"**Provider:** {basic_info['insurance_provider'] if basic_info['insurance_provider'] else 'None'}")
            st.markdown(f"**Policy Number:** {basic_info['insurance_number'] if basic_info['insurance_number'] else 'None'}")
            
            if basic_info['health_streak']:
                st.markdown(f"**Health Streak:** {basic_info['health_streak']} days 🔥")

def search_patients_advanced_doctor(search_term="", blood_group_filter="All"):
    conn = db.db_connection()
    if not conn: 
        return []
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT patient_id, first_name, last_name, email, phone, blood_group, date_of_birth
            FROM patients 
            WHERE 1=1
        '''
        params = []
        
        if search_term:
            query += ''' AND (patient_id LIKE %s OR first_name LIKE %s OR last_name LIKE %s 
                           OR email LIKE %s OR phone LIKE %s)'''
            search_param = f'%{search_term}%'
            params.extend([search_param] * 5)
        
        if blood_group_filter != "All":
            query += ' AND blood_group = %s'
            params.append(blood_group_filter)
        
        query += ' ORDER BY first_name ASC, last_name ASC'
        
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error searching patients: {e}")
        return []
    finally:
        cursor.close()
        conn.close()



def show_auth_page():
    pycss.load_css()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🌓 Toggle Theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown('<div class="main-header"><h1>🏥 E-Medical Record System</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.success_message:
        st.markdown(f'<div class="success-message">{st.session_state.success_message}</div>', 
                   unsafe_allow_html=True)
        st.session_state.success_message = None
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        if st.session_state.auth_mode == 'Login':
            st.markdown("### 🔐 Login to Your Account")
            
            role = st.radio("Login as:", ["👤 Patient", "👨‍⚕️ Doctor"], key="login_role_radio")
            
            with st.form("login_form"):
                email_or_id = st.text_input("📧 Email or ID", 
                                          help="Enter your email address or Patient ID/Doctor ID",
                                          key="login_email_id")
                password = st.text_input("🔒 Password", type="password", key="login_password")
                
                col_login, col_switch = st.columns([1, 1])
                with col_login:
                    login_button = st.form_submit_button("🔓 Login", use_container_width=True)
                
                if login_button:
                    st.session_state.login_error = False
    
                    if role == "👤 Patient":
                        success, user_data = login_patient(email_or_id, password)
                        if success:
                            otp = generate_otp()
                            success_otp, message = send_otp_email(user_data['email'], otp)
            
                            if success_otp:
                                st.session_state.otp_code = otp
                                st.session_state.otp_time = time.time()
                                st.session_state.otp_attempts = 0
                                st.session_state.pending_user_data = user_data
                                st.session_state.pending_action = 'login'
                                st.session_state.otp_email = user_data['email']
                                st.session_state.otp_stage = 'verification'
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to send OTP: {message}")
                        else:
                            st.session_state.login_error = True
                    elif role == "👨‍⚕️ Doctor":
                        success, user_data = login_doctor(email_or_id, password)
                        if success:
                            otp = generate_otp()
                            success_otp, message = send_otp_email(user_data['email'], otp)
            
                            if success_otp:
                                st.session_state.otp_code = otp
                                st.session_state.otp_time = time.time()
                                st.session_state.otp_attempts = 0
                                st.session_state.pending_user_data = user_data
                                st.session_state.pending_action = 'login'
                                st.session_state.otp_email = user_data['email']
                                st.session_state.otp_stage = 'verification'
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to send OTP: {message}")
                        else:
                            st.session_state.login_error = True






                            if st.session_state.login_error:
                                st.error("❌ Invalid credentials. Please check your email/ID and password.")
                                st.session_state.login_error = False





         
            st.markdown("---")
            col_reg1, col_reg2 = st.columns([1, 1])
            with col_reg1:
                st.markdown("Don't have an account?")
            with col_reg2:
                if st.button("📝 Sign Up", use_container_width=True):
                    st.session_state.auth_mode = 'Register'
                    st.rerun()

        elif st.session_state.auth_mode == 'Register':
            st.markdown("### 📝 Create New Account")
            
            role = st.radio("Register as:", ["👤 Patient", "👨‍⚕️ Doctor"], key="register_role_radio")

            if role == "👤 Patient":
                with st.form("patient_register_form", clear_on_submit=True):
                    st.markdown("#### Patient Registration")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name*", key="p_fname")
                        email = st.text_input("Email*", key="p_email")
                        password = st.text_input("Password*", type="password", key="p_pass")
                    with col2:
                        last_name = st.text_input("Last Name*", key="p_lname")
                        confirm_password = st.text_input("Confirm Password*", type="password", key="p_cpass")
                        phone = st.text_input("Phone", key="p_phone")
                    
                    with st.expander("📋 Medical Information (Optional)"):
                        col1, col2 = st.columns(2)
                        with col1:
                            dob = st.date_input("Date of Birth", min_value=datetime(1900,1,1), 
                                              max_value=date.today(), key="p_dob", value=None)
                            gender = st.selectbox("Gender", ['Prefer not to say', 'Male', 'Female', 'Other'], key="p_gender")
                            blood_group = st.selectbox("Blood Group", ['Unknown', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], key="p_blood")
                        with col2:
                            height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, key="p_height")
                            weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0, format="%.2f", key="p_weight")
                    
                    with st.expander("📞 Contact & Emergency Information (Optional)"):
                        address = st.text_area("Address", key="p_address")
                        col1, col2 = st.columns(2)
                        with col1:
                            emergency_contact = st.text_input("Emergency Contact Name", key="p_ec_name")
                            insurance_provider = st.text_input("Insurance Provider", key="p_ins_prov")
                        with col2:
                            emergency_phone = st.text_input("Emergency Contact Phone", key="p_ec_phone")
                            insurance_number = st.text_input("Insurance Number", key="p_ins_num")

                    register_button = st.form_submit_button("✅ Register Patient", use_container_width=True)

                    if register_button:
                        if not all([first_name, last_name, email, password, confirm_password]):
                            st.error("⚠️ Please fill in all required fields marked with *")
                        elif password != confirm_password:
                            st.error("⚠️ Passwords do not match.")
                        else:
                            patient_data = {
                                'first_name': first_name, 'last_name': last_name, 'email': email,
                                'password': password, 'phone': phone, 'date_of_birth': dob,
                                'gender': gender, 'blood_group': blood_group, 'address': address,
                                'emergency_contact': emergency_contact, 'emergency_phone': emergency_phone,
                                'insurance_provider': insurance_provider, 'insurance_number': insurance_number,
                                'height_cm': height, 'weight_kg': weight
                            }
                            success, result = register_patient(patient_data)
                            if success:

                                otp = generate_otp()
                                success_otp, message = send_otp_email(email, otp)
            
                                if success_otp:
                                    st.session_state.otp_code = otp
                                    st.session_state.otp_time = time.time()
                                    st.session_state.otp_attempts = 0
                                    st.session_state.pending_action = 'register'
                                    st.session_state.otp_email = email
                                    st.session_state.otp_stage = 'verification'
                                    st.session_state.success_message = f"✅ Registration data saved! Your Patient ID is: {result}. OTP sent to {email}"
                                    st.rerun()
                                else:
                                    st.session_state.success_message = f"✅ Patient registered successfully! Your Patient ID is: {result}"
                                    st.session_state.auth_mode = 'Login'
                                    st.error(f"⚠️ Could not send OTP: {message}")
                                    st.rerun()
                            else:
                                st.error(f"⚠️ Registration failed: {result}")

            elif role == "👨‍⚕️ Doctor":
                with st.form("doctor_register_form", clear_on_submit=True):
                    st.markdown("#### Doctor Registration")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name*", key="d_fname")
                        email = st.text_input("Email*", key="d_email")
                        password = st.text_input("Password*", type="password", key="d_pass")
                        license_number = st.text_input("Medical License Number*", key="d_license")
                    with col2:
                        last_name = st.text_input("Last Name*", key="d_lname")
                        confirm_password = st.text_input("Confirm Password*", type="password", key="d_cpass")
                        phone = st.text_input("Phone", key="d_phone")
                        specialization = st.text_input("Specialization", key="d_spec")
                    
                    with st.expander("🏥 Professional Information (Optional)"):
                        col1, col2 = st.columns(2)
                        with col1:
                            hospital = st.text_input("Hospital/Clinic", key="d_hospital")
                        with col2:
                            experience = st.number_input("Years of Experience", min_value=0, max_value=60, value=5, key="d_exp")

                    register_button = st.form_submit_button("✅ Register Doctor", use_container_width=True)

                    if register_button:
                        if not all([first_name, last_name, email, password, confirm_password, license_number]):
                            st.error("⚠️ Please fill in all required fields marked with *")
                        elif password != confirm_password:
                            st.error("⚠️ Passwords do not match.")
                        else:
                            doctor_data = {
                                'first_name': first_name, 'last_name': last_name, 'email': email,
                                'password': password, 'phone': phone, 'license_number': license_number,
                                'specialization': specialization, 'hospital': hospital,
                                'experience_years': experience
                            }
                            success, result = register_doctor(doctor_data)
                            if success:

                                otp = generate_otp()
                                success_otp, message = send_otp_email(email, otp)
            
                                if success_otp:
                                    st.session_state.otp_code = otp
                                    st.session_state.otp_time = time.time()
                                    st.session_state.otp_attempts = 0
                                    st.session_state.pending_action = 'register'
                                    st.session_state.otp_email = email
                                    st.session_state.otp_stage = 'verification'
                                    st.session_state.success_message = f"✅ Registration data saved! Your Doctor ID is: {result}. OTP sent to                     {email}"
                                    st.rerun()
                                else:
                                    st.session_state.success_message = f"✅ Doctor registered successfully! Your Doctor ID is: {result}"
                                    st.session_state.auth_mode = 'Login'
                                    st.error(f"⚠️ Could not send OTP: {message}")
                                    st.rerun()
                            else:
                                st.error(f"⚠️ Registration failed: {result}")
            
            st.markdown("---")
            col_login1, col_login2 = st.columns([1, 1])
            with col_login1:
                st.markdown("Already have an account?")
            with col_login2:
                if st.button("🔐 Login", use_container_width=True):
                    st.session_state.auth_mode = 'Login'
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ai data feeding 
def get_patient_context_for_ai(patient_id):
    """Gather comprehensive patient data for AI context"""
    context = {
        'patient_basic_info': {},
        'recent_records': [],
        'vital_trends': [],
        'allergies': [],
        'files_summary': [],
        'images_summary': [],
        'health_patterns': {}
    }
    
    conn = db.db_connection()
    if not conn:
        return context
    
    cursor = conn.cursor()
    
    try:
        # basic patient info
        cursor.execute('''
            SELECT first_name, last_name, date_of_birth, gender, blood_group, 
                   height_cm, weight_kg, health_streak, phone, address,
                   emergency_contact, emergency_phone, insurance_provider
            FROM patients WHERE patient_id = %s
        ''', (patient_id,))
        
        basic_info = cursor.fetchone()
        if basic_info:
            age = (date.today() - basic_info[2]).days // 365 if basic_info[2] else None
            bmi = None
            if basic_info[5] and basic_info[6]:
                try:
                    height_cm = float(basic_info[5])
                    weight_kg = float(basic_info[6])
                    height_m = height_cm / 100.0
                    bmi = None
                    if height_m > 0:
                        bmi = weight_kg / (height_m * height_m)
                except (TypeError, ValueError):
                    bmi = None

            
            context['patient_basic_info'] = {
                'name': f"{basic_info[0]} {basic_info[1]}",
                'age': age,
                'gender': basic_info[3],
                'blood_group': basic_info[4],
                'height_cm': basic_info[5],
                'weight_kg': basic_info[6],
                'bmi': round(bmi, 1) if bmi else None,
                'health_streak': basic_info[7],
                'phone': basic_info[8],
                'emergency_contact': basic_info[10],
                'emergency_phone': basic_info[11],
                'has_insurance': bool(basic_info[12])
            }
        
        # Comprehensive medical records (last 12 months)
        cursor.execute('''
            SELECT mr.visit_date, mr.diagnosis, mr.treatment, mr.prescription, 
                   mr.glucose_level, mr.blood_pressure_systolic, mr.blood_pressure_diastolic, 
                   mr.heart_rate, mr.temperature, mr.notes,
                   d.first_name, d.last_name, d.specialization
            FROM medical_records mr
            LEFT JOIN doctors d ON mr.doctor_id = d.doctor_id
            WHERE mr.patient_id = %s AND mr.visit_date >= %s
            ORDER BY mr.visit_date DESC LIMIT 20
        ''', (patient_id, date.today() - timedelta(days=365)))
        
        records = cursor.fetchall()
        for record in records:
            context['recent_records'].append({
                'date': record[0].strftime('%Y-%m-%d'),
                'diagnosis': record[1],
                'treatment': record[2],
                'prescription': record[3],
                'notes': record[9],
                'doctor': f"Dr. {record[10]} {record[11]}" if record[10] else "Unknown",
                'specialization': record[12],
                'vitals': {
                    'glucose': record[4],
                    'bp_systolic': record[5],
                    'bp_diastolic': record[6],
                    'heart_rate': record[7],
                    'temperature': record[8]
                }
            })
        
        # All allergies with details
        cursor.execute('''
            SELECT allergy_name, severity, notes FROM allergies WHERE patient_id = %s
        ''', (patient_id,))
        
        allergies = cursor.fetchall()
        for allergy in allergies:
            context['allergies'].append({
                'name': allergy[0],
                'severity': allergy[1],
                'notes': allergy[2]
            })
        
        # Medical files summary
        cursor.execute('''
            SELECT file_name, category, description, upload_date
            FROM medical_files WHERE patient_id = %s
            ORDER BY upload_date DESC LIMIT 10
        ''', (patient_id,))
        
        files = cursor.fetchall()
        for file in files:
            context['files_summary'].append({
                'name': file[0],
                'category': file[1],
                'description': file[2],
                'date': file[3].strftime('%Y-%m-%d')
            })
        
        # Medical images summary
        cursor.execute('''
            SELECT image_name, image_type, description, upload_date
            FROM medical_images WHERE patient_id = %s
            ORDER BY upload_date DESC LIMIT 10
        ''', (patient_id,))
        
        images = cursor.fetchall()
        for image in images:
            context['images_summary'].append({
                'name': image[0],
                'type': image[1],
                'description': image[2],
                'date': image[3].strftime('%Y-%m-%d')
            })
        
        # Vital trends analysis (last 6 months)...
        cursor.execute('''
            SELECT visit_date, glucose_level, blood_pressure_systolic, 
                   blood_pressure_diastolic, heart_rate, temperature
            FROM medical_records 
            WHERE patient_id = %s AND visit_date >= %s
            ORDER BY visit_date ASC
        ''', (patient_id, date.today() - timedelta(days=180)))
        
        vitals = cursor.fetchall()
        for vital in vitals:
            context['vital_trends'].append({
                'date': vital[0].strftime('%Y-%m-%d'),
                'glucose': vital[1],
                'bp_systolic': vital[2],
                'bp_diastolic': vital[3],
                'heart_rate': vital[4],
                'temperature': vital[5]
            })
        
        # Health patterns analysis
        if vitals:
            glucose_values = [v[1] for v in vitals if v[1] is not None]
            bp_sys_values = [v[2] for v in vitals if v[2] is not None]
            heart_rate_values = [v[4] for v in vitals if v[4] is not None]
            
            context['health_patterns'] = {
                'glucose_avg': round(sum(glucose_values)/len(glucose_values), 1) if glucose_values else None,
                'glucose_trend': 'stable',  # Could add trend analysis
                'bp_avg': round(sum(bp_sys_values)/len(bp_sys_values), 0) if bp_sys_values else None,
                'heart_rate_avg': round(sum(heart_rate_values)/len(heart_rate_values), 0) if heart_rate_values else None,
                'total_visits': len(records),
                'recent_diagnoses': list(set([r[1] for r in records[:5] if r[1]])),
                'frequent_medications': []  # Could analyze prescription patterns
            }
        
    except mysql.connector.Error as e:
        print(f"Error getting patient context: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return context

def generate_ai_response(user_message, patient_context=None):
    """Generate AI response using Gemini with comprehensive medical analysis"""
    if not AI_AVAILABLE:
        return "AI assistant is currently unavailable. Please check your API configuration."
    
    try:
        # Create comprehensive system prompt
        system_prompt = """You are an advanced AI medical assistant for an E-Medical Record System with access to comprehensive patient data.
        IMPORTANT GUIDELINES:
        1. You are NOT a replacement for professional medical advice - always remind users to consult healthcare providers
        2. Provide detailed analysis of the patient's medical data when relevant
        3. Identify patterns, trends, and potential concerns in their health data
        4. Be empathetic, supportive, and use clear, understandable language
        5. For serious symptoms or concerning patterns, recommend immediate medical attention
        6. Respond in plain text without HTML formatting
        7. When analyzing data, be specific about what the numbers mean and their normal ranges
        8. Explain medical terms in simple language
        9. Use local language (example Hindi) when user asks

        """
        # Add comprehensive patient context if available
        if patient_context and any(patient_context.values()):
            context_text = "\nCOMPREHENSIVE PATIENT DATA:\n"
            
            # Basic info
            basic_info = patient_context.get('patient_basic_info', {})
            if basic_info:
                context_text += f"""
                    PATIENT PROFILE:
                    - Name: {basic_info.get('name', 'Unknown')}
                    - Age: {basic_info.get('age', 'Unknown')} years
                    - Gender: {basic_info.get('gender', 'Unknown')}
                    - Blood Group: {basic_info.get('blood_group', 'Unknown')}
                    - BMI: {basic_info.get('bmi', 'Not calculated')}
                    - Health Streak: {basic_info.get('health_streak', 0)} days
                    - Has Insurance: {'Yes' if basic_info.get('has_insurance') else 'No'}

                    """
            
            # Recent medical records
            recent_records = patient_context.get('recent_records', [])
            if recent_records:
                context_text += f"RECENT MEDICAL HISTORY ({len(recent_records)} visits):\n"
                for i, record in enumerate(recent_records[:5]):  # Show last 5 visits
                    context_text += f"""
                        Visit {i+1} ({record['date']}):
                        - Doctor: {record['doctor']} ({record['specialization']})
                        - Diagnosis: {record['diagnosis'] or 'Not specified'}
                        - Treatment: {record['treatment'] or 'Not specified'}
                        - Prescription: {record['prescription'] or 'None'}
                        - Vital Signs: Glucose: {record['vitals']['glucose'] or 'N/A'} mg/dL, 
                        BP: {record['vitals']['bp_systolic'] or 'N/A'}/{record['vitals']['bp_diastolic'] or 'N/A'} mmHg, 
                        Heart Rate: {record['vitals']['heart_rate'] or 'N/A'} bpm, 
                        Temperature: {record['vitals']['temperature'] or 'N/A'}°C
                        """
            
            # Allergies
            allergies = patient_context.get('allergies', [])
            if allergies:
                context_text += f"\nKNOWN ALLERGIES ({len(allergies)}):\n"
                for allergy in allergies:
                    context_text += f"- {allergy['name']} ({allergy['severity']})\n"
            
            # Health patterns
            patterns = patient_context.get('health_patterns', {})
            if patterns:
                context_text += f"""
                    HEALTH PATTERNS ANALYSIS:
                    - Average Blood Glucose: {patterns.get('glucose_avg', 'N/A')} mg/dL
                    - Average Blood Pressure: {patterns.get('bp_avg', 'N/A')} mmHg (systolic)
                    - Average Heart Rate: {patterns.get('heart_rate_avg', 'N/A')} bpm
                    - Total Medical Visits: {patterns.get('total_visits', 0)}
                    - Recent Diagnoses: {', '.join(patterns.get('recent_diagnoses', [])) or 'None'}

                    """
            # Medical files and images
            files = patient_context.get('files_summary', [])
            images = patient_context.get('images_summary', [])
            if files or images:
                context_text += f"\nMEDICAL DOCUMENTATION:\n"
                if files:
                    context_text += f"- {len(files)} medical files on record (recent: {files[0]['category'] if files else 'None'})\n"
                if images:
                    context_text += f"- {len(images)} medical images on record (recent: {images[0]['type'] if images else 'None'})\n"
            
            system_prompt += context_text
        
        # Combine system prompt with user message
        full_prompt = system_prompt + f"\nPATIENT QUESTION: {user_message}"
        
        # Generate response
        response = AI_MODEL.generate_content(full_prompt)
        
        # Clean response
        clean_response = re.sub(r'<[^>]+>', '', response.text)
        clean_response = clean_response.replace('**', '')
        clean_response = clean_response.replace('*', '')
        clean_response = clean_response.strip()
        
        return clean_response
        
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request right now. Please try again or contact your healthcare provider if you have urgent medical concerns. Error: {str(e)}"
    
def show_ai_chat_interface():
    """Display the AI chat interface with proper CSS loading"""

    pycss.load_css()
    
    # Simple header with toggle button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🌙 Toggle Theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    # page title
    st.markdown('<div class="main-header"><h1>👾 AI Health Assistant</h1><p>Ask me anything about your health data, symptoms, or general health questions!</p></div>', unsafe_allow_html=True)
    
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_messages:
            for i, message_data in enumerate(st.session_state.chat_messages):
                if message_data["role"] == "user":
                    if st.session_state.dark_mode:
                        # Dark mode: White background + Black text
                        user_bg = "linear-gradient(135deg, #ffffff, #f0f0f0)"
                        user_text = "#000000"
                    else:
                        # Light mode: Blue background + White text  
                        user_bg = "linear-gradient(135deg, #2196F3, #1976D2)"
                        user_text = "#ffffff"
    
                    st.markdown(f"""
                    <div style="text-align: right; margin: 15px 0;">
                        <div class="user-bubble" style="background: {user_bg}; 
                                    color: {user_text} !important; 
                                    padding: 12px 16px; border-radius: 15px; display: inline-block; max-width: 80%;
                                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
                            <strong style="color: {user_text} !important;">You:</strong> 
                            <span style="color: {user_text} !important;">{message_data["content"]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # AI response - Correct colors for both themes
                    clean_content = message_data["content"].replace('<div>', '').replace('</div>', '').replace('<p>', '').replace('</p>', '')
                    if st.session_state.dark_mode:
                        # Dark mode: Blue background + White text
                        bg_color = "linear-gradient(135deg, #1976D2, #2196F3)"
                        text_color = "#ffffff"
                    else:
                        # Light mode: Green background + Black text
                        bg_color = "linear-gradient(135deg, #4CAF50, #45a049)"
                        text_color = "#000000"
    
                    st.markdown(f"""
                    <div style="text-align: left; margin: 15px 0;">
                        <div class="ai-bubble" style="background: {bg_color}; 
                                    color: {text_color} !important; 
                                    padding: 12px 16px; border-radius: 15px; display: inline-block; max-width: 80%;
                                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
                            <strong style="color: {text_color} !important;">👾 AI Assistant:</strong> 
                            <span style="color: {text_color} !important;">{clean_content}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="info-card" style="text-align: center; padding: 30px;">
                <h3>👋 Hello! I'm your AI health assistant.</h3>
                <p>You can ask me about:</p>
                <div style="text-align: left; max-width: 500px; margin: 20px auto;">
                    <p>📊 Your medical records and vital trends</p>
                    <p>💊 General health questions</p>
                    <p>🔍 Understanding your test results</p>
                    <p>🏥 Health recommendations</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat bar
    with st.form("ai_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("", key="ai_chat_input", placeholder="Ask me anything about your health...", label_visibility="collapsed")
        with col2:
            send_button = st.form_submit_button("Send 📤", use_container_width=True)
        
        if send_button and user_input:

            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            patient_context = None
            if st.session_state.user and st.session_state.user.get('role') == 'patient':
                patient_context = get_patient_context_for_ai(st.session_state.user['id'])
            
            # Generating response
            with st.spinner("🤔 Thinking..."):
                ai_response = generate_ai_response(user_input, patient_context)
            
            # adding ai to chat
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
            
            st.rerun()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):   # to clear chat
            st.session_state.chat_messages = []
            st.rerun()

def get_doctor_context_for_ai(doctor_id, selected_patients=None):
    """Gather comprehensive data for doctor's AI assistant"""
    context = {
        'doctor_info': {},
        'patient_summaries': [],
        'recent_activities': [],
        'statistics': {}
    }
    
    conn = db.db_connection()
    if not conn:
        return context
    
    cursor = conn.cursor()
    
    try:
        # Get doctor info
        cursor.execute('''
            SELECT first_name, last_name, specialization, hospital, experience_years
            FROM doctors WHERE doctor_id = %s
        ''', (doctor_id,))
        
        doc_info = cursor.fetchone()
        if doc_info:
            context['doctor_info'] = {
                'name': f"Dr. {doc_info[0]} {doc_info[1]}",
                'specialization': doc_info[2],
                'hospital': doc_info[3],
                'experience_years': doc_info[4]
            }
        
        # Get statistics for doctor's patients
        cursor.execute('''
            SELECT COUNT(DISTINCT patient_id) as patient_count,
                   COUNT(*) as total_records,
                   DATE(MAX(created_at)) as last_activity
            FROM medical_records WHERE doctor_id = %s
        ''', (doctor_id,))
        
        stats = cursor.fetchone()
        if stats:
            context['statistics'] = {
                'total_patients': stats[0],
                'total_records': stats[1],
                'last_activity': stats[2].strftime('%Y-%m-%d') if stats[2] else 'No activity'
            }
        
        # Get recent records summary
        cursor.execute('''
            SELECT mr.patient_id, p.first_name, p.last_name, mr.visit_date,
                   mr.diagnosis, mr.treatment, p.blood_group, p.date_of_birth
            FROM medical_records mr
            JOIN patients p ON mr.patient_id = p.patient_id
            WHERE mr.doctor_id = %s
            ORDER BY mr.visit_date DESC LIMIT 10
        ''', (doctor_id,))
        
        recent_records = cursor.fetchall()
        for record in recent_records:
            age = (date.today() - record[7]).days // 365 if record[7] else None
            context['recent_activities'].append({
                'patient_id': record[0],
                'patient_name': f"{record[1]} {record[2]}",
                'age': age,
                'blood_group': record[6],
                'visit_date': record[3].strftime('%Y-%m-%d'),
                'diagnosis': record[4],
                'treatment': record[5]
            })
        
        # If specific patients are selected, get detailed info
        if selected_patients:
            for patient_id in selected_patients:
                patient_context = get_patient_context_for_ai(patient_id)
                if patient_context['patient_basic_info']:
                    context['patient_summaries'].append({
                        'patient_id': patient_id,
                        'basic_info': patient_context['patient_basic_info'],
                        'recent_records': patient_context['recent_records'][:5],
                        'allergies': patient_context['allergies'],
                        'health_patterns': patient_context['health_patterns']
                    })
        
    except mysql.connector.Error as e:
        print(f"Error getting doctor context: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return context

def generate_doctor_ai_response(user_message, doctor_id, selected_patients=None):
    """Generate AI response specifically for doctors"""
    if not AI_AVAILABLE:
        return "AI assistant is currently unavailable. Please check your API configuration."
    
    try:
        # Create doctor-focused system prompt
        system_prompt = """You are an advanced AI medical assistant designed specifically for healthcare professionals.

        IMPORTANT GUIDELINES FOR DOCTORS:
        1. Provide clinical insights, differential diagnoses, and treatment recommendations
        2. Analyze patient data patterns and suggest clinical correlations
        3. Offer evidence-based medical information and guidelines
        4. Help with clinical decision-making and care planning
        5. Suggest follow-up tests, referrals, or monitoring when appropriate
        6. Use medical terminology appropriately while being clear
        7. Always emphasize that final clinical decisions rest with the attending physician
        8. Respond in plain text without HTML formatting
        9. Focus on clinical utility and actionable insights
        10. Consider differential diagnoses and clinical reasoning

        """
        
        # Add doctor context
        doctor_context = get_doctor_context_for_ai(doctor_id, selected_patients)
        
        if doctor_context and any(doctor_context.values()):
            context_text = "\nDOCTOR PROFILE AND CONTEXT:\n"
            
            # Doctor info
            doc_info = doctor_context.get('doctor_info', {})
            if doc_info:
                context_text += f"""
                PHYSICIAN PROFILE:
                - Name: {doc_info.get('name', 'Unknown')}
                - Specialization: {doc_info.get('specialization', 'General Practice')}
                - Hospital: {doc_info.get('hospital', 'Not specified')}
                - Experience: {doc_info.get('experience_years', 'Not specified')} years
                """
            
            # Statistics
            stats = doctor_context.get('statistics', {})
            if stats:
                context_text += f"""
                PRACTICE STATISTICS:
                - Total patients managed: {stats.get('total_patients', 0)}
                - Total medical records: {stats.get('total_records', 0)}
                - Last activity: {stats.get('last_activity', 'No activity')}
                """
            
            # Recent activities
            recent = doctor_context.get('recent_activities', [])
            if recent:
                context_text += f"\nRECENT PATIENT ENCOUNTERS ({len(recent)} recent):\n"
                for i, activity in enumerate(recent[:5]):
                    context_text += f"""
                    Patient {i+1}:
                    - ID: {activity['patient_id']} | Name: {activity['patient_name']}
                    - Age: {activity['age']} years | Blood Type: {activity['blood_group']}
                    - Visit Date: {activity['visit_date']}
                    - Diagnosis: {activity['diagnosis'] or 'Not specified'}
                    - Treatment: {activity['treatment'] or 'Not specified'}
                    """
            
            # Selected patient summaries
            patient_summaries = doctor_context.get('patient_summaries', [])
            if patient_summaries:
                context_text += f"\nSELECTED PATIENT DETAILED SUMMARIES:\n"
                for summary in patient_summaries:
                    basic = summary['basic_info']
                    patterns = summary['health_patterns']
                    context_text += f"""
                    PATIENT: {basic.get('name', 'Unknown')} (ID: {summary['patient_id']})
                    - Age: {basic.get('age', 'Unknown')} | Gender: {basic.get('gender', 'Unknown')}
                    - Blood Group: {basic.get('blood_group', 'Unknown')} | BMI: {basic.get('bmi', 'Not calculated')}
                    - Health Patterns: Avg Glucose: {patterns.get('glucose_avg', 'N/A')} mg/dL,
                      Avg BP: {patterns.get('bp_avg', 'N/A')} mmHg, Total Visits: {patterns.get('total_visits', 0)}
                    - Known Allergies: {len(summary['allergies'])} documented
                    - Recent Diagnoses: {', '.join(patterns.get('recent_diagnoses', [])) or 'None'}
                    """
            
            system_prompt += context_text
        
        # Generate response
        full_prompt = system_prompt + f"\nDOCTOR'S QUESTION/REQUEST: {user_message}"
        response = AI_MODEL.generate_content(full_prompt)
        
        # Clean response
        clean_response = re.sub(r'<[^>]+>', '', response.text)
        clean_response = clean_response.replace('**', '')
        clean_response = clean_response.replace('*', '')
        clean_response = clean_response.strip()
        
        return clean_response
        
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {str(e)}"
    
def show_doctor_ai_chat():
    """Display doctor-specific AI chat interface"""
    pycss.load_css()
    
    # Header with toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🌙 Toggle Theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    # Page title
    st.markdown('<div class="main-header"><h1>👾 AI Clinical Assistant</h1><p>Professional medical insights and clinical decision support</p></div>', unsafe_allow_html=True)
    
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.doctor_chat_messages:
            for message_data in st.session_state.doctor_chat_messages:
                if message_data["role"] == "user":
                    if st.session_state.dark_mode:
                        # Dark mode: White background + Black text
                        user_bg = "linear-gradient(135deg, #ffffff, #f0f0f0)"
                        user_text = "#000000"
                    else:
                        # Light mode: Blue background + White text  
                        user_bg = "linear-gradient(135deg, #2196F3, #1976D2)"
                        user_text = "#ffffff"
    
                    st.markdown(f"""
                    <div style="text-align: right; margin: 15px 0;">
                        <div class="user-bubble" style="background: {user_bg}; 
                                    color: {user_text} !important; 
                                    padding: 12px 16px; border-radius: 15px; display: inline-block; max-width: 80%;
                                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
                            <strong style="color: {user_text} !important;">You:</strong> 
                            <span style="color: {user_text} !important;">{message_data["content"]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Doctor AI response - Correct colors for both themes
                    clean_content = message_data["content"].replace('<div>', '').replace('</div>', '').replace('<p>', '').replace('</p>', '')
                    if st.session_state.dark_mode:
                        # Dark mode: Blue background + White text
                        bg_color = "linear-gradient(135deg, #1976D2, #2196F3)"
                        text_color = "#ffffff"
                    else:
                        # Light mode: Green background + Black text
                        bg_color = "linear-gradient(135deg, #4CAF50, #45a049)"
                        text_color = "#000000"
    
                    st.markdown(f"""
                    <div style="text-align: left; margin: 15px 0;">
                        <div class="ai-bubble" style="background: {bg_color}; 
                                    color: {text_color} !important; 
                                    padding: 12px 16px; border-radius: 15px; display: inline-block; max-width: 80%;
                                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
                            <strong style="color: {text_color} !important;">👾 Clinical AI:</strong> 
                            <span style="color: {text_color} !important;">{clean_content}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="info-card" style="text-align: center; padding: 30px;">
                <h3>👋 Hello Doctor! I'm your AI clinical assistant.</h3>
                <p>I can help you with:</p>
                <div style="text-align: left; max-width: 600px; margin: 20px auto;">
                    <p>🔍 Clinical analysis of patient data and trends</p>
                    <p>🧬 Differential diagnosis suggestions</p>
                    <p>💊 Treatment recommendations and guidelines</p>
                    <p>📊 Patient care planning and follow-up suggestions</p>
                    <p>🎯 Evidence-based medical insights</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("doctor_ai_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("", key="doctor_ai_chat_input", 
                                     placeholder="Ask about patient analysis, clinical decisions, or medical insights...", 
                                     label_visibility="collapsed")
        with col2:
            send_button = st.form_submit_button("Send 🚀", use_container_width=True)
        
        if send_button and user_input:
            st.session_state.doctor_chat_messages.append({"role": "user", "content": user_input})
            
            # Generate response with doctor context
            with st.spinner("🔬 Analyzing clinical data..."):
                ai_response = generate_doctor_ai_response(
                    user_input, 
                    st.session_state.user['id'], 
                    st.session_state.selected_patients if st.session_state.selected_patients else None
                )
            
            st.session_state.doctor_chat_messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
    
    # Controls
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.doctor_chat_messages = []
            st.rerun()
    with col2:
        if st.session_state.selected_patients:
            st.info(f"📋 {len(st.session_state.selected_patients)} patient(s) selected for AI analysis")

# Patient Dashboard 
def show_patient_dashboard():
    pycss.load_css()
    
    if st.session_state.show_ai_chat:
        show_ai_chat_interface()
        return
    
    if st.session_state.success_message:
        st.markdown(f'<div class="success-message">{st.session_state.success_message}</div>', 
                   unsafe_allow_html=True)
        st.session_state.success_message = None

    if st.session_state.show_health_streak_toast:
        streak = st.session_state.show_health_streak_toast
        st.toast(f"🔥 Health Streak: {streak} days! Keep it up!", icon="🎉")
        st.session_state.show_health_streak_toast = None
    
    with st.sidebar:
        st.title("Patient Menu")

        st.markdown('<div class="toggle-button">', unsafe_allow_html=True)
        if st.button("🌓 Toggle Theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown('<div class="toggle-button">', unsafe_allow_html=True)
        st.markdown("---")
        
        # pages in p. dash
    patient_choice = st.sidebar.radio("Navigate to:", [
        "🏠 Dashboard", "📋 View Records", "📊 Vital Trends", 
        "🖼️ Medical Images", "📁 My Files", "⚠️ Allergies", 
        "🔍 Find Doctors", "👾 AI Assistant", "ℹ️ About", "⚙️ Settings"
    ], key="patient_nav_radio")
        
    with st.sidebar:
        st.markdown("---")
        
        st.markdown('<div class="logout-button">', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, key="patient_logout"):
            st.session_state.user = None
            st.session_state.auth_mode = 'Login'
            st.session_state.success_message = "You have been logged out successfully."
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ai title bug (fixed.....huhh)
    if not st.session_state.show_ai_chat and patient_choice != "👾 AI Assistant":
        st.markdown(
            f'<div class="main-header"><h1>Hello, {st.session_state.user["name"]}!</h1>'
            f'<p>Patient ID: <strong>{st.session_state.user["id"]}</strong></p></div>',
            unsafe_allow_html=True
        )

    if patient_choice == "🏠 Dashboard":
        streak = st.session_state.user.get('health_streak', 0)
        if streak > 0:
            st.markdown(f'<div class="success-message">🔥 Your Health Streak: {streak} days! Keep logging in daily to maintain your streak!</div>', 
                       unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        
        # QR code details
        with col1:
            st.markdown("### Your QR Code")
            qr_data_b64 = generate_qr_code(st.session_state.user['qr_token'])
            st.markdown(f'<img src="data:image/png;base64,{qr_data_b64}" alt="QR Code" style="width:150px; height:150px; border: 3px solid {"#ffffff" if st.session_state.dark_mode else "#4CAF50"}; border-radius: 5px;">', unsafe_allow_html=True)
            st.caption("Scan for Emergency Access")
            
            # Download QR
            qr_download = qrhtml.qr_html(st.session_state.user, qr_data_b64)
            st.download_button(
                label="📥 Download QR Code",
                data=qr_download,
                file_name=f"emergency_qr_{st.session_state.user['id']}.html",
                mime="text/html",
                use_container_width=True
            )
            
            st.markdown(f'<div class="metric-card"><h4>📞 Phone:</h4> <p>{st.session_state.user["phone"] if st.session_state.user["phone"] else "Not provided"}</p></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><h4>🩸 Blood Group:</h4> <p style="color:{"red" if st.session_state.dark_mode else "#d32f2f"}; font-weight:bold;">{st.session_state.user["blood_group"] if st.session_state.user["blood_group"] else "Not provided"}</p></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Your Medical Overview")
            st.markdown(f"Current Date: **{date.today().strftime('%Y-%m-%d')}**")
            
            recent_records = patient_records(st.session_state.user['id'], start_date=date.today() - timedelta(days=30))
            st.markdown(f'<div class="metric-card"><h4>📅 Recent Visits (30 days):</h4> <p style="font-size: 1.5em; font-weight: bold;">{len(recent_records)}</p></div>', unsafe_allow_html=True)
            
            allergies = patient_allergies(st.session_state.user['id'])
            allergy_count = len(allergies)
            allergy_color = "red" if allergy_count > 0 else "green"
            st.markdown(f'<div class="metric-card"><h4>⚠️ Known Allergies:</h4> <p style="color: {allergy_color}; font-size: 1.5em; font-weight: bold;">{allergy_count}</p></div>', unsafe_allow_html=True)
            
            files = patient_files(st.session_state.user['id'])
            st.markdown(f'<div class="metric-card"><h4>📁 Medical Files:</h4> <p style="font-size: 1.5em; font-weight: bold;">{len(files)}</p></div>', unsafe_allow_html=True)
    
    elif patient_choice == "👾 AI Assistant":
        if AI_AVAILABLE:
            st.session_state.show_ai_chat = True 
            show_ai_chat_interface() 
            return  
        else:
            st.error("👾 AI Assistant is currently unavailable. Please check the API configuration.")
            st.info("Contact your system administrator to enable AI features.")
    
    # Replace the existing "View Records" section in show_patient_dashboard() with this enhanced version
    elif patient_choice == "📋 View Records":
        st.markdown("### Your Medical Records")

        with st.expander("🔍 Filter Records"):
            filter_col1, filter_col2, filter_col3 = st.columns(3)

            with filter_col1:
                start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365), key="p_rec_start_date")
            with filter_col2:
                end_date = st.date_input("End Date", value=date.today(), key="p_rec_end_date")
            with filter_col3:
                specialty_filter = st.selectbox("Filter by Specialty",["All Specialties", "Cardiology", "Neurology", "Orthopedics", "Dermatology","General Practice", "Pediatrics", "Gynecology", "Other"], key="specialty_filter")
        
        records = patient_records(st.session_state.user['id'], start_date, end_date)

        if records:
        # Download records button
            records_html = create_downloadable_records(records, st.session_state.user['name'])
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                label="📥 Download All Records",
                data=records_html,
                file_name=f"medical_records_{st.session_state.user['id']}_{date.today().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
            
            st.markdown(f"**Total Records Found:** {len(records)}")

            for i, record in enumerate(records):
                doctor_name = f"Dr. {record[13]} {record[14]}" if record[13] and record[14] else "Unknown Doctor"
                specialization = record[15] if record[15] else "General Practice"

                # Filter by specialty if selected
                if specialty_filter != "All Specialties" and specialty_filter.lower() not in specialization.lower():
                    continue

                with st.expander(f"🏥 Visit #{len(records)-i} - {record[3].strftime('%B %d, %Y')} - {doctor_name}"):
                    created_time = 'Unknown'
                    if record[12] is not None:
                        try:
                            created_time = record[12].strftime('%Y-%m-%d %H:%M')
                        except (AttributeError, ValueError):
                            created_time = str(record[12])

                    st.markdown(f"""
                    <div class="medical-record-card">
                    <h4 style="margin: 0; color: {'#2196F3' if st.session_state.dark_mode else '#2c3e50'};">📅 {record[3].strftime                    ('%A, %B %d, %Y')}</h4>
                    <p style="margin: 5px 0; color: {'#1976D2' if st.session_state.dark_mode else '#666666'};">
                        👨‍⚕️ <strong>{doctor_name}</strong> | 🏥 <strong>{specialization}</strong>
                    </p>
                    <p style="margin: 0; color: {'#1976D2' if st.session_state.dark_mode else '#666666'};">
                        🕐 Record ID: {record[0]} | Created: {created_time}
                    </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        st.markdown("### 📋 Clinical Information")
                        if record[4]:  # Diagnosis
                            st.markdown(f"""
                            <div class="clinical-info-card" style="border-left: 4px solid #ff6b6b;">
                                <h5 style="margin: 0; color: #ff6b6b;">🔍 Primary Diagnosis</h5>
                                <p style="margin: 5px 0; color: {'#2196F3' if st.session_state.dark_mode else '#2c3e50'};">{record[4]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if record[5]:  # Treatment
                                st.markdown(f"""
                            <div class="clinical-info-card" style="border-left: 4px solid #ff6b6b;">
                                <h5 style="margin: 0; color: #ff6b6b;">💊 Treatment Plan</h5>
                                <p style="margin: 5px 0; color: {'#2196F3' if st.session_state.dark_mode else '#2c3e50'};">{record[5]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        if record[6]:  # Prescription
                                st.markdown(f"""
                            <div class="clinical-info-card" style="border-left: 4px solid #ff6b6b;">
                                <h5 style="margin: 0; color: #ff6b6b;">💉 Prescription</h5>
                                <p style="margin: 5px 0; color: {'#2196F3' if st.session_state.dark_mode else '#2c3e50'};">{record[6]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                        if record[7]:  # Notes
                                st.markdown(f"""
                            <div class="clinical-info-card" style="border-left: 4px solid #ff6b6b;">
                                <h5 style="margin: 0; color: #ff6b6b;">📝 Doctor's Notes</h5>
                                <p style="margin: 5px 0; color: {'#2196F3' if st.session_state.dark_mode else '#2c3e50'};">{record[7]}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    with col2:
                        st.markdown("### 📊 Vital Signs")

                        vital_data = []
                        if record[8]:  # Glucose
                            glucose_status = "Normal" if 70 <= record[8] <= 140 else "Abnormal"
                            vital_data.append(("🩸 Blood Glucose", f"{record[8]} mg/dL", glucose_status))

                        if record[9] and record[10]:  # Blood Pressure
                            bp_status = "Normal" if record[9] < 140 and record[10] < 90 else "High"
                            vital_data.append(("💗 Blood Pressure", f"{record[9]}/{record[10]} mmHg", bp_status))
                    
                        if record[11]:  # Heart Rate
                            hr_status = "Normal" if 60 <= record[11] <= 100 else "Abnormal"
                            vital_data.append(("💓 Heart Rate", f"{record[11]} bpm", hr_status))
                    
                        if record[12]:  # Temperature
                            temp_status = "Normal" if 36.1 <= record[12] <= 37.2 else "Abnormal"
                            vital_data.append(("🌡️ Temperature", f"{record[12]}°C", temp_status))

                        if vital_data:
                            for icon_name, value, status in vital_data:
                                status_color = "#4CAF50" if status == "Normal" else "#ff6b6b"
                                st.markdown(f"""
                                <div style="background: {"#ffffff" if st.session_state.dark_mode else '#f8f9fa'}; 
                                           padding: 10px; border-radius: 6px; margin: 6px 0; 
                                           border: 1px solid {status_color};">
                                    <strong>{icon_name}</strong><br>
                                    <span style="font-size: 1.1em; color: {status_color};">{value}</span>
                                    <small style="color: {status_color}; float: right;">({status})</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No vital signs recorded for this visit")

                    st.markdown("---")
                    col_actions1, col_actions2, col_actions3 = st.columns(3)
                    with col_actions1:
                        if st.button(f"📋 View Details", key=f"details_{record[0]}"):
                            st.info("Detailed view would open in a modal or new page")
                    with col_actions2:
                        if st.button(f"📧 Email Record", key=f"email_{record[0]}"):
                            st.info("Email functionality would be implemented")
                    with col_actions3:
                        if st.button(f"📄 Print", key=f"print_{record[0]}"):
                            st.info("Print functionality would be implemented")
        else:
            st.info("No medical records found for the selected date range and filters.")
            st.markdown("### 📝 What you can do:")
            st.markdown("- Contact your doctor to add medical records")
            st.markdown("- Schedule an appointment through the 'Find Doctors' section")
            st.markdown("- Upload any personal health documents")
                                               
    elif patient_choice == "📊 Vital Trends":
        st.markdown("### Your Vital Signs Trends")
        
        vital_data = vital_trends(st.session_state.user['id'])
        
        if vital_data:
            import pandas as pd
            df = pd.DataFrame(vital_data, columns=['Date', 'Glucose', 'Systolic', 'Diastolic', 'Heart Rate', 'Temperature'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Blood Pressure Chart
            if df['Systolic'].notna().any() or df['Diastolic'].notna().any():
                fig_bp = go.Figure()
                fig_bp.add_trace(go.Scatter(x=df['Date'], y=df['Systolic'], mode='lines+markers', name='Systolic BP', line=dict(color='red')))
                fig_bp.add_trace(go.Scatter(x=df['Date'], y=df['Diastolic'], mode='lines+markers', name='Diastolic BP', line=dict(color='blue')))
                fig_bp.update_layout(title='Blood Pressure Trends', xaxis_title='Date', yaxis_title='mmHg')
                st.plotly_chart(fig_bp, use_container_width=True)
            
            # Glucose Chart
            if df['Glucose'].notna().any():
                fig_glucose = px.line(df, x='Date', y='Glucose', title='Blood Glucose Trends', markers=True)
                fig_glucose.update_layout(yaxis_title='mg/dL')
                st.plotly_chart(fig_glucose, use_container_width=True)
            
            # Heart Rate Chart
            if df['Heart Rate'].notna().any():
                fig_hr = px.line(df, x='Date', y='Heart Rate', title='Heart Rate Trends', markers=True)
                fig_hr.update_layout(yaxis_title='bpm')
                st.plotly_chart(fig_hr, use_container_width=True)
            
            # Temperature Chart
            if df['Temperature'].notna().any():
                fig_temp = px.line(df, x='Date', y='Temperature', title='Temperature Trends', markers=True)
                fig_temp.update_layout(yaxis_title='°C')
                st.plotly_chart(fig_temp, use_container_width=True)
        else:
            st.info("No vital signs data available to display trends.")

    elif patient_choice == "🖼️ Medical Images":
        st.markdown("### Your Medical Images")
        
        images = patient_images(st.session_state.user['id'])
        
        if images:
            for img in images:
                with st.expander(f"📷 {img[1]} - {img[5].strftime('%Y-%m-%d')}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        try:
                            image = Image.open(io.BytesIO(img[2]))
                            st.image(image, caption=img[1], use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not display image: {e}")
                    with col2:
                        st.markdown(f"**Type:** {img[3]}")
                        st.markdown(f"**Description:** {img[4] if img[4] else 'No description'}")
                        st.markdown(f"**Upload Date:** {img[5].strftime('%Y-%m-%d')}")
                        
                        # Download button for image
                        st.download_button(
                            label="📥 Download Image",
                            data=img[2],
                            file_name=img[1],
                            mime=img[3]
                        )
        else:
            st.info("No medical images uploaded yet.")

    elif patient_choice == "📁 My Files":
        st.markdown("### Your Medical Files")
    
        files = patient_files(st.session_state.user['id'])
    
        if files:
            for i, file in enumerate(files):
                with st.expander(f"📁 {file[1]} - {file[5].strftime('%Y-%m-%d')}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Category:** {file[3]}")
                        st.markdown(f"**Description:** {file[4] if file[4] else 'No description'}")
                        st.markdown(f"**Uploaded by:** Dr. {file[6]} {file[7]}" if file[6] and file[7] else "**Uploaded by:** System")
                        st.markdown(f"**Upload Date:** {file[5].strftime('%Y-%m-%d')}")
                    with col2:
                        st.download_button(
                            label="📥 Download File",
                            data=file[8],
                            file_name=file[1],
                            mime=file[2],
                            use_container_width=True,
                            key=f"download_{file[1]}_{i}"
                        )
        else:
            st.info("No medical files uploaded yet.")


    elif patient_choice == "⚠️ Allergies":
        st.markdown("### Your Allergies")
        
        allergies = patient_allergies(st.session_state.user['id'])
        
        if allergies:
            for allergy in allergies:
                severity_color = {"Mild": "orange", "Moderate": "red", "Severe": "darkred"}
                st.markdown(f'<div class="patient-card" style="border-left-color: {severity_color.get(allergy[1], "gray")}"><h4>{allergy[0]}</h4><p><strong>Severity:</strong> <span style="color: {severity_color.get(allergy[1], "gray")}">{allergy[1]}</span></p></div>', unsafe_allow_html=True)
        else:
            st.info("✅ No allergies recorded.")
            st.markdown("Contact your doctor to update your allergy information if needed.")

    elif patient_choice == "🔍 Find Doctors":
        st.markdown("### Find Healthcare Providers")
    
        # Enhanced search and filter section
        with st.expander("🔍 Search & Filter Options", expanded=True):
            col1, col2 = st.columns(2)
        
            with col1:
                search_term = st.text_input("🔍 Search by name, email, or hospital:", key="patient_search_doctors")
            
                specialty_options = ["All Specialties", "Cardiology", "Neurology", "Orthopedics", 
                                "Dermatology", "General Practice", "Pediatrics", "Gynecology", 
                                "Psychiatry", "Radiology", "Emergency Medicine", "Surgery", "Other"]
                specialty_filter = st.selectbox("🏥 Filter by Specialty:", specialty_options, key="specialty_filter")
        
            with col2:
                experience_options = ["Any Experience", "0-5 years", "5-10 years", "10-20 years", "20+ years"]
                experience_filter = st.selectbox("📅 Years of Experience:", experience_options,     key="experience_filter")
            
                location_filter = st.text_input("🌍 Filter by City/Hospital:", key="location_filter")
        
            # Search button
            if st.button("🔍 Search Doctors", use_container_width=True):
                st.session_state.doctor_search_results = search_doctors_advanced(
                    search_term, specialty_filter, experience_filter, location_filter
                )
    
        # Display results
        if hasattr(st.session_state, 'doctor_search_results'):
            doctors = st.session_state.doctor_search_results
        
            if doctors:
                st.markdown(f"### 👨‍⚕️ Found {len(doctors)} Doctor(s)")
            
                # Sort options
                sort_by = st.selectbox("Sort by:", ["Experience (High to Low)", "Name (A-Z)", "Recently Joined"],key="doctor_sort")
            
                if sort_by == "Experience (High to Low)":
                    doctors = sorted(doctors, key=lambda x: x[7] if x[7] else 0, reverse=True)
                elif sort_by == "Name (A-Z)":
                    doctors = sorted(doctors, key=lambda x: f"{x[1]} {x[2]}")
                elif sort_by == "Recently Joined":
                    doctors = sorted(doctors, key=lambda x: x[9], reverse=True)
            
                for doctor in doctors:
                    with st.expander(f"👨‍⚕️ Dr. {doctor[1]} {doctor[2]} - {doctor[5] if doctor[5] else 'General     Practice'}", expanded=False):
                        col1, col2, col3 = st.columns([2, 2, 1])
                    
                        with col1:
                            st.markdown(f"""
                            **👨‍⚕️ Doctor Information:**
                            - **Doctor ID:** {doctor[0]}
                            - **Email:** {doctor[3]}
                            - **Phone:** {doctor[4] if doctor[4] else 'Not provided'}
                            - **License:** {doctor[8] if doctor[8] else 'Not provided'}
                            """)
                    
                        with col2:
                            experience_years = doctor[7] if doctor[7] else 0
                            experience_level = "👶 Junior" if experience_years < 5 else "👨‍⚕️ Experienced" if experience_years < 15 else "🎖️ Senior"
                        
                            st.markdown(f"""
                            **🏥 Professional Details:**
                            - **Specialization:** {doctor[5] if doctor[5] else 'General Practice'}
                            - **Hospital/Clinic:** {doctor[6] if doctor[6] else 'Not specified'}
                            - **Experience:** {experience_years} years {experience_level}
                            - **Member Since:** {doctor[9].strftime('%Y') if doctor[9] else 'Unknown'}
                            """)
                    
                        with col3:
                            st.markdown("**Actions:**")
                            if st.button(f"📋 View Profile", key=f"profile_{doctor[0]}", use_container_width=True):
                                st.info("Detailed profile view would be implemented here")
                        
                            if st.button(f"⭐ Reviews", key=f"reviews_{doctor[0]}", use_container_width=True):
                                st.info("Doctor reviews would be displayed here")
                    
                        # Rating display..
                        st.markdown("---")
                        col_rating1, col_rating2, col_rating3 = st.columns(3)
                        with col_rating1:
                            st.markdown("⭐ **Rating:** 4.2/5 (24 reviews)")
                        with col_rating2:
                            st.markdown("🧑‍⚕️ Verified Patients: 20+")
                        with col_rating3:
                            st.markdown("💬 Feedback: Positive")
            else:
                st.info("🔍 No doctors found matching your search criteria.")
                st.markdown("### 💡 Try these suggestions:")
                st.markdown("- Broaden your search terms")
                st.markdown("- Try different specialty filters")  
                st.markdown("- Search by hospital or location")
    
        # specialty buttons
        st.markdown("### 🔥 Popular Specialties")
        col1, col2, col3, col4 = st.columns(4)
    
        specialties = [
            ("Cardiology", "❤️"),
            ("Neurology", "🧠"), 
            ("Orthopedics", "🦴"),
            ("General Practice", "👨‍⚕️")
        ]

        for i, (spec, icon) in enumerate(specialties):
            with [col1, col2, col3, col4][i]:
                if st.button(f"{icon} {spec}", key=f"quick_spec_{spec}", use_container_width=True):
                    st.session_state.doctor_search_results = search_doctors_advanced("", spec, "", "")
                    st.rerun()

    elif patient_choice == "ℹ️ About":
        st.markdown("### About E-Medical Record System")
        st.markdown(f'''
        <div class="info-card">
        <h4>🏥 Your Digital Health Companion</h4>
        <p>This secure medical records system helps you manage your health information digitally.</p>
        
        <h4>✨ Key Features:</h4>
        <ul>
        <li>📱 <strong>Emergency QR Code:</strong> Instant access to critical medical info</li>
        <li>📊 <strong>Vital Trends:</strong> Visualize your health progress over time</li>
        <li>🔒 <strong>Secure Storage:</strong> Your medical files and records</li>
        <li>🏆 <strong>Health Streak:</strong> Stay motivated with daily login rewards</li>
        <li>🔍 <strong>Doctor Search:</strong> Find healthcare providers easily</li>
        </ul>
        
        <h4>🛡️ Privacy & Security:</h4>
        <p>Your medical information is encrypted and secure. Only authorized healthcare providers can access your records with proper authentication.</p>
        </div>
        ''', unsafe_allow_html=True)

    elif patient_choice == "⚙️ Settings":
        st.markdown("### Account Settings")
        
        with st.expander("🎨 Display Settings"):
            current_theme = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
            st.markdown(f"**Current Theme:** {current_theme}")
            if st.button("🌓 Switch Theme", use_container_width=True):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        with st.expander("👤 Account Information"):
            st.markdown(f"**Name:** {st.session_state.user['name']}")
            st.markdown(f"**Patient ID:** {st.session_state.user['id']}")
            st.markdown(f"**Email:** {st.session_state.user['email']}")
            st.markdown(f"**Health Streak:** {st.session_state.user.get('health_streak', 0)} days")
        
        with st.expander("🔒 Security"):
            st.markdown("**Password Management**")
            st.info("To change your password, please contact your healthcare provider or system administrator.")
            
            st.markdown("**QR Code Security**")
            st.warning("⚠️ Your QR code contains emergency medical information. Keep it secure and only share with trusted individuals.")
    
# Doctor Dashboard
def show_doctor_dashboard():
    pycss.load_css()
    
    if st.session_state.success_message:
        st.markdown(f'<div class="success-message">{st.session_state.success_message}</div>', 
                   unsafe_allow_html=True)
        st.session_state.success_message = None
    
    with st.sidebar:

        st.title("Doctor Menu")
        st.markdown('<div class="toggle-button">', unsafe_allow_html=True)
        if st.button("🌓 Toggle Theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown('<div class="toggle-button">', unsafe_allow_html=True)
        st.markdown("---")
        
        doctor_options = [
        "🏠 Dashboard", "🔍 Find Patients", "📝 Add Record", 
        "📁 Upload Files", "🖼️ Upload Images", "📊 Patient Analytics", 
        "👾 AI Assistant","📋 Batch Upload", "ℹ️ About", "⚙️ Settings"
        ]
        doctor_choice = st.radio("Navigate to:", doctor_options, key="doctor_nav_radio")

        # ai title bug (fixed.....huhh)
    if not st.session_state.doctor_chat_messages and doctor_choice != "👾 AI Assistant":
        st.markdown(f'<div class="main-header"><h1>Welcome, {st.session_state.user["name"]}!</h1><p>Doctor ID: <strong>{st.session_state.user["id"]}</strong></p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("---")
        
        st.markdown('<div class="logout-button">', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, key="patient_logout"):
            st.session_state.user = None
            st.session_state.auth_mode = 'Login'
            st.session_state.success_message = "You have been logged out successfully."
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    if doctor_choice == "🏠 Dashboard":
        st.markdown("### Doctor Dashboard")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f'<div class="metric-card"><h4>👨‍⚕️ Specialization:</h4><p>{st.session_state.user.get("specialization", "General Practice")}</p></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><h4>🏥 Hospital:</h4><p>{st.session_state.user.get("hospital", "Not specified")}</p></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Quick Actions")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔍 Find Patient", use_container_width=True):
                    st.session_state.current_page = 'Find Patients'
                    st.rerun()
                if st.button("📁 Upload Files", use_container_width=True):
                    st.session_state.current_page = 'Upload Files'
                    st.rerun()
            with col_b:
                if st.button("📝 Add Record", use_container_width=True):
                    st.session_state.current_page = 'Add Record'
                    st.rerun()
                if st.button("📊 Analytics", use_container_width=True):
                    st.session_state.current_page = 'Patient Analytics'
                    st.rerun()
        
        st.markdown("### Today's Overview")
        today = date.today()
        st.markdown(f"Current Date: **{today.strftime('%A, %B %d, %Y')}**")
        
        st.info("📊 Patient activity and recent records will be displayed here in a production environment.")

    elif doctor_choice == "🔍 Find Patients":
        st.markdown("### Find & Manage Patients")
    
        # Enhanced search section
        with st.expander("🔍 Patient Search", expanded=True):
            col1, col2 = st.columns(2)
        
            with col1:
                search_term = st.text_input("Search by name, ID, email, or phone:", key="doctor_search_patients")
        
            with col2:
                blood_group_filter = st.selectbox(
                    "Filter by Blood Group:",
                    ["All", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                    key="blood_group_filter"
                )
    
        if search_term or blood_group_filter != "All":
            patients = search_patients_advanced_doctor(search_term, blood_group_filter)
        
            if patients:
                st.markdown(f"### Found {len(patients)} Patient(s)")
            
                selected_patients = []
            
                for patient in patients:
                    with st.expander(f"👤 {patient[1]} {patient[2]} (ID: {patient[0]})", expanded=False):
                        # Quick patient overview
                        col_overview1, col_overview2, col_overview3 = st.columns([2, 2, 1])
                    
                        with col_overview1:
                            st.markdown(f"""
                            **Basic Information:**
                            - Patient ID: {patient[0]}
                            - Email: {patient[3]}
                            - Phone: {patient[4] if patient[4] else 'Not provided'}
                            - Blood Group: {patient[5] if patient[5] else 'Not specified'}
                            """)
                    
                        with col_overview2:
                            # Get recent records count and last visit
                            recent_records = patient_records(patient[0])
                            last_visit = recent_records[0][3].strftime('%Y-%m-%d') if recent_records else 'No visits'
                        
                            st.markdown(f"""
                            **Medical Summary:**
                            - Total Records: {len(recent_records)}
                            - Last Visit: {last_visit}
                            - Allergies: {len(patient_allergies(patient[0]))} known
                            """)
                    
                        with col_overview3:
                            if st.checkbox(f"Select", key=f"select_patient_{patient[0]}"):
                                selected_patients.append(patient[0])
                        
                            if st.button(f"📋 Full History", key=f"history_{patient[0]}", use_container_width=True):
                                st.session_state.selected_patient_for_history = patient[0]
                                st.rerun()
                    
                        # Quick actions row
                        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
                    
                        with col_action1:
                            if st.button(f"📝 Add Record", key=f"add_record_{patient[0]}", use_container_width=True):
                                if patient[0] not in st.session_state.selected_patients:
                                    st.session_state.selected_patients = [patient[0]]
                                st.info("Patient selected for record creation")
                    
                        with col_action2:
                            if st.button(f"📁 Upload File", key=f"upload_file_{patient[0]}", use_container_width=True):
                                if patient[0] not in st.session_state.selected_patients:
                                    st.session_state.selected_patients = [patient[0]]
                                st.info("Patient selected for file upload")
                    
                        with col_action3:
                            files = patient_files(patient[0])
                            if st.button(f"📄 Files ({len(files)})", key=f"view_files_{patient[0]}", use_container_width=True):
                                if files:
                                    for file in files[:3]:  # Show first 3 files
                                        st.markdown(f"- {file[1]} ({file[3]})")
                                    if len(files) > 3:
                                        st.markdown(f"... and {len(files)-3} more files")
                                else:
                                    st.info("No files uploaded")
                    
                        with col_action4:
                            images = patient_images(patient[0])
                            if st.button(f"🖼️ Images ({len(images)})", key=f"view_images_{patient[0]}", use_container_width=True)    :
                                if images:
                                    st.markdown(f"Recent images: {', '.join([img[1] for img in images[:2]])}")
                                else:
                                    st.info("No images uploaded")
            
                # Store selected patients
                if selected_patients:
                    st.session_state.selected_patients = selected_patients
                    st.success(f"✅ Selected {len(selected_patients)} patient(s) for further actions.")
        
            else:
                st.info("No patients found matching your search criteria.")
    
        # Show detailed patient history if selected
        if hasattr(st.session_state, 'selected_patient_for_history'):
            show_detailed_patient_history(st.session_state.selected_patient_for_history)
    
    elif doctor_choice == "👾 AI Assistant":
        if AI_AVAILABLE:
            st.session_state.show_ai_chat = True 
            show_doctor_ai_chat()
            return 
        else:
            st.error("👾 AI Assistant is currently unavailable. Please check the API configuration.")
            st.info("Contact your system administrator to enable AI features.")

    elif doctor_choice == "📝 Add Record":
        st.markdown("### Add Medical Record")
        
        if st.session_state.selected_patients:
            selected_patient_id = st.selectbox(
                "Select Patient:", 
                st.session_state.selected_patients,
                format_func=lambda x: x
            )
        else:
            selected_patient_id = st.text_input("Enter Patient ID:", key="add_record_patient_id")
        
        if selected_patient_id:
            with st.form("add_medical_record_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    visit_date = st.date_input("Visit Date", value=date.today(), key="record_visit_date")
                    diagnosis = st.text_area("Diagnosis", key="record_diagnosis")
                    treatment = st.text_area("Treatment Plan", key="record_treatment")
                    prescription = st.text_area("Prescription", key="record_prescription")
                
                with col2:
                    notes = st.text_area("Additional Notes", key="record_notes")
                    
                    st.markdown("**Vital Signs (Optional):**")
                    glucose = st.number_input("Blood Glucose (mg/dL)", min_value=0.0, value=0.0, format="%.2f", key="record_glucose")
                    
                    col_bp1, col_bp2 = st.columns(2)
                    with col_bp1:
                        bp_sys = st.number_input("Systolic BP", min_value=0, value=0, key="record_bp_sys")
                    with col_bp2:
                        bp_dia = st.number_input("Diastolic BP", min_value=0, value=0, key="record_bp_dia")
                    
                    heart_rate = st.number_input("Heart Rate (bpm)", min_value=0, value=0, key="record_hr")
                    temperature = st.number_input("Temperature (°C)", min_value=0.0, value=0.0, format="%.1f", key="record_temp")
                
                submitted = st.form_submit_button("💾 Add Medical Record", use_container_width=True)
                
                if submitted:
                    record_data = {
                        'patient_id': selected_patient_id,
                        'doctor_id': st.session_state.user['id'],
                        'visit_date': visit_date,
                        'diagnosis': diagnosis if diagnosis else None,
                        'treatment': treatment if treatment else None,
                        'prescription': prescription if prescription else None,
                        'notes': notes if notes else None,
                        'glucose_level': glucose if glucose > 0 else None,
                        'blood_pressure_systolic': bp_sys if bp_sys > 0 else None,
                        'blood_pressure_diastolic': bp_dia if bp_dia > 0 else None,
                        'heart_rate': heart_rate if heart_rate > 0 else None,
                        'temperature': temperature if temperature > 0 else None
                    }
                    
                    if add_medical_record(record_data):
                        st.session_state.success_message = "✅ Medical record added successfully!"
                        st.rerun()
                    else:
                        st.error("❌ Failed to add medical record.")

    elif doctor_choice == "📁 Upload Files":
        st.markdown("### Upload Medical Files")
        
        if st.session_state.selected_patients:
            selected_patient_id = st.selectbox(
                "Select Patient:", 
                st.session_state.selected_patients,
                format_func=lambda x: x,
                key="upload_files_patient_select"
            )
        else:
            selected_patient_id = st.text_input("Enter Patient ID:", key="upload_files_patient_id")
        
        if selected_patient_id:
            with st.form("upload_files_form"):
                uploaded_files = st.file_uploader(
                    "Choose medical files", 
                    accept_multiple_files=True,
                    type=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt']
                )
                
                category = st.selectbox(
                    "File Category", 
                    ['Lab Report', 'Medical Report', 'Prescription', 'Insurance', 'Other'],
                    key="file_category"
                )
                
                description = st.text_area("File Description", key="file_description")
                
                submitted = st.form_submit_button("📤 Upload Files", use_container_width=True)
                
                if submitted and uploaded_files:
                    success_count = 0
                    for file in uploaded_files:
                        if add_medical_file(selected_patient_id, st.session_state.user['id'], file, category, description):
                            success_count += 1
                    
                    if success_count == len(uploaded_files):
                        st.session_state.success_message = f"✅ Successfully uploaded {success_count} file(s)!"
                        st.rerun()
                    else:
                        st.error(f"❌ Uploaded {success_count} out of {len(uploaded_files)} files.")

    elif doctor_choice == "🖼️ Upload Images":
        st.markdown("### Upload Medical Images")
        
        if st.session_state.selected_patients:
            selected_patient_id = st.selectbox(
                "Select Patient:", 
                st.session_state.selected_patients,
                format_func=lambda x: x,
                key="upload_images_patient_select"
            )
        else:
            selected_patient_id = st.text_input("Enter Patient ID:", key="upload_images_patient_id")
        
        if selected_patient_id:
            with st.form("upload_images_form"):
                uploaded_images = st.file_uploader(
                    "Choose medical images", 
                    accept_multiple_files=True,
                    type=['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff']
                )
                
                image_type = st.selectbox(
                    "Image Type", 
                    ['X-Ray', 'MRI', 'CT Scan', 'Ultrasound', 'Lab Result', 'Clinical Photo', 'Other'],
                    key="image_type"
                )
                
                description = st.text_area("Image Description", key="image_description")
                
                submitted = st.form_submit_button("🖼️ Upload Images", use_container_width=True)
                
                if submitted and uploaded_images:
                    success_count = 0
                    for image in uploaded_images:
                        if add_medical_image(selected_patient_id, st.session_state.user['id'], image, image_type, description):
                            success_count += 1
                    
                    if success_count == len(uploaded_images):
                        st.session_state.success_message = f"✅ Successfully uploaded {success_count} image(s)!"
                        st.rerun()
                    else:
                        st.error(f"❌ Uploaded {success_count} out of {len(uploaded_images)} images.")
        
    
    elif doctor_choice == "📋 Batch Upload":
        st.markdown("### 📋 Batch Upload Medical Records")
    
        # Template download
        st.markdown("#### Step 1: Download Template")
        st.info("📥 Download the template file, fill it with patient data, and upload it back for batch processing.")
    
        col1, col2, col3 = st.columns([1, 1, 1])
    
        with col1:
            # CSV download
            csv_template = generate_template_csv()
            st.download_button(
                label="📥 Download CSV Template",
                data=csv_template,
                file_name="medical_records_template.csv",
                mime="text/csv",
                use_container_width=True
            )
    
        with col2:
            st.info("💡 CSV format is recommended for compatibility")
    
        with col3:
            if st.button("📖 View Instructions", use_container_width=True):
                st.session_state.show_batch_instructions = not st.session_state.get('show_batch_instructions', False)
    
        # Instructions section
        if st.session_state.get('show_batch_instructions', False):
            with st.expander("📖 Template Instructions", expanded=True):
                st.markdown("""
                **Required Columns:**
                - `patient_id`: Must be exact Patient ID (e.g., PAT12345678)
                - `visit_date`: Date in YYYY-MM-DD format
            
                **Optional Columns:**
                - `diagnosis`: Primary diagnosis or condition
                - `treatment`: Treatment plan description
                - `prescription`: Medications prescribed
                - `notes`: Additional clinical notes
                - `glucose_level`: Blood glucose in mg/dL
                - `blood_pressure_systolic`: Systolic BP in mmHg
                - `blood_pressure_diastolic`: Diastolic BP in mmHg
                - `heart_rate`: Heart rate in bpm
                - `temperature`: Body temperature in °C
            
                **Important Notes:**
                ⚠️ Patient IDs must exist in the system
                ⚠️ Empty rows will be skipped
                ⚠️ Invalid data will be reported but won't stop the process
                """)
    
        st.markdown("---")
    
        # File upload section
        st.markdown("#### Step 2: Upload Filled Template")
    
        uploaded_template = st.file_uploader(
            "Choose your filled template file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload CSV or Excel file with medical records data",
            key="batch_upload_template"
        )
    
        if uploaded_template:
            st.success(f"✅ File uploaded: {uploaded_template.name}")
        
            # Preview and validation section
            st.markdown("#### Step 3: Preview and Validate")
        
            with st.spinner("🔍 Parsing and validating template..."):
                records_data, message = parse_template_file(uploaded_template)
        
            if records_data:
                st.success(message)
            
                # Show preview
                st.markdown(f"**📊 Preview of {len(records_data)} records:**")
            
                # Create preview dataframe
                import pandas as pd
                preview_df = pd.DataFrame(records_data)
            
                # Show first few records
                st.dataframe(preview_df.head(10), use_container_width=True)
            
                if len(records_data) > 10:
                    st.info(f"👆 Showing first 10 records. Total records to process: {len(records_data)}")
            
                # Validation section
                st.markdown("#### Step 4: Validation Results")
            
                validation_results = []
                valid_count = 0
            
                for i, record in enumerate(records_data):
                    issues = []
                
                    # Check patient exists
                    if record.get('patient_id'):
                        if not validate_patient_exists(record['patient_id']):
                            issues.append(f"Patient ID '{record['patient_id']}' not found")
                    else:
                        issues.append("Missing patient ID")
                
                    # Check visit date
                    if not record.get('visit_date'):
                        issues.append("Missing visit date")
                
                    # Check for basic clinical data
                    clinical_fields = ['diagnosis', 'treatment', 'prescription', 'notes']
                    if not any(record.get(field) for field in clinical_fields):
                        issues.append("No clinical data provided")
                
                    if not issues:
                        valid_count += 1
                    else:
                        validation_results.append(f"Row {i+1}: {', '.join(issues)}")
            
                # Show validation summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Valid Records", valid_count)
                with col2:
                    st.metric("⚠️ Records with Issues", len(validation_results))
                with col3:
                    st.metric("📊 Total Records", len(records_data))
            
                # Show validation issues if any
                if validation_results:
                    with st.expander(f"⚠️ Validation Issues ({len(validation_results)} records)"):
                        for issue in validation_results[:20]:  # Show first 20 issues
                            st.warning(issue)
                        if len(validation_results) > 20:
                            st.info(f"... and {len(validation_results) - 20} more issues")
            
                # Upload confirmation and processing
                st.markdown("#### Step 5: Process Records")
            
                if valid_count > 0:
                    col1, col2 = st.columns([1, 2])
                
                    with col1:
                        process_mode = st.radio(
                            "Processing Mode:",
                            ["Process Valid Records Only", "Process All Records"],
                            key="batch_process_mode"
                        )
                
                    with col2:
                        if process_mode == "Process Valid Records Only":
                            st.info(f"Will process {valid_count} valid records")
                        else:
                            st.warning("Will attempt to process all records. Invalid records may fail.")
                
                    # Final confirmation
                    st.markdown("---")
                    confirm_upload = st.checkbox(
                        f"✅ I confirm uploading {valid_count if process_mode == 'Process Valid Records Only' else len(records_data)} medical records",
                        key="confirm_batch_upload"
                    )
                
                    if confirm_upload:
                        col1, col2, col3 = st.columns([1, 1, 1])
                    
                        with col2:
                            if st.button("🚀 Process Records", use_container_width=True, type="primary"):
                                with st.spinner("🔄 Processing medical records..."):
                                    # Filter records if needed
                                    if process_mode == "Process Valid Records Only":
                                        filtered_records = []
                                        for i, record in enumerate(records_data):
                                            if validate_patient_exists(record.get('patient_id')) and record.get('visit_date'):
                                                filtered_records.append(record)
                                        process_records = filtered_records
                                    else:
                                        process_records = records_data
                                
                                    # Process the records
                                    success, result_message = add_batch_medical_records(
                                        process_records, 
                                        st.session_state.user['id']
                                    )
                                
                                    if success:
                                        st.session_state.success_message = f"🎉 {result_message}"
                                        # Clear the upload state
                                        if 'show_batch_instructions' in st.session_state:
                                            del st.session_state.show_batch_instructions
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {result_message}")
                else:
                    st.error("❌ No valid records found to process. Please check your template data.")
        
            else:
                st.error(f"❌ {message}")
                st.info("💡 Please check your file format and ensure it contains the required columns.")
    
        else:
            st.info("👆 Please upload a template file to continue")
    
        # Additional help section
        st.markdown("---")
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **Common Issues:**
            - **Patient not found**: Ensure Patient IDs are exact (e.g., PAT12345678)
            - **Date format errors**: Use YYYY-MM-DD format (e.g., 2024-01-15)
            - **File format issues**: Save Excel files as CSV for better compatibility
            - **Empty records**: Remove or fill empty rows in your template
        
            **Tips:**
            - Start with a small batch (5-10 records) to test the process
            - Keep a backup copy of your original data
            - Use the validation results to fix issues before processing
            """)

    elif doctor_choice == "📊 Patient Analytics":
        st.markdown("### Patient Analytics")
        
        if st.session_state.selected_patients:
            for patient_id in st.session_state.selected_patients:
                st.markdown(f"#### Analytics for Patient: {patient_id}")
                

                vital_data = vital_trends(patient_id)
                
                if vital_data:
                    import pandas as pd
                    df = pd.DataFrame(vital_data, columns=['Date', 'Glucose', 'Systolic', 'Diastolic', 'Heart Rate', 'Temperature'])
                    df['Date'] = pd.to_datetime(df['Date'])
                    

                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if df['Glucose'].notna().any():
                            avg_glucose = df['Glucose'].mean()
                            st.metric("Avg Glucose", f"{avg_glucose:.1f} mg/dL")
                    
                    with col2:
                        if df['Systolic'].notna().any():
                            avg_systolic = df['Systolic'].mean()
                            st.metric("Avg Systolic BP", f"{avg_systolic:.0f} mmHg")
                    
                    with col3:
                        if df['Heart Rate'].notna().any():
                            avg_hr = df['Heart Rate'].mean()
                            st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm")
                    
                    if df['Systolic'].notna().any() or df['Diastolic'].notna().any():
                        fig_bp = go.Figure()
                        fig_bp.add_trace(go.Scatter(x=df['Date'], y=df['Systolic'], mode='lines+markers', name='Systolic BP'))
                        fig_bp.add_trace(go.Scatter(x=df['Date'], y=df['Diastolic'], mode='lines+markers', name='Diastolic BP'))
                        fig_bp.update_layout(title='Blood Pressure Trends', xaxis_title='Date', yaxis_title='mmHg')
                        st.plotly_chart(fig_bp, use_container_width=True)
                
                st.markdown("---")
        else:
            st.info("Please select patients from the 'Find Patients' section to view their analytics.")

    elif doctor_choice == "ℹ️ About":
        st.markdown("### About Medical Records System - Doctor Portal")
        st.markdown(f'''
        <div class="info-card">
        <h4>🏥 E-Medical Record System</h4>
        <p>Comprehensive medical records system designed for healthcare professionals.</p>
        
        <h4>✨ Doctor Features:</h4>
        <ul>
        <li>🔍 <strong>Patient Search:</strong> Quickly find and access patient records</li>
        <li>📝 <strong>Record Management:</strong> Add detailed medical records with vital signs</li>
        <li>📁 <strong>File Upload:</strong> Store medical documents and reports securely</li>
        <li>🖼️ <strong>Image Management:</strong> Upload and manage medical images</li>
        <li>📊 <strong>Analytics:</strong> Track patient health trends and vital statistics</li>
        <li>🔒 <strong>Secure Access:</strong> Encrypted data with professional authentication</li>
        </ul>
        
        <h4>🛡️ Professional Standards:</h4>
        <p>This system adheres to healthcare data protection standards and maintains patient confidentiality at all times.</p>
        </div>
        ''', unsafe_allow_html=True)

    elif doctor_choice == "⚙️ Settings":
        st.markdown("### Doctor Settings")
        
        with st.expander("🎨 Display Settings"):
            current_theme = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
            st.markdown(f"**Current Theme:** {current_theme}")
            if st.button("🌓 Switch Theme", use_container_width=True):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        with st.expander("👨‍⚕️ Professional Information"):
            st.markdown(f"**Name:** {st.session_state.user['name']}")
            st.markdown(f"**Doctor ID:** {st.session_state.user['id']}")
            st.markdown(f"**Email:** {st.session_state.user['email']}")
            st.markdown(f"**Specialization:** {st.session_state.user.get('specialization', 'General Practice')}")
            st.markdown(f"**Hospital:** {st.session_state.user.get('hospital', 'Not specified')}")
        
        with st.expander("🔒 Security & Privacy"):
            st.markdown("**Access Control**")
            st.info("All patient data access is logged and monitored for security compliance.")
            
            st.markdown("**Password Management**")
            st.info("To change your password, please contact the system administrator.")

# Main app...
def main():
    query_params = st.query_params
    emergency_token = query_params.get("emergency")
    
    if emergency_token:
        show_emergency_page(emergency_token)
        return
    
    # Initializing...
    init_session_state()
    create_enhanced_tables()
     
    # main app flow
    if st.session_state.otp_stage == 'verification':
        show_otp_verification()
    elif st.session_state.user is None:
        show_auth_page()
    else:
        if st.session_state.user['role'] == 'patient':
            show_patient_dashboard()
        elif st.session_state.user['role'] == 'doctor':
            show_doctor_dashboard()

if __name__ == "__main__":
    main()