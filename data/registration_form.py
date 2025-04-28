from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField, RadioField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    profession = StringField('Профессия', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    role = RadioField('Выберите роль', choices=[('customer', 'Заказчик'), ('executor', 'Исполнитель')],
                      validators=[DataRequired()])
    submit = SubmitField('Войти')