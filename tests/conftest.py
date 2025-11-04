import pytest
import sys
import os

# Proje yolunu ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Note

@pytest.fixture
def app():
    """Test için Flask uygulaması oluştur"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client oluştur"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Test kullanıcısı oluştur - ID'yi döndür"""
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        user = User(
            email='test@example.com',
            first_name='Test',
            password=generate_password_hash('test123', method='pbkdf2:sha256')
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # ← ID'yi kaydet
        db.session.expunge(user)  # ← Session'dan çıkar
    
    # ID'yi döndür, obje değil
    return user_id