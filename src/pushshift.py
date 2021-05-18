import collections
import itertools

import requests
from bs4 import BeautifulSoup


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
