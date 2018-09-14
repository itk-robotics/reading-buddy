from __future__ import print_function #Todo delete. USED FOR logging 
from flask import render_template
from flask import request
from app import app
import json

import sys

stories = ['static/stories/book1/book1.json',
           'static/stories/book2/book2.json']
data = None

story_data = []
for story_json in stories:
    with app.open_resource(story_json) as f:
        json_data = json.load(f)
    story_data.append(json_data)

@app.route('/')
@app.route('/index')
def index():
<<<<<<< HEAD
    global data
    print('index', file=sys.stdout)
    with app.open_resource('static/stories/book1/book1.json') as f:
        data = json.load(f)
    return render_template('index.html', title='Robotten min laesemakker', stories=stories, data=data)
=======
    return render_template('index.html', title='Robotten min laesemakker', story_data=story_data)
>>>>>>> 334e2db4cd893f35f72ff7939a80a7ff79a925b1

@app.route('/story')
def story():
    global data
    print('story', file=sys.stdout)
    story_id = request.args.get('story', None)
    print('story_id = ' + str(story_id), file=sys.stdout)
    print('json data', file=sys.stdout)
    print(data, file=sys.stdout)
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


 def parse_story_json():
    global data
    print data[0].keys()[story_id][1]

