from __future__ import print_function
import sys
from flask import render_template
from flask import request
from app import app
import json
import os

import sys

stories = ['static/stories/book1/book1.json',
           'static/stories/book2/book2.json'] #TODO import list of stories from config file

story_data = []
story_id = -1
my_story = None
json_path = ""

@app.route('/')
@app.route('/index')
def index():
    for story_path in stories:
        story_data.append(read_json(story_path))
    return render_template('index.html', title='Robotten min laesemakker', story_data=story_data, )

@app.route('/story')
def story():
    story_id = int(request.args.get('story', None))
    json_path = stories[story_id]
    fprint(json_path)
    json_path = json_path.rsplit('/',1)[0] #cut off *.json in path
    return render_template('story.html', title='story', story_data=my_story, story_id=story_id, story_path=json_path)

@app.route('/page')
def page():
    #from json: chapters -> pages -> content
    #check for animations.
    
    return render_template('page.html', title='page', content = )


@app.route('/choice')
def choice():
    return render_template('choice.html', title='choice')    

@app.route('/question')
def question():
    return render_template('question.html', title='question')    


def read_json(path):
    with app.open_resource(path) as f:
        return json.load(f)
            
def fprint(data):
    print(data, file=sys.stdout)