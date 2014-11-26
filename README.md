MirrorKAN
=========

MirrorKAN is the CKAN repository server. It has the following features:

- Continuous integration of CKAN and its toolset
- Can update NetKAN mods and automatically push to CKAN-meta
- Can automatically do a deep copy of any CKAN repository, including itself

### Requirements
- Linux
- Python 2.7
- python-dateutil
- wget
- HTTP server

### Installation
Type the following in a bash shell to download and install MirrorKAN:

`wget https://raw.githubusercontent.com/KSP-CKAN/MirrorKAN/master/bootstrap.py; python bootstrap.py`

After the configuration wizard has completed, a shell script named 'all.sh' will be created. You can launch this script manually or add it to cron to run MirrorKAN. Note that the update process will take a while and will consume non-trivial amounts of disk space (Keeping 10GB free for MirrorKAN is a good rule of thumb)
