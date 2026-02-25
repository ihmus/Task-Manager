import pytest
from app import create_app, db
from app.models import User, Category
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        db.create_all()
        # Test için bir kategori ekleyelim
        cat = Category(name="Genel")
        db.session.add(cat)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """Giriş yapmış bir kullanıcı simüle eder."""
    with app.app_context():
        # Şifreyi auth.py'deki formata uygun hashliyoruz
        hashed_pw = generate_password_hash("123456", method='pbkdf2:sha256')
        user = User(email="test@test.com", first_name="Test", role="admin", password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        
        # auth.py'deki login rotasına post yapıyoruz
        client.post('/login', data={'email': 'test@test.com', 'password': '123456'}, follow_redirects=True)
        return client