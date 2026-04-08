import email_service

print("📧 Test maili gönderiliyor...")
success = email_service.send_anomaly_alert("127.0.0.1 (TEST)", 99, 99)

if success:
    print("✅ Test Başarılı! Lütfen gelen kutunuzu (ve Spam klasörünü) kontrol edin.")
else:
    print("❌ Test Başarısız. Şifre veya mail ayarlarını kontrol edin.")
