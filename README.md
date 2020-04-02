# architecture-collection
Awesome architecture collection for python

#### Command line

apt-get install build-essential python-dev

gunicorn --workers=2 --bind=0.0.0.0:5000 app:app
uwsgi --socket :3031 --logger file:logfile=/tmp/uwsgi.log,maxsize=2000000

Here is an example of my configuration file, placed in /etc/logrotate.d/my_app:

~/Documents/python-world/python-clean-architecture/logs/access.log {
    daily
    compress
    missingok
    dateext
    dateformat -%Y-%m-%d
    size 10k
    dateyesterday
    rotate 10000
}
Rotate monthly, add -YEAR-MONTH to rotated files, keep 10000 rotated files (see man logrotate).

The paths at first line are declared in my gunicorn_start script, something like:

/my/virtualenv/bin/gunicorn OPTIONS \
    --access-logfile /path/to/my/logs/gunicorn-access.log \
    --error-logfile /path/to/my/logs/gunicorn-error.log
