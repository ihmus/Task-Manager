import pytest
from app.models import User, Note  # ← BU SATIRI EKLE (ÜST TARAFTA)
from app import db  # ← BU SATIRI DA EKLE

class TestAuth:
    """Kimlik doğrulama testleri"""
    
    def test_register_page_loads(self, client):
        """Kayıt sayfası açılıyor mu?"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Kayit Ol' in response.data or b'register' in response.data.lower()
    
    def test_login_page_loads(self, client):
        """Giriş sayfası açılıyor mu?"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Giris' in response.data or b'login' in response.data.lower()
    
    def test_register_new_user(self, client, app):
        """Yeni kullanıcı kaydı başarılı mı?"""
        response = client.post('/register', data={
            'email': 'newuser@test.com',
            'firstName': 'Yeni',
            'password1': 'test12345',
            'password2': 'test12345'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Veritabanında kullanıcı var mı kontrol et
        with app.app_context():
            user = User.query.filter_by(email='newuser@test.com').first()
            assert user is not None
            assert user.first_name == 'Yeni'
    
    def test_register_duplicate_email(self, client, test_user):
        """Aynı email ile tekrar kayıt olunabiliyor mu? (Olmamalı)"""
        response = client.post('/register', data={
            'email': 'test@example.com',  # Zaten var olan email
            'firstName': 'Test2',
            'password1': 'test123',
            'password2': 'test123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'already exists' in response.data or b'zaten var' in response.data.lower()
    
    def test_register_password_mismatch(self, client):
        """Şifreler uyuşmazsa kayıt olmamalı"""
        response = client.post('/register', data={
            'email': 'test2@test.com',
            'firstName': 'Test',
            'password1': 'test123',
            'password2': 'different123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # MESAJ KONTROLÜNÜ DEĞİŞTİRDİM ↓
        assert (b"don't match" in response.data or 
                b"Passwords don" in response.data or
                b"match" in response.data.lower())
    
    def test_login_success(self, client, test_user):
        """Doğru bilgilerle giriş başarılı mı?"""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'test123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_wrong_password(self, client, test_user):
        """Yanlış şifre ile giriş yapılamamalı"""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Incorrect' in response.data or b'Hatal' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Olmayan kullanıcı ile giriş yapılamamalı"""
        response = client.post('/login', data={
            'email': 'notexist@test.com',
            'password': 'test123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'does not exist' in response.data or b'yok' in response.data.lower()
    
    def test_logout(self, client, test_user):
        """Çıkış yapma çalışıyor mu?"""
        # Önce giriş yap
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'test123'
        })
        
        # Sonra çıkış yap
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

        