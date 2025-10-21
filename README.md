### 🏥 E-Medical Record System

An advanced **digital healthcare platform** built with **Streamlit** that securely manages patient and doctor information, medical records, lab reports, prescriptions, and AI-assisted health insights.  

This project was developed as part of **SIH 2025 (Smart India Hackathon)** to provide a **secure, scalable, and AI-enabled EHR (Electronic Health Record) system**.

---

## 🚀 Features

- **Secure Authentication**
  - Login/Register for Patients 👤 and Doctors 👨‍⚕️  
  - OTP verification via email  
  - SHA-256 password hashing  

- **Patient Module**
  - Manage personal details, allergies, insurance info, emergency contacts  
  - Upload/download **medical files** and **medical images**  
  - Track **vital signs trends** (BP, glucose, heart rate, temperature)  
  - Generate **QR code** for emergency access to critical information  

- **Doctor Module**
  - Register and manage professional details  
  - Access patient records (with permission)  
  - Add/edit medical records, prescriptions, and notes  
  - Search patients and collaborate with other doctors  

- **Emergency Mode**
  - Quick access to patient’s **blood group, allergies, and emergency contacts**  
  - QR-code-based emergency record access  

- **AI Health Assistant (Gemini API)**
  - Patient AI: Personalized insights, health streak tracking, and trend analysis  
  - Doctor AI: Clinical decision support, patient summaries, and evidence-based suggestions  

- **Data Visualization**
  - Interactive charts (using Plotly) for vitals & medical history  

---

## 🛠️ Tech Stack

- **Frontend/UI:** [Streamlit](https://streamlit.io/) with custom CSS  
- **Backend:** Python, MySQL  
- **Database Connector:** `mysql.connector`  
- **Email & OTP:** `smtplib`, `secrets`  
- **AI Integration:** Google Gemini API (`google.generativeai`)  
- **Visualization:** Plotly  
- **Other Libraries:** dotenv, hashlib, qrcode, Pillow (PIL), base64, uuid, socket, io, uv 

---

## Important Note
<br>
Use .env-example file as a template file for .env file and fill out all Info before executing program. this file can be used for Database info, email info, api key etc.. So be sure to check it out !!
<br>
Few bugs are still there... Don't worry, I will fix them asap..
<br>
More Updates and Features are coming soon.




