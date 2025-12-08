# models.py (var olan koduna ekle veya güncelle)
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(35))
    description = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)
    attachments = db.relationship('Attachment', backref='note', cascade='all, delete-orphan', lazy=True)

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(260), nullable=False)          # özgün dosya adı (kullanıcı görecek)
    stored_name = db.Column(db.String(260), nullable=False)       # sunucuda saklanan benzersiz ad
    mime_type = db.Column(db.String(120))
    size = db.Column(db.Integer)                                  # byte cinsinden boyut
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
