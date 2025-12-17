# # models.py (var olan koduna ekle veya güncelle)
# from . import db
# from flask_login import UserMixin
# from sqlalchemy.sql import func
# from datetime import timedelta
# import pytz

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(35))
#     description = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     completed = db.Column(db.Boolean, default=False)
#     attachments = db.relationship('Attachment', backref='note', cascade='all, delete-orphan', lazy=True)
    
#     # AKTİF HALE GETİRİLEN VE EKLENEN ALANLAR
#     start_date = db.Column(db.DateTime(timezone=True), nullable=True)  # Görevin fiilen başlama tarihi
#     duration_days = db.Column(db.Integer, nullable=True)              # Kaç gün süreceği
#     deadline = db.Column(db.DateTime(timezone=True), nullable=True)    # Bitiş tarihi (Teslim)
    
#     @property
#     def remaining_time_status(self):
#         """Python ile kalan süreyi metin olarak hesaplar."""
#         if not self.deadline:
#             return None
        
#         now = datetime.now(pytz.utc) if self.deadline.tzinfo else datetime.now()
#         diff = self.deadline - now
        
#         if diff.total_seconds() < 0:
#             return "Süre Doldu"
        
#         days = diff.days
#         hours = diff.seconds // 3600
        
#         if days > 0:
#             return f"{days} gün {hours} saat kaldı"
#         return f"{hours} saat kaldı"

#     # @property
#     # def remaining_days(self):
#     #     """Kalan gün sayısını hesaplar."""
#     #     if self.deadline:
#     #         import pytz
#     #         from datetime import datetime
#     #         now = datetime.now(pytz.utc) if self.deadline.tzinfo else datetime.now()
#     #         delta = self.deadline - now
#     #         return max(0, delta.days)
#     #     return None
#       # YENİ ALANLAR
#     # start_date = db.Column(db.DateTime(timezone=True), nullable=True)  # Başlangıç tarihi
#     # duration_days = db.Column(db.Integer, nullable=True)  # Süre (gün cinsinden)
#     # deadline = db.Column(db.DateTime(timezone=True), nullable=True)  # Bitiş tarihi
    

    


# class Attachment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String(260), nullable=False)          # özgün dosya adı (kullanıcı görecek)
#     stored_name = db.Column(db.String(260), nullable=False)       # sunucuda saklanan benzersiz ad
#     mime_type = db.Column(db.String(120))
#     size = db.Column(db.Integer)                                  # byte cinsinden boyut
#     upload_date = db.Column(db.DateTime(timezone=True), default=func.now())
#     note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True)
#     password = db.Column(db.String(150))
#     first_name = db.Column(db.String(150))
#     role = db.Column(db.String(50), default="user")
#     notes = db.relationship('Note', backref='owner', lazy=True)

#     def has_role(self, *roles):
#         return self.role in roles
#     @property
#     def owner_name(self):
#         """Kolay kullanım için: sahibi adı yoksa e-posta veya Bilinmiyor döner."""
#         if getattr(self, "owner", None):
#             return self.owner.first_name or self.owner.email or "Bilinmiyor"
#         return "Bilinmiyor"



from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta # DATETIME EKLENDİ
import pytz

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(35))
    description = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)
    attachments = db.relationship('Attachment', backref='note', cascade='all, delete-orphan', lazy=True)
    
    # GÖREV SÜRE BİLGİLERİ
    start_date = db.Column(db.DateTime(timezone=True), nullable=True)  # Başlama tarihi
    duration_days = db.Column(db.Integer, nullable=True)              # Süre (gün)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True)    # Teslim tarihi
    
    @property
    def remaining_time_status(self):
        """Python ile kalan süreyi metin olarak hesaplar."""
        if not self.deadline:
            return None
        
        # Zaman dilimi kontrolü
        now = datetime.now(pytz.utc) if self.deadline.tzinfo else datetime.now()
        diff = self.deadline - now
        
        if diff.total_seconds() < 0:
            return "Süre Doldu"
        
        days = diff.days
        hours = diff.seconds // 3600
        
        if days > 0:
            return f"{days} gün {hours} saat kaldı"
        return f"{hours} saat kaldı"

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(260), nullable=False)
    stored_name = db.Column(db.String(260), nullable=False)
    mime_type = db.Column(db.String(120))
    size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime(timezone=True), default=func.now())
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String(50), default="user")
    notes = db.relationship('Note', backref='owner', lazy=True)

    def has_role(self, *roles):
        return self.role in roles

    @property
    def owner_name(self):
        return self.first_name or self.email or "Bilinmiyor"