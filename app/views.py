from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Note,User
from .utils import role_required
from datetime import datetime
from . import db
import uuid
import pytz
from sqlalchemy.orm import joinedload
import os
from flask import send_from_directory, request, jsonify, render_template, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import os
from .models import User, Note, Attachment,Category  # Attachment varsa, yoksa bu satırı ayarla
from .utils import role_required
from . import db
UPLOAD_FOLDER = "uploads"
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
    user_id = user_id or current_user.id
    user = User.query.get_or_404(user_id)

    # Yetki kontrolü
    if current_user.role != 'admin':
        if current_user.id != user.id and user.role == 'admin':
            abort(403)

    # 🔢 Sayaçlar
    total_tasks_count = 0
    completed_task_count = 0
    continuing_tasks = 0
    overdue_tasks = 0

    now = datetime.now(pytz.utc)

    notes = Note.query.filter_by(user_id=user.id).all()

    for note in notes:
        total_tasks_count += 1

        if note.completed:
            completed_task_count += 1
        else:
            # Deadline varsa kontrol et
            if note.deadline:
                deadline = note.deadline

                # Timezone yoksa UTC ekle
                if deadline.tzinfo is None:
                    deadline = deadline.replace(tzinfo=pytz.utc)

                if deadline < now:
                    overdue_tasks += 1
                else:
                    continuing_tasks += 1
            else:
                # Deadline yok ama tamamlanmamış → devam ediyor
                continuing_tasks += 1

    completion_percentage = (
        completed_task_count / total_tasks_count * 100
        if total_tasks_count > 0 else 0
    )

    completed_notes = Note.query.filter_by(
        user_id=user.id,
        completed=True
    ).order_by(Note.date.desc()).all()

    uncompleted_notes = Note.query.filter_by(
        user_id=user.id,
        completed=False
    ).order_by(Note.date.desc()).all()

    recent_notes = Note.query.filter_by(
        user_id=user.id
    ).order_by(Note.date.desc()).limit(10).all()

    return render_template(
        "user_profile.html",
        user=user,
        completion_percentage=completion_percentage,
        total_tasks_count=total_tasks_count,
        completed_task_count=completed_task_count,
        uncompleted_task_count=continuing_tasks + overdue_tasks,
        overdue_tasks=overdue_tasks,
        continuing_tasks=continuing_tasks,
        completed_notes=completed_notes,
        uncompleted_notes=uncompleted_notes,
        recent_notes=recent_notes
    )

@views.route('/download/attachment/<int:attachment_id>')
@login_required
def download_attachment(attachment_id):
    print("🔥 DOWNLOAD ROUTE ÇALIŞTI:", attachment_id)
    attachment = Attachment.query.get_or_404(attachment_id)
    note = attachment.note

    # 🔐 Yetki kontrolü
    if current_user.role != 'admin' and note.user_id != current_user.id:
        abort(403)

    # 🔴 TEK KAYNAK: config'ten al
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, attachment.stored_name)

    # Debug (istersen sonra kaldır)
    print("DOSYA:", attachment.stored_name)
    print("UPLOAD_FOLDER:", upload_folder)
    print("FULL PATH:", file_path)
    print("VAR MI:", os.path.exists(file_path))

    # Dosya gerçekten yoksa net hata ver
    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(
        upload_folder,                  # 🔴 BURASI ÖNEMLİ
        attachment.stored_name,
        as_attachment=True,
        download_name=attachment.filename
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
@views.route('/new-note', methods=['GET'])
@login_required
def home():
    default_mode = request.args.get('default_mode', '1', type=int)
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.date.desc()).all()
    categories = Category.query.all()
    return render_template('index.html', notes=notes, categories=categories, default_mode=default_mode)
from sqlalchemy import text

@views.route('/db_status')
def db_status():
    try:
        db.session.execute(text('SELECT 1'))
        status = "Active ✅"
    except Exception as e:
        status = f"Inactive ❌ ({e})"
    return f"<h3>Database Connection: {status}</h3>"

