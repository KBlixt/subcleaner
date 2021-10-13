from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser
from .cleaner import clean
from .subtitle import Subtitle
from .sub_block import SubBlock
from langdetect import detect
from datetime import datetime
from .directives import Directives


def main(package_dir: Path):
    deleted_blocks: list[SubBlock]
    subtitle: Subtitle

    directives = Directives()
    config_file: Path = package_dir.joinpath("../settings.config")
    if not config_file.is_file():
        config_file.write_text(package_dir.joinpath("example-settings.config").read_text())

    parse_args(directives)
    parse_config(config_file, directives, package_dir)

    subtitle_content: str = read_file(directives.subtitle_file)

    subtitle = Subtitle(subtitle_content)
    deleted_blocks = clean(subtitle, directives.regex_list)
    detected_language: str = detect(subtitle_content)

    if not directives.dry_run:
        write_file(directives.subtitle_file, str(subtitle))

    out_string = generate_out(deleted_blocks, directives, detected_language)
    if not directives.no_log and directives.log_dir is not None:
        append_file(directives.log_dir.joinpath("subcleaner.log"), generate_log(out_string))

    if not directives.silent:
        print(out_string)


def parse_args(directives: Directives) -> None:
    parser = ArgumentParser(description="Remove ads from subtitle. Removed blocks are sent to logfile. "
                                        "Can also check so that the language match language-label. "
                                        "Edit the settings.config file to change regex filter and "
                                        "where to store log.")

    parser.add_argument("subtitle", metavar="SUB", type=Path, default=None,
                        help="Path to subtitle to run script against. "
                             "Script currently only compatible with simple .srt files.")

    parser.add_argument("--language", "-l", metavar="LANG", type=str, dest="language", default=None,
                        help="Listed language code of the subtitle. if this argument is set then the script will "
                             "check that the language of the content matches LANG. If they don't match an empty "
                             "file called \"[SUB].lang-warn\" will be created alongside the subtitle file. "
                             "Language code according to 2-letter ISO-639, "
                             "[LANG] may contain :forced or other \":<tag>\"")

    parser.add_argument("--dry-run", "-n", action="store_true", dest="dry_run",
                        help="Dry run: If flag is set then nothing is printed and nothing is logged.")

    parser.add_argument("--silent", "-s", action="store_true", dest="silent",
                        help="Silent: If flag is set then script don't print to console.")

    parser.add_argument("--no-log", action="store_true", dest="no_log",
                        help="No log: If flag is set then nothing is logged.")

    args = parser.parse_args()

    # check usage:

    subtitle_file: Path = args.subtitle
    if subtitle_file is None:
        parser.print_help()
        exit()

    if not subtitle_file.is_absolute():
        subtitle_file = Path.cwd().joinpath(subtitle_file)

    if not subtitle_file.is_file() or subtitle_file.name[-4:] != ".srt":
        print("make sure that the subtitle-file is a srt-file")
        print("--help for more information.")
        exit()
    directives.subtitle_file = subtitle_file

    language: str = args.language
    if language is not None:
        if len(language.split(":")[0]) != 2:
            print("Use 2-letter ISO-639 standard language code.")
            print("--help for more information.")
            exit()
        directives.language = language.split(":")[0].lower()

    directives.silent = args.silent
    directives.no_log = args.no_log
    directives.dry_run = args.dry_run


def parse_config(config_file: Path, directives: Directives, package_dir: Path) -> None:
    cfg = ConfigParser()
    cfg.read(str(config_file))
    for regex in list(cfg.items("REGEX")):
        if len(regex[1]) != 0:
            directives.regex_list.append(regex[1])

    directives.log_dir = Path(cfg["SETTINGS"].get("log_dir", "log"))
    if not directives.log_dir.is_absolute():
        directives.log_dir = package_dir.joinpath(directives.log_dir)

    try:
        directives.log_dir.mkdir()
    except FileExistsError:
        if directives.log_dir.is_file():
            print("WARN: configured log directory is a file. Logging disabled.")
            directives.log_dir = None


def read_file(file_path: Path) -> str:
    try:
        with file_path.open("r") as file:
            return file.read()
    except UnicodeDecodeError:
        print("UnicodeDecodeError, unable to read file")
        exit()


def write_file(file_path: Path, content: str) -> None:
    with file_path.open("w") as file:
        file.write(content)


def append_file(file_path: Path, content: str) -> None:
    with file_path.open("a") as file:
        file.write(content)


def generate_log(out_string: str) -> str:
    return "\n".join(str(datetime.now())[:19] + ": " + line for line in out_string.split("\n")) + "\n"


def generate_out(deleted_blocks: list[SubBlock], directives, detected_language) -> str:
    report = "SUBTITLE: \"" + str(directives.subtitle_file) + "\"\n"
    if directives.dry_run:
        report += "\t[INFO]: Nothing will be altered, (Dry-run).\n"
    if directives.language is None or detected_language is None:
        report += "\t[INFO]: Didn't run language detection.\n"
    elif directives.language == detected_language:
        report += "\t[INFO]: Subtitle language match file label. \n"
    else:
        report += "\t[WARNING]: Detected language: \"" + detected_language + "\" does not match file label.\n"

    if len(deleted_blocks) > 0:
        report += "\t[INFO]: Removed " + str(len(deleted_blocks)) + " subtitle blocks:\n"
        report += "\t\t\t[---------Removed Blocks----------]"
        for block in deleted_blocks:
            report += "\n\t\t\t" + str(block.orig_index) + "\n\t\t\t"
            report += str(block).replace("\n", "\n\t\t\t")[:-3]
        report += "\t\t\t[---------------------------------]\n"
    else:
        report += "\t[INFO]: Removed " + str(len(deleted_blocks)) + " subtitle blocks.\n"

    report += "[---------------------------------------------------------------------------------]"
    return report


def report_unicode_error(directives) -> str:
    report = "SUBTITLE: \"" + str(directives.subtitle_file) + "\"\n"
    report += "\t[WARNING]: Unable to decode subtitle.\n"
    report += "[---------------------------------------------------------------------------------]"
    return report


if __name__ == '__main__':
    try:
        print("main")
    except KeyboardInterrupt:
        print("Interrupted")
        exit()
    except UnicodeDecodeError:
        print("Unable to read file, Unicode decode error")
        exit()
