"""
from __future__ import print_function #for debugging
import sys
import os
sys.path.insert(0, os.getcwd()+'/../packages') #TODO DELETE /..
from flask import render_template
from flask import request
from flask_server import flaskapp
import json

@flaskapp.route('/')
@flaskapp.route('/index')
def index():

    #fprint("story_data before return")
    #fprint(story_data)
    #fprint(_json_paths)
    fprint(_json_paths)

    return render_template('index.html', title='Robotten min laesemakker', story_data=story_data, story_path=_json_paths)

@flaskapp.route('/story')
def story():
    global story_data, story_id, my_story, json_path, current_chapter, current_page, animation, the_end

    the_end = False #starting a new story?
    story_id = int(request.args.get('story', None))
    json_path = stories[story_id]
    fprint(json_path)
    json_path.rsplit('/',1)[0] #cut off *.json in path.
    init_story(json_path)
    return render_template('story.html', title='story', story_data=story_data, story_id=story_id, story_path=json_path.rsplit('/',1)[0])

@flaskapp.route('/page')
def page():
    global story_data, story_id, my_story, json_path, current_chapter, current_page, animation, active_story, last_page, the_end

    #from json: chapters -> pages -> content
    #check for animations.
    if not the_end:
        fprint("current_page: " + str(current_page))
        fprint("current_chapter: " + str(current_chapter))
        page_content = active_story['chapters'][current_chapter]['pages'][current_page]['content']
        next_page() #increment current_page and current_chapter
    else:
        page_content = ["the end"]

    #fprint("page content:")
    #fprint(page_content)
    #fprint("last_page = "+ str(last_page))
    
    return render_template('page.html', title='page', content=page_content, story_id=story_id, lastpage = last_page, theend=the_end)


@flaskapp.route('/question')
def question():
    global story_data, story_id, my_story, json_path, current_chapter, current_page, animation, active_story, last_page

    question = active_story['chapters'][current_chapter]['question']
    choice_1 = active_story['chapters'][current_chapter]['options'].keys()[0]
    choice_2 = active_story['chapters'][current_chapter]['options'].keys()[1]

    return render_template('question.html', title='question', question=question, choice_1=choice_1, choice_2=choice_2)


@flaskapp.route('/choice')
def choice():
    global story_data, story_id, my_story, json_path, current_chapter, current_page, animation, active_story, last_page

    user_choice = request.args.get('choice', None)
    fprint("choice content, user selected: " + user_choice)
    fprint("initiate say or animation:")
    fprint(active_story['chapters'][current_chapter]['options'][user_choice])
    last_page = False  # reset bool to default
    current_chapter = current_chapter + 1

    return render_template('choice.html', title='choice', choice=user_choice)



#*** utilities ***


def read_json(path):
    with flaskapp.open_resource(path) as f:
        return json.load(f)

def fprint(data):
    print(data, file=sys.stdout)

def init_story(path):
    global story_data, story_id, my_story, json_path, current_chapter, current_page, animation, active_story

    active_story = read_json(path)
    current_chapter = 0
    current_page = 0
    fprint("story name: " + active_story['title']+". Story author: " + active_story['author'])



def next_page():
    global story_data, story_id, my_story, json_path, current_chapter, current_page, animation, active_story, last_page, the_end


    if (current_page+1) == len(active_story['chapters'][current_chapter]['pages']):
        fprint("end of chapter")
        current_page = 0
        last_page = True

    if (current_chapter+1) == len(active_story['chapters']):
        fprint("end of story")
        the_end = True

    current_page =  current_page + 1
    #fprint("number of pages in current chapter:")
    #fprint(len(active_story['chapters'][current_chapter]['pages']))

stories = next(os.walk('flask_server/static/stories/'))[1] #subfile-, and dir names in the stories dir
#fprint("stories from json file: " + str(stories) + ".\nExpecting type list; " + str(type(stories)))

for idx, book in enumerate(stories):
    stories[idx] = "static/stories/%s/%s.json" % (book, book)

#expected format: #stories = ['static/stories/book1/book1.json', 'static/stories/book2/book2.json']

story_data = []
story_id = -1
my_story = None
json_path = ""
current_chapter = -1
current_page = -1
animation = ["type","synchronicity", "path"] #e.g. ["say", 'async', "animations/Stand/Sky_01"]
active_story = "" #dict from json
last_page = False
the_end = False

_json_paths = []

for story_path in stories:
    _json_paths.append(story_path.rsplit('/', 1)[0])
    story_data.append(read_json(story_path))

def get_old_content_format():
    fprint("get old tracker format")
    fprint(story_tracker_deprecate())
    fprint(story_tracker_deprecate())
    fprint(story_tracker_deprecate())
    fprint(story_tracker_deprecate())
    fprint(story_tracker_deprecate())




def story_tracker_deprecate(): #todo delete
    global story_data, story_id, my_story, json_path, current_chapter, current_page, animation, active_story, last_page

    if len(active_story['chapters']) > 0:
        #there are unread chapters
        fprint("chapter count: " + str(len(active_story['chapters'])))

        if len(active_story['chapters'][0]['pages']) > 0:
            #there are unread pages
            fprint("page count: " + str(len(active_story['chapters'][0]['pages'])))
            #check if animation is given
            current_page = active_story['chapters'][0]['pages'][0] #get uppermost page

            if 'animation' in current_page.keys():
                fprint("do say()/runBehavior(): " + current_page['animation'])

            #data to return
            page_content = active_story['chapters'][0]['pages'][0]['content']

            active_story['chapters'][0]['pages'].pop(0)
            if len(active_story['chapters'][0]['pages']) == 0:
                last_page = True
            else:
                last_page = False


        else:
            #end of chapter
            question = active_story['chapters'][0]['question']
            fprint("question type = " + str(type(question)))
            fprint(question)
            active_story['chapters'].pop(0)
            #TODO return 'warning' at last page / before question....

            return question
    else:
        #all chapters have been read
        fprint("story is complete!")
        return ["complete", ""]

    return ["content", page_content]

"""