import sqlite3

def init_db():
    conn = sqlite3.connect('guvenlik.db')
    c = conn.cursor()

    # --- ESKİ TABLOLARI SİL (SIFIRLAMA İŞLEMİ) ---
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('DROP TABLE IF EXISTS login_attempts')
    c.execute('DROP TABLE IF EXISTS ip_tracking')

    # --- 1. KULLANICILAR TABLOSU (GÜNCELLENDİ) ---
    # created_at: Kullanıcının kayıt olduğu tarih ve saati otomatik tutar.
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- 2. SALDIRI LOGLARI ---
    # timestamp: Hatalı giriş yapılan tarih ve saati tutar.
    c.execute('''
        CREATE TABLE login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            username_tried TEXT,
            action_taken TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- 3. IP TAKİP VE BAN TABLOSU ---
    c.execute('''
        CREATE TABLE ip_tracking (
            ip_address TEXT PRIMARY KEY,
            fail_count INTEGER DEFAULT 0,
            lock_until DATETIME
        )
    ''')

    conn.commit()
    conn.close()
    print("Veritabanı SIFIRLANDI ve 'Kayıt Tarihi' sütunuyla yeniden oluşturuldu.")

if __name__ == '__main__':
    init_db()