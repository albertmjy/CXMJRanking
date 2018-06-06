
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, TIMESTAMP, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from module import db_model

def create_survey_tables():
    eng = create_engine("sqlite:///data/cxmj_ranking.db")
    Base = db_model.Base

    Base.metadata.bind = eng
    Base.metadata.create_all(eng)

    Session = sessionmaker(bind=eng)
    ses = Session()

    # word1 = ses.query(db_model.Word).filter(db_model.Word.WordId == 1).first()

    props = [db_model.SurveyProp(WordId=1), db_model.SurveyProp(WordId=2), db_model.SurveyProp(WordId=8)]
    forms = [db_model.SurveyForm(Prop=props), db_model.SurveyForm(), db_model.SurveyForm(), db_model.SurveyForm()]


    datalist = [db_model.SurveyData(UserName="albert", Form=forms), db_model.SurveyData(UserName="chris")]
    ses.add_all(datalist)
    ses.commit()


def save_to_survey_table():
    pass

def load_from_survey_table():
    pass

def read_words():
    eng = create_engine("sqlite:///data/cxmj_ranking.db")
    Base = db_model.Base # declarative_base()

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
    cat_count = ses.query(db_model.Category).count()

    json_response = dict()
    cat = ses.query(db_model.Category)
    # create json structure
    for c in cat:
        if (c.SubCategory is not None):
            json_response[c.RootCategory] = {} if c.RootCategory not in json_response else json_response[c.RootCategory]
            json_response[c.RootCategory][c.SubCategory] = []
        else:
            json_response[c.RootCategory] = []
    # print("\t\t", json_response)

    # fill the word
    all_words = ses.query(db_model.Word)
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