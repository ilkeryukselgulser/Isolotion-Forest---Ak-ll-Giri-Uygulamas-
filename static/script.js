const passwordInput = document.getElementById('passwordInput');
const strengthBar = document.getElementById('strengthBar');
const strengthText = document.getElementById('strengthText');

// Regex Listesi
const checks = {
    length: /.{8,}/,
    lower: /[a-z]/,
    upper: /[A-Z]/,
    num: /\d/,
    special: /[!@#$%^&*(),.?":{}|<>]/
};

passwordInput.addEventListener('input', function() {
    const val = passwordInput.value;
    let score = 0;

    // Her kuralı tek tek kontrol et ve UI güncelle
    // 1. Uzunluk
    if(checks.length.test(val)) {
        document.getElementById('req-length').innerHTML = "🟢 En az 8 Karakter";
        document.getElementById('req-length').classList.add('valid');
        score += 20;
    } else {
        document.getElementById('req-length').innerHTML = "🔴 En az 8 Karakter";
        document.getElementById('req-length').classList.remove('valid');
    }

    // 2. Küçük Harf
    if(checks.lower.test(val)) {
        document.getElementById('req-lower').innerHTML = "🟢 Küçük Harf (a-z)";
        document.getElementById('req-lower').classList.add('valid');
        score += 20;
    } else {
        document.getElementById('req-lower').innerHTML = "🔴 Küçük Harf (a-z)";
        document.getElementById('req-lower').classList.remove('valid');
    }

    // 3. Büyük Harf
    if(checks.upper.test(val)) {
        document.getElementById('req-upper').innerHTML = "🟢 Büyük Harf (A-Z)";
        document.getElementById('req-upper').classList.add('valid');
        score += 20;
    } else {
        document.getElementById('req-upper').innerHTML = "🔴 Büyük Harf (A-Z)";
        document.getElementById('req-upper').classList.remove('valid');
    }

    // 4. Rakam
    if(checks.num.test(val)) {
        document.getElementById('req-num').innerHTML = "🟢 Rakam (0-9)";
        document.getElementById('req-num').classList.add('valid');
        score += 20;
    } else {
        document.getElementById('req-num').innerHTML = "🔴 Rakam (0-9)";
        document.getElementById('req-num').classList.remove('valid');
    }

    // 5. Özel Karakter
    if(checks.special.test(val)) {
        document.getElementById('req-special').innerHTML = "🟢 Özel Karakter (!@#..)";
        document.getElementById('req-special').classList.add('valid');
        score += 20;
    } else {
        document.getElementById('req-special').innerHTML = "🔴 Özel Karakter (!@#..)";
        document.getElementById('req-special').classList.remove('valid');
    }

    // Bar Genişliğini ve Rengini Ayarla
    strengthBar.style.width = score + '%';

    if(score < 40) {
        strengthBar.style.backgroundColor = "red";
        strengthText.innerText = "Şifre Gücü: Zayıf";
    } else if(score < 80) {
        strengthBar.style.backgroundColor = "orange";
        strengthText.innerText = "Şifre Gücü: Orta";
    } else {
        strengthBar.style.backgroundColor = "green";
        strengthText.innerText = "Şifre Gücü: Güçlü";
    }



    // --- ŞİFREYİ GÖSTER / GİZLE ÖZELLİĞİ ---
const togglePassword = document.querySelector('#togglePassword');
const passwordField = document.querySelector('#passwordInput');

togglePassword.addEventListener('click', function () {
    // 1. Input tipini değiştir (password <-> text)
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    
    // 2. İkonu değiştir (Göz açık <-> Göz üstü çizili)
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
});
});