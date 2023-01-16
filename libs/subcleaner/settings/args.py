import logging
from argparse import ArgumentParser
import glob
from pathlib import Path
from typing import Optional, List

from libs.subcleaner import languages
from . import config

logger = logging.getLogger(__name__)

parser = ArgumentParser(description="Remove ads from subtitle. Removed blocks are sent to logfile. "
                                    "Can also check that the subtitle language match the file name language code. ")

subtitles: List[Path]
parser.add_argument("subtitle", metavar="SUB", type=str, default=list(), nargs="*",
                    help="Path to subtitles to run script against. "
                         "Script currently only compatible with simple .srt files.")

libraries: List[Path]
parser.add_argument("--library", "-r", metavar="LIB", type=str, dest="library", default=list(), nargs="*",
                    help="Run the script also on any subtitle found recursively under directory LIB. "
                         "If LANG is specified it will only run it on subtitles that have a "
                         "language label matching LANG.")

language: Optional[str]
parser.add_argument("--language", "-l", metavar="LANG", type=str, dest="language", default=None,
                    help="ISO-639 language code. If this argument is set then the script will "
                         "check that the language of the content matches LANG and report results to log. "
                         "code may contain :forced or other \"LANG:<tag>\" but these tags will be ignored")

purge_list: List[int]
parser.add_argument("--destroy", "-d", type=int, nargs="+", default=list(),
                    help="original_index of blocks to remove from SUB, this option is not compatible with the "
                         "library option. When this option is passed the script will mark the "
                         "specified blocks as ads and then run normally. "
                         "Example to destroy block 4 and 78: -d 4 78")

dry_run: bool
parser.add_argument("--dry-run", "-n", action="store_true", dest="dry_run",
                    help="Dry run: If flag is set then no files are modified.")

silent: bool
parser.add_argument("--silent", "-s", action="store_true", dest="silent",
                    help="Silent: If flag is set then script don't print info messages to console.")

minimal: bool
parser.add_argument("--minimal", "-m", action="store_true", dest="minimal",
                    help="[DEPRECATED] Minimal: If flag is set then script will show less info."
                         "deprecated, this does nothing at the moment.")

removed_only: bool
parser.add_argument("--removed", "-a", action="store_true", dest="removed_only",
                    help="Removed Only: If flag is set then script will only show removed blocks.")

errors_only: bool
parser.add_argument("--errors", "-e", action="store_true", dest="errors_only",
                    help="Errors: If flag is set then script will show only "
                         "the errors and will run in --dry-run mode.")

no_log: bool
parser.add_argument("--no-log", action="store_true", dest="no_log",
                    help="No log: If flag is set then nothing is logged.")

sensitive: bool
parser.add_argument("--sensitive", action="store_true", dest="sensitive",
                    help="Sensitive: logs all blocks adjacent to ads as warnings.")

explain: bool
parser.add_argument("--explain", action="store_true", dest="explain",
                    help="Explain: when this is enabled each block will be given a list of reasons "
                         "why they got removed/warned. (debugging tool)")

args = parser.parse_args()
# check usage:

if len(args.subtitle) == 0 and len(args.library) == 0:
    parser.print_help()
    exit()

libraries = []
for library_str in args.library:
    library: Path = Path(library_str)
    if not library.is_absolute():
        if library_str[0:2] == "./":
            library = Path.cwd().joinpath(library)
        else:
            library = config.relative_base.joinpath(library)

    for item in glob.glob(glob.escape(str(library)).replace("[*]", "*")):
        item = Path(item).resolve()
        if item.is_dir():
            libraries.append(item)

subtitles = []
for file_str in args.subtitle:
    file = Path(file_str)
    if not file.is_absolute():
        if file_str[0:2] == "./":
            file = Path.cwd().joinpath(file)
        else:
            file = config.relative_base.joinpath(file)

    for item in glob.glob(glob.escape(str(file)).replace("[*]", "*")):
        item = Path(item).resolve()
        if item.is_file() and item.name[-4:] == ".srt":
            subtitles.append(item)

language = None
if args.language:
    language = args.language.replace("-", ":").split(":")[0].replace("\"", "").replace("'", "").lower()
    if not languages.is_language(language):
        logger.error("'" + args.language + "' is not a valid ISO-639 language.\n--help for more information.")
        exit(1)

destroy_list = args.destroy
if destroy_list and (len(subtitles) != 1 or len(libraries) != 0):
    logger.error("option --destroy require one and only one specified subtitle file.\nsee --help for more info.")
    exit(1)

silent = args.silent
no_log = args.no_log
dry_run = args.dry_run
errors_only = args.errors_only
removed_only = args.removed_only
sensitive = args.sensitive
explain = args.explain
