from flask_app import db

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_file= db.Column(db.String(20), nullable=False, default='default.pdf')
    career = db.Column(db.String,nullable=False)
