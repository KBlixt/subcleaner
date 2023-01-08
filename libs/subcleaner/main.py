from pathlib import Path
import logging
from typing import List
from .subtitle import Subtitle, ParsingException, SubtitleContentException
from libs.subcleaner import cleaner, report_generator
from . import args
from . import config

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

files_handled: List[str] = []


def main():
    for file in args.subtitles:
        if file.suffix == ".srt":
            clean_file(file)

    for library in args.libraries:
        clean_directory(library)

    if files_handled == 0:
        logger.info(f"no srt files found.")

    logger.info(f"subcleaner finished successfully. {len(files_handled)} files cleaned.")


def clean_file(subtitle_file: Path) -> None:
    if subtitle_file.name in files_handled:
        return
    logger.info("[---------------------------------------------------------------------------------]")
    logger.info(f"now cleaning subtitle: {subtitle_file}")

    try:
        subtitle = Subtitle(subtitle_file)
    except (UnicodeDecodeError, ParsingException, SubtitleContentException) as e:
        logger.error(f"subcleaner was unable to decode the file. reason:")
        logger.error(e)
        return
    if len(subtitle.blocks) == 0:
        logger.warning("Subtitle file is empty.")
        return

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

    else:
        with subtitle_file.open("w", encoding="UTF-8") as file:
            file.write(subtitle.to_content())

    files_handled.append(subtitle_file.name)
    logger.info(f"Done. Cleaning report:\n{report_generator.generate_report(subtitle)}\n")
    if args.dry_run:
        logger.warning("dry run: nothing was altered.")


def clean_directory(directory: Path) -> None:
    for file in directory.iterdir():
        if file.is_dir() and not file.is_symlink():
            clean_directory(file)

        if not file.is_file() or file.suffix != ".srt":
            continue

        if not args.language:
            clean_file(file)
            continue

        if len(file.suffixes) >= 2 and args.language == file.suffixes[-2][1:3]:
            clean_file(file)
