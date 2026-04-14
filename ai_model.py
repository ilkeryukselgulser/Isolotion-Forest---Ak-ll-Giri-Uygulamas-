import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import random


X_train = []

for _ in range(1000):
    hour = random.randint(8, 23)      
    attempts = random.randint(1, 2)  
    X_train.append([hour, attempts])


for _ in range(50):
    hour = random.randint(0, 5)       
    attempts = random.randint(5, 15) 
    X_train.append([hour, attempts])

X_train = np.array(X_train)


clf = IsolationForest(contamination=0.05, random_state=42)
clf.fit(X_train)


with open('anomaly_model.pkl', 'wb') as f:
    pickle.dump(clf, f)

print("Yapay Zeka Modeli Eğitildi ve 'anomaly_model.pkl' olarak kaydedildi! 🤖")


print("\n--- Test Sonuçları ---")
test_cases = [
    [14, 1], 
    [0, 10],  
    [3, 5]     
]

for case in test_cases:
   
    pred = clf.predict([case])[0]
    durum = "✅ Normal" if pred == 1 else "🚨 ANOMALİ (Saldırı Şüphesi)"
    print(f"Saat: {case[0]}, Deneme: {case[1]} -> Sonuç: {durum}")
