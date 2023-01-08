#!/usr/bin/env python3
import sys

from configparser import DuplicateOptionError
from libs.subcleaner import main

import logging

logger = logging.getLogger("main")


if __name__ == '__main__':
    try:
        main.main()
        exit(0)
    except KeyboardInterrupt:
        logger.warning("subcleaner was interrupted.")
        exit(0)
    except PermissionError as e:
        logger.error("subcleaner ran into an permission error. Permission denied to: \"" + e.filename + "\"")
        exit(1)
    except DuplicateOptionError as e:
        logger.warning("subcleaner was unable to read config file \"" + e.args[2].name +
              "\" because there are multiple keys with the same name:\n" 
              "Option '" + e.option + "' already exists in section '" + e.section + "'")
        exit(1)
