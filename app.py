from flask import Flask, render_template, request, redirect, url_for, flash, session
import re
import sqlite3
import pickle
import numpy as np
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import email_service # Mail servisini ekle

app = Flask(__name__)
app.secret_key = "super_gizli_anahtar"

# --- AYARLAR ---
MAX_FAILURES = 3       # 3 Hata hakkı
BAN_DURATION = 1       # 1 Dakika ceza

# --- YAPAY ZEKA MODELİNİ YÜKLE ---
try:
    with open('anomaly_model.pkl', 'rb') as f:
        ai_model = pickle.load(f)
    AI_ACTIVE = True
    print("✅ Yapay Zeka Modeli Yüklendi.")
except:
    print("⚠️ UYARI: 'anomaly_model.pkl' bulunamadı. AI devre dışı. Önce ai_model.py çalıştırın.")
    AI_ACTIVE = False

# --- VERİTABANI BAĞLANTISI ---
def get_db_connection():
    conn = sqlite3.connect('guvenlik.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ŞİFRE KONTROLÜ (Regex) ---
def validate_password_backend(password):
    errors = []
    if len(password) < 8: errors.append("En az 8 karakter olmalı.")
    if not re.search(r"[a-z]", password): errors.append("Küçük harf eksik.")
    if not re.search(r"[A-Z]", password): errors.append("Büyük harf eksik.")
    if not re.search(r"\d", password): errors.append("Rakam eksik.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): errors.append("Özel karakter eksik.")
    return errors

# --- BAN KONTROLÜ ---
def check_ban_status(ip_address):
    conn = get_db_connection()
    record = conn.execute('SELECT * FROM ip_tracking WHERE ip_address = ?', (ip_address,)).fetchone()
    conn.close()

    if record and record['lock_until']:
        lock_time = datetime.strptime(record['lock_until'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() < lock_time:
            remaining = (lock_time - datetime.now()).seconds
            return True, remaining
    return False, 0

# --- HONEYPOT (BOT TUZAĞI) ---
def check_honeypot(form_data, ip_address):
    # 'website' alanı doluysa kesin bottur
    if form_data.get('website'):
        conn = get_db_connection()
        # 10 Yıl Banla
        ban_time = datetime.now() + timedelta(days=3650)
        conn.execute('INSERT OR REPLACE INTO ip_tracking (ip_address, fail_count, lock_until) VALUES (?, ?, ?)', 
                     (ip_address, 9999, ban_time))
        
        # Loga kaydet
        username_tried = form_data.get('username', 'Unknown')
        conn.execute('INSERT INTO login_attempts (ip_address, username_tried, action_taken) VALUES (?, ?, ?)', 
                     (ip_address, username_tried, "BANLANDI (10 Yıl) - Honeypot"))
        
        conn.commit()
        conn.close()
        return True
    return False

# --- AI RİSK KONTROLÜ ---
def check_ai_risk(hour, attempts):
    if not AI_ACTIVE: return False
    
    # Model Tahmini: -1 (Anomali), 1 (Normal)
    prediction = ai_model.predict([[hour, attempts]])[0]
    
    if prediction == -1:
        return True # RİSKLİ
    return False

# --- ROTA: KAYIT (/register) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Honeypot Kontrolü
        if check_honeypot(request.form, request.remote_addr):
            return redirect(url_for('login')) 

        username = request.form['username']
        password = request.form['password']

        # 2. Şifre Validasyonu
        validation_errors = validate_password_backend(password)
        if validation_errors:
            for error in validation_errors: flash(error, "danger")
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_pw))
            conn.commit()
            flash("Kayıt başarılı! Şimdi giriş yapabilirsiniz.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Bu kullanıcı adı zaten alınmış.", "warning")
        finally:
            conn.close()

    return render_template('register.html')

# --- ROTA: GİRİŞ (/login) ---
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    client_ip = request.remote_addr

    # 1. Ban Kontrolü
    is_banned, wait_time = check_ban_status(client_ip)
    if is_banned:
        flash(f"Erişim engellendi! {wait_time} saniye beklemelisiniz.", "danger")
        return render_template('login.html', banned=True)

    if request.method == 'POST':
        # 2. Honeypot Kontrolü
        if check_honeypot(request.form, client_ip):
            return redirect(url_for('login'))

        username = request.form['username']
        password = request.form['password']
        
        # 3. AI Risk Analizi
        conn = get_db_connection()
        ip_record = conn.execute('SELECT * FROM ip_tracking WHERE ip_address = ?', (client_ip,)).fetchone()
        
        current_hour = datetime.now().hour
        current_attempts = (ip_record['fail_count'] if ip_record else 0) + 1
        
        ai_risk = False
        if check_ai_risk(current_hour, current_attempts):
            ai_risk = True
            flash("⚠️ Yapay Zeka sistemi davranışınızda anomali tespit etti! (Şüpheli saat/sıklık)", "warning")
            
            # --- MAİL GÖNDER ---
            # Arka planda mail at (Basit olması için thread kullanmıyoruz, biraz bekletebilir)
            print("📨 Anomali tespit edildi, admin maili tetikleniyor...")
            email_service.send_anomaly_alert(client_ip, current_hour, current_attempts)
            
            # İstersen burada ekstra önlem alabilirsin (örn: Captcha göster)

        # 4. Şifre Kontrolü
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if not ip_record:
            conn.execute('INSERT INTO ip_tracking (ip_address, fail_count) VALUES (?, 0)', (client_ip,))
            conn.commit()

        if user and check_password_hash(user['password_hash'], password):
            # BAŞARILI
            conn.execute('UPDATE ip_tracking SET fail_count = 0, lock_until = NULL WHERE ip_address = ?', (client_ip,))
            conn.commit()
            
            # SESSION BAŞLAT
            session['user'] = username
            session['logged_in'] = True
            
            flash(f"Hoş geldin {username}!", "success")
            return redirect(url_for('dashboard'))
        
        else:
            # BAŞARISIZ
            # (INSERT işlemi aşağıda failure logic içinde yapılacak, çünkü action_taken bilgisini orada belirliyoruz)
            
            # Hata sayacını artır (az önce current_attempts hesaplamıştık ama veritabanı için tekrar bakalım)
            new_fail_count = (ip_record['fail_count'] if ip_record else 0) + 1
            
            action_msg = ""

            if new_fail_count >= MAX_FAILURES:
                # Limit Aşıldı -> BANLA
                ban_time = datetime.now() + timedelta(minutes=BAN_DURATION)
                conn.execute('UPDATE ip_tracking SET fail_count = ?, lock_until = ? WHERE ip_address = ?', 
                             (new_fail_count, ban_time, client_ip))
                flash(f"HESABINIZ GEÇİCİ OLARAK KİLİTLENDİ! {BAN_DURATION} dakika giriş yapamazsınız.", "danger")
                action_msg = f"BANLANDI ({BAN_DURATION} Dk) - Limit Aşımı"
            else:
                # Uyar
                conn.execute('UPDATE ip_tracking SET fail_count = ? WHERE ip_address = ?', (new_fail_count, client_ip))
                remaining = MAX_FAILURES - new_fail_count
                flash(f"Hatalı giriş! Kalan hakkınız: {remaining}", "warning")
                action_msg = f"Uyarı ({new_fail_count}. Hata)"
                
                if ai_risk:
                    action_msg += " (AI Anomali Şüphesi)"
            
            # Log kaydı (action_taken ile)
            conn.execute('INSERT INTO login_attempts (ip_address, username_tried, action_taken) VALUES (?, ?, ?)', 
                         (client_ip, username, action_msg))
            
            conn.commit()
            
        conn.close()
        return redirect(url_for('login'))

    return render_template('login.html')

# --- ROTA: DASHBOARD (/logs) ---
@app.route('/logs')
def show_logs():
    conn = get_db_connection()
    
    # Tablo Verileri
    logs = conn.execute('SELECT * FROM login_attempts ORDER BY timestamp DESC').fetchall()
    banned_ips = conn.execute('SELECT * FROM ip_tracking WHERE fail_count >= ?', (MAX_FAILURES,)).fetchall()
    users = conn.execute('SELECT username, created_at FROM users ORDER BY created_at DESC').fetchall()
    
    # Grafik Verisi 1: En çok saldıran 5 IP
    top_ips_query = conn.execute('SELECT ip_address, COUNT(*) as count FROM login_attempts GROUP BY ip_address ORDER BY count DESC LIMIT 5').fetchall()
    top_ips_labels = [row['ip_address'] for row in top_ips_query]
    top_ips_data = [row['count'] for row in top_ips_query]

    # Grafik Verisi 2: Kullanıcı vs Ban Oranı
    user_count = len(users)
    ban_count = len(banned_ips)
    
    conn.close()
    
    return render_template('logs.html', 
                           logs=logs, banned=banned_ips, users=users,
                           chart_ips=json.dumps(top_ips_labels),
                           chart_counts=json.dumps(top_ips_data),
                           stat_users=user_count,
                           stat_bans=ban_count)

# --- ROTA: BANKACILIK DASHBOARD (/dashboard) ---
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('login'))
    
    return render_template('banking.html', username=session['user'])

# --- ROTA: ÇIKIŞ (/logout) ---
@app.route('/logout')
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)