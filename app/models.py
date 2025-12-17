# # models.py (var olan koduna ekle veya güncelle)
# from . import db
# from flask_login import UserMixin
# from sqlalchemy.sql import func
# from datetime import timedelta

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(35))
#     description = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     completed = db.Column(db.Boolean, default=False)
#     attachments = db.relationship('Attachment', backref='note', cascade='all, delete-orphan', lazy=True)


#       # YENİ ALANLAR
#     start_date = db.Column(db.DateTime(timezone=True), nullable=True)  # Başlangıç tarihi
#     duration_days = db.Column(db.Integer, nullable=True)  # Süre (gün cinsinden)
#     deadline = db.Column(db.DateTime(timezone=True), nullable=True)  # Bitiş tarihi
    

#      user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     completed = db.Column(db.Boolean, default=False)
#     attachments = db.relationship('Attachment', backref='note', cascade='all, delete-orphan', lazy=True)

#     def calculate_deadline(self):
#         """Başlangıç tarihi ve süreye göre deadline hesapla"""
#         if self.start_date and self.duration_days:
#             return self.start_date + timedelta(days=self.duration_days)
#         return None

#     def get_duration_text(self):
#         """Süreyi okunabilir formatta döndür"""
#         if not self.duration_days:
#             return "Süre belirlenmedi"
        
#         days = self.duration_days
        
#         if days >= 365:
#             years = days // 365
#             return f"{years} yıl"
#         elif days >= 30:
#             months = days // 30
#             remaining_days = days % 30
#             if remaining_days > 0:
#                 return f"{months} ay {remaining_days} gün"
#             return f"{months} ay"
#         elif days >= 7:
#             weeks = days // 7
#             remaining_days = days % 7
#             if remaining_days > 0:
#                 return f"{weeks} hafta {remaining_days} gün"
#             return f"{weeks} hafta"
#         else:
#             return f"{days} gün"

#     def get_progress_percentage(self):
#         """Görevin ne kadarının geçtiğini yüzde olarak hesapla"""
#         if not self.start_date or not self.deadline:
#             return 0
        
#         import pytz
#         from datetime import datetime
        
#         now = datetime.now(pytz.utc)
#         start = self.start_date
#         end = self.deadline
        
#         if start.tzinfo is None:
#             start = start.replace(tzinfo=pytz.utc)
#         if end.tzinfo is None:
#             end = end.replace(tzinfo=pytz.utc)
        
#         total_duration = (end - start).total_seconds()
#         elapsed = (now - start).total_seconds()
        
#         if total_duration <= 0:
#             return 0
        
#         percentage = (elapsed / total_duration) * 100
#         return min(max(percentage, 0), 100)  # 0-100 arası sınırla

#     def get_status_color(self):
#         """Tamamlanma durumuna göre renk döndürür"""
#         if self.completed:
#             return 'bg-green-100 border-green-500'
#         else:
#             if not self.deadline:
#                 return 'bg-blue-100 border-blue-500'
            
#             import pytz
#             from datetime import datetime
            
#             now = datetime.now(pytz.utc)
#             deadline = self.deadline
            
#             if deadline.tzinfo is None:
#                 deadline = deadline.replace(tzinfo=pytz.utc)
            
#             time_left = (deadline - now).total_seconds()
            
#             if time_left < 0:
#                 return 'bg-red-100 border-red-500'
#             elif time_left < 86400:
#                 return 'bg-orange-100 border-orange-500'
#             elif time_left < 259200:
#                 return 'bg-yellow-100 border-yellow-500'
#             else:
#                 return 'bg-blue-100 border-blue-500'

#     def get_status_badge(self):
#         """Durum badge'i döndürür"""
#         if self.completed:
#             return {
#                 'text': 'Tamamlandı',
#                 'class': 'bg-green-500 text-white'
#             }
#         else:
#             if not self.deadline:
#                 return {
#                     'text': 'Devam Ediyor',
#                     'class': 'bg-blue-500 text-white'
#                 }
            
#             import pytz
#             from datetime import datetime
            
#             now = datetime.now(pytz.utc)
#             deadline = self.deadline
            
#             if deadline.tzinfo is None:
#                 deadline = deadline.replace(tzinfo=pytz.utc)
            
#             time_left = (deadline - now).total_seconds()
            
