from pathlib import Path


class Directives(object):
    regex_list: list
    log_dir: Path
    subtitle_file: Path
    language: str
    dry_run: bool
    silent: bool
    no_log: bool

    def __init__(self):
        self.regex_list = []
        self.log_dir = None
        self.subtitle_file = None
        self.language = None
        self.dry_run = True
        self.silent = False
        self.no_log = False
