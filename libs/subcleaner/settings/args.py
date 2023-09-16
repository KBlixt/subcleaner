import argparse
import logging
import glob
from pathlib import Path
from typing import Optional, List

from libs.subcleaner import languages
from . import config

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Remove ads from subtitle. Removed blocks are sent to logfile. "
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
                         "assume that the SUB's language is LANG regardless of filenames and content. "
                         "code may contain :forced or other \"LANG:<tag>\" but these tags will be ignored")

purge_list: List[int]
parser.add_argument("--destroy", "-d", type=int, nargs="+", default=list(),
                    help="original_index of blocks to remove from SUB, this option is not compatible with the "
                         "library option. When this option is passed the script will mark the "
                         "specified blocks as ads and then run normally. "
                         "Example to destroy block 4 and 78: -d 4 78")

dry_run: bool
parser.add_argument("--dry-run", "-n", action="store_true", dest="dry_run",
                    help="Dry run: No files are modified. (debug)")

silent: bool
parser.add_argument("--silent", "-s", action="store_true", dest="silent",
                    help="Silent: Only print warnings or errors in stdout.")

minimal: bool
parser.add_argument("--minimal", "-m", action="store_true", dest="minimal",
                    help=argparse.SUPPRESS)

removed_only: bool
parser.add_argument("--removed", "-a", action="store_true", dest="removed_only",
                    help="Removed Only: Will only show removed blocks in cleaning report.")

errors_only: bool
parser.add_argument("--errors", "-e", action="store_true", dest="errors_only",
                    help="Errors: Only print errors and will run in --dry-run mode.")

no_log: bool
parser.add_argument("--no-log", action="store_true", dest="no_log",
                    help="No log: Nothing is logged to file.")

sensitive: bool
parser.add_argument("--sensitive", action="store_true", dest="sensitive",
                    help="Sensitive: Log all blocks adjacent to ads as warnings (debug).")

explain: bool
parser.add_argument("--explain", action="store_true", dest="explain",
                    help=argparse.SUPPRESS)

no_explain: bool
parser.add_argument("--no-explain", action="store_true", dest="no_explain",
                    help="No explain: suppresses explanations for why blocks got removed or received warnings.")

end_report: bool
parser.add_argument("--end-report", action="store_true", dest="end_report",
                    help="End Report: shows a report at the end displaying unique removed/warning blocks in this run"
                         "removed blocks with less than 9 warnings are sorted from fewest removed block with same content "
                         "and warning is sorted from most warned blocks with the same content. (debug)")

debug: bool
parser.add_argument("--debug", action="store_true", dest="debug",
                    help="Debug: argument collection that contains arguments: "
                         "--dry-run, --sensitive and --end-report")

args = parser.parse_args()
# check usage:

if len(args.subtitle) == 0 and len(args.library) == 0:
    parser.print_help()
    exit()

debug = args.debug
if debug:
    print("debug mode.")

if debug:
    print(f"arg.library: {args.library}")

libraries = []
for library_str in args.library:
    library: Path = Path(library_str)
    if not library.is_absolute():
        if library_str[0:2] == "./":
            library = Path.cwd().joinpath(library)
        else:
            library = config.relative_base.joinpath(library)
        if debug:
            print(f"library: {library}")
    for item in glob.glob(glob.escape(str(library)).replace("[*]", "*")):
        if debug:
            print(f"item: {item}")
        item = Path(item).resolve()
        if item.is_dir():
            libraries.append(item)
        else:
            if debug:
                print(f"not added item: {item}")
                print(f"{item.is_block_device()} {item.is_symlink()}")

if debug:
    print(f"arg.subtitle: {args.subtitle}")

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
dry_run = args.dry_run or args.debug
errors_only = args.errors_only
removed_only = args.removed_only
sensitive = args.sensitive or args.debug
explain = not args.no_explain
end_report = args.end_report or args.debug
