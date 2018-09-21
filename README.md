# A robot as a reading buddy

Instruction for setting up and running this project "Læsemakker"

## Setup

- Copy reading_buddy to '~/.local/share/PackageManager/apps/'

## Installation

- N/A

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
