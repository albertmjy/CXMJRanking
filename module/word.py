

import json
import io

from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, aliased
from sqlalchemy.sql import exists

def write():
    return "I'm the word"

def read_data():
    with io.open("static/resources/source2.json") as fp:
        # json_data = json.load(fp)
        json_data = _read_db()
        # _conver_to_db(json_data)
    return json_data


def _read_db():
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

    Session = sessionmaker(bind=eng)
    ses = Session()

    # # select * from Categories a where exists (select RootCategory from Categories where RootCategory=a.RootCategory group by RootCategory having count(*)>1)
    # ali_cat = aliased(Category)
    # # condition stmt having sub category
    # stmt = ses.query(Category).filter(Category.RootCategory==ali_cat.RootCategory).group_by(Category.RootCategory).having(func.count(Category.RootCategory) > 1)
    # rs3 = ses.query(ali_cat).filter(stmt.exists())
    # for cat in rs3:
    #     print("\t", cat.CategoryId, cat.RootCategory, cat.SubCategory)

    # start real work
    cat_count = ses.query(Category).count()

    json_response = dict()
    cat = ses.query(Category)
    # create json structure
    for c in cat:
        if (c.SubCategory is not None):
            json_response[c.RootCategory] = {} if c.RootCategory not in json_response else json_response[c.RootCategory]
            json_response[c.RootCategory][c.SubCategory] = []
        else:
            json_response[c.RootCategory] = []
    # print("\t\t", json_response)

    # fill the word
    all_words = ses.query(Word)
    for word in all_words:
        root_cat = word.Category.RootCategory
        sub_cat = word.Category.SubCategory
        item = {'key':word.Key, 'name':word.Name, 'value':word.Value}
        if sub_cat is None:
            json_response[root_cat].append(item)
        else:
            json_response[root_cat][sub_cat].append(item)

    # for i in range(1, cat_count+1):
    #     words_x = all_words.filter(Word.CategoryId==i)
    #     for w in words_x:
    #         print(w.Category.RootCategory, w.Category.SubCategory, w.Name)
    #         if (w.Category.SubCategory is None):
    #             json_response[w.Category.RootCategory]
    #
    #         json_response[w.Category.RootCategory]
    return json_response



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

