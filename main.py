import os
from datetime import datetime

from flask import Flask, render_template, redirect, request, flash, url_for, abort
from werkzeug.utils import secure_filename

from data import db_session
from data.jobsform import JobsForm
from data.loginform import LoginForm
from data.registration_form import RegisterForm, ExecutorRegistrationForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.user import User
from data.vacancy import Vacancy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

db_session.global_init("db/work_in_cloud.db")

login_manager = LoginManager()
login_manager.init_app(app)

messages = []


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
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()

        avatar = form.avatar.data
        avatar_path = None
        if avatar:
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join('static/' + app.config['UPLOAD_FOLDER'] + '/' + filename))
            avatar_path = filename
        else:
            avatar_path = r"basic_avatar.jpg"

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой email уже зарегистрирован.")

        common_data = {
            'name': form.name.data,
            'email': form.email.data,
            'about': form.about.data,
            'surname': form.surname.data,
            'role': role,
            'avatar_path': "static/" + app.config['UPLOAD_FOLDER'] + '/' + avatar_path
        }

        if role.lower() == 'executor':
            common_data.update({
                'portfolio_link': form.portfolio_link.data,
                'profession': form.profession.data
            })

        user = User(**common_data)
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
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data) and form.role.data == user.role:
            login_user(user, remember=form.remember_me.data)
            return redirect("/main")
        return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/main')
@login_required
def main_page():
    return render_template('home.html')


@app.route('/jobs')
@login_required
def jobs():
    db_sess = db_session.create_session()
    for jobs in db_sess.query(Vacancy).join(User).all():
        print(jobs.id)
    return render_template('jobs.html', arr=db_sess.query(Vacancy).join(User).all())


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
        return redirect('/jobs')
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
            return redirect('/jobs')
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
    return redirect('/jobs')


@app.route('/work/<int:job_id>')
@login_required
def work_detail(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Vacancy).join(User).filter(Vacancy.id == job_id).first()

    return render_template('work_detail.html', job=job)


@app.route('/respond_to_job/<int:job_id>', methods=['GET'])
@login_required
def respond_to_job(job_id):
    if current_user.role != 'executor':
        abort(403)

    db_sess = db_session.create_session()
    job = db_sess.query(Vacancy).get(job_id)

    if not job:
        abort(404)

    # Добавляем ID исполнителя к списку откликнувшихся
    if str(current_user.id) not in job.responders.split():
        job.responders = f"{job.responders} {current_user.id}".strip()
        db_sess.commit()

    return redirect(request.referrer or url_for('give_a_job'))


@app.route('/chat/<int:customer_id>-<int:executor_id>-<int:job_id>')
@login_required
def chat(customer_id, executor_id, job_id):
    # Проверка доступа
    db_sess = db_session.create_session()
    job = db_sess.query(Vacancy).get(job_id)
    customer = db_sess.query(User).get(customer_id)
    executor = db_sess.query(User).get(executor_id)
    if not job:
        abort(404)

    # Проверяем, что текущий пользователь - либо заказчик, либо откликнувшийся исполнитель
    responders = job.responders.split() if job.responders else []
    if not (current_user.id == customer_id or
            (current_user.role == 'executor' and str(current_user.id) in responders)):
        abort(403)

    # Здесь можно добавить логику получения сообщений
    return render_template('chat.html',
                           customer=customer,
                           executor=executor,
                           job_id=job_id,
                           job=job)


@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    job_id = request.form.get('job_id')
    receiver_id = request.form.get('receiver_id')
    message_content = request.form.get('message')

    # Здесь должна быть логика сохранения сообщения в БД
    # Например, можно создать таблицу messages и сохранять там

    flash('Сообщение отправлено', 'success')
    return redirect(url_for('chat',
                            customer_id=current_user.id if current_user.role == 'customer' else receiver_id,
                            executor_id=receiver_id if current_user.role == 'customer' else current_user.id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# @app.route("/send", methods=['POST'])
# @login_required
# def send_message():
#     participant = request.form.get('participant')
#     message_content = request.form.get('message')
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     messages.append({
#         'sender': participant,
#         'content': message_content,
#         'timestamp': now
#     })
#     print(messages)
#     return redirect(request.referrer or "/eee")


@app.route('/eee')
def eee():
    return render_template('eee.html', messages=messages)


@app.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    print(user.name)
    return render_template('profile.html', user=user)


@app.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    role = current_user.role
    if role == 'customer':
        form = RegisterForm()
    else:
        form = ExecutorRegistrationForm()

    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(id)

        if not user or user != current_user:
            abort(403)

        if user:
            form.email.data = user.email
            form.name.data = user.name
            form.surname.data = user.surname
            form.about.data = user.about
            if role == 'executor':
                form.profession.data = user.profession
                form.portfolio_link.data = user.portfolio_link

            form.avatar.data = user.avatar_path
        else:
            abort(404)

    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(id)

        if not user or user != current_user:
            abort(403)

        file = form.avatar.data
        if file is not None and file.filename != '':
            # Пользователь выбрал новый файл
            filename = secure_filename(file.filename)
            filepath = os.path.join('static', app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            user.avatar_path = filepath


        if user:
            # Обновляем данные из формы
            user.email = form.email.data
            user.name = form.name.data
            user.surname = form.surname.data
            user.about = form.about.data

            if role == 'executor':
                user.profession = form.profession.data
                user.portfolio_link = form.portfolio_link.data

            # Сохраняем изменения в базе данных
            db_sess.commit()
            return redirect('/profile')
        else:
            abort(404)

    return render_template('edit_profile.html',
                           title='Редактирование профиля',
                           form=form,
                           role=role
                           )


@app.route("/search", methods=["POST"])
@login_required
def search_jobs():
    query = request.form.get("query")  # Берём значение из input-a формы
    db_sess = db_session.create_session()
    print(query)
    if query:
        res = db_sess.query(Vacancy).filter(Vacancy.job_name.contains(query)).all()
    else:
        res = []

    return render_template("jobs.html", res=res, query=query, arr=db_sess.query(Vacancy).join(User).all())


@app.route("/about")
@login_required
def about():

    return render_template("about.html")



if __name__ == '__main__':
    app.run(port=5252, host='127.0.0.1')
