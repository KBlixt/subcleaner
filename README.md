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

Then run the script with:

```python3 ./subcleaner.py path/to/subtitle.srt```


the script comes with a default config that contains common regexes for 
English and Swedish. Remove what you don't need and 

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

If you wish to add language checking add ``` -l {{subtitles_language_code2}}"``` to the end of 
the command. It doesn't do anything currently but log a 
WARNING in the logfile if the language doesn't match with the labeled. in the future 
I hope it'll automatically delete miss-labeled languages and add them to
the bazarr blacklist in order to automatically trigger a re-download.

# Config
In the settings.config you can change regex and logging file.

### Regex:
Editing the regex fields changes what regex is used for ad-detection. 
regex should aim towards matching ads exclusively. 

### Logging:
Changing log_path changes where the removed subtitle blocks are logged.

# Thank you :)
Please, If you find any issues or a useful regex, feel free to share in "Issues".

__________________
###### Future:
Better exception handling. for now, 
just make sure that you don't run into any permission issues.
