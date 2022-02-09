# Subcleaner
Subcleaner is a python3 script for removing ads from .srt subtitle files.
The script is more sophisticated than a simple search and delete per line
and can use different regex profiles for different languages.
Once the script have identified ad-blocks they get removed and the remaining blocks 
get re-indexed.

The script can also determine the language in the script and inform if the actual 
language doesn't match up to the subtitle language label. This is optional. 
It uses python langdetect package to detect what actual language is in the subtitle.
However, running the language detection program takes a 
couple of seconds extra (depending on hardware). so if you run a batch job be prepared
for the extra time.

works well with [Bazarr](https://github.com/morpheus65535/bazarr) directly installed and in 
a docker container.


# Installing
Cloning and running with python3 should work. 
You can also make the script executable, the shebang is already in place

```cd /opt```

```git clone https://github.com/KBlixt/subcleaner.git```

```cd subcleaner```

Then install the default config by testing to run the script with:

```python3 ./subcleaner.py -h```

Or if you make it executable:

```./subcleaner.py -h```

the script comes with a default config and default regex profiles for
English and Swedish. Read the config section further down for more information about 
customization.

### Windows:
It should be the same method, although you'll have to figure out how to clone the project
and install python3. 

# Bazarr
Unlock the scripts full potential by running it after downloading a subtitle from 
[Bazarr](https://github.com/morpheus65535/bazarr). Enable custom post-processing and use
the command:

```python3 /path/to/subcleaner/subcleaner.py "{{subtitles}}" -s``` (note the quotation)

It should work 
right out the gate provided the paths and permissions are set up correctly.
If you wish to enable language checking simply add:

``` -l {{subtitles_language_code2}}```

It doesn't really do anything currently. It logs a 
WARNING in the logfile if the language doesn't match with the labeled. in the future 
I hope it'll automatically delete miss-labeled languages and add them to
the bazarr blacklist in order to automatically trigger a re-download.

in the bazarr log it should confirm that the script ran successfully or give you 
an error message that tells you what's wrong. if nothing is output then you've probably 
set the script path wrong.

### Docker

If you run Bazarr in a docker container, as you should,
make sure the Bazarr container have access to the script directory. Either
mount /opt/subcleaner directly into the container as a volume or install the script inside 
the Bazarr config directory. 

# Setup
Install the default config simply by running the script once or copy the default config into
the script root directory.
With the subcleaner.conf file installed you can modify the settings within it.
the config file contains instructions what each of the settings does.

### Regex:
Under the regex directory you can set up custom language profiles with regex 
for ad detection. 
If you need help to set up custom profiles there is a README in the directory to 
guide you.

### If you make a useful regex profile for a non-default language, PLEASE let me know! 
I'll review it and add it to the included default profiles. And it'll help out others that use 
that language. :)

# Thank you :)
Please, If you find any issues or have any questions feel free to 
open an issue or discussion.

__________________
###### Future (possibly):

* add functionality to restore false positives more easily 
and approve deletion of warning blocks.

* ASS support?

* Automatic subtitle deletion if language don't match label. (need bazarr to blacklist removed files for this to be implemented)

