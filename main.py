from flask import Flask, render_template
from flask import jsonify,url_for,send_file
from flask import request, json

# import json

from module import survey_serv
from module import word


app = Flask(__name__)
# app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def hello_world():
    return render_template("hello.html")

@app.route('/word/<action>')
def _word(action):
    if action == "show":
        return render_template('word/show.html', action=action, data=word.read_data(), url=request.url)
    if action == "edit":
        return render_template("word/edit.html", action=action, host_url=request.host_url)

# @app.route('/survey/save', method=['POST'])
@app.route('/survey/<action>', methods=['GET', 'POST'])
def survey(action):
    if action == 'edit':
        data = word.read_data()
        keys = list(data.keys())
        return render_template('survey/edit.html', action=action, data=word.read_data(), keys=keys, url=request.url)
    if action == "save" and request.method == 'POST':
        req_data = request.data
        filename = survey_serv.save(req_data)
        return filename
    if action == "list":
        return render_template('survey/list.html', action=action, data=survey_serv.list_survey(), url=request.url)
    if action == "show":
        return render_template("survey/show.html", action=action, user=request.args['user'], date=request.args['date'], url=request.url)
    if action == "analysis":
        return render_template("survey/analysis.html", action=action, date=request.args['date'])


@app.route('/service/survey/analysis', methods=['GET', 'POST'])
def survey_service_analysis():
    return survey_serv.survey_content_list(request.args['date'])

@app.route('/service/survey/list', methods=['GET', 'POST'])
def survey_service():
    return survey_serv.list_survey()

@app.route('/service/survey/show', methods=['GET', 'POST'])
def survey_service_show():
    return survey_serv.show(request.args['date'], request.args['user'])

@app.route('/data/<name>')
def data(name):
    # return url_for('static', filename='resources/source.json')
    return send_file("static/" + name)



if __name__ == '__main__':
    app.run()
