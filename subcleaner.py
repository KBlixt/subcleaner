#!/usr/bin/env python3
from configparser import DuplicateOptionError
from subcleaner.main import main
from pathlib import Path

if __name__ == '__main__':
    try:
        main(Path(__file__).absolute().parent)
        print("subcleaner completed successfully.")
        exit()
    except KeyboardInterrupt:
        print("subcleaner was interrupted.")
        exit()
    except PermissionError as e:
        print("subcleaner ran into an permission error. Permission denied to: \"" + e.filename + "\"")
        exit()
    except UnicodeDecodeError as e:
        print("subcleaner was unable to decode the file because: \"" + e.reason + "\"")
        exit()
    except DuplicateOptionError as e:
        print("subcleaner was unable to read config file because there are multiple keys with the same name: " 
              "Option '" + e.option + "' already exists in section '" + e.section + "'")
        exit()