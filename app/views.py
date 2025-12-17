# from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
# from flask_login import login_required, current_user
# from .models import Note,User
# from .utils import role_required
# from datetime import datetime
# from . import db
# import pytz
# from sqlalchemy.orm import joinedload
# import os
# from flask import send_from_directory, request, jsonify, render_template, flash, redirect, url_for, current_app
# from werkzeug.utils import secure_filename
# import os
# from .models import User, Note, Attachment  # Attachment varsa, yoksa bu satırı ayarla
# from .utils import role_required
# from . import db
# UPLOAD_FOLDER = "uploads"
# views = Blueprint('views', __name__)
# @views.route('/admin')
# @login_required
# @role_required('admin')
# def admin_panel():
#     page = request.args.get('page', 1, type=int)
#     per_page = 12
#     users = User.query.options(joinedload(User.notes)) \
#         .order_by(User.first_name) \
#         .paginate(page=page, per_page=per_page, error_out=False)
#     user_cards = []
#     for user in users.items:
#         notes = sorted(user.notes, key=lambda n: n.date, reverse=True)
#         completed = sum(1 for n in notes if n.completed)
#         recent_notes = notes[:3]
#         total_notes = len(notes)
#         user_cards.append({
#             'id': user.id,
#             'name': user.first_name or user.email,
#             'role': user.role,
#             'total_notes': total_notes,
#             'completed': completed,
#             'recent_notes': recent_notes
#         })
#     # sadece admin görebilir
#     users = User.query.all()
#     return render_template('admin.html', users=users, user_cards=user_cards,active_page='admin_panel')
# @views.route('/users')
# @login_required
# #@role_required('admin')  # sadece admin görsün istersen
# def users_list():
#     page = request.args.get('page', 1, type=int)
#     per_page = 12

#     users = User.query.options(joinedload(User.notes)) \
#         .order_by(User.first_name) \
#         .paginate(page=page, per_page=per_page, error_out=False)

#     user_cards = []
#     for user in users.items:

#         # --------- ROLE FİLTRESİ ---------
#         # Eğer giriş yapan admin değilse ve listedeki kişi admin ise gösterme
#         if current_user.role != "admin" and user.role == "admin":
#             continue
#         # ---------------------------------

#         notes = sorted(user.notes, key=lambda n: n.date, reverse=True)
#         recent_notes = notes[:3]
#         total_notes = len(notes)
#         completed = sum(1 for n in notes if n.completed)

#         user_cards.append({
#             'id': user.id,
#             'name': user.first_name or user.email,
#             'role': user.role,
#             'total_notes': total_notes,
#             'completed': completed,
#             'recent_notes': recent_notes
#         })

#     return render_template('users_list.html', users=users, user_cards=user_cards,active_page='pano')

# # @views.route("/user/<int:user_id>")
# # @login_required
# # def user_profile(user_id):
# #     user = User.query.get_or_404(user_id)

# #     # Yetki kontrolü
# #     if current_user.role != 'admin':
# #         if current_user.id != user.id and user.role == 'admin':
# #             abort(403)

# #     # 🔢 Görev sayıları
# #     total_notes = Note.query.filter_by(user_id=user.id).count()

# #     completed_task_count = Note.query.filter_by(
# #         user_id=user.id,
# #         completed=True
# #     ).count()

# #     uncompleted_notes_count = Note.query.filter_by(
# #         user_id=user.id,
# #         completed=False
# #     ).count()
# #     total_tasks_count = completed_task_count + uncompleted_notes_count

# #     completed_notes = Note.query.filter_by(
# #         user_id=user.id,
# #         completed=True
# #     ).order_by(Note.date.desc()).all()

# #     uncompleted_notes = Note.query.filter_by(
# #         user_id=user.id,
# #         completed=False
# #     ).order_by(Note.date.desc()).all()

