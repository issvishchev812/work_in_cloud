import datetime
import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase

class Vacancy(SqlAlchemyBase):
    __tablename__ = 'vacancy'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    job_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    company_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    salary = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean)
