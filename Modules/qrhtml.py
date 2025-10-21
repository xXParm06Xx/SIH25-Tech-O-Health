from datetime import datetime, date, timedelta

def qr_html(patient_info, qr_data_b64):
    """Create downloadable QR code with patient info"""
    theme_colors = {
        'bg_gradient': 'radial-gradient(circle at top left, #000000 0%, #121212 100%)',
        'card_bg': 'linear-gradient(135deg, #ffffff, #f0f0f0, #e8e8e8)',
        'text_color': '#ff0000',
        'border_color': '#ffffff',
        'secondary_bg': 'linear-gradient(135deg, #2a2a2a, #3a3a3a, #2a2a2a)',
        'secondary_text': '#ffffff'
    }
    
    qr_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Emergency QR Code - {patient_info['name']}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 20px;
                background: {theme_colors['bg_gradient']};
                color: {theme_colors['secondary_text']};
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                animation: fadeIn 1s ease-in-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .main-header {{
                background: {theme_colors['card_bg']};
                padding: 2rem;
                border-radius: 16px;
                color: {theme_colors['text_color']};
                text-align: center;
                margin-bottom: 2.5rem;
                box-shadow: 
                    0 12px 30px rgba(255, 255, 255, 0.5),
                    0 0 50px rgba(255, 255, 255, 0.3) inset,
                    0 4px 20px rgba(255, 255, 255, 0.4);
                border: 2px solid {theme_colors['border_color']};
                animation: headerGlow 2s ease-in-out infinite alternate;
            }}
            
            @keyframes headerGlow {{
                0% {{ 
                    box-shadow: 
                        0 12px 30px rgba(255, 255, 255, 0.4),
                        0 0 40px rgba(255, 255, 255, 0.2) inset;
                }}
                100% {{ 
                    box-shadow: 
                        0 16px 40px rgba(255, 255, 255, 0.6),
                        0 0 60px rgba(255, 255, 255, 0.4) inset;
                }}
            }}
            
            .main-header h1 {{
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 8px rgba(255, 255, 255, 0.3);
            }}
            
            .main-header h2 {{
                font-size: 1.8rem;
                font-weight: 600;
                margin: 0;
            }}
            
            .content-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
                margin-bottom: 2rem;
            }}
            
            .qr-container {{
                background: {theme_colors['secondary_bg']};
                padding: 2rem;
                border-radius: 16px;
                border: 2px solid {theme_colors['border_color']};
                text-align: center;
                box-shadow: 
                    0 8px 25px rgba(255, 255, 255, 0.3),
                    0 0 15px rgba(255, 255, 255, 0.15) inset;
                transition: transform 0.3s ease;
            }}
            
            .qr-container:hover {{
                transform: translateY(-5px);
            }}
            
            .qr-container img {{
                width: 200px;
                height: 200px;
                border: 3px solid {theme_colors['border_color']};
                border-radius: 10px;
                margin-bottom: 1rem;
                background: white;
                padding: 10px;
            }}
            
            .patient-info {{
                background: {theme_colors['secondary_bg']};
                padding: 2rem;
                border-radius: 16px;
                border: 2px solid {theme_colors['border_color']};
                box-shadow: 
                    0 8px 25px rgba(255, 255, 255, 0.3),
                    0 0 15px rgba(255, 255, 255, 0.15) inset;
            }}
            
            .patient-info h3 {{
                color: {theme_colors['secondary_text']};
                margin-bottom: 1.5rem;
                font-size: 1.5rem;
                border-bottom: 2px solid {theme_colors['border_color']};
                padding-bottom: 0.5rem;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.8rem 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .info-label {{
                font-weight: bold;
                color: {theme_colors['secondary_text']};
            }}
            
            .info-value {{
                color: {theme_colors['secondary_text']};
                font-weight: 500;
            }}
            
            .blood-group {{
                color: #ff6b6b !important;
                font-weight: bold !important;
                font-size: 1.1em;
            }}
            
            .emergency-notice {{
                background: linear-gradient(135deg, #ff4757, #ff3838);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                margin: 2rem 0;
                font-weight: bold;
                font-size: 1.1rem;
                box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4);
                animation: emergencyPulse 2s ease-in-out infinite alternate;
            }}
            
            @keyframes emergencyPulse {{
                from {{ box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4); }}
                to {{ box-shadow: 0 12px 35px rgba(255, 71, 87, 0.6); }}
            }}
            
            .footer {{
                text-align: center;
                margin-top: 3rem;
                padding: 2rem;
                background: {theme_colors['secondary_bg']};
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .print-notice {{
                background: rgba(76, 175, 80, 0.1);
                border: 1px solid #4CAF50;
                padding: 1rem;
                border-radius: 8px;
                margin-top: 1rem;
                font-size: 0.9rem;
            }}
            
            @media (max-width: 768px) {{
                .content-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .main-header h1 {{
                    font-size: 2rem;
                }}
                
                .qr-container img {{
                    width: 150px;
                    height: 150px;
                }}
            }}
            
            @media print {{
                body {{
                    background: white;
                    color: black;
                }}
                
                .main-header, .qr-container, .patient-info {{
                    box-shadow: none;
                    border: 2px solid #333;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="main-header">
                <h1>🚨 EMERGENCY MEDICAL INFORMATION</h1>
                <h2>{patient_info['name']}</h2>
            </div>
            
            <div class="emergency-notice">
                ⚠️ This QR code provides instant access to critical medical information in emergency situations
            </div>
            
            <div class="content-grid">
                <div class="qr-container">
                    <img src="data:image/png;base64,{qr_data_b64}" alt="Emergency QR Code">
                    <h3>Emergency QR Code</h3>
                    <p>Scan for instant medical access</p>
                    <div class="print-notice">
                        💡 Print this page and keep it in your wallet, car, or emergency kit
                    </div>
                </div>
                
                <div class="patient-info">
                    <h3>👤 Patient Information</h3>
                    <div class="info-item">
                        <span class="info-label">Name:</span>
                        <span class="info-value">{patient_info['name']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Patient ID:</span>
                        <span class="info-value">{patient_info['id']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Blood Group:</span>
                        <span class="info-value blood-group">{patient_info.get('blood_group', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Phone:</span>
                        <span class="info-value">{patient_info.get('phone', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span class="info-value">{patient_info.get('email', 'N/A')}</span>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <h3>🏥 E-Medical Record System</h3>
                <p>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                <p><strong>For Emergency Use Only</strong></p>
                <div class="print-notice">
                    📱 Scan the QR code with any smartphone camera to access emergency medical information
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return qr_html.encode('utf-8')