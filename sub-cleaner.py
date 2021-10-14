#!/usr/bin/env python3

from subcleaner.main import main
from pathlib import Path

if __name__ == '__main__':
    try:
        main(Path(__file__).absolute().parent)
        print("Sub-cleaner completed successfully.")
        exit()
    except KeyboardInterrupt:
        print("Sub-cleaner was Interrupted.")
        exit()
    except PermissionError as e:
        print("Sub-cleaner ran into an permission error. Permission denied to: \"" + e.filename + "\"")
        exit()
