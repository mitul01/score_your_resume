from flask_app import db

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_file= db.Column(db.LargeBinary, nullable=False)
    file_name=db.Column(db.String,nullable=False,default="default.pdf")
    career = db.Column(db.String,nullable=False)
    weighted_score=db.Column(db.Integer,nullable=False,default=0)