#             if time_left < 0:
#                 return {
#                     'text': 'Gecikti',
#                     'class': 'bg-red-500 text-white'
#                 }
#             elif time_left < 86400:
#                 return {
#                     'text': 'Acil',
#                     'class': 'bg-orange-500 text-white'
#                 }
#             elif time_left < 259200:
#                 return {
#                     'text': 'Yaklaşıyor',
#                     'class': 'bg-yellow-500 text-white'
#                 }
#             else:
#                 return {
#                     'text': 'Devam Ediyor',
#                     'class': 'bg-blue-500 text-white'
#                 }

#     def get_deadline_alert_color(self):
#         """Deadline'a göre alert rengi döndürür"""
#         if not self.deadline:
#             return 'gray'
        
#         if self.completed:
#             return 'green'
        
#         import pytz
#         from datetime import datetime
        
#         now = datetime.now(pytz.utc)
#         deadline = self.deadline
        
#         if deadline.tzinfo is None:
#             deadline = deadline.replace(tzinfo=pytz.utc)
        
#         time_left = (deadline - now).total_seconds()
        
#         if time_left < 0:
#             return 'red'
#         elif time_left < 86400:
#             return 'orange'
#         elif time_left < 259200:
#             return 'yellow'
#         else:
#             return 'green'

#     def get_deadline_message(self):
#         """Deadline için mesaj döndürür"""
#         if not self.deadline:
#             return 'Deadline yok'
        
#         if self.completed:
#             return 'Tamamlandı'
        
#         import pytz
#         from datetime import datetime
        
#         now = datetime.now(pytz.utc)
#         deadline = self.deadline
        
#         if deadline.tzinfo is None:
#             deadline = deadline.replace(tzinfo=pytz.utc)
        
#         time_left = (deadline - now).total_seconds()
        
#         if time_left < 0:
#             days_over = abs(int(time_left // 86400))
#             return f'{days_over} gün gecikti'
        
#         days_left = int(time_left // 86400)
#         hours_left = int((time_left % 86400) // 3600)
        
