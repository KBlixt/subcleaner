from glob import glob
from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser
from .cleaner import Cleaner
from .subtitle import Subtitle
from datetime import datetime

cleaner: Cleaner
relative_base: Path
package_dir: Path
subtitles: list
libraries: list
destroy_list: list
log_dir: Path
language: str
default_language: str
dry_run: bool
silent: bool
no_log: bool
regex_defaults: bool
fix_overlaps: bool


def main(package_dir_from: Path):
    global package_dir
    package_dir = package_dir_from

    parse_config()
    parse_args()

    if len(subtitles) != 0:
        for file in subtitles:
            clean_file(file)

    if destroy_list is not None:
        return

    if len(libraries) != 0:
        for library in libraries:
            clean_directory(library)


def clean_file(subtitle_file: Path) -> None:

    try:
        subtitle = Subtitle(subtitle_file, language, destroy_list)
    except UnicodeDecodeError as e:
        print("subcleaner was unable to decode file: \"" + str(subtitle_file) + "\n\" reason: \"" + e.reason + "\"")
        return

    if not language:
        if default_language:
            subtitle.language = default_language
        else:
            subtitle.determine_language()

    cleaner.run_regex(subtitle)
    cleaner.find_ads(subtitle)
    cleaner.remove_ads(subtitle)
    if fix_overlaps:
        cleaner.fix_overlap(subtitle)

    if len(subtitle.blocks) == 0:
        print("Exiting, There might be an issue with the regex, "
              "because everything in the subtitle would have gotten deleted."
              "Nothing was changed.")
        exit()

    if not (silent and no_log):
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
                                        "Can also check that the subtitle language match the file name language code. "
                                        "Edit the subcleaner.conf file to change regex filter and "
                                        "where to store log.")

    parser.add_argument("subtitle", metavar="SUB", type=str, default=list(), nargs="*",
                        help="Path to subtitles to run script against. "
                             "Script currently only compatible with simple .srt files.")

    parser.add_argument("--language", "-l", metavar="LANG", type=str, dest="language", default=None,
                        help="2-letter ISO-639 language code. If this argument is set then the script will "
                             "check that the language of the content matches LANG and report results to log. "
                             "code may contain :forced or other \"LANG:<tag>\" but these tags will be ignored")

    parser.add_argument("--library", "-r", metavar="LIB", type=str, dest="library", default=list(), nargs="*",
                        help="Run the script also on any subtitle found recursively under directory LIB. "
                             "If LANG is specified it will only run it on subtitles that have a "
                             "language label matching LANG.")

    parser.add_argument("--destroy", "-d", type=int, nargs="+", default=None,
                        help="index of blocks to remove from SUB, this option is not compatible with the "
                             "library option. When this option is passed the script will mark the "
                             "specified blocks as ads and then run normally. "
                             "Example to destroy block 4 and 78: -d 4 78")

    parser.add_argument("--dry-run", "-n", action="store_true", dest="dry_run",
                        help="Dry run: If flag is set then no files are modified.")

    parser.add_argument("--silent", "-s", action="store_true", dest="silent",
                        help="Silent: If flag is set then script don't print to console.")

    parser.add_argument("--no-log", action="store_true", dest="no_log",
                        help="No log: If flag is set then nothing is logged.")

    args = parser.parse_args()

    # check usage:

    if len(args.subtitle) == 0 and len(args.library) == 0:
        parser.print_help()
        exit()

    global libraries
    libraries = list()
    for library_str in args.library:
        library: Path = Path(library_str)
        if not library.is_absolute():
            if library_str[0] == ".":
                library = Path.cwd().joinpath("/".join(library.parts))
            else:
                library = relative_base.joinpath(library)

        if not library.is_dir():
            for item in glob(str(library)):
                item = Path(item)
                if item.is_dir():
                    libraries.append(item)
            continue
        libraries.append(library)

    global subtitles
    subtitles = list()

    for file_str in args.subtitle:
        file: Path = Path(file_str)
        if not file.is_absolute():
            if file_str[0] == ".":
                file = Path.cwd().joinpath("/".join(file.parts))
            else:
                file = relative_base.joinpath(file)

        if not (file.is_file() and file.name[-4:] == ".srt"):
            for item in glob(str(file)):
                item = Path(item)
                if item.is_file() and item.name[-4:] == ".srt":
                    subtitles.append(item)
            continue
        subtitles.append(file)

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
    if destroy_list is not None and len(subtitles) != 1:
        print("option --destroy require one and only one specified subtitle file.")
        print("see --help for more info.")
        exit()


