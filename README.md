# A robot as a reading buddy

Instruction for setting up and running this project "Læsemakker"

## Setup
- Insert story files in 'reading-buddy\flask_server\static\stories'
- Open 'Python App.pml' in Choregraphe and install on robot.

## Launch the app on the robot
- Use voice command 'læsemakker' to launch reading_buddy
- Follow instructions on Peppers tablet.

## How to create new stories

- Navigate to '~/.local/share/PackageManager/apps/reading_buddy/flask_server/static/stories'
- Duplicate the folder 'drageridderne'
- Rename the new folder and .json. They must have identical names.
- Use the .json file as template for new content.
- Upload to robot.

## Frontend Development Setup

### Build assets

Run `yarn install` this installs all the required node packages.

Build og watch files for development:

`yarn run build:dev` or `yarn run watch`

Build for production:

`yarn run build:production`

We are assuming you have Python 2.7 installed

### Virtual environments

Run `pip install virtualenv` to install virtual environments

Create a virtual environment `virtualenv venv`

Activate the new virtual environment `source venv/bin/activate`

### Flask (Phyton framework)

To run local you need to uncomment the code in `routes.py` by removing """ in to and bottom of the file.

Install Flask `pip install flask`

Check that flask is running - run `import flask`

Tell flask what to import `export FLASK_APP=laesemakker.py`

Enable debugmode `export FLASK_ENV=development`

Run the local webserver `flask run`

