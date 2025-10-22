from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from datetime import datetime
from . import db
import pytz
import json

views = Blueprint('views', __name__)


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
            'color':note.color
        })

    return render_template("home.html", user=current_user, notes=notes_with_time)



@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})