def parse_config() -> None:
    config_file: Path = package_dir.joinpath("subcleaner.conf")

    if not config_file.is_file():
        config_file.write_text(package_dir.joinpath("default_config", "subcleaner.conf").read_text())

    cfg = ConfigParser()
    cfg.read(str(config_file), encoding="UTF-8")

    global regex_defaults
    regex_defaults = cfg['SETTINGS'].getboolean("use_defaults", True)

    global cleaner
    cleaner = Cleaner(package_dir.joinpath("regex"), regex_defaults)

    sections = cfg.sections()

    if "REGEX" in sections and "PURGE_REGEX" not in sections:
        # for backwards-compatibility:
        cfg.add_section("PURGE_REGEX")
        for key, value in cfg.items("REGEX"):
            cfg.set("PURGE_REGEX", key, value)
        cfg.remove_section("REGEX")

    if cfg.has_section("PURGE_REGEX") or cfg.has_section("WARNING_REGEX"):
        print("Config file is out of date. Converting the config file to follow latest config-layout will enable "
              "more granular ad-detection and warnings.")
        cleaner.exclusive_configs.append(cfg)

    global log_dir
    log_dir = Path(cfg["SETTINGS"].get("log_dir", "log/"))
    if not log_dir.is_absolute():
        log_dir = package_dir.joinpath(log_dir)
    try:
        log_dir.mkdir()
    except FileExistsError:
        if log_dir.is_file():
            print("WARN: configured log directory is a file. Logging disabled.")
            log_dir = None
            global no_log
            no_log = True

    global relative_base
    temp: str = cfg['SETTINGS'].get("relative_path_base", "")
    if temp == "" or temp == ".":
        relative_base = Path.cwd()
    else:
        relative_base = Path(temp)

    global fix_overlaps
    fix_overlaps = cfg['SETTINGS'].getboolean("fix_overlaps", True)

    global default_language
    default_language = cfg['SETTINGS'].get("default_language", "")
    if any(default_language == test for test in ["blank", "Blank", ""]):
        default_language = None


def write_file(file_path: Path, content: str) -> None:
    with file_path.open("w", encoding="UTF-8") as file:
        file.write(content)


def append_file(file_path: Path, content: str) -> None:
    with file_path.open("a", encoding="UTF-8") as file:
        file.write(content)


def generate_log(out_string: str) -> str:
    return "\n".join(str(datetime.now())[:19] + ": " + line for line in out_string.split("\n")) + "\n"


def generate_out(subtitle_file: Path, subtitle: Subtitle) -> str:
    report = "SUBTITLE: \"" + str(subtitle_file) + "\"\n"
    if dry_run:
        report += "    [INFO]: Nothing will be altered, (Dry-run).\n"

    if language is None:
        report += "    [INFO]: Didn't run language detection.\n"
    elif subtitle.check_language():
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
        report += "    [WARNING]: Potential ads in " + \
                  str(len(subtitle.warning_blocks)) + " subtitle blocks, please verify:\n"
        report += "               [---------Warning Blocks----------]"
        for block in subtitle.warning_blocks:
            report += "\n               " + str(block.index) + "\n               "
            report += str(block).replace("\n", "\n               ")[:-15]
        report += "               [---------------------------------]\n"
        report += "               To remove blocks use: subcleaner -d\n"
    report += "[---------------------------------------------------------------------------------]"
    return report
