#!/usr/bin/env python3

from subcleaner.main import main
from pathlib import Path

if __name__ == '__main__':
    try:
        main(Path(__file__).absolute().parent)
    except KeyboardInterrupt:
        print("Interrupted")
        exit()
