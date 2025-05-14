from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from data.db_session import SqlAlchemyBase
from datetime import datetime


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    job_id = Column(Integer, ForeignKey('vacancy.id'))
    content = Column(Text)
    file_path = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    job = relationship("Vacancy")