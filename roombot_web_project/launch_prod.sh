#!/bin/bash

# Navigate to the parent directory where Pipenv is located
if cd /usr/local/bin/RoomBotUCF/; then
    echo "Changed directory to /usr/local/bin/RoomBotUCF/"
else
    echo "Directory /usr/local/bin/RoomBotUCF/ not found!"
    exit 1
fi


# Run Gunicorn inside Pipenv with a directory change
if pipenv run bash -c "cd roombot_web_project && gunicorn roombot_web_project.wsgi:application --bind 0.0.0.0:8080"; then
    echo "Gunicorn server started on 0.0.0.0:8080"
else
    echo "Failed to start Gunicorn server!"
    exit 1
fi