# #     recent_notes = Note.query.filter_by(
# #         user_id=user.id
# #     ).order_by(Note.date.desc()).limit(10).all()
# #     completion_percentage = (completed_task_count / total_tasks_count * 100) if total_tasks_count > 0 else 0
    
# #     return render_template(
# #         "user_profile.html",
# #         user=user,
# #         completion_percentage=completion_percentage,
# #         total_notes=total_notes,
# #         completed_task_count=completed_task_count,
# #         uncompleted_task_count=uncompleted_notes_count,
# #         completed_notes=completed_notes,
# #         uncompleted_notes=uncompleted_notes,
# #         recent_notes=recent_notes
# #     )
# # @views.route('/download/attachment/<int:attachment_id>')
# # @login_required
# # def download_attachment(attachment_id):
# #     print("🔥 DOWNLOAD ROUTE ÇALIŞTI:", attachment_id)
# #     attachment = Attachment.query.get_or_404(attachment_id)
# #     note = attachment.note

# #     # 🔐 Yetki kontrolü
# #     if current_user.role != 'admin' and note.user_id != current_user.id:
# #         abort(403)

# #     # 🔴 TEK KAYNAK: config'ten al
# #     upload_folder = current_app.config['UPLOAD_FOLDER']
# #     file_path = os.path.join(upload_folder, attachment.stored_name)

# #     # Debug (istersen sonra kaldır)
# #     print("DOSYA:", attachment.stored_name)
# #     print("UPLOAD_FOLDER:", upload_folder)
# #     print("FULL PATH:", file_path)
# #     print("VAR MI:", os.path.exists(file_path))

# #     # Dosya gerçekten yoksa net hata ver
# #     if not os.path.exists(file_path):
# #         abort(404)

# #     return send_from_directory(
# #         upload_folder,                  # 🔴 BURASI ÖNEMLİ
# #         attachment.stored_name,
# #         as_attachment=True,
# #         download_name=attachment.filename
# #     )
# # @views.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
# # @login_required
# # @role_required('admin')
# # def user_admin_edit(user_id):
# #     user = User.query.get_or_404(user_id)

# #     if request.method == 'POST':
# #         # Form alanlarına göre güncelle
# #         new_first_name = request.form.get('first_name', '').strip()
# #         new_role = request.form.get('role', 'user')
# #         if new_first_name:
# #             user.first_name = new_first_name
# #         user.role = new_role
# #         try:
# #             db.session.commit()
# #             flash('Kullanıcı bilgileri güncellendi.', 'success')
# #         except Exception:
# #             db.session.rollback()
# #             flash('Güncelleme sırasında hata oluştu.', 'error')
# #         return redirect(url_for('views.users_list'))

# #     # GET: formu göster
# #     return render_template('admin_edit_user.html', user=user)
# # Admin only: assign task via POST (JSON or form)
# @views.route('/admin/assign_task', methods=['POST'])
# @login_required
# @role_required('admin')
# def admin_assign_task():
#     """
#     Beklenen POST payload (form veya JSON):
#     - user_id (zorunlu)
#     - title (zorunlu)
#     - description (opsiyonel)
#     - file (opsiyonel, enctype multipart/form-data)
#     """
#     # user_id al
#     try:
#         # hem form hem json destekle
#         data = request.form if request.form else request.get_json(force=True, silent=True) or {}
#         user_id = int(data.get('user_id'))
#     except Exception:
#         return jsonify({'error':'invalid_user_id'}), 400

#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({'error':'user_not_found'}), 404

#     title = (data.get('title') or '').strip()
#     description = data.get('description') or None

#     if not title:
#         return jsonify({'error':'title_required'}), 400

#     # create note assigned to user
#     new_note = Note(
#         title=title[:200],
#         description=description if description else None,
#         user_id=user.id
#     )

#     try:
#         db.session.add(new_note)
#         db.session.flush()  # id almak için (commit öncesi)

