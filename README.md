MirrorKAN
=========

MirrorKAN is the CKAN repository server. It has the following features:

- Continuous integration of CKAN and its toolset
- Can update NetKAN mods and automatically push to CKAN-meta
- Can automatically mirror any CKAN repository, including itself

Requirements:

- Linux
- Python 2.7
- python-dateutil
- wget
- HTTP server

Installation:
Type the following in a bash shell to bootstrap MirrorKAN and launch the configuration wizard:

`wget https://raw.githubusercontent.com/KSP-CKAN/MirrorKAN/master/bootstrap.py; python bootstrap.py`

After the configuration has completed, a shell script named 'all.sh' will be created. You can launch this script manually or add it to cron to run MirrorKAN.
