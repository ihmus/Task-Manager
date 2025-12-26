


#  Dosya Yükleme (Attachment) Testi
# Bu test, bir göreve dosya eklendiğinde sistemin bunu kabul edip etmediğini ölçer. io.BytesIO kullanarak sanal bir dosya oluşturacağız,
# böylece bilgisayarına gerçek bir dosya kaydetmek zorunda kalmayacak


import io
from app.models import Note, Attachment
from app import db

def test_file_upload_with_note(auth_client, app):
    """Görev oluştururken dosya yükleme işlemini test et."""
    with app.app_context():
        # Sanal bir dosya oluşturuyoruz (İçinde 'test verisi' yazan bir text dosyası gibi)
        data = {
            'title': 'Dosyalı Görev',
            'description': 'Dosya eklenmiş açıklama',
            'category_id': '1',
            'start_date': '2023-12-01T10:00',
            'deadline': '2023-12-10T10:00',
            'file': (io.BytesIO(b"deneme icerigi"), 'test_dosyasi.txt')
        }
        
        # Dosya gönderirken 'content_type' belirtmek önemlidir (multipart/form-data)
        response = auth_client.post('/create_note', data=data, content_type='multipart/form-data', follow_redirects=True)
        
        assert response.status_code == 200
        
        # Veritabanında Attachment kaydı oluşmuş mu bak
        attachment = Attachment.query.first()
        assert attachment is not None
        assert attachment.filename == 'test_dosyasi.txt'