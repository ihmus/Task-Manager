from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from datetime import datetime
from . import db
import pytz
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    default_mode = request.args.get('default_mode', '1', type=int)
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.date.desc()).all()
    return render_template('index.html', notes=notes, default_mode=default_mode)


# Yeni görev oluşturma işlemi
@views.route('/create', methods=['POST'])
@login_required
def create_note():
    note_title = request.form.get('title')
    description = request.form.get('description')
    
    # Validasyon
    if not note_title or len(note_title) < 1:
        flash('Görev başlığı boş olamaz!', 'error')
        # return redirect(url_for('views.new_note'))
        return redirect(url_for('views.home'))

    
    if len(note_title) > 200:
        flash('Görev başlığı 200 karakterden uzun olamaz!', 'error')
        # return redirect(url_for('views.new_note'))
        return redirect(url_for('views.home'))

    
    # Yeni not oluştur
    new_note = Note(
        title=note_title,
        description=description if description else None,
        user_id=current_user.id
    )
    
    try:
        db.session.add(new_note)
        db.session.commit()
        flash('Görev başarıyla oluşturuldu!', 'success')
        return redirect(url_for('views.home'))
    except Exception as e:
        db.session.rollback()
        flash('Görev oluşturulurken bir hata oluştu.', 'error')
        return redirect(url_for('views.new_note'))

@views.route('/my-profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Profilim / Çalışan listesi"""
    # Çalışan listesi veya profil bilgisi
    notes_with_time = []
    return render_template("profile.html", notes=notes_with_time, active_page='profile')

@views.route('/edit/<int:note_id>', methods=['GET'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Kullanıcının kendi notunu düzenlemesini sağla
    if note.user_id != current_user.id:
        flash('Bu görevi düzenleme yetkiniz yok.', 'error')
        return redirect(url_for('views.home'))
    
    return render_template('edit_note.html', note=note)
@views.route('/update/<int:note_id>', methods=['POST'])
@login_required
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Kullanıcının kendi notunu güncellemesini sağla
    if note.user_id != current_user.id:
        flash('Bu görevi güncelleme yetkiniz yok.', 'error')
        return redirect(url_for('views.home'))
    
    # Formdan verileri al
    title = request.form.get('title')
    description = request.form.get('description')
    color = request.form.get('color')
    
    # Validasyon
    if not title or len(title) < 1:
        flash('Görev başlığı boş olamaz!', 'error')
        return redirect(url_for('views.edit_note', note_id=note_id))
    
    # Notu güncelle
    note.title = title
    note.description = description if description else None
    note.color = color if color else 'purple'
    
    try:
        db.session.commit()
        flash('Görev başarıyla güncellendi!', 'success')
        return redirect(url_for('views.task_details', note_id=note_id))
    except Exception as e:
        db.session.rollback()
        flash('Görev güncellenirken bir hata oluştu.', 'error')
        return redirect(url_for('views.edit_note', note_id=note_id))
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
        
        
        if seconds < 60:
            time_passed =  f"{seconds} saniye önce"
            color = "green"

        elif seconds < 3600: # dakika
            time_passed = f"{seconds // 60} dakika önce"
            color = "orange"

        elif seconds < 86400: # saat
            time_passed = f"{seconds // 3600} saat önce"
            color = "red"

        else:  # gün
            time_passed = f"{seconds // 86400} gün önce"
            color = "brown"


        notes_with_time.append({
            'id': note.id,
            'title': note.title,
            'time_passed': time_passed,
            'color': color,
            'completed': note.completed
        })
    # color rank: daha küçük = daha üstte
    color_rank = {
        'green': 1,
        'orange': 2,
        'red': 3,
        'brown': 4
    }

    # Filtreleme / sıralama
    notes_with_time = sorted(notes_with_time, key=lambda n: color_rank[n['color']])


    if status_filter == 'active':
        # En eski en üstte
        notes_with_time = sorted(notes_with_time, key=lambda n: color_rank[n['color']], reverse=True)
    else:
        # En yeni en üstte
        notes_with_time = sorted(notes_with_time, key=lambda n: color_rank[n['color']])

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
@views.route('/note/<int:note_id>')
def task_details(note_id):
    note = Note.query.get_or_404(note_id)
    # burada gerekirse time_passed hesaplamasını güncelle
    note_date = note.date
    if note_date.tzinfo is None:
            note_date = note_date.replace(tzinfo=pytz.utc)
    delta = datetime.now(pytz.utc) - note_date
    seconds = int(delta.total_seconds())
        
        
    if seconds < 60:
            time_passed =  f"{seconds} saniye önce"
            color = "green"

    elif seconds < 3600: # dakika
            time_passed = f"{seconds // 60} dakika önce"
            color = "orange"

    elif seconds < 86400: # saat
            time_passed = f"{seconds // 3600} saat önce"
            color = "red"

    else:  # gün
            time_passed = f"{seconds // 86400} gün önce"
            color = "brown"
    
    return render_template('task_detail.html', note=note,color=color)
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

