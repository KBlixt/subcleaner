from glob import glob
from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser
from .cleaner import Cleaner
from .subtitle import Subtitle
from datetime import datetime


cleaner: Cleaner = Cleaner()
single_subtitle_file: Path
library_dir: Path
destroy_list: list
log_dir: Path
language: str
dry_run: bool
silent: bool
no_log: bool


def main(package_dir: Path):

    parse_config(package_dir)
    parse_args()

    if single_subtitle_file is not None:
        clean_file(single_subtitle_file)

    if destroy_list is not None:
        return

    if library_dir is not None:
        clean_directory(library_dir)


def clean_file(subtitle_file: Path) -> None:
    try:
        subtitle = Subtitle(subtitle_file, destroy_list)
    except UnicodeDecodeError as e:
        print("subcleaner was unable to decode file: \"" + str(subtitle_file) + "\n\" reason: \"" + e.reason + "\"")
        return

    cleaner.run_regex(subtitle)
    cleaner.find_ads(subtitle)
    cleaner.remove_ads(subtitle)
    cleaner.fix_overlap(subtitle)

    if not silent or not no_log:
        out = generate_out(subtitle_file, subtitle)
        if not silent:
            print(out)

        if not no_log and log_dir is not None:
            append_file(log_dir.joinpath("subcleaner.log"), generate_log(out))

    if not dry_run:
        write_file(subtitle_file, str(subtitle))


def clean_directory(directory: Path) -> None:
    for file in directory.iterdir():
        if file.is_dir() and not file.is_symlink():
            clean_directory(file)

        try:
            if file.is_file():
                extensions = file.name.split(".")
                if extensions[-1] != "srt":
                    continue
                if language is not None:
                    if extensions[-2] == language:
                        clean_file(file)
                        continue
                    if extensions[-3] == language:
                        clean_file(file)
                else:
                    clean_file(file)
        except IndexError:
            continue


def parse_args() -> None:
    parser = ArgumentParser(description="Remove ads from subtitle. Removed blocks are sent to logfile. "
                                        "Can also check so that the language match language-label. "
                                        "Edit the subcleaner.conf file to change regex filter and "
                                        "where to store log.")

    parser.add_argument("subtitle", metavar="SUB", type=Path, default=None, nargs="?",
                        help="Path to subtitle to run script against. "
                             "Script currently only compatible with simple .srt files.")

    parser.add_argument("--language", "-l", metavar="LANG", type=str, dest="language", default=None,
                        help="2-letter ISO-639 language code. If this argument is set then the script will "
                             "check that the language of the content matches LANG and report results to log. "
                             "code may contain :forced or other \"LANG:<tag>\" but these tags will be ignored")

    parser.add_argument("--library", "-r", metavar="LIB", type=Path, dest="library", default=None,
                        help="Run the script also on any subtitle found recursively under directory LIB. "
                             "If LANG is specified it will only run it on subtitles that have a "
                             "language label matching the LANG code.")

    parser.add_argument("--destroy", "-d", type=int, nargs="+", default=None,
                        help="index of blocks to remove from SUB, this option is not compatible with the "
                             "library option. When this option is passed the script will only remove the "
                             "specified blocks. The subtitle will be re-indexed after. "
                             "Example to destroy block 4 and 78: -d 4 78")

    parser.add_argument("--dry-run", "-n", action="store_true", dest="dry_run",
                        help="Dry run: If flag is set then no files are modified.")

    parser.add_argument("--silent", "-s", action="store_true", dest="silent",
                        help="Silent: If flag is set then script don't print to console.")

    parser.add_argument("--no-log", action="store_true", dest="no_log",
                        help="No log: If flag is set then nothing is logged.")

    args = parser.parse_args()

    # check usage:

    if args.subtitle is None and args.library is None:
        parser.print_help()
        exit()

    global library_dir
    library_dir = args.library
    if library_dir is not None:
        if not library_dir.is_absolute():
            library_dir = Path.cwd().joinpath(library_dir)
        glob_library_dir = glob(str(library_dir))
        if len(glob_library_dir) == 1:
            library_dir = Path(glob_library_dir[0])

        if not library_dir.is_dir():
            print("'" + str(args.library) + "' is not a path to a single directory.")
            print("--help for more information.")
            exit()

    global single_subtitle_file
    single_subtitle_file = args.subtitle
    if single_subtitle_file is not None:
        if not single_subtitle_file.is_absolute():
            single_subtitle_file = Path.cwd().joinpath(single_subtitle_file)
        glob_single_subtitle_file = glob(str(single_subtitle_file))
        if len(glob_single_subtitle_file) == 1:
            single_subtitle_file = Path(glob_single_subtitle_file[0])

        if not single_subtitle_file.is_file() or single_subtitle_file.name[-4:] != ".srt":
            print("'" + str(args.subtitle) + "' is not a path to a single srt file.")
            print("--help for more information.")
            exit()

    global language
    if args.language is not None:
        language = args.language.split(":")[0].replace("\"", "").lower()
        if len(language) != 2:
            print("'" + args.language + "' does not contain a valid 2-letter ISO-639 language code.")
            print("--help for more information.")
            exit()
    else:
        language = None

    global silent
    silent = args.silent
    global no_log
    no_log = args.no_log
    global dry_run
    dry_run = args.dry_run
    global destroy_list
    destroy_list = args.destroy
    if destroy_list is not None and single_subtitle_file is None:
        print("option --destroy require a subtitle file to be specified.")
        print("see --help for more info.")
        exit()


