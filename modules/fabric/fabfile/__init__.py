from fabric.api import *
from fabric.contrib import project

"""
In order to deploy, run "fab <env> deploy"
"""

# Config. Adjust these settings according to your server
# If you need to specify a file system path, please add a trailing slash
config = {
    'live': {
        'server': 'root@cmbhosting.no-ip.biz',
        'django': {
            'site_dir_name': '$SITE_NAME-live',
            'site_root': '/opt/django/sites/$SITE_NAME-live/',
            'project_dir_name': '$PROJECT_NAME',
            'project_root': '/opt/django/sites/$SITE_NAME-live/$PROJECT_NAME/',
            'settings_module': '$PROJECT_NAME.settings.live'
        },
        'virtualenv': {
            'path': '/opt/django/virtualenvs/$SITE_NAME-live/',
            'requirements_file': '/opt/django/sites/$SITE_NAME-live/requirements/requirements_live.txt',
        },
        'git': {
            'server_name': 'origin',
            'branch_name': 'live',
        },
        'webserver': {
            'touch_file': '/opt/django/sites/$SITE_NAME-live/uwsgi/live/django_wsgi.py'
        }
    },
    'stage': {
        'server': 'root@cmbhosting.no-ip.biz',
        'django': {
            'site_dir_name': '$SITE_NAME',
            'site_root': '/opt/django/sites/$SITE_NAME-stage/',
            'project_dir_name': '$PROJECT_NAME',
            'project_root': '/opt/django/sites/$SITE_NAME-stage/$PROJECT_NAME/',
            'settings_module': '$PROJECT_NAME.settings.stage'
        },
        'virtualenv': {
            'path': '/opt/django/virtualenvs/$SITE_NAME-stage/',
            'requirements_file': '/opt/django/sites/$SITE_NAME-stage/requirements/requirements_live.txt',
        },
        'git': {
            'server_name': 'origin',
            'branch_name': 'stage',
        },
        'webserver': {
            'touch_file': '/opt/django/sites/$SITE_NAME-stage/uwsgi/stage/django_wsgi.py'
        }
    }
}

# Environments. Add as much as you defined in "config"
def stage():
    env.environment = 'stage'
    env.hosts = [config[env.environment]['server']]

def live():
    env.environment = 'live'
    env.hosts = [config[env.environment]['server']]

# Fab Tasks

def prepare_server():
    site_name = config[env.environment]['django']['site_dir_name']
    site_root = config[env.environment]['django']['site_root']
    with cd('/'):
        run('mkdir -p /opt/django/virtualenvs')
        run('mkdir -p {0}'.format(site_root))
    with cd(config[env.environment]['virtualenv']['path'] + "../"):
        run('virtualenv --no-site-packages {0}'.format(site_name))
    with cd(site_root):
        run('git init')
        run('sudo -u postgres createuser -d -R -S {0}'.format(site_name))
        run('sudo -u postgres createdb -T template1 -O {0} {1}'.format(site_name, site_name))
        run('ln -s {0}uwsgi/{1}/uwsgi.xml /etc/uwsgi/apps-enabled/{2}.xml'.format(site_root, env.environment, site_name))
        run('ln -s {0}hosting/nginx/virtualhost-{1}.conf /etc/nginx/sites-enabled/{2}.conf'.format(site_root, env.environment, site_name))	

def prepare_deploy():
    with lcd('/home/workspace-django/projects/$SITE_NAME/$PROJECT_NAME'):
        local("python2 ./manage.py test main")
    with lcd('/home/workspace-django/projects/$SITE_NAME'):
        local('git checkout master')
        local('git add -A && git commit')
        local('git push')
        local('git checkout {0}'.format(config[env.environment]['git']['branch_name']))
        local('git merge master')
        local('git push')
        local('git checkout master')

def deploy():
    """
    Deploy, migrate, collect static files, restart webserver
    """
    _git_pull()
    _migrate()
    _collect_static_files()
    _restart_webserver()

# Install requirements
def install_requirements():
    """
    This is basically the same as deployment, but additionally
    installs the requirements.
    Important: Migrations are executed too!
    """
    _git_pull()
    _install_requirements()
    _syncdb()
    _migrate()
    _restart_webserver()


# Helpers

def __activate():
    return 'export LANG=it_IT.UTF-8 && source {0}bin/activate && export DJANGO_SETTINGS_MODULE={1} && export PYTHONPATH={2}'.format(
        config[env.environment]['virtualenv']['path'],
        config[env.environment]['django']['settings_module'],
        config[env.environment]['django']['site_root'],
        )

def __deactivate():
    return 'deactivate'

def _git_pull():
    with cd(config[env.environment]['django']['site_root']):
        # git reset --hard HEAD
        run('git pull {0} {1}'.format(
            config[env.environment]['git']['server_name'],
            config[env.environment]['git']['branch_name'])
        )

def _migrate():
    with cd(config[env.environment]['django']['project_root']):
        run(
            __activate() + \
            '&& django-admin.py migrate && ' + \
            __deactivate()
        )

def _syncdb():
    with cd(config[env.environment]['django']['project_root']):
        run(
            __activate() + \
            '&& django-admin.py syncdb && ' + \
            __deactivate()
        )

def _collect_static_files():
    with cd(config[env.environment]['django']['project_root']):
        run(
            __activate() + \
            '&& django-admin.py collectstatic --noinput && ' + \
            __deactivate()
        )

def _restart_webserver():
    run('touch {0}'.format(config[env.environment]['webserver']['touch_file']))

def _install_requirements():
    with cd(config[env.environment]['django']['site_root']):
        run(
            __activate() + \
            '&& pip install -r {0} && '.format(config[env.environment]['virtualenv']['requirements_file']) + \
            __deactivate()
        )
