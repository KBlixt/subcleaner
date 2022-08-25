from pathlib import Path
import logging

from .subtitle import Subtitle, ParsingException
from libs.subcleaner.cleaner import Cleaner
import args
import config
import log_config

cleaner = Cleaner(config.home_dir.joinpath("regex"), config.use_default_regex)

logger = logging.getLogger(__name__)


def main():
    for file in args.subtitles:
        clean_file(file)

    for library in args.libraries:
        clean_directory(library)


def clean_file(subtitle_file: Path) -> None:
    logger.info(f"now working on subtitle: {subtitle_file}")

    try:
        subtitle = Subtitle(subtitle_file, args.language, args.destroy_list)
    except UnicodeDecodeError as e:
        logger.error(f"subcleaner was unable to decode the file. reason:")
        logger.error(e)
        return
    except ParsingException as e:
        logger.error(f"subcleaner was unable to decode the file! reason:")
        logger.error(e)
        return

    if not args.language:
        if config.default_language:
            subtitle.language = config.default_language
        else:
            subtitle.determine_language(True)

    cleaner.run_regex(subtitle)
    cleaner.find_ads(subtitle)
    cleaner.remove_ads(subtitle)
    if config.fix_overlaps:
        cleaner.fix_overlap(subtitle)

    if len(subtitle.blocks) == 0:
        logger.error("There might be an issue with the regex, "
                     "because everything in the subtitle would have gotten deleted."
                     "Nothing was altered.")
        return

    if args.dry_run:
        logger.warning("dry run: nothing was altered!")
        return

    with subtitle_file.open("w", encoding="UTF-8") as file:
        file.write(subtitle.to_content())


def clean_directory(directory: Path) -> None:
    for file in directory.iterdir():
        if file.is_dir() and not file.is_symlink():
            clean_directory(file)

        try:
            if not file.is_file():
                continue

            extensions = file.name.split(".")
            if extensions[-1] != "srt":
                continue

            if not args.language:
                clean_file(file)
                continue

            if args.language == extensions[-2][:2]:
                clean_file(file)

        except IndexError:
            continue


def generate_out(subtitle_file: Path, subtitle: Subtitle) -> str:
    report = "SUBTITLE: \"" + str(subtitle_file) + "\"\n"
    if args.dry_run:
        report += "    [INFO]: Nothing will be altered, (Dry-run).\n"

    if args.language is None:
        report += "    [INFO]: Didn't run language detection.\n"
    elif subtitle.language_is_correct():
        report += "    [INFO]: Subtitle language match file label. \n"
    else:
        report += "    [WARNING]: Subtitle language does not match file label.\n"

    if len(subtitle.ad_blocks) > 0:
        report += "    [INFO]: Removed " + str(len(subtitle.ad_blocks)) + " subtitle blocks:\n"
        report += "            [---------Removed Blocks----------]"
        for block in subtitle.ad_blocks:
            report += "\n            " + str(block.original_index) + "\n            "
            report += str(block).replace("\n", "\n            ")[:-12]
        report += "            [---------------------------------]\n"
    else:
        report += "    [INFO]: Removed 0 subtitle blocks.\n"

    if len(subtitle.warning_blocks) > 0:
        report += "    [WARNING]: Potential ads in " + \
                  str(len(subtitle.warning_blocks)) + " subtitle blocks, please verify:\n"
        report += "               [---------Warning Blocks----------]"
        d_command = "subcleaner '" + str(subtitle_file) + "' -d"
        for block in subtitle.warning_blocks:
            d_command += " " + str(block.original_index)
            report += "\n               " + str(block.original_index) + "\n               "
            report += str(block).replace("\n", "\n               ")[:-15]
        report += "               [---------------------------------]\n"
        report += "    [INFO] To remove all these blocks use: \n"
        report += d_command + " \n"

    report += "\n[---------------------------------------------------------------------------------]"
    return report
