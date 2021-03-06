MirrorKAN
=========

MirrorKAN is the [CKAN](http://ksp-ckan.org) repository server. It has the following features:

- Continuous integration of CKAN and its toolset
- Can update NetKAN mods and automatically push to CKAN-meta
- Can automatically do a deep copy of any CKAN repository, including itself

### Package dependencies
- Python 2.7
- python-dateutil
- python-jsonschema
- wget
- git
- Perl
- Mono
- python-pytz (optional, --generate-api and --generate-feeds only)
- python-pyrss2gen (optional, --generate-feeds only)

If you're on Ubuntu or Debian, this command-line will fetch all dependencies:
```
apt-get install python wget git perl python-pip mono-devel
pip install dateutils jsonschema pytz pyrss2gen
```

### Configuring the HTTP server
The only thing MirrorKAN needs from your HTTP server is to be able to serve static content at a predefined url.
This means you need to have a local _/path/to/folder/_ which is accessible through some _http://example.com/path/to/folder_ URL. Creating a _/path/to/folder/foo.txt_ means that the file _foo.txt_ must be available at _http://example.com/path/to/folder/foo.txt_. MirrorKAN will ask for both the local path and the URL path during its installation. Note that you can give MirrorKAN an arbitrary URL for testing purposes if an HTTP server is not available.
The configuration script will also ask for a directory to store the API files, this is only necessary if you are calling generate_scripts.py with --generate-api.

### Installation
Type the following in a bash shell to download and install MirrorKAN _to the current working directory_:
Note that you can re-run the same command in the future to update MirrorKAN.

```
wget -O bootstrap.py https://raw.githubusercontent.com/KSP-CKAN/MirrorKAN/master/bootstrap.py; python bootstrap.py
```

After the configuration wizard has completed, a shell script named 'all.sh' will be created. You can launch this script manually or add it to cron to run MirrorKAN. Note that the update process will take a while and will consume non-trivial amounts of disk space (Keeping 10GB free for MirrorKAN is a good rule of thumb)

### Special use-cases

To build CKAN and NetKAN from master:
```
python MirrorKAN/generate_scripts.py --build-ckan | sh
```

To regenerate NetKAN metadata only - this will build the latest netkan.exe, fetch the latest NetKAN and CKAN-meta repos, run all netkan files through netkan.exe, then make a commit and push to CKAN-meta. 
```
python MirrorKAN/generate_scripts.py --build-ckan --update-netkan --push-ckan-meta | sh 
```

### GitHub OAuth
You may wish to provide a GitHub app token in because NetKAN will generate a lot of API requests and the API rate-limiting may make it fail spontaneously. To have MirrorKAN use your GitHub token save it to `<mirrorkan_root>/MirrorKAN/github.token`
