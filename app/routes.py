from flask import render_template
from flask import request
from app import app
import json

@app.route('/')
@app.route('/index')
def index():
    robot = {'name': 'Norma'}
    stories = [
        {   
            'title': 'Bog 1',
            'author': {'firstname': 'John', 'lastname': 'Jones'},
            'cover_url': '//placehold.it/200x300&text=bog1',
            'data_url': 'static/stories/drageridderen/drageridderen.json'
        },
        {   
            'title': 'Bog 2',
            'author': {'firstname': 'John', 'lastname': 'Jones'},
            'cover_url': '//placehold.it/200x300&text=bog2',
            'data_url': 'static/stories/drageridderen/drageridderen.json'
        },
    ]
    return render_template('index.html', title='Robotten min laesemakker', robot=robot, stories=stories )

@app.route('/story')
def story():
    return render_template('story.html', title='story')

@app.route('/page')
def page():
    return render_template('page.html', title='page')

@app.route('/choice')
def choice():
    return render_template('choice.html', title='choice')    

@app.route('/question')
def question():
    return render_template('question.html', title='question')    