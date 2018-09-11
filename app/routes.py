from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    robot = {'name': 'Norma'}
    stories = [
        {   
            'title': 'Drageridderne - Tiggerdrengen Tam',
            'author': {'firstname': 'John', 'lastname': 'Jones'},
            'cover_url': 'static/stories/drageridderen/assets/images/cover-dragekrigeren-tiggerdrengen-tam.jpg',
            'data_url': 'static/stories/drageridderen/drageridderen.json'
        },
        {   
            'title': 'Drageridderne - Tiggerdrengen Tam',
            'author': {'firstname': 'John', 'lastname': 'Jones'},
            'cover_url': 'static/stories/drageridderen/assets/images/cover-dragekrigeren-tiggerdrengen-tam.jpg',
            'data_url': 'static/stories/drageridderen/drageridderen.json'
        },
    ]
    return render_template('index.html', title='Robotten min laesemakker', robot=robot, stories=stories)