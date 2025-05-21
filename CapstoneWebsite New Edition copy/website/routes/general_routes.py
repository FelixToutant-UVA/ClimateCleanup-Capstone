"""
General routes for the application.
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..models import Note
from .. import db
import json

general_bp = Blueprint('general_bp', __name__)

@general_bp.route('/')
def home():
    """
    Home page.
    """
    return render_template("index.html", user=current_user)

@general_bp.route('/about-us')
def about_us():
    """
    About us page.
    """
    return render_template("about_us.html", user=current_user)

@general_bp.route('/article')
def article():
    """
    Article page.
    """
    return render_template("article.html", user=current_user)

@general_bp.route('/delete-note', methods=['POST'])
def delete_note():
    """
    Delete a note.
    """
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})
