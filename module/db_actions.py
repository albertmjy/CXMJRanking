
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, TIMESTAMP, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
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
    submit_date = datetime.strptime(resp_obj['date'], '%Y-%m-%d')
    name = resp_obj['user'].strip()
    ses = db_model.Session()

    # check if date exist
    survey_model = ses.query(db_model.SurveyData).filter(db_model.SurveyData.UserName == name,
                                                  db_model.SurveyData.SubmitDate == submit_date).scalar()
    if survey_model is None:
        print(survey_model, "create new")
        create_survey(resp_obj, ses, submit_date, name)
    else:
        print(survey_model, "update")
        update_survey(resp_obj, ses, survey_model)

    # survey_data = resp_obj['surveyData']  # deprecated
    # survey_word = resp_obj['surveyWord']
    # # print(survey_word)
    # form_model_list = create_by_survey_word(survey_word, ses)
    # survey_model = db_model.SurveyData(UserName=name, Form=form_model_list, SubmitDate=datetime.strptime(submit_date, '%Y-%m-%d'))
    #
    # ses.add(survey_model)
    # ses.commit()
    #
    # return survey_model.SurveyId

def create_survey(resp_obj, ses, submit_date, name):
    # survey_data = resp_obj['surveyData']  # deprecated
    survey_word = resp_obj['surveyWord']
    # print(survey_word)
    form_model_list = create_by_survey_word(survey_word, ses)
    survey_model = db_model.SurveyData(UserName=name, Form=form_model_list,
                                       SubmitDate=submit_date)

    ses.add(survey_model)
    ses.commit()

    return survey_model.SurveyId

def update_survey(resp_obj, ses, survey_model):
    survey_word = resp_obj['surveyWord']
    for form in survey_model.Form:
        idx = form.FormOrder -1
        props = form.Prop
        comments = form.Comments

        print(survey_word[idx])
        print(props)
        print("*"*50)

        ###### update word ######
        # extract submitted word id list
        word_id_list = []
        for w in survey_word[idx]['words']:
            word_id_list.append(w['id'])

        for p in props:
            # delete cancelled word from user
            if p.WordId not in word_id_list:
                ses.delete(p)
            # remove the exists id
            else:
                word_id_list.remove(p.WordId)

        # add new left word id
        for w_id in word_id_list:
            w_model = db_model.SurveyProp(WordId=w_id)
            props.append(w_model)

        ###### update comments ######
        # extract submitted cat id list
        cat_id_list = []
        for cmt in survey_word[idx]['comments']:
            cat_id = _get_cat_id(cmt, ses)
            cat_id_list.append(cat_id)
            cmt['id'] = cat_id

        for c in comments:
            # delete cancelled comments model
            if c.CategoryId not in cat_id_list:
                ses.delete(c)
            # remove the exist comments cat id
            else:
                cat_id_list.remove(c.CategoryId)


        # add new added comments or update exists
        for cmt in survey_word[idx]['comments']:
            # new added
            if cmt['id'] in cat_id_list:
                c_model = db_model.SurveyComments(Content=cmt['val'], CategoryId=cmt['id'])
                comments.append(c_model)
            # update exists
            else:
                for c in comments:
                    if c.CategoryId == cmt['id']:
                        c.Content = cmt['val']

    ses.commit()

    print(survey_model.Form)

def _calc_score(ses, word_id_list):
    all_word_models = ses.query(db_model.Word)

    score_obj = {'sum':0, 'score':0}
    pos_sum, neg_sum = 0, 0
    for w in all_word_models:
        if w.Value > 0:
            pos_sum += w.Value
        else:
            neg_sum += w.Value

        if w.WordId in word_id_list:
            score_obj['sum'] += w.Value

    score_obj['score'] = (score_obj['sum']-neg_sum)/(pos_sum - neg_sum)
    return score_obj

def create_by_survey_word(survey_word,ses):
    form_model_list = []
    for idx, form in enumerate(survey_word):
        word_id_list = []

        form_word_list = []
        for w in form['words']:
            word_id_list.append(w['id'])  #  appended for latter score calc usage
            w_model = db_model.SurveyProp(WordId=w['id'])
            form_word_list.append(w_model)

        form_comment_list = []
        for c in form['comments']:
            cat_id = _get_cat_id(c, ses)
            # print(cat_id, c)
            c_model = db_model.SurveyComments(Content=c['val'], CategoryId=cat_id)
            form_comment_list.append(c_model)

        # calc score
        score_obj = _calc_score(ses, word_id_list)

        form_model = db_model.SurveyForm(Prop=form_word_list, Comments=form_comment_list, FormOrder=idx+1, Score=score_obj['sum'], ScoreInDecimal=score_obj['score'])
        form_model_list.append(form_model)

    return form_model_list
# temporary use
def _get_cat_id(cat_obj, ses):
    cat = cat_obj['cat']
    sub = cat_obj['sub'] if cat_obj['sub'] != "" else None
    cat_id = ses.query(db_model.Category.CategoryId).filter(db_model.Category.RootCategory==cat, db_model.Category.SubCategory==sub).scalar()

    return cat_id



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


# @Deprecated, no use any more
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