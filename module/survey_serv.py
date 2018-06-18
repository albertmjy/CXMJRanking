
import io, json, re

import time, os
from collections import Counter

from module import word
from module import db_actions

def test():
    return "life isnot easy"

def save(req_data):
    date_str = time.strftime("%Y-%m-%d")
    path_of_day = "data/"+date_str
    if not os.path.exists(path_of_day):
        os.mkdir(path_of_day)

    obj = json.loads(req_data)  # obj = json.loads(req_data.decode('utf8'))

    db_actions.save_to_survey_table(obj)

    score_list = calc_score(obj)
    obj['score_list'] = score_list
    obj['score_list_decimal'] = to_decimal(score_list, word.read_data())

    filepath = path_of_day + "/" + obj['user'] + ".json"

    with io.open(filepath, "w", encoding="utf8") as fp:
        # fp.write(req_data)
        # json.dump(obj, fp)
        fp.write(json.dumps(obj, indent=1).encode('latin-1').decode('unicode_escape'))
    return str(obj['score_list_decimal'])

def list_survey():
    list_data = dict()
    for root, path, filename in os.walk("data"):
        if not path:
            list_data[root[5:]] = filename

    return json.dumps(list_data)

def survey_content_list(date_str):
    list_content = _get_list_content(date_str)

    merge_list = merge_word(list_content)
    for tea in merge_list:
        for cat in tea:
            if isinstance(tea[cat], list):
                tea[cat] = Counter(tea[cat]).most_common()
            else:
                parent_cat = tea[cat]
                for sub in parent_cat:
                    parent_cat[sub] = Counter(parent_cat[sub]).most_common()
        print(tea)

    # for cat in merge_list:
    #     print(cat)
    #     if isinstance(merge_list[cat], list):
    #         merge_list[cat] = Counter(merge_list[cat]).most_common()
    #     else:
    #         parent_cat = merge_list[cat]
    #         for sub in parent_cat:
    #             parent_cat[sub] = Counter(parent_cat[sub]).most_common()

    # Counter to count the word
    print(merge_list)

    return json.dumps(merge_list)

# data module
def merge_word(list_content):
    count_result = []
    coll = []
    # ls = dict()
    for i in range(4):
        ls = dict()
        print("\n")
        for obj in list_content:
            print(i, "merge word:", obj)
            current_survey_data = obj['surveyData'][i]
            # print("\t", current_survey_data)

            for cat in current_survey_data:
                if 'values' in current_survey_data[cat]:
                    if cat not in ls:
                        ls[cat] = []

                    for v in current_survey_data[cat]['values']:
                        ls[cat].append(v['value'])
                    comm_list = re.findall(r"\w+", current_survey_data[cat]['comments'])
                    ls[cat] += comm_list
                    # comm_list = current_survey_data[cat]['comments'].split(' ')
                    # ls[cat] += [ el for el in comm_list if len(el)>0 ]
                else:
                    if cat not in ls:
                        ls[cat] = dict()
                    # print("\t\t", cat)
                    for sub in current_survey_data[cat]:
                        # print("\t"*3, sub, ls[cat])
                        if sub not in ls[cat]:
                            ls[cat][sub] = []
                        current_sub = current_survey_data[cat][sub]
                        # print("\t" * 4, current_sub)
                        for v in current_sub['values']:
                            ls[cat][sub].append(v['value'])
                        # comm_list += re.findall(r'\w+', current_sub['comments'])
                        comm_list = re.findall(r'\w+', current_sub['comments'])
                        ls[cat][sub] += comm_list
                        # comm_list = current_sub['comments'].split(' ')
                        # ls[cat][sub] += [el for el in comm_list if len(el)>0]

            #     print(cat)
            # print("*"*50)
        coll.append(ls)

    return coll


# data module
def _get_list_content(date_str):
    survey_data_list = []
    path = "data/" + date_str
    for fname in os.listdir(path):
        with io.open(path+"/"+fname, 'r', encoding='utf8') as fp:
            survey_data_list.append(json.load(fp))
    # for entry in os.scandir(path):
    #     if entry.is_file():
    #         with io.open(entry.path, "r", encoding='utf8') as fp:
    #             survey_data_list.append(json.load(fp))
    return survey_data_list

def show(date_str, user):
    path = "data/" + date_str + "/" + user

    with io.open(path, "r", encoding="utf8") as fp:
        json_str = fp.read()
    return json_str

def to_decimal(score_list, json_scource):
    decimal_list = []
    denominator = model_sum_pos(json_scource) - model_sum_neg(json_scource)
    for score in score_list:
        numerator = score - model_sum_neg(json_scource)
        decimal_list.append(numerator/denominator)

    return decimal_list

def calc_score(json_data):
    keys = json_data['keys']
    subs = json_data['subs']
    sv_data = json_data['surveyData']

    key_str = []
    score_list = []

    json_source = word.read_data()

    for i,v in enumerate(sv_data):
        score = 0
        cat_obj = v[keys[i]]
        print(i)

        for cat in v:
            if "values" in v[cat]:
                for it in v[cat]['values']:
                    key_str.append(it['key'])
                    score += _find_key_value(it['key'], json_source[cat])

            else:
                for sub in v[cat]:
                    # key_str.append(sub)
                    for it in v[cat][sub]['values']:
                        print(it['key'])
                        key_str.append(it['key'])
                        score += _find_key_value(it['key'], json_source[cat][sub])
        score_list.append(score)

    return score_list
    # return ' '.join(key_str)


def _find_key_value(key, cat_data):
    for it in cat_data:
        if it['key'] == key:
            return it['value']


def model_sum(model_source):
    total = 0
    total_list =[]
    for cat in model_source:
        if isinstance(model_source[cat], list):
            total_list += [it['value'] for it in model_source[cat]]
            # for it in model_source[cat]:
            #     total += it['value']
        else:
            # total += model_sum(model_source[cat])
            total_list += model_sum(model_source[cat])
    # return total
    return total_list


def model_sum_pos(model_source):
    total = 0
    for cat in model_source:
        if isinstance(model_source[cat], list):
            for it in model_source[cat]:
                if it['value'] > 0:
                    total += it['value']
        else:
            total += model_sum_pos(model_source[cat])
    return total


def model_sum_neg(model_source):
    total = 0
    for cat in model_source:
        if isinstance(model_source[cat], list):
            for it in model_source[cat]:
                if it['value'] < 0:
                    print(it['value'])
                    total += it['value']
        else:
            total += model_sum_neg(model_source[cat])
    return total

def extract_keys():
    pass