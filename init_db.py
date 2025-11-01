from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Veritabanı ve tablolar başarıyla oluşturuldu!") 

# her defasında tablo oluşturuldu mu oluşturulmadı mı anlamam için bu kodu yazdım