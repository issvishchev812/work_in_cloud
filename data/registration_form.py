from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired, InputRequired, Optional


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    avatar = FileField(label='Выберите аватарку', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только jpg/png'),
        Optional(),  # Сделали поле опциональным
    ])
    submit = SubmitField('Войти')

class ExecutorRegistrationForm(RegisterForm):
    # Дополнительные поля для исполнителя
    portfolio_link = StringField('Ссылка на портфолио', validators=[DataRequired()])
    profession = StringField('Профессия', validators=[DataRequired()])