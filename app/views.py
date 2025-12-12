from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Note,User
from .utils import role_required
from datetime import datetime
from . import db
import pytz
from sqlalchemy.orm import joinedload
import os
from flask import request, jsonify, render_template, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import os
from .models import User, Note, Attachment  # Attachment varsa, yoksa bu satırı ayarla
from .utils import role_required
from . import db

views = Blueprint('views', __name__)
@views.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    users = User.query.options(joinedload(User.notes)) \
        .order_by(User.first_name) \
        .paginate(page=page, per_page=per_page, error_out=False)
    user_cards = []
    for user in users.items:
        notes = sorted(user.notes, key=lambda n: n.date, reverse=True)
        completed = sum(1 for n in notes if n.completed)
        recent_notes = notes[:3]
        total_notes = len(notes)
        user_cards.append({
            'id': user.id,
            'name': user.first_name or user.email,
            'role': user.role,
            'total_notes': total_notes,
            'completed': completed,
            'recent_notes': recent_notes
        })
    # sadece admin görebilir
    users = User.query.all()
    return render_template('admin.html', users=users, user_cards=user_cards,active_page='admin_panel')
@views.route('/users')
@login_required
#@role_required('admin')  # sadece admin görsün istersen
def users_list():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    users = User.query.options(joinedload(User.notes)) \
        .order_by(User.first_name) \
        .paginate(page=page, per_page=per_page, error_out=False)

    user_cards = []
    for user in users.items:

        # --------- ROLE FİLTRESİ ---------
        # Eğer giriş yapan admin değilse ve listedeki kişi admin ise gösterme
        if current_user.role != "admin" and user.role == "admin":
            continue
        # ---------------------------------

        notes = sorted(user.notes, key=lambda n: n.date, reverse=True)
        recent_notes = notes[:3]
        total_notes = len(notes)
        completed = sum(1 for n in notes if n.completed)

        user_cards.append({
            'id': user.id,
            'name': user.first_name or user.email,
            'role': user.role,
            'total_notes': total_notes,
            'completed': completed,
            'recent_notes': recent_notes
        })

    return render_template('users_list.html', users=users, user_cards=user_cards,active_page='pano')
@views.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)

    # Eğer giriş yapan admin değilse
    if current_user.role != 'admin':

        # Kendi profiline erişebilir
        if current_user.id == user.id:
            pass

        # Ama admin kullanıcı profiline erişemez
        elif user.role == 'admin':
            return abort(403)

        # Admin olmayan başka kullanıcı profiline erişebilir

    total_notes = Note.query.filter_by(user_id=user.id).count()
    recent_notes = Note.query.filter_by(user_id=user.id).order_by(Note.date.desc()).limit(10)

    return render_template(
        "user_profile.html",
        user=user,
        total_notes=total_notes,
        recent_notes=recent_notes
    )

@views.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def user_admin_edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Form alanlarına göre güncelle
        new_first_name = request.form.get('first_name', '').strip()
        new_role = request.form.get('role', 'user')
        if new_first_name:
            user.first_name = new_first_name
        user.role = new_role
        try:
            db.session.commit()
            flash('Kullanıcı bilgileri güncellendi.', 'success')
        except Exception:
            db.session.rollback()
            flash('Güncelleme sırasında hata oluştu.', 'error')
        return redirect(url_for('views.users_list'))

    # GET: formu göster
    return render_template('admin_edit_user.html', user=user)