def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed

# Yeni görev oluşturma işlemi
@views.route('/create_note', methods=['POST'])
@login_required
def create_note():
    # GET: Form sayfasını göster
    if request.method == 'GET':
        categories = Category.query.all()
        return render_template('new_note.html', categories=categories, active_page='new_note')
    
    # POST: Form verilerini işle
    # -----------------------------
    # FORM VERİLERİ
    # -----------------------------
    title = (request.form.get("title") or "").strip()
    description = request.form.get("description") or None
    category_id = request.form.get("category_id") or None
    
    # Boş string'i None'a çevir
    if category_id == "":
        category_id = None
    else:
        category_id = int(category_id) if category_id else None
    
    uploaded = request.files.get("file")

    # -----------------------------
    # TARİHLER
    # -----------------------------
    start_date = None
    deadline = None
    duration_days = None

    start_raw = request.form.get("start_date")
    deadline_raw = request.form.get("deadline")
    duration_raw = request.form.get("duration")

    try:
        if start_raw:
            start_date = datetime.strptime(start_raw, "%Y-%m-%dT%H:%M")
            if start_date.tzinfo is None:
                start_date = pytz.utc.localize(start_date)

        if deadline_raw:
            deadline = datetime.strptime(deadline_raw, "%Y-%m-%dT%H:%M")
            if deadline.tzinfo is None:
                deadline = pytz.utc.localize(deadline)

        if duration_raw and duration_raw.strip():
            duration_days = int(duration_raw)
    except ValueError as e:
        flash("Tarih veya süre formatı hatalı.", "error")
        categories = Category.query.all()
        return render_template('new_note.html', categories=categories, active_page='new_note')

    # -----------------------------
    # VALIDATION
    # -----------------------------
    if not title:
        flash("Görev başlığı zorunludur.", "error")
        categories = Category.query.all()
        return render_template('new_note.html', categories=categories, active_page='new_note')

    if deadline and start_date and deadline < start_date:
        flash("Bitiş tarihi başlangıçtan önce olamaz.", "error")
        categories = Category.query.all()
        return render_template('new_note.html', categories=categories, active_page='new_note')

    # -----------------------------
    # DOSYA KONTROL
    # -----------------------------
    filename = None
    ext = None

    if uploaded and uploaded.filename:
        filename = secure_filename(uploaded.filename)
        ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

        allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "txt"})
        if allowed and ext not in allowed:
            flash(f"Bu dosya türüne ({ext}) izin verilmiyor.", "error")
            categories = Category.query.all()
            return render_template('new_note.html', categories=categories, active_page='new_note')

    # -----------------------------
    # NOTE OLUŞTUR
    # -----------------------------
    new_note = Note(
        title=title[:200],
        description=description,
        user_id=current_user.id,
        category_id=category_id,
        start_date=start_date,
        duration_days=duration_days,
        deadline=deadline
    )

    try:
        db.session.add(new_note)
        db.session.flush()  # note.id al

        # -----------------------------
        # DOSYA KAYDET
        # -----------------------------
        if uploaded and filename:
            stored_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
            upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, stored_name)
            uploaded.save(file_path)

            attachment = Attachment(
                filename=filename,
                stored_name=stored_name,
                mime_type=uploaded.mimetype,
                size=os.path.getsize(file_path),
                note_id=new_note.id,
            )

            db.session.add(attachment)

        db.session.commit()
        flash("Görev başarıyla oluşturuldu! 🎉", "success")
        return redirect(url_for("views.gorevler"))

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("create_note error")
        flash("Görev oluşturulurken hata oluştu. Lütfen tekrar deneyin.", "error")
        categories = Category.query.all()
        return render_template('new_note.html', categories=categories, active_page='new_note')

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
    user = User.query.get_or_404(current_user.id)
    # Kullanıcının kendi notunu düzenlemesini sağla
    if note.user_id != current_user.id and user.role != 'admin':
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
    status_filter = request.args.get('status')
    default_mode = int(request.args.get('default_mode', 1))
    user_id = request.args.get('user_id', type=int)
    category_id = request.args.get('category_id', type=int)  # YENİ: Kategori filtresi

    if not status_filter:
        status_filter = {1: 'all', 2: 'active', 3: 'passive'}.get(default_mode, 'all')

    # --- USER & ROLE FILTER ---
    base_query = Note.query
    
    if user_id:
        base_query = base_query.filter_by(user_id=user_id)
    else:
        if current_user.role == "admin":
            pass  # Tüm notları göster
        else:
            base_query = base_query.filter_by(user_id=current_user.id)
    
    # TÜM NOTLARI AL (Kategori sayıları için)
    all_notes = base_query.all()
    
    # --- CATEGORY FILTER ---
    query = base_query
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    notes = query.all()

    # --- KATEGORİLERİ ÇEK ---
    if current_user.role == "admin":
        # Admin tüm kategorileri görsün
        all_categories = Category.query.all()
    else:
        # Kullanıcının notlarındaki kategorileri göster
        user_note_ids = [n.id for n in Note.query.filter_by(user_id=current_user.id).all()]
        category_ids = db.session.query(Note.category_id).filter(
            Note.id.in_(user_note_ids),
            Note.category_id.isnot(None)
        ).distinct().all()
        category_ids = [c[0] for c in category_ids]
        all_categories = Category.query.filter(Category.id.in_(category_ids)).all() if category_ids else []

    now = datetime.now(pytz.utc)

    # ÖNCE TÜM NOTLAR İÇİN RENK VE ZAMAN HESAPLA
    for note in notes:
        note_date = note.date
        if note_date.tzinfo is None:
            note_date = note_date.replace(tzinfo=pytz.utc)

        seconds = int((now - note_date).total_seconds())

        if seconds < 60:
            note.time_passed = f"{seconds} saniye önce"
            note.color = "green"
        elif seconds < 3600:
            note.time_passed = f"{seconds // 60} dakika önce"
            note.color = "orange"
        elif seconds < 86400:
            note.time_passed = f"{seconds // 3600} saat önce"
            note.color = "red"
        else:
            note.time_passed = f"{seconds // 86400} gün önce"
            note.color = "brown"

    # SONRA STATUS FİLTRESİ UYGULA (Template'de filtreleme yapılacak)
    # Template'deki {% if (default_mode == 1) or ... %} kısmı zaten filtreliyor

    return render_template(
        "gorevler.html",
        notes=notes,
        all_notes=all_notes,  # YENİ: Kategori sayıları için
        default_mode=default_mode,
        active_page='gorevler',
        categories=all_categories,
        selected_category_id=category_id
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

@views.route('/new-task')
@login_required
def new_task():
    return render_template('new_task.html', active_page='new_task')


@views.route('/istatistikler')
@login_required
def istatistikler():
    user_id = current_user.id
<<<<<<< HEAD
    now = datetime.now(pytz.utc)
    all_notes = Note.query.filter_by(user_id=user_id).all()
    
    total = len(all_notes)
    completed = sum(1 for n in all_notes if n.completed)
    
    # Geciken: Tamamlanmamış VE deadline'ı geçmiş
    overdue = sum(1 for n in all_notes if not n.completed and n.deadline and (n.deadline.replace(tzinfo=pytz.utc) if n.deadline.tzinfo is None else n.deadline) < now)
    
    # Devam Eden: Tamamlanmamış VE (deadline'ı geçmemiş VEYA deadline'ı yok)
    continuing = total - completed - overdue

    completion_percentage = round((completed / total * 100), 1) if total > 0 else 0

    return render_template(
        'istatistikler.html',
        total_tasks=total,
        completed_tasks=completed,
        overdue_tasks=overdue,
        continuing_tasks=continuing,
        completion_percentage=completion_percentage
=======

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
>>>>>>> 8ab0c1b3eb0abcb6b10b7c15856b73f85100c0c7
    )
