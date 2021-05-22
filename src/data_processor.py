import io
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import psycopg2

from src import archive
from src.config import Config


def get_already_processed_files(config: Config) -> list[str]:
    """
    Get list of already processed archives
    :param config: Configuration object
    :return: List of already processed archives
    """
    already_processed_files = []
    if os.path.exists(config.already_processed):
        with open(config.already_processed, 'r') as f:
            already_processed_files = f.read().splitlines()

    return already_processed_files


def append_archive_to_already_processed_list(config: Config, file_name: str) -> None:
    """
    Append new entry to a file with list of already processed archives.
    :param config: Configuration object
    :param file_name: Names of archive to append
    """
    with open(config.already_processed, 'a') as f:
        f.write(f"{file_name}\n")


def process_file(config: Config, archive_file: Path) -> None:
    """
    Process archive file. Extract it and insert GamesDeals submissions into database.
    :param config:
    :param archive_file:
    :return:
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Processing file {archive_file.name} ")

    conn = psycopg2.connect(config.psql_conn_str)
    conn.autocommit = True

    game_deals_entries = 0

    with conn:
        proc = archive.decompress(archive_file)
        for line in io.TextIOWrapper(proc.stdout, encoding='utf-8'):
            if line:
                try:
                    submission = json.loads(line)
                    if submission.get('subreddit') == config.subreddit:
                        game_deals_entries += 1
                        with conn.cursor() as c:
                            c.execute('INSERT INTO submissions (created_utc, submission_id, title) VALUES (%s,%s,%s)',
                                      (datetime.utcfromtimestamp(int(submission.get('created_utc', 0))),
                                       submission['id'],
                                       submission['title']))
                except json.decoder.JSONDecodeError:
                    logger.exception(f'Could not process line: {line}')
                except Exception:
                    logger.exception(f'Unexpected error while processing line: {line}')

    conn.close()
    logger.info(f'{config.subreddit} submissions in {archive_file}: {game_deals_entries}')
