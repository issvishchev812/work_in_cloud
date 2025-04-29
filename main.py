from flask import Flask, render_template, redirect, request, flash, url_for
from data import db_session
from data.loginform import LoginForm
from data.users import User
from data.registration_form import RegisterForm, ExecutorRegistrationForm
from flask_login import LoginManager, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/work_in_cloud.db")

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_role')
def select_role():
    return render_template('select_role.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    print(form.data)
    role = request.args.get('role', None)
    if not role or role.lower() not in ['customer', 'executor']:
        flash('Пожалуйста, выберите правильный тип учетной записи.', 'warning')
        return redirect(url_for('select_role'))  # Перенаправляем обратно на выбор роли

    if role.lower() == 'executor':
        role_name_for_h1 = 'исполнителя'

        form = ExecutorRegistrationForm()
    else:
        role_name_for_h1 = 'заказчика'

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            portfolio_link=form.portfolio_link.data,
            profession=form.profession.data,
            surname=form.surname.data,
            role=role
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, role=role, rnfh=role_name_for_h1)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=5252, host='127.0.0.1')

