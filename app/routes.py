from flask import render_template
from flask import request
from app import app
import json
import requests

@app.route('/')
@app.route('/index')
def index():
    stories = [
        {   
            'id' : '1',
            'data_url': 'static/stories/book1/book1.json'
        },
        {   
            'id' : '2',
            'data_url': 'static/stories/book2/book2.json'
        },
    ]
    # with app.open_resource('static/stories/book1/book1.json') as f:
    #    data = json.load(f)
    return render_template('index.html', title='Robotten min laesemakker', stories=stories )

@app.route('/story')
def story():
    story_id = request.args.get('story', None)
    #response = requests.get("static/stories/drageridderen/drageridderen.json")
    #todos = json.loads(response.text)
    return render_template('story.html', title='story', story_id=story_id )

@app.route('/page')
def page():
    return render_template('page.html', title='page')

@app.route('/choice')
def choice():
    return render_template('choice.html', title='choice')    

@app.route('/question')
def question():
    return render_template('question.html', title='question')    