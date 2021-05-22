import collections
import hashlib
import itertools
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def _get_available_files():
    """
    Fetch files available to download.
    :return: Dictionary. Key is file extension, value is list of files with given extension.
    """
    r = requests.get('https://files.pushshift.io/reddit/submissions/')
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr', class_='file')

    files = collections.defaultdict(list)
    for row in rows:
        file = row.find('td').find('a').text
        name, extension = file.split('.')
        files[extension].append(name)

    return files


def get_files_to_dl(since=None):
    """
    Fetch list of files to download. Files are ordered in chronological order
    :param since: Date in format YYYY-MM
    :return: List of files to download
    """
    available_files = _get_available_files()

    bz2_to_dl = map(lambda f: f"{f}.bz2", [x for x in available_files['bz2'] if x not in available_files['xz']])
    xz_to_dl = map(lambda f: f"{f}.xz", available_files['xz'])
    zst_to_dl = map(lambda f: f"{f}.zst", available_files['zst'])

    files = list(itertools.chain(bz2_to_dl, xz_to_dl, zst_to_dl))
    files.sort(key=lambda x: x.split('.')[0].split('_')[-1])  # sort by date

    if since:
        first_matching = next(filter(lambda x: x.split('.')[0].split('_')[-1] == since, files))
        starting_index = files.index(first_matching)
        return files[starting_index:]
    return files


def get_sha_sums() -> dict[str, str]:
    """
    Download shasums of all reddit submissions files.
    :return: Directory, key is filename, value is expected shasum
    """
    r = requests.get('https://files.pushshift.io/reddit/submissions/sha256sums.txt')
    sha_sums = {}
    for line in r.text.splitlines():
        if line:
            sha_sum, file = line.split('  ')
            sha_sums[file] = sha_sum
    return sha_sums


def download_file(file_name: str, output_dir: os.PathLike) -> None:
    """
    Download file with given name for pushshift.
    :param file_name: Name of the file on pusshift
    :param output_dir: Output directory where archive should be saved
    :return:
    """
    with requests.get(f'https://files.pushshift.io/reddit/submissions/{file_name}', stream=True) as r:
        r.raise_for_status()
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        chunk_size = 8192
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(Path(output_dir, file_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                progress_bar.update(len(chunk))
                f.write(chunk)
    progress_bar.close()


def does_sha_match(file: Path, sha_sums: dict[str, str]) -> bool:
    """
    Checks if shasum of downloaded file matches with the sum provided by pushshift
    :param file: Path to archive file
    :param sha_sums: Directory with sha sums from pusshift
    :return: True is sum matches, otherwise False
    """
    sha256_hash = hashlib.sha256()
    with open(file, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha_sums[file.name] == sha256_hash.hexdigest()
