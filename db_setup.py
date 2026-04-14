import sqlite3

def init_db():
    conn = sqlite3.connect('guvenlik.db')
    c = conn.cursor()

   
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('DROP TABLE IF EXISTS login_attempts')
    c.execute('DROP TABLE IF EXISTS ip_tracking')

  
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')


    c.execute('''
        CREATE TABLE login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            username_tried TEXT,
            action_taken TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

 
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
