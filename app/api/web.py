"""
Blueprint pour servir les pages web (frontend)
"""

from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint('web', __name__)


@bp.route('/')
def index():
    """Page d'accueil - redirige vers le dashboard"""
    return redirect(url_for('web.dashboard'))


@bp.route('/login')
def login():
    """Page de connexion"""
    return render_template('login.html')


@bp.route('/dashboard')
def dashboard():
    """Page du tableau de bord"""
    return render_template('dashboard.html')


@bp.route('/assets')
def assets():
    """Page de gestion des assets"""
    return render_template('assets.html')


@bp.route('/missions')
def missions():
    """Page de gestion des missions"""
    return render_template('missions.html')


@bp.route('/users')
def users():
    """Page de gestion des utilisateurs"""
    return render_template('users.html')


@bp.route('/reports')
def reports():
    """Page des rapports"""
    return render_template('reports.html')
