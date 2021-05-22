# Pushshift downloader 

Python app to process reddit submission archives hosted on https://files.pushshift.io/reddit/submissions/


## What does this app do?

This app builds a database of submission titles and creation date of given subreddit.


## Prerequisites

- Postgres database
- zstd
- xz-utils
- bzip2

This project was created and tested on Python 3.9.5


## Installation

1. Clone this repo
2. Create python virtual environment 
3. Install required dependencies: `pip install -r requirements.txt`
4. Create postgres table (see [sql file](submissions.sql))


## Configuration

Rename `config.example.json` to `config.json`

```json
{
  "data_dir": "Path to directory into which archives should be downloaded and extracted",
  "already_processed": "Path to a file containing list of already processed archives.",
  "psql_conn_str": "postgres connection string https://www.postgresql.org/docs/current/libpq-connect.html",
  "subreddit": "Name of subreddit which submissions will be inserted into database"
}
```

See [example file](config.example.json).


## Running the app

Start the app via: `python -m src.main`
By default, app downloads archives starting with 2009-04 (r/GameDeals was created on that time).
The script accepts optional parameter with starting date in format YYYY-MM.
Example: `python -m src.main "2012-10"`


### Possible improvements

- Add multithreading. Keep downloading the files while processing 
- Dockerize the whole project. 
