import os
from dataclasses import dataclass


@dataclass
class Config:
    """
    App configuration
    """
    data_dir: os.PathLike
    psql_conn_str: str
    already_processed: os.PathLike
    subreddit: str
