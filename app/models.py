""" 
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(35))
    description=db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False) 
####################    ^      #######################
#                       |      #######################
#                       |      #######################
#                       |      #######################
#                       |      #######################
#    userin id bilgisinide bu tabloya veriyoruz      #
######################################################

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note') # Burada ilişki verdik ileride user üzerinden ulaşabilmek için

""" 

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    duration_months = db.Column(db.Integer)  # 🆕 görev süresi (ay cinsinden)
    end_date = db.Column(db.DateTime(timezone=True))  # 🆕 bitiş tarihi
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)

    def calculate_progress(self):
        """Görev süresinin yüzde kaçının geçtiğini hesaplar"""
        if not self.end_date or not self.date:
            return 0
        total_days = (self.end_date - self.date).days
        passed_days = (datetime.now() - self.date).days
        if total_days <= 0:
            return 100
        return min(max((passed_days / total_days) * 100, 0), 100)

    def remaining_time(self):
        """Kalan süreyi ay ve gün cinsinden döndürür"""
        if not self.end_date:
            return "Süre belirtilmemiş"
        now = datetime.now()
        if now >= self.end_date:
            return "Süre doldu!"
        delta = relativedelta(self.end_date, now)
        if delta.months == 0 and delta.days == 0:
            return "Son gün!"
        return f"{delta.months} ay {delta.days} gün"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
