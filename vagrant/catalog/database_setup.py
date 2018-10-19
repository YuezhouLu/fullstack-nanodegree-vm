import os
import sys
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))


class Maker(Base):
    __tablename__ = 'maker'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    logo = Column(String(250), nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref = 'maker')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo
        }


class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    date = Column(DateTime, nullable = False)
    description = Column(String(250))
    photo = Column(String(250))
    maker_id = Column(Integer, ForeignKey('maker.id'))
    maker = relationship(Maker, backref = backref('model', cascade = 'all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref = 'model')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'photo': self.photo,
            'maker': self.maker.name
        }

engine = create_engine('sqlite:///mygarage.db')

Base.metadata.create_all(engine)