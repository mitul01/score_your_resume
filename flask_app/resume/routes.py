from flask import render_template,request,Blueprint,flash
from flask_app.model import Resume
from flask_app.forms import ResumeForm
from flask_app.score import ScoreResume
from werkzeug.utils import secure_filename
import secrets
import os

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
                print('No selected file')
                return render_template('index.html') #return redirect(request.url)
            if file and allowed_file(file.filename):
                print('File Found')
                file_path=save_file(file)
                sr=ScoreResume(file_path,"Data Science")
                score=sum(sr.points())
                #verbs=sr.get_verbs()
                passive=sr.voice()
                print(score,passive)
                return str(score)
        else:
            return ("No file found")