#         # Eğer Attachment modeli varsa ve dosya gönderildiyse kaydet
#         # NOT: request.files works only when enctype multipart/form-data
#         if 'file' in request.files:
#             uploaded = request.files['file']
#             if uploaded and uploaded.filename:
#                 # izin verilen dosyalara göre kontrol et (ALLOWED_EXTENSIONS app config'de ise)
#                 allowed = current_app.config.get('ALLOWED_EXTENSIONS')
#                 filename = secure_filename(uploaded.filename)
#                 if allowed:
#                     ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
#                     if ext not in allowed:
#                         db.session.rollback()
#                         return jsonify({'error':'file_type_not_allowed'}), 400

#                 # benzersiz stored_name oluştur
#                 import uuid
#                 stored_name = f"{uuid.uuid4().hex}{'.' + filename.rsplit('.',1)[1].lower() if '.' in filename else ''}"
#                 upload_folder = current_app.config['UPLOAD_FOLDER']
#                 dest = os.path.join(upload_folder, stored_name)
#                 uploaded.save(dest)
#                 uploaded.save(dest)
#                 size = os.path.getsize(dest)

#                 # Attachment modeli varsa kaydet
#                 try:
#                     att = Attachment(
#                         filename=filename,
#                         stored_name=stored_name,
#                         mime_type=uploaded.mimetype,
#                         size=size,
#                         note_id=new_note.id
#                     )
#                     db.session.add(att)
#                 except Exception:
#                     # Attachment modeli yoksa ignore et
#                     current_app.logger.debug("Attachment modele kaydedilemedi (model yok veya hata).")

#         db.session.commit()
#         # Eğer istek AJAX/JSON bekliyorsa JSON dön
#         if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({'ok':True, 'note_id': new_note.id})
#         else:
#             flash('Görev başarıyla atandı.', 'success')
#             return redirect(url_for('views.users_list'))

#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.exception("assign_task hata")
#         return jsonify({'error':'server_error', 'msg': str(e)}), 500
# @views.route('/', methods=['GET'])
# @login_required
# def home():
#     default_mode = request.args.get('default_mode', '1', type=int)
#     notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.date.desc()).all()
#     return render_template('index.html', notes=notes, default_mode=default_mode)

# from sqlalchemy import text

# @views.route('/db_status')
# def db_status():
#     try:
#         db.session.execute(text('SELECT 1'))
#         status = "Active ✅"
#     except Exception as e:
#         status = f"Inactive ❌ ({e})"
#     return f"<h3>Database Connection: {status}</h3>"


# # Yeni görev oluşturma işlemi
# @views.route('/create', methods=['POST'])
# @login_required
# def create_note():
#     note_title = request.form.get('title')
#     description = request.form.get('description')
    
#     # Validasyon
#     if not note_title or len(note_title) < 1:
#         flash('Görev başlığı boş olamaz!', 'error')
        
    
#     if len(note_title) > 200:
#         flash('Görev başlığı 200 karakterden uzun olamaz!', 'error')
        
    
#     # Yeni not oluştur
#     new_note = Note(
#         title=note_title,
#         description=description if description else None,
#         user_id=current_user.id
#     )
    
#     try:
#         db.session.add(new_note)
#         db.session.commit()
#         flash('Görev başarıyla oluşturuldu!', 'success')
#         return redirect(url_for('views.home'))
#     except Exception as e:
#         db.session.rollback()
#         flash('Görev oluşturulurken bir hata oluştu.', 'error')
#         return redirect(url_for('views.home'))

# @views.route('/my-profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     """Profilim / Çalışan listesi"""
#     # Çalışan listesi veya profil bilgisi
#     notes_with_time = []
#     return render_template("profile.html", notes=notes_with_time, active_page='profile')

# @views.route('/edit/<int:note_id>', methods=['GET'])
# @login_required
# def edit_note(note_id):
#     note = Note.query.get_or_404(note_id)