# Admin only: assign task via POST (JSON or form)
@views.route('/admin/assign_task', methods=['POST'])
@login_required
@role_required('admin')
def admin_assign_task():
    """
    Beklenen POST payload (form veya JSON):
    - user_id (zorunlu)
    - title (zorunlu)
    - description (opsiyonel)
    - file (opsiyonel, enctype multipart/form-data)
    """
    # user_id al
    try:
        # hem form hem json destekle
        data = request.form if request.form else request.get_json(force=True, silent=True) or {}
        user_id = int(data.get('user_id'))
    except Exception:
        return jsonify({'error':'invalid_user_id'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error':'user_not_found'}), 404

    title = (data.get('title') or '').strip()
    description = data.get('description') or None

    if not title:
        return jsonify({'error':'title_required'}), 400

    # create note assigned to user
    new_note = Note(
        title=title[:200],
        description=description if description else None,
        user_id=user.id
    )

    try:
        db.session.add(new_note)
        db.session.flush()  # id almak için (commit öncesi)

        # Eğer Attachment modeli varsa ve dosya gönderildiyse kaydet
        # NOT: request.files works only when enctype multipart/form-data
        if 'file' in request.files:
            uploaded = request.files['file']
            if uploaded and uploaded.filename:
                # izin verilen dosyalara göre kontrol et (ALLOWED_EXTENSIONS app config'de ise)
                allowed = current_app.config.get('ALLOWED_EXTENSIONS')
                filename = secure_filename(uploaded.filename)
                if allowed:
                    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    if ext not in allowed:
                        db.session.rollback()
                        return jsonify({'error':'file_type_not_allowed'}), 400

                # benzersiz stored_name oluştur
                import uuid
                stored_name = f"{uuid.uuid4().hex}{'.' + filename.rsplit('.',1)[1].lower() if '.' in filename else ''}"
                upload_folder = current_app.config.get('UPLOAD_FOLDER') or os.path.join(os.path.abspath(os.getcwd()), 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                dest = os.path.join(upload_folder, stored_name)
                uploaded.save(dest)
                size = os.path.getsize(dest)

                # Attachment modeli varsa kaydet
                try:
                    att = Attachment(
                        filename=filename,
                        stored_name=stored_name,
                        mime_type=uploaded.mimetype,
                        size=size,
                        note_id=new_note.id
                    )
                    db.session.add(att)
                except Exception:
                    # Attachment modeli yoksa ignore et
                    current_app.logger.debug("Attachment modele kaydedilemedi (model yok veya hata).")

        db.session.commit()
        # Eğer istek AJAX/JSON bekliyorsa JSON dön
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok':True, 'note_id': new_note.id})
        else:
            flash('Görev başarıyla atandı.', 'success')
            return redirect(url_for('views.users_list'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("assign_task hata")
        return jsonify({'error':'server_error', 'msg': str(e)}), 500
@views.route('/', methods=['GET'])
@login_required
def home():
    default_mode = request.args.get('default_mode', '1', type=int)
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.date.desc()).all()
    return render_template('index.html', notes=notes, default_mode=default_mode)

from sqlalchemy import text

@views.route('/db_status')
def db_status():
    try:
        db.session.execute(text('SELECT 1'))
        status = "Active ✅"
    except Exception as e:
        status = f"Inactive ❌ ({e})"
    return f"<h3>Database Connection: {status}</h3>"


# Yeni görev oluşturma işlemi
@views.route('/create', methods=['POST'])
@login_required
def create_note():
    note_title = request.form.get('title')
    description = request.form.get('description')
    
    # Validasyon
    if not note_title or len(note_title) < 1:
        flash('Görev başlığı boş olamaz!', 'error')
        
    
    if len(note_title) > 200:
        flash('Görev başlığı 200 karakterden uzun olamaz!', 'error')
        
    
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
        return redirect(url_for('views.home'))

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
    status_filter = request.args.get('status', 'active')
    default_mode = int(request.args.get('default_mode', 1))
    user_id = request.args.get('user_id', type=int)

    notes_with_time = []

    # --- ROLE & USER FİLTRE ---
    # if current_user.role == "admin":
    #     if user_id:
    #         notes = Note.query.filter_by(user_id=user_id).all()
    #     else:
    #         notes = Note.query.all()
    # else:
    #     notes = current_user.notes
    # -------------------------
    if user_id:
        notes = Note.query.filter_by(user_id=user_id).all()
    else:
        if current_user.role == "admin":
            notes = Note.query.all()
        else:
            notes = Note.query.filter_by(user_id=current_user.id).all()

    for note in notes:
        if status_filter == 'active' and note.completed:
            continue
        if status_filter == 'passive' and not note.completed:
            continue

        note_date = note.date.replace(tzinfo=pytz.utc) if note.date.tzinfo is None else note.date
        delta = datetime.now(pytz.utc) - note_date
        seconds = int(delta.total_seconds())

        if seconds < 60:
            time_passed, color = f"{seconds} saniye önce", "green"
        elif seconds < 3600:
            time_passed, color = f"{seconds // 60} dakika önce", "orange"
        elif seconds < 86400:
            time_passed, color = f"{seconds // 3600} saat önce", "red"
        else:
            time_passed, color = f"{seconds // 86400} gün önce", "brown"

        notes_with_time.append({
            'id': note.id,
            'title': note.title,
            'time_passed': time_passed,
            'color': color,
            'completed': note.completed,
            'owner': note.owner.first_name if note.owner else "Bilinmiyor"
        })

    return render_template(
        "gorevler.html",
        notes=notes_with_time,
        default_mode=default_mode,
        active_page='gorevler'
    )

@views.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    #if note.user_id != current_user.id and not current_user.has_role('admin'):
    if not current_user.has_role('admin'):
        flash("Sadece admin kullanıcısı notları silebilir", "error")
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

