import pytest
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

def test_admin_access_denied_for_user(client, app):
    """Normal rolündeki kullanıcının admin sayfasına erişimi engellenmelidir."""
    with app.app_context():
        hashed_password = generate_password_hash("123", method='pbkdf2:sha256')
        user = User(email="normal@test.com", first_name="Normal", role="user", password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # 2. Giriş yap
        client.post('/login', data={'email': 'normal@test.com', 'password': '123'}, follow_redirects=True)
        
        # 3. Admin sayfasını dene
        response = client.get('/admin', follow_redirects=True)
        
        # 4. Kontrol: Giriş başarılı olmalı ama yetki hatası vermeli
        assert b"Bu i" in response.data and b"yetkiniz yok" in response.data


        

def test_admin_access_allowed_for_admin(client, app):
    """Admin rolündeki kullanıcının admin sayfasına erişimi serbest olmalıdır."""
    with app.app_context():
        # 1. Admin kullanıcıyı hashli şifreyle oluştur
        hashed_password = generate_password_hash("123", method='pbkdf2:sha256')
        admin = User(email="admin@test.com", first_name="Admin", role="admin", password=hashed_password)
        db.session.add(admin)
        db.session.commit()
        
        # 2. Giriş yap
        client.post('/login', data={'email': 'admin@test.com', 'password': '123'}, follow_redirects=True)
        
        # 3. Admin sayfasına git
        response = client.get('/admin')
        
       
        assert response.status_code == 200
        assert b"Admin Panel" in response.data # Sayfa başlığını veya içeriğini kontrol et




def test_user_registration(client):
    """Yeni kullanıcı kayıt rotasını test eder."""
    # 1. HATA DÜZELTMESİ: auth.py içinde form verileri 'firstName', 'password1' ve 'password2' olarak bekleniyor.
    data = {
        'email': 'yeni_kullanici@test.com',
        'firstName': 'Yeni',       # 'first_name' yerine 'firstName' olmalı
        'password1': 'password123', # 'password' yerine 'password1' olmalı
        'password2': 'password123'  # 'confirm_password' yerine 'password2' olmalı
    }
    
    # 2. HATA DÜZELTMESİ: auth.py içinde rota '/register' olarak tanımlanmış, '/auth/sign-up' değil.
    # Blueprint kullandığınız için URL tam yolu genellikle '/register' şeklindedir.
    response = client.post('/register', data=data, follow_redirects=True) 
    
    assert response.status_code == 200
    # Mesaj kontrolü: auth.py içinde 'Account created!' mesajı dönüyor
    assert b"Account created!" in response.data or b"Yeni" in response.data