#     if note.user_id != current_user.id and current_user.role != 'admin':
#         flash('Bu görevi düzenleme yetkiniz yok.', 'error')
#         return redirect(url_for('views.home'))

#     return render_template('edit_note.html', note=note)

# @views.route('/update/<int:note_id>', methods=['POST'])
# @login_required
# def update_note(note_id):
#     note = Note.query.get_or_404(note_id)
    
#     # Kullanıcının kendi notunu güncellemesini sağla
#     if note.user_id != current_user.id:
#         flash('Bu görevi güncelleme yetkiniz yok.', 'error')
#         return redirect(url_for('views.home'))
    
#     # Formdan verileri al
#     title = request.form.get('title')
#     description = request.form.get('description')
#     color = request.form.get('color')
    
#     # Validasyon
#     if not title or len(title) < 1:
#         flash('Görev başlığı boş olamaz!', 'error')
#         return redirect(url_for('views.edit_note', note_id=note_id))
    
#     # Notu güncelle
#     note.title = title
#     note.description = description if description else None
#     note.color = color if color else 'purple'
    
#     try:
#         db.session.commit()
#         flash('Görev başarıyla güncellendi!', 'success')
#         return redirect(url_for('views.task_details', note_id=note_id))
#     except Exception as e:
#         db.session.rollback()
#         flash('Görev güncellenirken bir hata oluştu.', 'error')
#         return redirect(url_for('views.edit_note', note_id=note_id))
    
# @views.route('/gorevler')
# @login_required
# def gorevler():
#     status_filter = request.args.get('status', 'active')
#     default_mode = request.args.get('default_mode', 1, type=int)

#     if current_user.role == 'admin':
#         notes = Note.query.all()
#     else:
#         notes = Note.query.filter_by(user_id=current_user.id).all()

#     filtered_notes = []
#     for note in notes:
#         if status_filter == 'active' and note.completed:
#             continue
#         if status_filter == 'passive' and not note.completed:
#             continue
#         filtered_notes.append(note)

#     return render_template(
#         'gorevler.html',
#         notes=filtered_notes,
#         default_mode=default_mode,
#         active_page='gorevler'
#     )

# @views.route('/delete-note/<int:note_id>', methods=['POST'])
# @login_required
# def delete_note(note_id):
#     note = Note.query.get_or_404(note_id)

#     if note.user_id != current_user.id and current_user.role != 'admin':
#         flash("Bu görevi silme yetkiniz yok", "error")
#         return redirect(url_for('views.gorevler'))

#     db.session.delete(note)
#     db.session.commit()

#     flash("Görev silindi!", "success")
#     return redirect(url_for('views.gorevler'))


# @views.route('/note/<int:note_id>')
# def task_details(note_id):
#     note = Note.query.get_or_404(note_id)
#     # burada gerekirse time_passed hesaplamasını güncelle
#     note_date = note.date
#     if note_date.tzinfo is None:
#             note_date = note_date.replace(tzinfo=pytz.utc)
#     delta = datetime.now(pytz.utc) - note_date
#     seconds = int(delta.total_seconds())
        
        
#     if seconds < 60:
#             time_passed =  f"{seconds} saniye önce"
#             color = "green"

#     elif seconds < 3600: # dakika
#             time_passed = f"{seconds // 60} dakika önce"
#             color = "orange"

#     elif seconds < 86400: # saat
#             time_passed = f"{seconds // 3600} saat önce"
#             color = "red"

#     else:  # gün
#             time_passed = f"{seconds // 86400} gün önce"
#             color = "brown"
#     if note.user_id != current_user.id and current_user.role != 'admin':
#         abort(403)
    
#     return render_template('task_detail.html', note=note,color=color)

# @views.route('/note/<int:note_id>/toggle', methods=['POST'])
# @login_required
# def toggle_note(note_id):
#     note = Note.query.get_or_404(note_id)

