from flask import render_template,request,Blueprint
from flask_app.model import Resume

resume=Blueprint('resume',__name__)

@resume.route('/')
def index():
    return render_template('index.html')
