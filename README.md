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
- git
- HTTP server
- Perl
- Java
- All of NetKAN's requirements

### Configuring the HTTP server
The only thing MirrorKAN needs from your HTTP server is to be able to serve static content at a predefined url.
This means you need to have a local _/path/to/folder/_ which is accessible through some _http://example.com/path/to/folder_ URL. Creating a _/path/to/folder/foo.txt_ means that the file _foo.txt_ must be available at _http://example.com/path/to/folder/foo.txt_. MirrorKAN will ask for both the local path and the URL path during its installation. Note that you can give MirrorKAN an arbitrary URL for testing purposes if an HTTP server is not available.

### Installation
Type the following in a bash shell to download and install MirrorKAN _to the current working directory_:
Note that you can re-run the same command in the future to update MirrorKAN.

```
wget -O bootstrap.py https://raw.githubusercontent.com/KSP-CKAN/MirrorKAN/master/bootstrap.py; python bootstrap.py
```

After the configuration wizard has completed, a shell script named 'all.sh' will be created. You can launch this script manually or add it to cron to run MirrorKAN. Note that the update process will take a while and will consume non-trivial amounts of disk space (Keeping 10GB free for MirrorKAN is a good rule of thumb)

### Special use-cases

To regenerate NetKAN metadata only - this will build the latest netkan.exe, fetch the latest NetKAN and CKAN-meta repos, run all netkan files through netkan.exe, then make a commit and push to CKAN-meta. You may wish to provide a GitHub app token in MirrorKAN/github.token because NetKAN will generate a lot of API requests and the API rate-limiting may make it fail spontaneously.
```
python MirrorKAN/generate_scripts.py --build-ckan --update-netkan --push-ckan-meta | sh 
```
