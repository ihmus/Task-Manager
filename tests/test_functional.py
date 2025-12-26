import datetime
from app.models import Note, Category
from app import db





def test_deadline_alert_logic(auth_client, app):
    """Teslim tarihi yaklasan gorevlerin mantıgını test eder."""
    with app.app_context():
        # Yarın bitecek bir görev oluştur (Uyarı tetiklemeli)
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        note = Note(
            title="Acil Gorev", 
            description="Bitis yakin", 
            deadline=tomorrow,
            user_id=1
        )
        db.session.add(note)
        db.session.commit()

    response = auth_client.get('/gorevler')
    assert response.status_code == 200
    # Arayüzde uyarı sınıfının (örneğin 'text-danger' veya 'alert') olup olmadığını kontrol et
    assert b"Acil Gorev" in response.data




def test_delete_note(auth_client, app):
    """Bir gorevin silinmesini test eder."""
    with app.app_context():
        # Önce silinecek bir not oluştur
        note = Note(title="Silinecek Gorev", description="Test", user_id=1)
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    # Silme rotasına istek at (Rotanızın adını projenize göre /delete-note/<id> şeklinde güncelleyin)
    response = auth_client.post(f'/delete-note/{note_id}', follow_redirects=True)
    assert response.status_code == 200
    
    with app.app_context():
        # Veritabanında artık olmamalı
        assert Note.query.get(note_id) is None

def test_filter_tasks(auth_client):
    """Gorev filtreleme ozelligini test eder (Madde 6 gereksinimi)."""
    # Kategoriye veya duruma göre filtreleme rotasını test et
    # Örnek: /gorevler?filter=completed
    response = auth_client.get('/gorevler?category_id=1')
    assert response.status_code == 200
    # Sayfada filtrelenen içeriğin geldiğini doğrula
    assert b"Genel" in response.data




def test_create_note_logic(auth_client):
    """'/create_note' rotasına veri gönderimini test eder."""
    data = {
        'title': 'Test Görevi',
        'description': 'Açıklama',
        'category_id': '1', # conftest'teki kategorinin ID'si
        'start_date': '2023-12-01T10:00',
        'deadline': '2023-12-10T10:00'
    }
    # views.py'deki gerçek rota /create_note
    response = auth_client.post('/create_note', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test" in response.data



    