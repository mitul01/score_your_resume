from flask import render_template,request,flash,redirect,url_for
from flask_app import db,app
from flask_app.model import Resume
# from flask_app.forms import ResumeForm
from flask_app.model import Resume
from flask_app.score import ScoreResume,weighted_score,run_all
from werkzeug.utils import secure_filename
import secrets
import os
import PyPDF2
from random import randint
import time
from rq import Queue
from worker import conn
q = Queue(connection=conn)
# UPLOAD_FOLDER = os.path.join(app.root_path,'resume/resume_files')
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

def boost_score(score):
    if score<=50:
        boost=randint(0, 1)
        if boost:
            return score+20
        else:
            return score

## Routes
@app.route('/')
def index():
    return render_template('index.html',error="")

@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        if request.files['file-5[]']:
            file = request.files['file-5[]']
            if file.filename == '':
                return render_template('index.html',error="Error Try again")
            if file and allowed_file(file.filename):
                sr=ScoreResume(file,get_file_extension(file))
                keywords_score=q.enqueue(sr.points).result
                print(keywords_score)
                word_count_score=q.enqueue(sr.word_count).result
                polarity_score=q.enqueue(sr.polarity).result
                subjectivity_score=q.enqueue(sr.subjectivity).result
                passive_score=q.enqueue(sr.voice).result
                quantify_score=q.enqueue(sr.quantifier_score).result
                career=q.enqueue(sr.get_career).result
                final_score=q.enqueue(weighted_score,keywords_score,word_count_score,subjectivity_score,polarity_score,passive_score,quantify_score).result
                final_score=q.enqueue(boost_score,final_score).result
                time.sleep(15)
                # resume=Resume(file_name=secure_filename(file.filename),resume_file=file.read(),career=sr.get_career(),weighted_score=final_score)
                # db.session.add(resume)
                # db.session.commit()
                return render_template('score.html',keyword_score=keywords_score,word_count_score=word_count_score,
                                               polarity_score=polarity_score,subjectivity_score=subjectivity_score,
                                               quantify_score=quantify_score,passive_score=passive_score,final_score=final_score,
                                               career=career)
            else:
                render_template('index.html',error="Please upload .docx or pdf file")

        else:
            return render_template('index.html',error="No file uploaded")

    return render_template('index.html',error="")
