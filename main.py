from flask import Flask, render_template, redirect, request, flash, url_for
from data import db_session
from data.loginform import LoginForm
from data.executor import Executor
from data.customer import Customer
from data.registration_form import RegisterForm, ExecutorRegistrationForm
from flask_login import LoginManager, login_user, login_required, logout_user

from data.user import User

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
    return render_template('select_role.html')

@app.route('/select_role')
def select_role():
    return render_template('select_role.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    role = request.args.get('role', None)
    if not role or role.lower() not in ['customer', 'executor']:
        flash('Пожалуйста, выберите правильный тип учетной записи.', 'warning')
        return redirect(url_for('select_role'))  # Перенаправляем обратно на выбор роли

    if role.lower() == 'executor':
        form = ExecutorRegistrationForm()
    else:
        form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()

        if role.lower() == 'executor':
            if db_sess.query(Executor).filter(Executor.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")

            executor = Executor(
                name=form.name.data,
                email=form.email.data,
                about=form.about.data,
                surname=form.surname.data,
                profession=form.profession.data,
                portfolio_link=form.portfolio_link.data
            )
            executor.set_password(form.password.data)
            db_sess.add(executor)
        else:
            if db_sess.query(Customer).filter(Customer.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")

            customer = Customer(
                name=form.name.data,
                email=form.email.data,
                about=form.about.data,
                surname=form.surname.data
            )
            customer.set_password(form.password.data)
            db_sess.add(customer)

        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            surname=form.surname.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)

        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, role=role)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.role.data == 'executor':
            executor = db_sess.query(Executor).filter(Executor.email == form.email.data).first()
            if executor and executor.check_password(form.password.data):
                login_user(executor, remember=form.remember_me.data)
                return redirect("/main")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)

        else:
            customer = db_sess.query(Customer).filter(Customer.email == form.email.data).first()
            if customer and customer.check_password(form.password.data):
                login_user(customer, remember=form.remember_me.data)
                return redirect("/main")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/main')
@login_required
def main_page():
    return render_template('home.html')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=5252, host='127.0.0.1')

