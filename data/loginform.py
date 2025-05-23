from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired
from wtforms import SelectField


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    role = SelectField('Вы: ', choices=[('customer', 'Клиент'), ('executor', 'Исполнитель')])
    submit = SubmitField('Войти')