# A robot as a reading buddy

Instruction for setting up and running this project "Læsemakker"

## Setup on robot

- Copy reading_buddy to '~/.local/share/PackageManager/apps/'

## Launch the app on the robot

- Navigate to '~/.local/share/PackageManager/apps/reading_buddy'
- Run 'python main.py'
- Connect a browser to book-server via the endpoints shown on Pepper's tablet.

## How to create new stories

- Navigate to '~/.local/share/PackageManager/apps/reading_buddy/flask_server/static/stories'
- Duplicate the folder 'drageridderne'
- Rename the new folder 'drageridderne' folder and .json. They must have identical names.
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

Install Flask `pip install flask`

Check that flask is running - run `import flask`

Run the local webserver `flask run`
