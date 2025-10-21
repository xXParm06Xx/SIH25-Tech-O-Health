# CSS, HTML Module for E-Medical Record System
import streamlit as st

def load_css():
    if st.session_state.dark_mode:
        css = """
        <style>
        .stApp {
            background: #ffffff !important;
            color: #2196F3 !important;
        }
        .main-header {
            /* keep your background / glow / border settings */
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2.5rem;
            box-shadow: 
                0 12px 30px rgba(33, 150, 243, 0.3),
                0 0 50px rgba(255, 255, 255, 0.2) inset,
                0 4px 20px rgba(33, 150, 243, 0.2);
            animation: headerGlow 2s ease-in-out infinite alternate;
            border: 2px solid #2196F3;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #2196F3, #64B5F6, #2196F3);
            border-radius: 16px;
            z-index: -1;
            animation: borderGlow 3s ease-in-out infinite;
        }
        .main-header h1, .main-header p, .main-header * {
            color: #ffffff !important;
            text-shadow: 2px 2px 8px rgba(33, 150, 243, 0.3);
            font-weight: bold;
        }
        @keyframes headerGlow {
            0% { 
                box-shadow: 
                    0 12px 30px rgba(33, 150, 243, 0.3),
                    0 0 40px rgba(255, 255, 255, 0.2) inset,
                    0 4px 20px rgba(33, 150, 243, 0.2);
            }
            100% { 
                box-shadow: 
                    0 16px 40px rgba(33, 150, 243, 0.5),
                    0 0 60px rgba(255, 255, 255, 0.4) inset,
                    0 6px 25px rgba(33, 150, 243, 0.4);
            }
        }
        @keyframes borderGlow {
            0%, 100% { opacity: 0.8; }
            50% { opacity: 1; }
        }
        
        h1, h2, h3, h4, h5, h6 { 
            color: #2196F3 !important; 
            text-shadow: 2px 2px 8px rgba(33, 150, 243, 0.3); 
        }
        
        .metric-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 1.3rem; 
            border-radius: 12px; 
            border: 2px solid #2196F3; 
            margin: 0.8rem 0;
            box-shadow: 
                0 6px 20px rgba(33, 150, 243, 0.25),
                0 0 20px rgba(255, 255, 255, 0.15) inset;
            color: #2196F3 !important; 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .metric-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 
                0 12px 30px rgba(33, 150, 243, 0.4),
                0 0 30px rgba(255, 255, 255, 0.25) inset;
        }
        
        .patient-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 1.6rem; 
            border-radius: 14px; 
            border-left: 5px solid #2196F3; 
            margin: 1.5rem 0;
            box-shadow: 
                0 8px 25px rgba(33, 150, 243, 0.3),
                0 0 15px rgba(255, 255, 255, 0.15) inset;
            color: #2196F3 !important; 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .patient-card:hover {
            transform: translateX(8px);
            box-shadow: 
                0 12px 35px rgba(33, 150, 243, 0.4),
                0 0 25px rgba(255, 255, 255, 0.2) inset;
        }
        
        .auth-form {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 2.2rem; 
            border-radius: 18px; 
            border: 2px solid #2196F3;
            box-shadow: 
                0 12px 35px rgba(33, 150, 243, 0.35),
                0 0 20px rgba(255, 255, 255, 0.1) inset; 
            margin: 2rem 0; 
            color: #2196F3 !important;
            backdrop-filter: blur(5px);
        }
        .auth-form h1, .auth-form h2, .auth-form h3, .auth-form label, .auth-form p, .auth-form span, .auth-form div {
            color: #2196F3 !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #2196F3, #1976D2, #42A5F5) !important; 
            color: #ffffff !important; 
            border: none !important;
            border-radius: 30px !important; 
            padding: 0.7rem 1.5rem !important; 
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; 
            box-shadow: 
                0 4px 15px rgba(33, 150, 243, 0.4),
                0 2px 8px rgba(255, 255, 255, 0.2) inset !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd) !important;
            color: #000000 !important;
            border: 2px solid #2196F3 !important;
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 
                0 8px 25px rgba(33, 150, 243, 0.5),
                0 4px 12px rgba(0, 0, 0, 0.1) inset !important;
        }

        .toggle-button > button {
            background: linear-gradient(135deg, #2196F3, #1976D2) !important;
            color: #ffffff !important;
            border: 2px solid #2196F3 !important;
        }
        .toggle-button > button:hover {
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important;
            color: #000000 !important;
            border: 2px solid #2196F3 !important;
        }
        
        .logout-button > button {
            background: linear-gradient(135deg, #ff0000, #cc0000, #ff1a1a) !important; 
            color: white !important;
        }
        .logout-button > button:hover {
            background: linear-gradient(135deg, #cc0000, #990000, #cc1a1a) !important;
            transform: translateY(-3px) scale(1.05) !important;
        }
        .css-1d391kg, .css-1y4p8pa {
            background: linear-gradient(180deg, #2196F3, #1976D2) !important;
            color: #ffffff !important;
            border-right: 2px solid #42A5F5 !important;
        }
        .success-message {
            background: linear-gradient(135deg, #4CAF50, #45a049, #66bb6a); 
            color: white;
            padding: 1.2rem; 
            border-radius: 10px; 
            margin: 1rem 0; 
            text-align: center; 
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
            animation: successPulse 2s ease-in-out infinite alternate;
        }
        @keyframes successPulse {
            from { box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4); }
            to { box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6); }
        }
        
        .info-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 1.6rem; 
            border-radius: 14px; 
            border: 2px solid #2196F3; 
            margin: 1rem 0;
            box-shadow: 
                0 6px 20px rgba(33, 150, 243, 0.25),
                0 0 15px rgba(255, 255, 255, 0.1) inset; 
            color: #2196F3 !important;
            transition: all 0.3s ease;
        }
        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: 
                0 10px 30px rgba(33, 150, 243, 0.35),
                0 0 25px rgba(255, 255, 255, 0.15) inset;
        }
        .stTextInput > div > div > input { 
            color: #2196F3 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #2196F3 !important; 
            border-radius: 8px !important;
            padding: 0.6rem !important;
            transition: all 0.3s ease !important;
        }
        .stTextInput > div > div > input:focus {
            box-shadow: 0 0 15px rgba(33, 150, 243, 0.5) !important;
            border-color: #1976D2 !important;
        }
        
        .stTextArea > div > div > textarea { 
            color: #2196F3 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #2196F3 !important; 
            border-radius: 8px !important;
        }
        .stSelectbox > div > div > div { 
            color: #2196F3 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #2196F3 !important;
        }
        .stNumberInput > div > div > input { 
            color: #2196F3 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #2196F3 !important; 
            border-radius: 8px !important;
        }

        /* Add to both light and dark mode CSS blocks */
        .custom-expander .streamlit-expanderHeader {
            background-color: #ffffff !important;
            color: #2c3e50 !important;
            border: 1px solid #4CAF50 !important;
            border-radius: 8px !important;
            margin: 5px 0 !important;
        }

        .custom-expander .streamlit-expanderContent {
            background-color: #ffffff !important;
            border: 1px solid #4CAF50 !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }
        
        .stRadio > div { color: #2196F3 !important; }
        .stRadio label { color: #2196F3 !important; font-weight: 500 !important; }




        /* Narrowed text color rule: don't force every <div> to blue (was causing AI text & spinner issues) */
        p, span { color: #2196F3 !important; }

        /* Ensure success message text is always white in dark mode */
        .success-message {
            color: #ffffff !important;
        }

        /* Add classes for AI/user chat bubbles — these will override generic rules */
        .ai-bubble, .ai-bubble * {
            color: #ffffff !important;           /* white text on AI bubble in dark mode */
        }

        /* Keep user bubble text readable — inherit (so inline styles still work) */
        .user-bubble, .user-bubble * {
            color: inherit !important;
        }

        /* Sidebar styling for dark mode */
        .stSidebar {
            background: linear-gradient(180deg, #2196F3, #1976D2) !important;
        }
        .stSidebar * { color: #ffffff !important; }
        .stSidebar .stRadio > div { color: #ffffff !important; }
        .stSidebar .stRadio label { color: #ffffff !important; }
        .stSidebar h1, .stSidebar h2, .stSidebar h3 { color: #ffffff !important; }
        .stSidebar .stButton > button {
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important;
            color: #2196F3 !important;
            border: 2px solid #ffffff !important;
        }
        .stSidebar .stButton > button:hover {
            background: linear-gradient(135deg, #42A5F5, #1976D2) !important;
            color: #ffffff !important;
            border: 2px solid #ffffff !important;
        }
        .stSidebar .stMarkdown {
            color: #ffffff !important;
        }
        
        /* Medical Records Section Styling */
        .medical-record-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 5px solid #2196F3;
            color: #2196F3 !important;
        }

        .clinical-info-card {
            background: #ffffff;
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
            color: #2196F3 !important;
        }

        .vital-signs-card {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            margin: 6px 0;
            border: 1px solid #2196F3;
            color: #2196F3 !important;
        }

        /* Filter sections */
        .filter-section {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 20px;
            border-radius: 12px;
            border: 2px solid #2196F3;
            margin: 15px 0;
        }

        /* Doctor search results */
        .doctor-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 20px;
            border-radius: 14px;
            border: 2px solid #2196F3;
            margin: 15px 0;
            color: #2196F3 !important;
        }

        /* Patient analytics cards */
        .analytics-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 18px;
            border-radius: 12px;
            border: 2px solid #2196F3;
            color: #2196F3 !important;
        }

        .stApp button,
        .stApp .stButton > button,
        .stApp .stDownloadButton > button { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
        .stApp button:hover,
        .stApp .stButton > button:hover { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }

        /* Also include the same .login-btn/.btn-dark rules so custom buttons behave consistently */
        .login-btn, .btn-dark { background: #000; color: #fff !important; }
        .login-btn:hover, .btn-dark:hover { background: #fff; color: #000 !important; }

        /* Spinner styling for dark mode */
        .stSpinner > div {
            border-color: #2196F3 !important;
        }
        .stSpinner > div > div {
            border-top-color: #2196F3 !important;
        }
        .stAlert > div {
            background-color: rgba(33, 150, 243, 0.1) !important;
            color: #2196F3 !important;
            border: 1px solid #2196F3 !important;
        }

        /* Text cursor visibility for dark mode */
        .stTextInput > div > div > input {
            caret-color: #2196F3 !important;
        }
        .stTextArea > div > div > textarea {
            caret-color: #2196F3 !important;
        }
        .stSelectbox > div > div > input {
            caret-color: #2196F3 !important;
        }
        .stNumberInput > div > div > input {
            caret-color: #2196F3 !important;
        }

        </style>
        """













    else:
        # light mode - updated for better button contrast and form visibility
        css = """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 50%, #f0f2f5 100%);
            color: #2c3e50;
        }
        .main-header {
            background: linear-gradient(135deg, #4CAF50, #45a049, #66bb6a);
            padding: 2rem; 
            border-radius: 16px; 
            color: white !important; 
            text-align: center;
            margin-bottom: 2.5rem; 
            box-shadow: 
                0 12px 35px rgba(76, 175, 80, 0.4),
                0 4px 20px rgba(76, 175, 80, 0.2),
                0 0 40px rgba(76, 175, 80, 0.15) inset;
            animation: headerGlowLight 2s ease-in-out infinite alternate;
            border: 2px solid rgba(76, 175, 80, 0.3);
            backdrop-filter: blur(5px);
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #4CAF50, #66bb6a, #4CAF50);
            border-radius: 16px;
            z-index: -1;
            animation: borderGlowLight 3s ease-in-out infinite;
        }
        .main-header h1, .main-header p, .main-header * {
            color: white !important;
            text-shadow: 2px 2px 8px rgba(33, 150, 243, 0.3);
            font-weight: bold;
        }
        @keyframes headerGlowLight {
            0% { 
                box-shadow: 
                    0 12px 35px rgba(76, 175, 80, 0.35),
                    0 4px 20px rgba(76, 175, 80, 0.15),
                    0 0 30px rgba(76, 175, 80, 0.1) inset;
            }
            100% { 
                box-shadow: 
                    0 16px 45px rgba(76, 175, 80, 0.5),
                    0 6px 25px rgba(76, 175, 80, 0.25),
                    0 0 50px rgba(76, 175, 80, 0.2) inset;
            }
        }
        @keyframes borderGlowLight {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        h1, h2, h3, h4, h5, h6 { 
            color: #2c3e50 !important; 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1); 
        }
        
        .metric-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa); 
            padding: 1.3rem; 
            border-radius: 12px; 
            border: 2px solid #4CAF50;
            margin: 0.8rem 0; 
            box-shadow: 
                0 6px 20px rgba(76, 175, 80, 0.15),
                0 2px 10px rgba(0, 0, 0, 0.05); 
            color: #2c3e50 !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .metric-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 
                0 12px 30px rgba(76, 175, 80, 0.25),
                0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .patient-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa); 
            padding: 1.6rem; 
            border-radius: 14px; 
            border-left: 5px solid #4CAF50;
            margin: 1.5rem 0; 
            box-shadow: 
                0 8px 25px rgba(76, 175, 80, 0.15),
                0 2px 10px rgba(0, 0, 0, 0.05); 
            color: #2c3e50 !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .patient-card:hover {
            transform: translateX(8px);
            box-shadow: 
                0 12px 35px rgba(76, 175, 80, 0.25),
                0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .auth-form {
            background: linear-gradient(135deg, #ffffff, #f8f9fa); 
            padding: 2.2rem; 
            border-radius: 18px; 
            border: 2px solid #4CAF50;
            box-shadow: 
                0 12px 35px rgba(76, 175, 80, 0.2),
                0 4px 15px rgba(0, 0, 0, 0.05); 
            margin: 2rem 0; 
            color: #2c3e50 !important;
            backdrop-filter: blur(5px);
        }
        .auth-form h1, .auth-form h2, .auth-form h3, .auth-form label, .auth-form p, .auth-form span, .auth-form div {
            color: #2c3e50 !important;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #4CAF50, #45a049, #66bb6a) !important; 
            color: #ffffff !important; 
            border: none !important;
            border-radius: 30px !important; 
            padding: 0.7rem 1.5rem !important; 
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 
                0 4px 15px rgba(76, 175, 80, 0.3),
                0 2px 8px rgba(255, 255, 255, 0.2) inset !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #45a049, #388e3c, #4CAF50) !important;
            color: #ffffff !important;
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 
                0 8px 25px rgba(76, 175, 80, 0.4),
                0 4px 12px rgba(255, 255, 255, 0.3) inset !important;
        }
        
        .toggle-button > button {
            background: linear-gradient(135deg, #2c3e50, #34495e) !important;
            color: #ffffff !important;
            border: 2px solid #4CAF50 !important;
        }
        .toggle-button > button:hover {
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important;
            color: #2c3e50 !important;
            border: 2px solid #4CAF50 !important;
        }
        
        .logout-button > button {
            background: linear-gradient(135deg, #ff0000, #cc0000, #ff1a1a) !important; 
            color: white !important;
        }
        .logout-button > button:hover {
            background: linear-gradient(135deg, #cc0000, #990000, #cc1a1a) !important;
            transform: translateY(-3px) scale(1.05) !important;
        }

        .css-1d391kg, .css-1y4p8pa {
            background: linear-gradient(180deg, #f0f2f5, #e9ecef) !important;
            color: #2c3e50 !important;
            border-right: 2px solid #dee2e6 !important;
        }
        
        .success-message {
            background: linear-gradient(135deg, #4CAF50, #45a049, #66bb6a); 
            color: white;
            padding: 1.2rem; 
            border-radius: 10px; 
            margin: 1rem 0; 
            text-align: center; 
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            animation: successPulseLight 2s ease-in-out infinite alternate;
        }
        @keyframes successPulseLight {
            from { box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3); }
            to { box-shadow: 0 6px 20px rgba(76, 175, 80, 0.5); }
        }
        
        .info-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa); 
            padding: 1.6rem; 
            border-radius: 14px; 
            border: 2px solid #4CAF50;
            margin: 1rem 0; 
            box-shadow: 
                0 6px 20px rgba(76, 175, 80, 0.15),
                0 2px 10px rgba(0, 0, 0, 0.05); 
            color: #2c3e50 !important;
            transition: all 0.3s ease;
        }
        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: 
                0 10px 30px rgba(76, 175, 80, 0.25),
                0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .stTextInput > div > div > input { 
            color: #2c3e50 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #4CAF50 !important; 
            border-radius: 8px !important;
            padding: 0.6rem !important;
            transition: all 0.3s ease !important;
        }
        .stTextInput > div > div > input:focus {
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.3) !important;
            border-color: #45a049 !important;
        }
        
        .stTextArea > div > div > textarea { 
            color: #2c3e50 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #4CAF50 !important; 
            border-radius: 8px !important;
        }
        .stSelectbox > div > div > div { 
            color: #2c3e50 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #4CAF50 !important;
        }
        .stNumberInput > div > div > input { 
            color: #2c3e50 !important; 
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; 
            border: 2px solid #4CAF50 !important; 
            border-radius: 8px !important;
        }

        /* Fix for expander headers in light mode */
        .streamlit-expanderHeader {
            background-color: #ffffff !important;
            color: #2c3e50 !important;
            border: 1px solid #4CAF50 !important;
        }
        
        /* Fix for expanded content background */
        .streamlit-expanderContent {
            background-color: #ffffff !important;
            border: 1px solid #4CAF50 !important;
            border-top: none !important;
        }

        /* Add to both light and dark mode CSS blocks */
        .custom-expander .streamlit-expanderHeader {
            background-color: #ffffff !important;
            color: #2c3e50 !important;
            border: 1px solid #4CAF50 !important;
            border-radius: 8px !important;
            margin: 5px 0 !important;
        }

        .custom-expander .streamlit-expanderContent {
            background-color: #ffffff !important;
            border: 1px solid #4CAF50 !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }
        .stRadio > div { color: #2c3e50 !important; }
        .stRadio label { color: #2c3e50 !important; font-weight: 500 !important; }
        p, span, div { color: #2c3e50 !important; }

        .stSidebar {
            background: linear-gradient(180deg, #4CAF50, #45a049) !important;
        }
        .stSidebar * { color: #ffffff !important; }
        .stSidebar .stRadio > div { color: #ffffff !important; }
        .stSidebar .stRadio label { color: #ffffff !important; }
        .stSidebar h1, .stSidebar h2, .stSidebar h3 { color: #ffffff !important; }
        .stSidebar .stButton > button {
            background: linear-gradient(135deg, #ffffff, #f8f9fa) !important;
            color: #4CAF50 !important;
            border: 2px solid #ffffff !important;
        }
        .stSidebar .stButton > button:hover {
            background: linear-gradient(135deg, #66bb6a, #4CAF50) !important;
            color: #ffffff !important;
            border: 2px solid #ffffff !important;
        }
        .stSidebar .stMarkdown {
            color: #ffffff !important;
        }
        
        /* Medical Records Section Styling */
        .medical-record-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 5px solid #2196F3;
            color: #2196F3 !important;
        }

        .clinical-info-card {
            background: #ffffff;
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
            color: #2196F3 !important;
        }

        .vital-signs-card {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            margin: 6px 0;
            border: 1px solid #2196F3;
            color: #2196F3 !important;
        }

        /* Filter sections */
        .filter-section {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 20px;
            border-radius: 12px;
            border: 2px solid #2196F3;
            margin: 15px 0;
        }

        /* Doctor search results */
        .doctor-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 20px;
            border-radius: 14px;
            border: 2px solid #2196F3;
            margin: 15px 0;
            color: #2196F3 !important;
        }

        /* Patient analytics cards */
        .analytics-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa, #e3f2fd);
            padding: 18px;
            border-radius: 12px;
            border: 2px solid #2196F3;
            color: #2196F3 !important;
        }

        .stApp button,
        .stApp input[type="submit"],
        .stApp input[type="button"],
        .stApp .stDownloadButton > button,
        .stApp .stButton > button,
        .stApp .stDownloadButton > button * ,
        .stApp .stButton > button * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        /* Hover (when background becomes light) -> black text for readability */
        .stApp button:hover,
        .stApp input[type="submit"]:hover,
        .stApp input[type="button"]:hover,
        .stApp .stDownloadButton > button:hover,
        .stApp .stButton > button:hover,
        .stApp .stDownloadButton > button:hover * ,
        .stApp .stButton > button:hover * {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* For any custom HTML pseudo-buttons you kept: style classes you might add */
        .login-btn,
        .btn-dark {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: #000000;
            color: #ffffff !important;
            border-radius: 8px;
            border: 1px solid #000000;
            cursor: pointer;
            text-decoration: none;
        }
        .login-btn:hover,
        .btn-dark:hover {
            background: #ffffff;
            color: #000000 !important;
            border-color: #000000;
        }

        /* Ensure icons/text inside buttons don't keep wrong color */
        .login-btn *, .btn-dark * { color: inherit !important; }

        /* Optional: make download buttons match */
        .stApp .stDownloadButton > button { padding: 0.45rem 0.9rem; border-radius: 8px; }

        /* Spinner styling for light mode */
        .stSpinner > div {
            border-color: #4CAF50 !important;
        }
        .stSpinner > div > div {
            border-top-color: #4CAF50 !important;
        }
        .stAlert > div {
            background-color: rgba(76, 175, 80, 0.1) !important;
            color: #2c3e50 !important;
            border: 1px solid #4CAF50 !important;
        }

        /* Text cursor visibility for light mode */
        .stTextInput > div > div > input {
            caret-color: #2c3e50 !important;
        }
        .stTextArea > div > div > textarea {
            caret-color: #2c3e50 !important;
        }
        .stSelectbox > div > div > input {
            caret-color: #2c3e50 !important;
        }
        .stNumberInput > div > div > input {
            caret-color: #2c3e50 !important;
        }

        </style>
        """
        
    st.markdown(css, unsafe_allow_html=True)