def parse_config(package_dir: Path) -> None:
    config_file: Path = package_dir.joinpath("subcleaner.conf")

    if not config_file.is_file():
        config_file.write_text(package_dir.joinpath("default-config", "subcleaner.conf").read_text())

    cfg = ConfigParser()
    cfg.read(str(config_file))
    sections = cfg.sections()

    if "REGEX" in sections and "PURGE_REGEX" not in sections:
        # for backwards-compatibility:
        for regex in list(cfg.items("REGEX")):
            if len(regex[1]) != 0:
                cleaner.purge_regex_list.append(regex[1])
        print("Config file is out of date. Converting the config file to follow latest config-layout will enable "
              "more granular ad-detection and warnings.")
    else:
        for regex in list(cfg.items("PURGE_REGEX")):
            if len(regex[1]) != 0:
                cleaner.purge_regex_list.append(regex[1])

        for regex in list(cfg.items("WARNING_REGEX")):
            if len(regex[1]) != 0:
                cleaner.warning_regex_list.append(regex[1])

    global log_dir
    try:
        log_dir = Path(cfg["SETTINGS"].get("log_dir", "log"))
    except KeyError:
        log_dir = Path("log")
    if not log_dir.is_absolute():
        log_dir = package_dir.joinpath(log_dir)

    try:
        log_dir.mkdir()
    except FileExistsError:
        if log_dir.is_file():
            print("WARN: configured log directory is a file. Logging disabled.")
            log_dir = None


def write_file(file_path: Path, content: str) -> None:
    with file_path.open("w") as file:
        file.write(content)


def append_file(file_path: Path, content: str) -> None:
    with file_path.open("a") as file:
        file.write(content)


def generate_log(out_string: str) -> str:
    return "\n".join(str(datetime.now())[:19] + ": " + line for line in out_string.split("\n")) + "\n"


def generate_out(subtitle_file: Path, subtitle: Subtitle) -> str:
    report = "SUBTITLE: \"" + str(subtitle_file) + "\"\n"
    if dry_run:
        report += "    [INFO]: Nothing will be altered, (Dry-run).\n"

    if language is None:
        report += "    [INFO]: Didn't run language detection.\n"
    elif subtitle.check_language(language):
        report += "    [INFO]: Subtitle language match file label. \n"
    else:
        report += "    [WARNING]: Subtitle language does not match file label.\n"

    if len(subtitle.ad_blocks) > 0:
        report += "    [INFO]: Removed " + str(len(subtitle.ad_blocks)) + " subtitle blocks:\n"
        report += "            [---------Removed Blocks----------]"
        for block in subtitle.ad_blocks:
            report += "\n            " + str(block.index) + "\n            "
            report += str(block).replace("\n", "\n            ")[:-12]
        report += "            [---------------------------------]\n"
    else:
        report += "    [INFO]: Removed 0 subtitle blocks.\n"

    if len(subtitle.warning_blocks) > 0:
        report += "    [WARNING]: Potential ads in " + str(len(subtitle.warning_blocks)) + " subtitle blocks, please verify:\n"
        report += "               [---------Warning Blocks----------]"
        for block in subtitle.warning_blocks:
            report += "\n               " + str(block.index) + "\n               "
            report += str(block).replace("\n", "\n               ")[:-15]
        report += "               [---------------------------------]\n"
        report += "               To remove blocks use: subcleaner -d\n"
    report += "[---------------------------------------------------------------------------------]"
    return report
