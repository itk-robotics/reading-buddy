from __future__ import print_function
import sys
from flask import render_template
from flask import request
from app import app
import json

import sys

stories = ['static/stories/book1/book1.json',
           'static/stories/book2/book2.json']

story_data = []
for story_json in stories:
    with app.open_resource(story_json) as f:
        json_data = json.load(f)
    story_data.append(json_data)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Robotten min laesemakker', story_data=story_data, )

@app.route('/story')
def story():
    story_id = int(request.args.get('story', None))
    my_story = story_data[story_id]
    print(stories[story_id], file=sys.stdout)
    return render_template('story.html', title='story', story_data=my_story, story_id=story_id)

@app.route('/page')
def page():
    return render_template('page.html', title='page')

@app.route('/choice')
def choice():
    return render_template('choice.html', title='choice')    

@app.route('/question')
def question():
    return render_template('question.html', title='question')    


#def parse_story_json():
    #print data[0].keys()[story_id][1]

