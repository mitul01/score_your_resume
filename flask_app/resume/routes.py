from flask import render_template,request,Blueprint
# from flask_app.model import Resume
from flask_app.forms import ResumeForm
from flask_app.score import ScoreResume

resume=Blueprint('resume',__name__)

def save_file(form):
    random_hex=secrets.token_hex(8)
    _,f_ext= os.path.splitext(form.filename)
    file_fn = random_hex + f_ext
    file_path= os.path.join(resume.root_path,'static','resume_files',file_fn)

    f=open(file_path,'rb')
    f.save(file_path)
    f.close()
    return file_fn,file_path

@resume.route('/')
def index():
    form=ResumeForm()
    if form.validate_on_submit():
        if form.resumeFile.data:
            resume_file,file_path=save_file(form.filename.data)
            sr=ScoreResume(file_path,form.career.data)
            sr.points()
            # resume=Resume(resume_file=resume_file,career=form.career.data)
    return render_template('index.html')
