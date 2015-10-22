from flask import render_template
from . import main


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/map')
def get_map():
    return render_template('main/map.html')