from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    job_name = StringField("Title of job", validators=[DataRequired()])
    work_size = IntegerField("Duration", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    salary = IntegerField("Salary", validators=[DataRequired()])
    is_finished = BooleanField("Is finished")
    submit = SubmitField('Submit')