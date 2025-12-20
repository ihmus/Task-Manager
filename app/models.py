from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
import pytz

# -------------------------------
# CATEGORY MODEL
# -------------------------------

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(30), default="indigo")  # UI rengi

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

    # ilişkiler
    notes = db.relationship(
        'Note',
        backref='category',
        lazy=True,
        cascade='all, delete'
    )

    def __repr__(self):
        return f"<Category {self.name}>"

# -------------------------------
# NOTE MODEL
# -------------------------------

class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(35))
    description = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)

    # 🔹 KATEGORİ
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    # 🔹 EKLER
    attachments = db.relationship(
        'Attachment',
        backref='note',
        cascade='all, delete-orphan',
        lazy=True
    )

    # 🔹 GÖREV ZAMAN BİLGİLERİ
    start_date = db.Column(db.DateTime(timezone=True), nullable=True)
    duration_days = db.Column(db.Integer, nullable=True)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True)

    @property
    def deadline_status(self):
        if self.completed:
            return None

        if not self.deadline:
            return "Teslim tarihi yok"

        now = datetime.now(pytz.utc)
        deadline = self.deadline

        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=pytz.utc)

        diff = deadline - now

        if diff.total_seconds() < 0:
            return "⛔ Gecikti"

        days = diff.days
        hours = diff.seconds // 3600

        if days > 0:
            return f"⏳ {days}g {hours}s kaldı"
        return f"⏳ {hours} saat kaldı"

    @property
    def category_color(self):
        return self.category.color if self.category else "gray"

# -------------------------------
# ATTACHMENT MODEL
# -------------------------------
class Attachment(db.Model):
    __tablename__ = "attachment"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(260), nullable=False)
    stored_name = db.Column(db.String(260), nullable=False)
    mime_type = db.Column(db.String(120))
    size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime(timezone=True), default=func.now())

    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)

# -------------------------------
# USER MODEL
# -------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String(50), default="user")

    notes = db.relationship(
        'Note',
        backref='owner',
        lazy=True
    )

    def has_role(self, *roles):
        return self.role in roles

    @property
    def owner_name(self):
        return self.first_name or self.email or "Bilinmiyor"
