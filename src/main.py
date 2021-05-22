import json
import logging
import logging.config
import sys
from pathlib import Path

from src import data_processor
from src import pushshift
from src.config import Config


def main(cfg: Config, since: str = '2009-04'):
    """
    Runs the workflow
    :param cfg: Configuration object
    :param since: Date in format: YYYY-MM. Defaults to 2009-04 (r/GameDeals was created on that date)
    """
    logger = logging.getLogger(__name__)

    files = pushshift.get_files_to_dl(since)
    sha_sums = pushshift.get_sha_sums()

    already_processed_files = data_processor.get_already_processed_files(cfg)

    for file_name in files:
        if file_name in already_processed_files:
            logger.info(f'{file_name} already processed. Skipping')
            continue

        logger.info(f"Processing file: {file_name}")

        archive_file = Path(cfg.data_dir, file_name)
        pushshift.download_file(file_name, cfg.data_dir)
        logger.info(f'Downloaded {file_name}')

        if pushshift.does_sha_match(archive_file, sha_sums):
            data_processor.process_file(config, archive_file)
            data_processor.append_archive_to_already_processed_list(config, file_name)
        else:
            logger.error(f"SHA Sums don't match. File: {file_name}")

        if archive_file.exists():
            archive_file.unlink()


if __name__ == '__main__':
    with open('logging.json') as f:
        config = json.load(f)
    logging.config.dictConfig(config)

    with open('config.json') as f:
        config = json.load(f, object_hook=lambda d: Config(**d))

    main(config, *sys.argv[1:])
