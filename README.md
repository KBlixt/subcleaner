# Subcleaner
Subcleaner is a python3 script for removing ads from .srt subtitle files.
The script is more sophisticated than a simple search and delete per line
and uses different regex profiles for different languages.
Once the script have identified ad-blocks they get removed and the remaining blocks 
get re-indexed.

Can clean entire libraries in recursive mode and works well with [Bazarr](https://github.com/morpheus65535/bazarr) 
directly installed or as a container from the [linuxserver/bazarr](https://hub.docker.com/r/linuxserver/bazarr) image.

# Installing
Cloning and running with python3 should work.

```cd /opt```

```git clone https://github.com/KBlixt/subcleaner.git```

```cd subcleaner```

Install the default config simply by running the script once or copy the default config into
the script root directory.

```python3 ./subcleaner.py -h```

With the subcleaner.conf file installed you can modify the settings within it.
the config file contains instructions what each of the settings does.

## Bazarr
Unlock the scripts full potential by running it after downloading a subtitle from 
[Bazarr](https://github.com/morpheus65535/bazarr). Enable custom post-processing and use
the command:

```python3 /opt/subcleaner/subcleaner.py "{{subtitles}}" -s``` (note the quotation)

It should work 
right out the gate provided the paths and permissions are set up correctly.

in the bazarr log it should confirm that the script ran successfully or give you 
an error message that tells you what's wrong. if nothing is output then you've probably 
set the script path wrong.

## Docker

If you run Bazarr in a docker container, as you should,
make sure the Bazarr container have access to the script directory. Either
mount /opt/subcleaner directly into the container as a volume or install the script inside 
the Bazarr config directory.

I have verified that this works on the [linuxserver/bazarr](https://hub.docker.com/r/linuxserver/bazarr) image.

# Languages:
The script have a few language profiles included by default:

- English
- Spanish
- Portuguese
- Dutch
- Indonesian
- Swedish

If you want to run the script against any other language you'll have to either create a profile for it
or disable the requirement in the subcleaner.conf file. It's recommended to create
a language profile. read the README in the regex_profiles directory for more info and guidance.

### If you make a useful regex profile for a non-default language, PLEASE let me know! 
I'll review it and add it to the included default profiles. And it'll help out others that use 
that language in the future! :)

# Setup
Install the default config simply by running the script once or copy the default config into
the script root directory.
With the subcleaner.conf file installed you can modify the settings within it.
the config file contains instructions what each of the settings does.

__________________


# Thank you :)
Please, If you find any issues or have any questions feel free to 
open an issue or discussion.

__________________
###### Future (possibly):

* Automatic subtitle deletion if language don't match label.

* better ui for confirming/reverting deletion of ads.

* ASS support?

