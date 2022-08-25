from argparse import ArgumentParser
from glob import glob
from pathlib import Path
from typing import Optional

from libs.subcleaner import config

parser = ArgumentParser(description="Remove ads from subtitle. Removed blocks are sent to logfile. "
                                    "Can also check that the subtitle language match the file name language code. ")

subtitles: list[Path]
parser.add_argument("subtitle", metavar="SUB", type=str, default=list(), nargs="*",
                    help="Path to subtitles to run script against. "
                         "Script currently only compatible with simple .srt files.")

language: Optional[str]
parser.add_argument("--language", "-l", metavar="LANG", type=str, dest="language", default=None,
                    help="2-letter ISO-639 language code. If this argument is set then the script will "
                         "check that the language of the content matches LANG and report results to log. "
                         "code may contain :forced or other \"LANG:<tag>\" but these tags will be ignored")

libraries: list[Path]
parser.add_argument("--library", "-r", metavar="LIB", type=str, dest="library", default=list(), nargs="*",
                    help="Run the script also on any subtitle found recursively under directory LIB. "
                         "If LANG is specified it will only run it on subtitles that have a "
                         "language label matching LANG.")

purge_list: list[int]
parser.add_argument("--destroy", "-d", type=int, nargs="+", default=None,
                    help="original_index of blocks to remove from SUB, this option is not compatible with the "
                         "library option. When this option is passed the script will mark the "
                         "specified blocks as ads and then run normally. "
                         "Example to destroy block 4 and 78: -d 4 78")

dry_run: bool
parser.add_argument("--dry-run", "-n", action="store_true", dest="dry_run",
                    help="Dry run: If flag is set then no files are modified.")

silent: bool
parser.add_argument("--silent", "-s", action="store_true", dest="silent",
                    help="Silent: If flag is set then script don't print to console.")

no_log: bool
parser.add_argument("--no-log", action="store_true", dest="no_log",
                    help="No log: If flag is set then nothing is logged.")

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

    library = library.resolve()
    for item in glob(str(library)):
        item = Path(item)
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

    file = file.resolve()
    for item in glob(str(file)):
        item = Path(item)
        if item.is_file() and item.name[-4:] == ".srt":
            subtitles.append(item)

language = None
if args.language:
    language = args.language.split(":")[0].replace("\"", "").replace("'", "").lower()
    if len(language) != 2:
        print("'" + args.language + "' does not contain a valid 2-letter ISO-639 language code.")
        print("--help for more information.")
        exit()

destroy_list = args.destroy
if destroy_list and len(subtitles) != 1 and len(libraries) != 0:
    print("option --destroy require one and only one specified subtitle file.")
    print("see --help for more info.")
    exit()

silent = args.silent
no_log = args.no_log
dry_run = args.dry_run
