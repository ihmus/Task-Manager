import pytest
from app.models import User, Note
from app import db

def test_new_user(app):
    """Yeni bir kullanıcı oluşturulmasını test et."""
    with app.app_context():
        user = User(email="model@test.com", first_name="Model", password="password")
        db.session.add(user)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(email="model@test.com").first()
        assert retrieved_user is not None
        assert retrieved_user.first_name == "Model"




def test_note_creation(app):
    """Not oluşturma ve veritabanı kaydını test et."""
    with app.app_context():
        note = Note(title="Test Başlığı", description="Test İçeriği")
        db.session.add(note)
        db.session.commit()
        
        retrieved_note = Note.query.filter_by(title="Test Başlığı").first()
        assert retrieved_note is not None
        assert retrieved_note.description == "Test İçeriği"