# Subcleaner
Subcleaner is a python3 script for removing ads from .srt subtitle files.
The script is more sophisticated than a simple search and delete per line.
It matches each block against all regexes included in the config. Then the blocks that 
have the most matches gets removed. only the first 15min / last 10 blocks 
in the file are analyzed.
Once the script have identified ad-blocks they get removed and the remaining blocks 
get re-indexed.

The script can also determine the language in the script and inform if the language 
in the file doesn't match up to the subtitle language label. this is optional.

# Installing
Cloning and running with python3 should work. 
You can also make the script executable, the shebang is already in place

```cd /opt```

```git clone https://github.com/KBlixt/subcleaner.git```

```cd subcleaner```

Then install the default config by testing to run the script with:

```python3 ./subcleaner.py -h```

the script comes with a default config that contains common regexes for 
English and Swedish. Read the config section further down for more information.

# Bazarr
Unlock the scripts full potential by running it after downloading a subtitle from 
[Bazarr](https://github.com/morpheus65535/bazarr). Enable custom post-processing and use
the command:

```python3 /path/to/subcleaner/subcleaner.py "{{subtitles}}" -s``` (note the quotation)

If you run Bazarr in a docker container, as you should,
make sure the Bazarr container have access to the script directory. Either
mount /opt/subcleaner into the container as a volume or install the directory inside 
the Bazarr config directory. It should work 
right out the gate provided the paths and permissions are set up correctly.
If you wish to enable language checking simply add:

``` -l {{subtitles_language_code2}}"``` 

It doesn't really do anything currently. It logs a 
WARNING in the logfile if the language doesn't match with the labeled. in the future 
I hope it'll automatically delete miss-labeled languages and add them to
the bazarr blacklist in order to automatically trigger a re-download.

in the bazarr log it should confirm that the script ran successfully or give you 
an error message that tells you what's wrong. if nothing is output then you've probably 
set the script path wrong.

# Config
Install the default config by running the script once with only the '-h' argument
with subcleaner.conf installed you can change the regex and the logging file.
read instructions in the config file. the default config comes with regex for 
English subtitles and Swedish

### Regex:
Editing the regex fields changes what regex is used for ad-detection. 
Regex should aim towards matching ads exclusively. 

### Logging:
Changing log_path changes where the removed subtitle blocks are logged.

# Thank you :)
Please, If you find any issues or a useful regex, feel free to share in "Issues".

__________________
###### Future:
* Language specific regexes.


* Automatic subtitle deletion if language don't match label. (need bazarr to blacklist removed files for this to be implemented)


* Try to detect mixed blocks that are one row subtitle and one row ads.
