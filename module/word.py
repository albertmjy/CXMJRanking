

import json
import io

from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, aliased
from sqlalchemy.sql import exists

from module import db_actions

def write():
    return "I'm the word"

def read_data():
    # with io.open("static/resources/source2.json") as fp:
        # json_data = json.load(fp)
        # _conver_to_db(json_data)

    # db_actions.create_survey_tables()
    # json_data = json.dumps(db_actions.read_words())
    json_data = db_actions.read_words()
    return json_data


# executed once, don't use again'
def _conver_to_db(json_data):
    eng = create_engine("sqlite:///data/cxmj_ranking.db")
    Base = declarative_base()

    class Category(Base):
        __tablename__ = "Categories"

        CategoryId = Column(Integer, primary_key=True)
        RootCategory = Column(String)
        SubCategory = Column(String)

    class Word(Base):
        __tablename__ = "Words"

        WordId = Column(Integer, primary_key=True)
        Key = Column(String)
        Name = Column(String)
        Value = Column(Float)
        CategoryId = Column(Integer, ForeignKey("Categories.CategoryId"))

        Category = relationship("Category")

    Base.metadata.bind = eng
    Base.metadata.create_all(eng)

    Session = sessionmaker(bind=eng)
    ses = Session()

    cat_list = []
    word_list = []
    i = 0
    for cat in json_data:
        i += 1
        if isinstance(json_data[cat], list):
            # print(cat, json_data[cat])
            cat_list.append(Category(CategoryId=i, RootCategory=cat))
            print(i)
            for w in json_data[cat]:
                word_list.append(Word(Key=w['key'], Name=w['name'], Value=w['value'], CategoryId=i))
        else:
            # print(cat)
            i -= 1
            for sub in json_data[cat]:
                i += 1
                # print("\t- ", sub, json_data[cat][sub])
                print(i)
                cat_list.append( Category(CategoryId=i, RootCategory=cat, SubCategory=sub))
                for w in json_data[cat][sub]:
                    word_list.append(Word(Key=w['key'], Name=w['name'], Value=w['value'], CategoryId=i))

    print(cat_list)
    ses.add_all(cat_list)
    ses.add_all(word_list)
    ses.commit()

