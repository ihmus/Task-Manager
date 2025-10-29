from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from datetime import datetime
from dateutil.relativedelta import relativedelta
from . import db
import pytz
import json

views = Blueprint('views', __name__)

#13.satırdan itibaren schule ekledi

from dateutil.relativedelta import relativedelta #bu satırı da yukardan silmeyi unutma eğer kodların tamamını silersen

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')
        months = request.form.get('months')  # 🆕 yeni alan

        if len(note) < 1:
            flash('Note is too short!', category='error')
        elif not months or not months.isdigit():
            flash('Lütfen ay cinsinden geçerli bir süre giriniz!', category='error')
        else:
            months = int(months)
            start_date = datetime.now()
            end_date = start_date + relativedelta(months=months)

            new_note = Note(
                data=note,
                duration_months=months,
                end_date=end_date,
                user_id=current_user.id
            )
            db.session.add(new_note)
            db.session.commit()
            flash('Görev eklendi!', category='success')
            return redirect(url_for('views.home'))

    notes_with_time = []
    for note in current_user.notes:
        progress = note.calculate_progress()
        remaining = note.remaining_time()

        if progress < 50:
            color = "green"
        elif progress < 80:
            color = "orange"
        else:
            color = "red"

        notes_with_time.append({
            'id': note.id,
            'data': note.data,
            'color': color,
            'progress': round(progress),
            'remaining': remaining
        })

    return render_template("index.html", notes=notes_with_time)






"""
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    ##############################################
    #              Not Ekleme Kısmı              #
    ##############################################

    if request.method == 'POST': 
        note = request.form.get('note')# Html üzerinden notu al 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #not için şema hazırla
            db.session.add(new_note) # Databaseye notu ekle
            db.session.commit()
            flash('Note added!', category='success')
            return redirect(url_for('views.home'))

    ################################################
    #    Mevcut Kullanıcı notlarıyla İşlem         #
    ################################################
    notes_with_time = []
    for note in current_user.notes:
        note_date = note.date
        if note_date.tzinfo is None:
            # naive ise UTC yap
            note_date = note_date.replace(tzinfo=pytz.utc)
        delta = datetime.now(pytz.utc) - note_date
        seconds = int(delta.total_seconds())
        if seconds < 60:
            time_passed = f"{seconds} seconds ago"
            note.color = "green"
        elif seconds < 3600:
            time_passed = f"{seconds // 60} minutes ago"
            note.color = "orange"
        elif seconds < 86400:
            time_passed = f"{seconds // 3600} hours ago"
            note.color = "red"
        else:
            time_passed = f"{seconds // 86400} days ago"
            note.color = "brown"

        notes_with_time.append({
            'id': note.id,
            'data': note.data,
            'time_passed': time_passed,
            'color':note.color,
        })

    return render_template("index.html",notes=notes_with_time)

"""
    
@views.route('/calisanlar', methods=['GET', 'POST'])
@login_required
def calisanlar():
    """Profilim / Çalışan listesi"""
    # Çalışan listesi veya profil bilgisi
    notes_with_time = []
    return render_template("calisanlar.html", notes=notes_with_time, active_page='calisanlar')


@views.route('/gorevler', methods=['GET', 'POST'])
@login_required
def gorevler():
    """Görevler sayfası"""
    status_filter = request.args.get('status', 'active')  # default aktif
    default_mode = int(request.args.get('default_mode', 1))  # default 1
    notes_with_time = []

    for note in current_user.notes:
        note_date = note.date
        if note_date.tzinfo is None:
            note_date = note_date.replace(tzinfo=pytz.utc)
        delta = datetime.now(pytz.utc) - note_date
        seconds = int(delta.total_seconds())

        # Zaman kontrolü
        if seconds < 86400:
            time_passed = f"{seconds // 3600} saat önce" if seconds >= 3600 else f"{seconds // 60} dakika önce" if seconds >= 60 else f"{seconds} saniye önce"
            note.color = "green"  # aktif
        else:
            time_passed = f"{seconds // 86400} gün önce"
            note.color = "red"  # pasif

        # Yüzdelik için örnek değer
        note.percentage = 50  # placeholder, ileride gerçek değer ile değiştir

        notes_with_time.append({
            'id': note.id,
            'data': note.data,
            'time_passed': time_passed,
            'color': note.color,
            'percentage': note.percentage,
            'completed': note.completed
        })

    # Filtreleme
    if status_filter == 'active':
        # Aktifler önce
        notes_with_time = [n for n in notes_with_time if n['color'] != 'red'] + [n for n in notes_with_time if n['color'] == 'red']
    else:
        # Pasifler önce
        notes_with_time = [n for n in notes_with_time if n['color'] == 'red'] + [n for n in notes_with_time if n['color'] != 'red']

    return render_template("gorevler.html", notes=notes_with_time, active_page='gorevler',default_mode=default_mode)

@views.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("Bu neden oldu", "error")
        return redirect(url_for('views.gorevler'))

    db.session.delete(note)
    db.session.commit()
    flash("Not silindi!", "success")
    
    # default_mode parametresi ile redirect
    default_mode = request.form.get('default_mode', 1)
    return redirect(url_for('views.gorevler', default_mode=default_mode))

@views.route('/note/<int:note_id>/toggle', methods=['POST'])
@login_required
def toggle_note(note_id):
    note = Note.query.get_or_404(note_id)

    # Toggle tamamlanma durumu
    note.completed = not note.completed
    db.session.commit()

    # POST form verisinden al
    default_mode = request.form.get('default_mode', 1)

    # redirect ederken default_mode parametresini gönder
    return redirect(url_for('views.gorevler', default_mode=default_mode))

