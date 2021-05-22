import subprocess
from pathlib import Path


def _get_output_file(filename: Path) -> str:
    return str(Path(filename.parent, filename.stem))


def _decompress_zst(filename: Path):
    return subprocess.Popen(['zstdcat', filename], stdout=subprocess.PIPE)


def _decompress_xz(filename: Path):
    return subprocess.Popen(['xzcat', filename], stdout=subprocess.PIPE)


def _decompress_bz2(filename: Path):
    return subprocess.Popen(['bzcat', filename], stdout=subprocess.PIPE)


def decompress(archive: Path):
    """
    Decompress provided archive file with a 3rd party software.
    :param archive: Path to archive file
    """
    decompressors = {
        '.xz': _decompress_xz,
        '.bz2': _decompress_bz2,
        '.zst': _decompress_zst
    }
    return decompressors[archive.suffix](archive)
