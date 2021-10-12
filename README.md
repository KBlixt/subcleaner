# Sub-Cleaner
Sub-cleaner is a python3 script for removing adds from .srt subtitle files.
The script is more sophisticated than a simple search and delete per line.
It matches each block against all regexes included in the config. Then the blocks that 
have the most matches gets removed. only the first 15min / last 10 blocks 
in the file are analyzed.
Once the script have identified add-blocks they get removed and the remaining blocks 
get re-indexed.

The script can also determine the language in the script and inform if the language 
in the file doesn't match up to the subtitle language label. this is optional.
# Installing
Cloning and running with python3 should work. 
You can also make the script executable, the shebang is already in place

```cd /opt```

```git clone https://github.com/KBlixt/sub-cleaner.git```

```cd sub-cleaner```

```python3 ./sub-cleaner.py path/to/subtitle.srt```

Unlock the scripts full potential by running it after downloading a subtitle from 
[Bazarr](https://github.com/morpheus65535/bazarr). Enable custom post-processing and use
the command:

```python3 /path/to/sub-cleaner/sub-cleaner.py "{{subtitles}}"``` (note the quotation)

If you run Bazarr in a docker container, as you should,
make sure the Bazarr container have access to the script directory. Either
mount /opt/sub-cleaner into the container as a volume or install the directory inside 
the Bazarr config directory. It should work 
right out the gate provided the paths and permissions are set up correctly.
# Config
In the settings.config you can change regex and logging file.
### Regex:
Editing the regex fields changes what regex is used for add-detection. 
regex should aim towards matching adds exclusively. 

### Logging:
Changing log_path changes where the removed subtitle blocks are logged.
# Thank you :)
Please, If you find any issues or a useful regex, feel free to share in "Issues".
### Future:
- Better exception handling.
- Better logging.