#         if days_left > 0:
#             return f'{days_left} gün kaldı'
#         elif hours_left > 0:
#             return f'{hours_left} saat kaldı'
#         else:
#             minutes_left = int((time_left % 3600) // 60)
#             return f'{minutes_left} dakika kaldı'


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
from datetime import timedelta
import pytz # YENİ: get_progress_percentage ve diğer metodlar için eklendi
from datetime import datetime # YENİ: get_progress_percentage ve diğer metodlar için eklendi

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200)) # Başlık 35 karakterden 200'e çıkarıldı (views.py ile uyumlu olması için)
    description = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    
    # Yeni Alanlar - Doğru Girintiyle Eklenmiştir
    start_date = db.Column(db.DateTime(timezone=True), nullable=True)   # Başlangıç tarihi
    duration_days = db.Column(db.Integer, nullable=True)    # Süre (gün cinsinden)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True)     # Bitiş tarihi
    
    # İlişkili Alanlar - Tekrar tanımlanmadığından emin olundu
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)
    attachments = db.relationship('Attachment', backref='note', cascade='all, delete-orphan', lazy=True)

    def calculate_deadline(self):
        """Başlangıç tarihi ve süreye göre deadline hesapla"""
        if self.start_date and self.duration_days:
            return self.start_date + timedelta(days=self.duration_days)
        return None

    def get_duration_text(self):
        """Süreyi okunabilir formatta döndür"""
        if not self.duration_days:
            return "Süre belirlenmedi"
        
        days = self.duration_days
        
        if days >= 365:
            years = days // 365
            return f"{years} yıl"
        elif days >= 30:
            months = days // 30
            remaining_days = days % 30
            if remaining_days > 0:
                return f"{months} ay {remaining_days} gün"
            return f"{months} ay"
        elif days >= 7:
            weeks = days // 7
            remaining_days = days % 7
            if remaining_days > 0:
                return f"{weeks} hafta {remaining_days} gün"
            return f"{weeks} hafta"
        else:
            return f"{days} gün"

    def get_progress_percentage(self):
        """Görevin ne kadarının geçtiğini yüzde olarak hesapla"""
        if not self.start_date or not self.deadline:
            return 0
        
        # İç import yerine dosya başında import edildi
        
        now = datetime.now(pytz.utc)
        start = self.start_date
        end = self.deadline
        
        # Zira zaman dilimi (timezone) bilgisi eksik olabilir
        if start.tzinfo is None:
            start = start.replace(tzinfo=pytz.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=pytz.utc)
        
        total_duration = (end - start).total_seconds()
        elapsed = (now - start).total_seconds()
        
        if total_duration <= 0:
            # Deadline geçmişse veya başlangıç tarihi daha büyükse
            if now > end:
                return 100 # Süre bitti
            return 0 # Süre daha başlamadı

        
        percentage = (elapsed / total_duration) * 100
        return min(max(percentage, 0), 100)  # 0-100 arası sınırla

    def get_status_color(self):
        """Tamamlanma durumuna göre renk döndürür"""
        if self.completed:
            return 'bg-green-100 border-green-500'
        else:
            if not self.deadline:
                return 'bg-blue-100 border-blue-500'
            
            # İç import yerine dosya başında import edildi
            
            now = datetime.now(pytz.utc)
            deadline = self.deadline
            
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=pytz.utc)
            
            time_left = (deadline - now).total_seconds()
            
            if time_left < 0:
                return 'bg-red-100 border-red-500'
            elif time_left < 86400:
                return 'bg-orange-100 border-orange-500'
            elif time_left < 259200:
                return 'bg-yellow-100 border-yellow-500'
            else:
                return 'bg-blue-100 border-blue-500'

    def get_status_badge(self):
        """Durum badge'i döndürür"""
        if self.completed:
            return {
                'text': 'Tamamlandı',
                'class': 'bg-green-500 text-white'
            }
        else:
            if not self.deadline:
                return {
                    'text': 'Devam Ediyor',
                    'class': 'bg-blue-500 text-white'
                }
            
            # İç import yerine dosya başında import edildi
            
            now = datetime.now(pytz.utc)
            deadline = self.deadline
            
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=pytz.utc)
            
            time_left = (deadline - now).total_seconds()
            
            if time_left < 0:
                return {
                    'text': 'Gecikti',
                    'class': 'bg-red-500 text-white'
                }
            elif time_left < 86400:
                return {
                    'text': 'Acil',
                    'class': 'bg-orange-500 text-white'
                }
            elif time_left < 259200:
                return {
                    'text': 'Yaklaşıyor',
                    'class': 'bg-yellow-500 text-white'
                }
            else:
                return {
                    'text': 'Devam Ediyor',
                    'class': 'bg-blue-500 text-white'
                }

    def get_deadline_alert_color(self):
        """Deadline'a göre alert rengi döndürür"""
        if not self.deadline:
            return 'gray'
        
        if self.completed:
            return 'green'
        
        # İç import yerine dosya başında import edildi
        
        now = datetime.now(pytz.utc)
        deadline = self.deadline
        
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=pytz.utc)
        
        time_left = (deadline - now).total_seconds()
        
        if time_left < 0:
            return 'red'
        elif time_left < 86400:
            return 'orange'
        elif time_left < 259200:
            return 'yellow'
        else:
            return 'green'

    def get_deadline_message(self):
        """Deadline için mesaj döndürür"""
        if not self.deadline:
            return 'Deadline yok'
        
        if self.completed:
            return 'Tamamlandı'
        
        # İç import yerine dosya başında import edildi
        
        now = datetime.now(pytz.utc)
        deadline = self.deadline
        
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=pytz.utc)
        
        time_left = (deadline - now).total_seconds()
        
        if time_left < 0:
            days_over = abs(int(time_left // 86400))
            if days_over == 0:
                 return "Bugün Gecikti"
            return f'{days_over} gün gecikti'
        
        days_left = int(time_left // 86400)
        hours_left = int((time_left % 86400) // 3600)
        
        if days_left > 0:
            return f'{days_left} gün kaldı'
        elif hours_left > 0:
            return f'{hours_left} saat kaldı'
        else:
            minutes_left = max(1, int((time_left % 3600) // 60)) # Minimum 1 dakika göster
            return f'{minutes_left} dakika kaldı'


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(260), nullable=False)        # özgün dosya adı (kullanıcı görecek)
    stored_name = db.Column(db.String(260), nullable=False)     # sunucuda saklanan benzersiz ad
    mime_type = db.Column(db.String(120))
    size = db.Column(db.Integer)                                # byte cinsinden boyut
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
        """Kolay kullanım için: sahibi adı yoksa e-posta veya Bilinmiyor döner."""
        if getattr(self, "owner", None):
            return self.owner.first_name or self.owner.email or "Bilinmiyor"
        return "Bilinmiyor"