#     # Toggle tamamlanma durumu
#     note.completed = not note.completed
#     db.session.commit()

#     # POST form verisinden al
#     default_mode = request.form.get('default_mode', 1)

#     # redirect ederken default_mode parametresini gönder
#     return redirect(url_for('views.gorevler', default_mode=default_mode))

# @views.route('/new-task')
# @login_required
# def new_task():
#     return render_template('new_task.html', active_page='new_task')


# @views.route('/istatistikler')
# @login_required
# def istatistikler():
#     user_id = current_user.id

#     total_tasks = Note.query.filter_by(user_id=user_id).count()
#     completed_tasks = Note.query.filter_by(
#         user_id=user_id,
#         completed=True
#     ).count()

#     pending_tasks = total_tasks - completed_tasks

#     completion_percentage = (
#         round((completed_tasks / total_tasks) * 100, 1)
#         if total_tasks > 0 else 0
#     )

#     return render_template(
#         'istatistikler.html',
#         total_tasks=total_tasks,
#         completed_tasks=completed_tasks,
#         pending_tasks=pending_tasks,
#         completion_percentage=completion_percentage,
#         active_page='istatistikler'
#     )

# @views.route('/pano')
# @login_required
# def pano():
#     if current_user.role == 'admin':
#         flash("Bu sayfa sadece kullanıcılar içindir.", "error")
#         return redirect(url_for('views.admin_panel'))

#     completed_tasks = Note.query.filter_by(
#         user_id=current_user.id,
#         completed=True
#     ).order_by(Note.date.desc()).all()

#     pending_tasks = Note.query.filter_by(
#         user_id=current_user.id,
#         completed=False
#     ).order_by(Note.date.desc()).all()

#     return render_template(
#         'pano.html',
#         completed_tasks=completed_tasks,
#         pending_tasks=pending_tasks,
#         active_page='pano'
#     )


# # ======================================================
# # USER PROFILE
# # ======================================================
# @views.route("/user/<int:user_id>")
# @login_required
# def user_profile(user_id):
#     user = User.query.get_or_404(user_id)

#     if current_user.role != 'admin' and current_user.id != user.id:
#         abort(403)

#     total_notes = Note.query.filter_by(user_id=user.id).count()
#     completed_task_count = Note.query.filter_by(user_id=user.id, completed=True).count()
#     uncompleted_task_count = Note.query.filter_by(user_id=user.id, completed=False).count()

#     completed_notes = Note.query.filter_by(
#         user_id=user.id, completed=True
#     ).order_by(Note.date.desc()).all()

#     uncompleted_notes = Note.query.filter_by(
#         user_id=user.id, completed=False
#     ).order_by(Note.date.desc()).all()

#     recent_notes = Note.query.filter_by(
#         user_id=user.id
#     ).order_by(Note.date.desc()).limit(10).all()

#     completion_percentage = (
#         (completed_task_count / total_notes) * 100
#         if total_notes > 0 else 0
#     )

#     return render_template(
#         "user_profile.html",
#         user=user,
#         completion_percentage=completion_percentage,
#         total_notes=total_notes,
#         completed_task_count=completed_task_count,
#         uncompleted_task_count=uncompleted_task_count,
#         completed_notes=completed_notes,
#         uncompleted_notes=uncompleted_notes,
#         recent_notes=recent_notes,
#         active_page='profile'
#     )


from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from .models import Note,User, Attachment # Attachment modelinin import edildiğinden emin ol
from .utils import role_required
from datetime import datetime, timedelta # YENİ: timedelta eklendi
from . import db
import pytz
from sqlalchemy.orm import joinedload
import os
from werkzeug.utils import secure_filename
import uuid # YENİ: uuid eklendi
from sqlalchemy import text


