from __future__ import print_function
import sys
from flask import render_template
from flask import request
from app import app
import json
import os

import sys


@app.route('/')
@app.route('/index')
def index():
    for story_path in stories:
        story_data.append(read_json(story_path))
    return render_template('index.html', title='Robotten min laesemakker', story_data=story_data, )

@app.route('/story')
def story():
    global story_data, story_id, my_story, json_path, chapter, page, animation

    story_id = int(request.args.get('story', None))
    json_path = stories[story_id]
    fprint(json_path)
    json_path.rsplit('/',1)[0] #cut off *.json in path.
    init_story(json_path) #set active_story
    return render_template('story.html', title='story', story_data=my_story, story_id=story_id, story_path=json_path.rsplit('/',1)[0])

@app.route('/page')
def page():
    global story_data, story_id, my_story, json_path, chapter, page, animation, active_story

    #from json: chapters -> pages -> content
    #check for animations.
    page_content = story_tracker()
    fprint("page content:")
    fprint(page_content)
    
    return render_template('page.html', title='page', content = page_content)


@app.route('/choice')
def choice():
    global story_data, story_id, my_story, json_path, chapter, page, animation, active_story

    return render_template('choice.html', title='choice')    

@app.route('/question')
def question():
    global story_data, story_id, my_story, json_path, chapter, page, animation, active_story

    return render_template('question.html', title='question')    



""""*** utilities ***"""


def read_json(path):
    with app.open_resource(path) as f:
        return json.load(f)

def fprint(data):
    print(data, file=sys.stdout)

def init_story(path):
    global story_data, story_id, my_story, json_path, chapter, page, animation, active_story

    active_story = read_json(path)
    chapter = len(active_story['chapters'])
    fprint("story name: " + active_story['title']+". Story author: " + active_story['author'])
    fprint("number of chapters: " + str(chapter))

def story_tracker():
    global story_data, story_id, my_story, json_path, chapter, page, animation, active_story

    if len(active_story['chapters']) > 0:
        #there are unread chapters
        fprint("chapter count: " + str(len(active_story['chapters'])))

        if len(active_story['chapters'][0]['pages']) > 0:
            #there are unread pages
            fprint("page count: " + str(len(active_story['chapters'][0]['pages'])))
            #check if animation is given
            page = active_story['chapters'][0]['pages'][0] #get uppermost page

            if 'animation' in page.keys():
                fprint("do say()/runBehavior(): " + page['animation'])

            #data to return
            page_content = active_story['chapters'][0]['pages'][0]['content']

            #finally
            active_story['chapters'][0]['pages'].pop(0)

        else:
            #end of chapter
            question = active_story['chapters'][0]['question']
            fprint(question)
            active_story['chapters'].pop(0)
            return ["question", question]
    else:
        #all chapters have been read
        fprint("story is complete!")
        return ["complete", ""]

    return ["content", page_content]


stories = os.listdir('app/static/stories') #subfile-, and dir names in the stories dir
#fprint("stories from json file: " + str(stories) + ".\nExpecting type list; " + str(type(stories)))

#TODO DELETE HOTFIX
stories = ['book1', 'book2']

for idx, book in enumerate(stories): #expected format: #stories = ['static/stories/book1/book1.json', 'static/stories/book2/book2.json']
    stories[idx] = "static/stories/%s/%s.json" %(book, book)

story_data = []
story_id = -1
my_story = None
json_path = ""
chapter = -1
page = -1
animation = ["type","synchronicity", "path"] #e.g. ["say", 'async', "animations/Stand/Sky_01"]
active_story = "" #dict from json