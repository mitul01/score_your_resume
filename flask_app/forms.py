from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField , FileAllowed

class ResumeForm(FlaskForm):
    career = StringField('Career',validators=[DataRequired()])
    resumeFile = FileField('Upload Resume', validators=[FileAllowed(['pdf', 'docx'])])
    submit = SubmitField('Calculate Score')
