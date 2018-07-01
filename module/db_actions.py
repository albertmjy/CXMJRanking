
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, TIMESTAMP, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from collections import namedtuple

from module import db_model

def create_survey_tables():
    eng = create_engine("sqlite:///data/cxmj_ranking.db")
    Base = db_model.Base

    Base.metadata.bind = eng
    Base.metadata.create_all(eng)

    Session = sessionmaker(bind=eng)
    ses = Session()

    props = [db_model.SurveyProp(WordId=1), db_model.SurveyProp(WordId=2), db_model.SurveyProp(WordId=8)]
    forms = [db_model.SurveyForm(Prop=props), db_model.SurveyForm(), db_model.SurveyForm(), db_model.SurveyForm()]

    datalist = [db_model.SurveyData(UserName="albert", Form=forms), db_model.SurveyData(UserName="chris")]
    ses.add_all(datalist)
    ses.commit()


def save_to_survey_table(resp_obj):
    submit_date = resp_obj['date']
    name = resp_obj['user']
    survey_data = resp_obj['surveyData']
    survey_word = resp_obj['surveyWord']
    print(survey_word)

    eng = create_engine("sqlite:///data/cxmj_ranking.db")
    Session = sessionmaker(bind=eng)
    ses = Session()
    q = ses.query(db_model.Category)

    form_model_list = []
    for i in range(0, 4):
        print("*" * 50)
        print(survey_data[i])
        form_model = _single_form(survey_data[i], q, i)

        form_model_list.append(form_model)

    datalist = db_model.SurveyData(UserName=name, Form=form_model_list)
    ses.add(datalist)
    ses.commit()
    # print(form_model)

def _get_key_list(cat_data):
    prop_key_list = []
    for prop in cat_data["values"]:
        key = prop['key']
        prop_key_list.append(key)
    return prop_key_list

def _make_prop_model(cat_model, key_list):
    prop_model_list = []

    cat_words = cat_model.Words
    selected_word = [w for w in cat_words if w.Key in key_list]

    for word_model in selected_word:
        prop_model_list.append(db_model.SurveyProp(WordId=word_model.WordId))

    return prop_model_list

def _make_comments_model(comment, cat_id):
    return db_model.SurveyComments(Content=comment, CategoryId=cat_id)

def _single_form(form_data, q, idx):
    # q.filter()
    Flat_Category = namedtuple('flat_cat', ['cat_model', 'keys', 'comment'])
    cat_tuples = []
    # extract each word data
    for cat in form_data:
        # no sub category
        if "values" in form_data[cat]:
            cat_model = q.filter(db_model.Category.RootCategory == cat).scalar()
            # cat_model_list.append(cat_model)

            selected_key_list = _get_key_list(form_data[cat])
            flat_cat = Flat_Category(cat_model, selected_key_list, form_data[cat]['comments'])
            cat_tuples.append(flat_cat)
        # sub categories
        else:
            for subcat in form_data[cat]:
                cat_model = q.filter(db_model.Category.RootCategory == cat, db_model.Category.SubCategory == subcat).scalar()
                # cat_model_list.append(cat_model)
                selected_key_list = _get_key_list(form_data[cat][subcat])
                flat_cat = Flat_Category(cat_model, selected_key_list, form_data[cat][subcat]['comments'])
                cat_tuples.append(flat_cat)

    # 'cat_model', 'keys', 'comment'
    comment_model_list = []
    prop_model_list = []
    for cat_tup in cat_tuples:
        key_list = cat_tup.keys
        cat_model = cat_tup.cat_model
        comment = cat_tup.comment

        # make up SurveyComments model
        if comment != "":
            cat_id = cat_model.CategoryId
            comment_model_list.append( db_model.SurveyComments(CategoryId=cat_id, Content=comment))

        # make up props models
        word_models = cat_model.Words
        word_ids = [w.WordId for w in word_models if w.Key in key_list]
        prop_model_list += [db_model.SurveyProp(WordId=wid) for wid in word_ids]

    return db_model.SurveyForm(Prop=prop_model_list, Comments=comment_model_list, FormOrder=idx+1)

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
        item = {'key':word.Key, 'name':word.Name, 'value':word.Value, 'inc':word.Inclusion, 'exc':word.Exclusion, 'id':word.WordId}
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