import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime


SENDER_EMAIL = "ilkeryuk.gulser@gmail.com"  
SENDER_PASSWORD = 


ADMIN_EMAIL = "ilkeryukselgulser1907@gmail.com"

def send_anomaly_alert(ip_address, hour, attempts):
    """
    Anomali tespit edildiğinde admin'e mail atar.
    """
    subject = f"🚨 ACİL: Yapay Zeka Anomali Tespiti! - {ip_address}"
    
    body = f"""
    Merhabalar,
    
    Yapay Zeka güvenlik sistemi şüpheli bir giriş denemesi yakaladı.
    
    DETAYLAR:
    --------------------------------------------------
    📅 Zaman: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    💻 IP Adresi: {ip_address}
    🕒 Giriş Saati: {hour}:00
    🔢 Deneme Sıklığı: {attempts}
    --------------------------------------------------
    
    Sistem bu davranışı "ANORMAL" olarak işaretledi. 
    Lütfen paneli kontrol edin.
    
    Saygılar,
    Akıllı Giriş Güvenlik Sistemi
    """

    try:
     
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

     
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(SENDER_EMAIL, SENDER_PASSWORD.replace(" ", ""))
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, text)
        server.quit()
        
        print(f"📧 [POSTACI] Mail başarıyla gönderildi: {ADMIN_EMAIL}")
        return True
    
    except Exception as e:
        print(f"❌ [POSTACI] Mail gönderilirken hata oluştu: {str(e)}")
        print("💡 İPUCU: Gmail 'Uygulama Şifresi' aldığınızdan ve SENDER_PASSWORD alanına yazdığınızdan emin olun.")
        return False
