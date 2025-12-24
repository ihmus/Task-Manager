import pytest
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

def test_admin_access_denied_for_user(client, app):
    """Normal rolündeki kullanıcının admin sayfasına erişimi engellenmelidir."""
    with app.app_context():
        # 1. Şifreyi projenin kullandığı yöntemle hashleyerek kaydet
        hashed_password = generate_password_hash("123", method='pbkdf2:sha256')
        user = User(email="normal@test.com", first_name="Normal", role="user", password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # 2. Giriş yap
        client.post('/login', data={'email': 'normal@test.com', 'password': '123'}, follow_redirects=True)
        
        # 3. Admin sayfasını dene
        response = client.get('/admin', follow_redirects=True)
        
        # 4. Kontrol: Giriş başarılı olmalı ama yetki hatası vermeli
        # Mesajdaki Türkçe karakterler için 'Bu i' kısmını kontrol etmek daha güvenlidir
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
        
        # 4. Kontrol: Yönlendirme olmadan direkt 200 OK almalıyız
        assert response.status_code == 200
        assert b"Admin Panel" in response.data # Sayfa başlığını veya içeriğini kontrol et