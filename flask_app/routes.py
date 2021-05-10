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
                scores=q.enqueue(run_all,sr)
                list_scores=scores.result
                keywords_score=list_scores[0]
                word_count_score=list_scores[1]
                polarity_score=list_scores[2]
                subjectivity_score=list_scores[3]
                passive_score=list_scores[4]
                quantify_score=list_scores[5]
                career=list_scores[6]
                # keywords_score=q.enqueue(sr.points)[0]
                # word_count_score=q.enqueue(sr.points)[1]
                # polarity_score=q.enqueue(sr.sentiment)[0]
                # subjectivity_score=q.enqueue(sr.sentiment)[1]
                # passive_score=q.enqueue(sr.voice)
                # quantify_score=q.enqueue(sr.quantifier_score)
                # career=q.enqueue(sr.get_career)
                final_score_eq=q.enqueue(weighted_score,keywords_score,word_count_score,subjectivity_score,polarity_score,passive_score,quantify_score)
                final_score=final_score_eq.result
                final_score=boost_score(final_score)
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