# Dosya uzantısı kontrolü için yardımcı fonksiyon (Mevcut kodda yoktu, eklenmeli)
def allowed_file(filename):
    # Bu fonksiyon normalde app config'den ALLOWED_EXTENSIONS'ı okumalıdır.
    # Varsayılan olarak sadece örnek uzantıları kabul edelim:
    if not current_app.config.get('ALLOWED_EXTENSIONS'):
        return True # Eğer config yoksa herşeye izin ver
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# UPLOAD_FOLDER = "uploads" # Bu satırın global olarak bir kez tanımlandığından emin olun
views = Blueprint('views', __name__)
UPLOAD_FOLDER = "uploads"

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
                # uuid import edildi
                stored_name = f"{uuid.uuid4().hex}{'.' + filename.rsplit('.',1)[1].lower() if '.' in filename else ''}"
                upload_folder = current_app.config['UPLOAD_FOLDER']
                dest = os.path.join(upload_folder, stored_name)
                uploaded.save(dest)
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


@views.route('/db_status')
def db_status():
    try:
        db.session.execute(text('SELECT 1'))
        status = "Active ✅"
    except Exception as e:
        status = f"Inactive ❌ ({e})"
    return f"<h3>Database Connection: {status}</h3>"


# GÜNCELLENMİŞ: Yeni görev oluşturma işlemi (Duration desteği ile)
@views.route('/create', methods=['POST'])
@login_required
def create_note():
    note_title = request.form.get('title')
    description = request.form.get('description')
    
    # YENİ: Başlangıç tarihi ve süre
    start_date_str = request.form.get('start_date')
    duration_days = request.form.get('duration_days')
    duration_unit = request.form.get('duration_unit', 'days')  # days, weeks, months, years
    
    # Eski yöntem: Direkt deadline
    deadline_str = request.form.get('deadline')
    
    # Validasyon
    if not note_title or len(note_title) < 1:
        flash('Görev başlığı boş olamaz!', 'error')
        return redirect(url_for('views.home'))
    
    if len(note_title) > 200:
        flash('Görev başlığı 200 karakterden uzun olamaz!', 'error')
        return redirect(url_for('views.home'))
    
    # Başlangıç tarihi ve süre parse et
    start_date = None
    duration_in_days = None
    deadline = None
    
    try:
        # YÖNTEM 1: Başlangıç + Süre (Yeni yöntem)
        if start_date_str and duration_days:
            # Not: Frontend'den gelen formatı kontrol ettim, '%Y-%m-%dT%H:%M'
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            start_date = start_date.replace(tzinfo=pytz.utc)
            
            # Süreyi güne çevir
            duration_value = int(duration_days)
            if duration_unit == 'weeks':
                duration_in_days = duration_value * 7
            elif duration_unit == 'months':
                duration_in_days = duration_value * 30
            elif duration_unit == 'years':
                duration_in_days = duration_value * 365
            else:  # days
                duration_in_days = duration_value
            
            # Deadline'ı otomatik hesapla
            deadline = start_date + timedelta(days=duration_in_days)
            
        # YÖNTEM 2: Direkt deadline (Eski yöntem)
        elif deadline_str:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            deadline = deadline.replace(tzinfo=pytz.utc)
            
    except Exception as e:
        flash('Geçersiz tarih formatı veya süre değeri.', 'error')
        current_app.logger.error(f"Tarih/Süre hatası: {e}")
        return redirect(url_for('views.home'))

    # Yeni not oluştur
    new_note = Note(
        title=note_title,
        description=description if description else None,
        start_date=start_date, # YENİ alan
        duration_days=duration_in_days, # YENİ alan
        deadline=deadline, # GÜNCELLENMİŞ alan
        user_id=current_user.id
    )
    
    try:
        db.session.add(new_note)
        db.session.flush() # ID almak için
        
        # Dosya yükleme
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file and uploaded_file.filename:
                if allowed_file(uploaded_file.filename):
                    filename = secure_filename(uploaded_file.filename)
                    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    stored_name = f"{uuid.uuid4().hex}.{ext}"
                    
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    file_path = os.path.join(upload_folder, stored_name)
                    uploaded_file.save(file_path)
                    
                    attachment = Attachment(
                        filename=filename,
                        stored_name=stored_name,
                        mime_type=uploaded_file.mimetype,
                        size=os.path.getsize(file_path),
                        note_id=new_note.id
                    )
                    db.session.add(attachment)
                else:
                    flash('Geçersiz dosya türü.', 'error')
        
        db.session.commit()
        flash('Görev başarıyla oluşturuldu!', 'success')
        return redirect(url_for('views.home'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("create_note hata")
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

    if note.user_id != current_user.id and current_user.role != 'admin':
        flash('Bu görevi düzenleme yetkiniz yok.', 'error')
        return redirect(url_for('views.home'))

    return render_template('edit_note.html', note=note)

# GÜNCELLENMİŞ: Görev güncelleme işlemi (Duration desteği ile)
@views.route('/update/<int:note_id>', methods=['POST'])
@login_required
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Yetki kontrolü (Admin başkasının notunu da güncelleyebilir)
    if note.user_id != current_user.id and current_user.role != 'admin':
        flash('Bu görevi güncelleme yetkiniz yok.', 'error')
        return redirect(url_for('views.home'))
    
    # Formdan verileri al
    title = request.form.get('title')
    description = request.form.get('description')
    
    # YENİ: Başlangıç tarihi ve süre
    start_date_str = request.form.get('start_date')
    duration_days = request.form.get('duration_days')
    duration_unit = request.form.get('duration_unit', 'days')
    
    # Eski yöntem: Direkt deadline
    deadline_str = request.form.get('deadline')

    # Validasyon
    if not title or len(title) < 1:
        flash('Görev başlığı boş olamaz!', 'error')
        return redirect(url_for('views.edit_note', note_id=note_id))

    # Tarihleri parse et
    start_date = None
    duration_in_days = None
    deadline = None
    
    try:
        # YÖNTEM 1: Başlangıç + Süre
        if start_date_str and duration_days:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            start_date = start_date.replace(tzinfo=pytz.utc)
            
            duration_value = int(duration_days)
            if duration_unit == 'weeks':
                duration_in_days = duration_value * 7
            elif duration_unit == 'months':
                duration_in_days = duration_value * 30
            elif duration_unit == 'years':
                duration_in_days = duration_value * 365
            else:
                duration_in_days = duration_value
            
            deadline = start_date + timedelta(days=duration_in_days)
            
        # YÖNTEM 2: Direkt deadline
        elif deadline_str:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            deadline = deadline.replace(tzinfo=pytz.utc)
            
    except Exception as e:
        flash('Geçersiz tarih formatı veya süre değeri.', 'error')
        current_app.logger.error(f"Tarih/Süre hatası: {e}")
        return redirect(url_for('views.edit_note', note_id=note_id))
    
    # Notu güncelle
    note.title = title
    note.description = description if description else None
    note.start_date = start_date # YENİ alan
    note.duration_days = duration_in_days # YENİ alan
    note.deadline = deadline # GÜNCELLENMİŞ alan
    
    try:
        # Dosya yükleme
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file and uploaded_file.filename:
                if allowed_file(uploaded_file.filename):
                    filename = secure_filename(uploaded_file.filename)
                    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    stored_name = f"{uuid.uuid4().hex}.{ext}"
                    
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    file_path = os.path.join(upload_folder, stored_name)
                    uploaded_file.save(file_path)
                    
                    # Not: Bu kısımda Attachment modeli mevcut olmalı
                    attachment = Attachment(
                        filename=filename,
                        stored_name=stored_name,
                        mime_type=uploaded_file.mimetype,
                        size=os.path.getsize(file_path),
                        note_id=note.id
                    )
                    db.session.add(attachment)
                else:
                    flash('Geçersiz dosya türü.', 'error')

        db.session.commit()
        flash('Görev başarıyla güncellendi!', 'success')
        return redirect(url_for('views.task_details', note_id=note_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("update_note hata")
        flash('Görev güncellenirken bir hata oluştu.', 'error')
        return redirect(url_for('views.edit_note', note_id=note_id))

    
@views.route('/gorevler')
@login_required
def gorevler():
    status_filter = request.args.get('status', 'active')
    default_mode = request.args.get('default_mode', 1, type=int)

    if current_user.role == 'admin':
        notes = Note.query.all()
    else:
        notes = Note.query.filter_by(user_id=current_user.id).all()

    filtered_notes = []
    for note in notes:
        if status_filter == 'active' and note.completed:
            continue
        if status_filter == 'passive' and not note.completed:
            continue
        filtered_notes.append(note)

    return render_template(
        'gorevler.html',
        notes=filtered_notes,
        default_mode=default_mode,
        active_page='gorevler'
    )

@views.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id and current_user.role != 'admin':
        flash("Bu görevi silme yetkiniz yok", "error")
        return redirect(url_for('views.gorevler'))

    db.session.delete(note)
    db.session.commit()

    flash("Görev silindi!", "success")
    return redirect(url_for('views.gorevler'))


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
    if note.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
    
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

@views.route('/new-task')
@login_required
def new_task():
    return render_template('new_task.html', active_page='new_task')


@views.route('/istatistikler')
@login_required
def istatistikler():
    user_id = current_user.id

    total_tasks = Note.query.filter_by(user_id=user_id).count()
    completed_tasks = Note.query.filter_by(
        user_id=user_id,
        completed=True
    ).count()

    pending_tasks = total_tasks - completed_tasks

    completion_percentage = (
        round((completed_tasks / total_tasks) * 100, 1)
        if total_tasks > 0 else 0
    )

    return render_template(
        'istatistikler.html',
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        completion_percentage=completion_percentage,
        active_page='istatistikler'
    )

@views.route('/pano')
@login_required
def pano():
    if current_user.role == 'admin':
        flash("Bu sayfa sadece kullanıcılar içindir.", "error")
        return redirect(url_for('views.admin_panel'))

    completed_tasks = Note.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(Note.date.desc()).all()

    pending_tasks = Note.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(Note.date.desc()).all()

    return render_template(
        'pano.html',
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        active_page='pano'
    )


# ======================================================
# USER PROFILE
# ======================================================
@views.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)

    if current_user.role != 'admin' and current_user.id != user.id:
        abort(403)

    total_notes = Note.query.filter_by(user_id=user.id).count()
    completed_task_count = Note.query.filter_by(user_id=user.id, completed=True).count()
    uncompleted_task_count = Note.query.filter_by(user_id=user.id, completed=False).count()

    completed_notes = Note.query.filter_by(
        user_id=user.id, completed=True
    ).order_by(Note.date.desc()).all()

    uncompleted_notes = Note.query.filter_by(
        user_id=user.id, completed=False
    ).order_by(Note.date.desc()).all()

    recent_notes = Note.query.filter_by(
        user_id=user.id
    ).order_by(Note.date.desc()).limit(10).all()

    completion_percentage = (
        (completed_task_count / total_notes) * 100
        if total_notes > 0 else 0
    )

    return render_template(
        "user_profile.html",
        user=user,
        completion_percentage=completion_percentage,
        total_notes=total_notes,
        completed_task_count=completed_task_count,
        uncompleted_task_count=uncompleted_task_count,
        completed_notes=completed_notes,
        uncompleted_notes=uncompleted_notes,
        recent_notes=recent_notes,
        active_page='profile'
    )

# @views.route('/download/attachment/<int:attachment_id>') ve diğer yoruma alınmış routelar
# ... (orijinal dosyadaki yoruma alınmış routelar buraya dahil edilmedi, ancak isterseniz ekleyebilirim)