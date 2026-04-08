import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import random

# --- 1. SAHTE VERİ ÜRETİMİ (EĞİTİM İÇİN) ---
# Senaryo: Normal kullanıcılar gündüz (08:00 - 23:00) arası giriş yapar.
# Ve dakikada en fazla 1-2 deneme yaparlar.

# Veri Formatı: [Günün Saati (0-24), Dakikadaki Deneme Sayısı]
X_train = []

# 1000 tane "Normal" davranış ekleyelim
for _ in range(1000):
    hour = random.randint(8, 23)      # Sabah 8, Gece 11 arası
    attempts = random.randint(1, 2)   # 1 veya 2 deneme
    X_train.append([hour, attempts])

# 50 tane "Anormal" (Saldırı) davranışı ekleyelim
for _ in range(50):
    hour = random.randint(0, 5)       # Gece yarısı 00:00 - 05:00 arası
    attempts = random.randint(5, 15)  # Hızlı hızlı 5-15 deneme
    X_train.append([hour, attempts])

X_train = np.array(X_train)

# --- 2. MODEL EĞİTİMİ (ISOLATION FOREST) ---
# contamination=0.05 -> Verinin %5'i anomalidir varsayımı
clf = IsolationForest(contamination=0.05, random_state=42)
clf.fit(X_train)

# --- 3. MODELİ KAYDET ---
# Flask içinde tekrar tekrar eğitmemek için modeli dosyaya kaydediyoruz.
with open('anomaly_model.pkl', 'wb') as f:
    pickle.dump(clf, f)

print("Yapay Zeka Modeli Eğitildi ve 'anomaly_model.pkl' olarak kaydedildi! 🤖")

# --- 4. TEST ---
print("\n--- Test Sonuçları ---")
test_cases = [
    [14, 1],   # Öğleden sonra saat 2, 1 deneme -> (NORMAL OLMALI)
    [0, 10],   # Gece saat 00, 10 deneme -> (ANOMALİ OLMALI)
    [3, 5]     # Gece saat 3, 5 deneme -> (ANOMALİ OLMALI)
]

for case in test_cases:
    # Predict: 1 (Normal), -1 (Anomali)
    pred = clf.predict([case])[0]
    durum = "✅ Normal" if pred == 1 else "🚨 ANOMALİ (Saldırı Şüphesi)"
    print(f"Saat: {case[0]}, Deneme: {case[1]} -> Sonuç: {durum}")