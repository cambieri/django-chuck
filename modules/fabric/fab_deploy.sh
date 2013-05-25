source /home/workspace-django/virtualenvs/$SITE_NAME/bin/activate
cd /home/workspace-django/projects/$SITE_NAME/$PROJECT_NAME/
fab live prepare_deploy
fab live deploy
deactivate
