
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, TIMESTAMP, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "User"

    UserId = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)
    TeaAge = Column(String)

class SurveyData(Base):
    __tablename__= "Survey_Data"

    SurveyId = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("User.UserId"))
    UserName = Column(String)  # backward compatibility
    SubmitDate = Column(DATETIME)
    # Arr = Column(ARRAY(String(50)))

    Timestamp = Column(TIMESTAMP,onupdate=datetime.utcnow(), default=datetime.utcnow())
    CreateTime = Column(DATETIME, default=datetime.utcnow())

    User = relationship("User")
    Form = relationship("SurveyForm")

class SurveyForm(Base):
    __tablename__ = "Survey_Form"

    FormId = Column(Integer, primary_key=True, autoincrement=True)
    FormOrder = Column(Integer)
    TeaId = Column(Integer) # left in case
    TeaName = Column(String) # left in case
    Score = Column(Float)
    ScoreInDecimal = Column(Float)
    SurveyId = Column(Integer, ForeignKey("Survey_Data.SurveyId"))

    Prop = relationship("SurveyProp")
    Comments = relationship("SurveyComments")

class SurveyProp(Base):
    __tablename__ = "Survey_Prop"

    PropId = Column(Integer, primary_key=True, autoincrement=True)
    FormId = Column(Integer, ForeignKey("Survey_Form.FormId"))
    WordId = Column(Integer, ForeignKey("Words.WordId"))

    Word = relationship("Word")

class SurveyComments(Base):
    __tablename__ = "Survey_Comments"

    CommentId = Column(Integer, primary_key=True, autoincrement=True)
    FormId = Column(Integer, ForeignKey("Survey_Form.FormId"))
    CategoryId = Column(Integer, ForeignKey("Categories.CategoryId"))
    Content = Column(String, nullable=False)

class Category(Base):
    __tablename__ = "Categories"

    CategoryId = Column(Integer, primary_key=True)
    RootCategory = Column(String)
    SubCategory = Column(String)

    Words = relationship("Word")


class Word(Base):
    __tablename__ = "Words"

    WordId = Column(Integer, primary_key=True)
    Key = Column(String)
    Name = Column(String)
    Value = Column(Float)
    Inclusion = Column(String)
    Exclusion = Column(String)
    CategoryId = Column(Integer, ForeignKey("Categories.CategoryId"))

    Category = relationship("Category")
