from flask import render_template,request,Blueprint,flash,redirect
from flask_app import db
from flask_app.model import Resume
from flask_app.forms import ResumeForm
from flask_app.model import Resume
from flask_app.score import ScoreResume,weighted_score
from werkzeug.utils import secure_filename
import secrets
import os
import PyPDF2

resume=Blueprint('resume',__name__)
UPLOAD_FOLDER = os.path.join(resume.root_path,'resume_files')
ALLOWED_EXTENSIONS = {'pdf','docx'}

# UTILS
def save_file(file):
    random_hex=secrets.token_hex(8)
    _,f_ext= os.path.splitext(file.filename)
    file_fn = random_hex + f_ext
    filename = secure_filename(file_fn)
    file_path= os.path.join(UPLOAD_FOLDER,filename)
    file.save(file_path)
    return file_path

def get_file_extension(file):
    ext=file.filename.rsplit('.', 1)[1].lower()
    ext= str('.'+ ext)
    return str(ext)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## Routes
@resume.route('/')
def index():
    return render_template('index.html')

@resume.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        if request.files['file-5[]']:
            file = request.files['file-5[]']
            if file.filename == '':
                return redirect('index.html') #return redirect(request.url)
            if file and allowed_file(file.filename):
                resume=Resume(file_name=file.filename,resume_file=file.read(),career="Data Science")
                db.session.add(resume)
                db.session.commit()
                print(get_file_extension(file))
                sr=ScoreResume(file,get_file_extension(file),"Data Science")
                print(sr.points())
                return render_template('score.html',keyword_points=sr.points())
        else:
            return render_template('index.html')
