from flask_app import db

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_file=db.Column(db.LargeBinary,nullable=False)
