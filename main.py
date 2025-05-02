from flask import Flask, render_template, redirect, request, flash, url_for, abort
from data import db_session
from data.jobsform import JobsForm
from data.loginform import LoginForm
from data.executor import Executor
from data.customer import Customer
from data.registration_form import RegisterForm, ExecutorRegistrationForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.user import User
from data.vacancy import Vacancy

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
            surname=form.surname.data,
            role=role
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


@app.route('/give_a_job')
@login_required
def give_a_job():
    db_sess = db_session.create_session()
    for job in db_sess.query(Vacancy).join(Customer).all():
        print(job.id)
    return render_template('give_a_job.html', arr=db_sess.query(Vacancy).join(Customer).all())


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Vacancy(
            creator_id=current_user.id,
            job_name=form.job_name.data,
            work_size=form.work_size.data,
            description=form.description.data,
            salary=form.salary.data
        )
        db_sess.add(job)
        db_sess.commit()
        return redirect('/give_a_job')
    return render_template('add_job.html', title='Добавление работы',
                           form=form)


@app.route('/jobs_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Vacancy).get(id)
        if not jobs or jobs.customer != current_user:
            abort(403)
        if jobs:
            form.job_name.data = jobs.job_name
            form.salary.data = jobs.salary
            form.work_size.data = jobs.work_size
            form.description.data = jobs.description
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Vacancy).get(id)
        if not jobs or jobs.customer != current_user:
            abort(403)
        if jobs:
            # Обновляем данные из формы
            jobs.job_name = form.job_name.data
            jobs.salary = form.salary.data
            jobs.work_size = form.work_size.data
            jobs.description = form.description.data
            jobs.is_finished = form.is_finished.data
            # Сохраняем изменения в базе данных
            db_sess.commit()
            return redirect('/give_a_job')
        else:
            abort(404)
    return render_template('edit_jobs.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Vacancy).get(id)
    if not jobs or jobs.customer != current_user:
        abort(403)
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/give_a_job')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=5252, host='127.0.0.1')

