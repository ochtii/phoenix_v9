# phoenix/app/routes/main.py
"""
Main blueprint for Phoenix root route and error handlers.
"""
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Home page route.
    """
    return render_template('base.html')
