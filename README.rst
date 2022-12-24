===========
trakt-tools
===========
.. image:: https://img.shields.io/travis/fuzeman/trakt-tools.svg?maxAge=2592000?style=flat-square
    :target: https://travis-ci.org/fuzeman/trakt-tools
.. image:: https://img.shields.io/github/release/fuzeman/trakt-tools.svg?maxAge=2592000?style=flat-square
    :target: https://github.com/fuzeman/trakt-tools/releases/latest
.. image:: https://img.shields.io/pypi/v/trakt-tools.svg?maxAge=2592000?style=flat-square
    :target: https://pypi.python.org/pypi/trakt-tools

Command-line tools for Trakt.tv.

**I've done my best to ensure there isn't any critical bugs in this application, but please ensure your Trakt.tv profile has been backed up before running any operations with this application.**

**If you are concerned about data-loss:** I would suggest reviewing the created backups yourself, they are simple JSON files that can be opened in any text editor. Backup files are structured exactly how they are returned from the Trakt.tv API.

**Note:** Only history from a backup can be applied to your profile currently. Support for applying collection, playback, ratings, and watchlist data from a backup has not been implemented yet.

-------
Install
-------

.. code-block::

    pip install trakt-tools

-----
Usage
-----

From a command-line, either run:

.. code-block::

    trakt_tools [COMMAND] [ARGS]

or:

.. code-block::

    python -m trakt_tools.runner.main [COMMAND] [ARGS]

''''''''
Commands
''''''''

.. code-block::

    Usage: trakt_tools [OPTIONS] COMMAND [ARGS]...

    Options:
      --debug / --no-debug  Display debug messages.
      --rate-limit INTEGER  Maximum number of requests per minute. (default: 20)
      --help                Show this message and exit.

    Commands:
      history:duplicates:merge  Merge duplicate history records
      history:duplicates:scan   Scan for duplicate history records
      profile:backup:apply      Apply backup to a Trakt.tv profile (history)
      profile:backup:create     Create backup of a Trakt.tv profile.

````````````````````````````````
:code:`history:duplicates:merge`
````````````````````````````````

.. code-block::

    Usage: trakt_tools history:duplicates:merge [OPTIONS]

      Merge duplicate history records

    Options:
      --token TEXT            Trakt.tv authentication token. (default: "TRAKT_TOKEN" or Prompt)
      --backup-dir TEXT       Directory that backups should be stored in. (default: "./backups")
      --delta-max INTEGER     Maximum delta between history records to consider as duplicate. (in seconds) (default: 600)
      --per-page INTEGER      Request page size. (default: 1000)
      --backup / --no-backup  Backup profile before applying any changes. (default: prompt)
      --review / --no-review  Review each action before applying them. (default: prompt)
      --help                  Show this message and exit.

```````````````````````````````
:code:`history:duplicates:scan`
```````````````````````````````

.. code-block::

    Usage: trakt_tools history:duplicates:scan [OPTIONS]

      Scan for duplicate history records

    Options:
      --token TEXT         Trakt.tv authentication token. (default: "TRAKT_TOKEN" or Prompt)
      --delta-max INTEGER  Maximum delta between history records to consider as duplicate. (in seconds) (default: 600)
      --per-page INTEGER   Request page size. (default: 1000)
      --help               Show this message and exit.

````````````````````````````````````````````
:code:`profile:backup:apply`
````````````````````````````````````````````

.. code-block::

    Usage: trakt_tools profile:backup:apply [OPTIONS] BACKUP_ZIP

      Apply backup to a Trakt.tv profile.

      Only history can be applied to your profile currently. Support for applying collection,
      playback, ratings, and watchlist data has not been implemented yet.

      Note: History already on your profile will be duplicated, `history:duplicates:merge` can be run
      afterwards to merge any duplicates in your history.

      BACKUP_ZIP is the location of the zip file created by the profile:history:backup command

    Options:
      --token TEXT  Trakt.tv authentication token. (default: "TRAKT_TOKEN" or Prompt)
      --help        Show this message and exit.

`````````````````````````````
:code:`profile:backup:create`
`````````````````````````````

.. code-block::

    Usage: trakt_tools profile:backup:create [OPTIONS]

      Create backup of a Trakt.tv profile.

    Options:
      -y, --yes           Automatic yes to confirmation prompts.
      --token TEXT        Trakt.tv authentication token. (default: "TRAKT_TOKEN" or Prompt)
      --backup-dir TEXT   Directory that backups should be stored in. (default: "./backups")
      --per-page INTEGER  Request page size. (default: 1000)
      --help              Show this message and exit.


--------
Examples
--------

**Delete duplicate history record(s):**

.. code-block::

    $ trakt_tools history:duplicates:merge
    Navigate to https://trakt.tv/pin/10248
    Pin: <Type PIN, ENTER>

    Requesting profile...
    Logged in as u'fuzeman'

    Would you like to continue? [yes]: <ENTER>

    Create profile backup? [yes]: <ENTER>

    Collection
     - Received 248 movie(s)
     - Writing to "collection\movies.json"...
     - Received 377 show(s)
     - Writing to "collection\shows.json"...

    History
     - Received 1000 item(s) (page 1 of 16)
     - Received 1000 item(s) (page 2 of 16)
     - Received 1000 item(s) (page 3 of 16)
     - Received 1000 item(s) (page 4 of 16)
     - Received 1000 item(s) (page 5 of 16)
     - Received 1000 item(s) (page 6 of 16)
     - Received 1000 item(s) (page 7 of 16)
     - Received 1000 item(s) (page 8 of 16)
     - Received 1000 item(s) (page 9 of 16)
     - Received 1000 item(s) (page 10 of 16)
     - Received 1000 item(s) (page 11 of 16)
     - Received 1000 item(s) (page 12 of 16)
     - Received 1000 item(s) (page 13 of 16)
     - Received 1000 item(s) (page 14 of 16)
     - Received 1000 item(s) (page 15 of 16)
     - Received 665 item(s) (page 16 of 16)
     - Writing to "history.json"...

    Playback Progress
     - Received 92 item(s)
     - Writing to "playback.json"...

    Ratings
     - Received 352 item(s)
     - Writing to "ratings.json"...

    Watchlist
     - Received 161 item(s)
     - Writing to "watchlist.json"...

    Compressing backup...
    Cleaning up...
    Backup has been saved to: ".\backups\fuzeman\2016-09-15_05-16-27.639000.zip"

    Scanning for duplicates...
     - Processing 1000 items... (page 1 of 16)
     - Processing 1000 items... (page 2 of 16)
     - Processing 1000 items... (page 3 of 16)
     - Processing 1000 items... (page 4 of 16)
     - Processing 1000 items... (page 5 of 16)
     - Processing 1000 items... (page 6 of 16)
     - Processing 1000 items... (page 7 of 16)
     - Processing 1000 items... (page 8 of 16)
     - Processing 1000 items... (page 9 of 16)
     - Processing 1000 items... (page 10 of 16)
     - Processing 1000 items... (page 11 of 16)
     - Processing 1000 items... (page 12 of 16)
     - Processing 1000 items... (page 13 of 16)
     - Processing 1000 items... (page 14 of 16)
     - Processing 1000 items... (page 15 of 16)
     - Processing 665 items... (page 16 of 16)

    Found 2 show(s) and 2 movie(s) with duplicates

    Review every action? [yes]: <ENTER>

    "Breaking Bad" (2008)
            S01E01 - 4 plays -> 3 plays
                    Jan 21, 2008 03:00 PM NZDT (2008-01-21T02:00:00+00:00)
                    Sep 26, 2011 10:18 PM NZDT (2011-09-26T09:18:20+00:00)
                    Oct 06, 2013 04:47 PM NZDT (2013-10-06T03:47:08+00:00)

    Remove 1 duplicate history record(s) for "Breaking Bad" (2008)? [yes]: <ENTER>
    Removed 1 episode record(s) from history

    ----------------------------------------------------------------------

    "Orphan Black" (2013)
            S01E01 - 3 plays -> 2 plays
                    Mar 31, 2013 03:00 PM NZDT (2013-03-31T02:00:00+00:00)
                    Apr 08, 2013 01:23 AM NZST (2013-04-07T13:23:52+00:00)

    Remove 1 duplicate history record(s) for "Orphan Black" (2013)? [yes]: <ENTER>
    Removed 1 episode record(s) from history

    ----------------------------------------------------------------------

    "Inception" (2010) - 4 plays -> 3 plays
            Sep 14, 2016 10:15 PM NZST (2016-09-14T10:15:00+00:00)
            Jul 16, 2010 10:00 PM NZST (2010-07-16T10:00:00+00:00)
            Oct 26, 2011 07:07 PM NZDT (2011-10-26T06:07:25+00:00)

    Remove 1 duplicate history record(s) for "Inception" (2010)? [yes]: <ENTER>
    Removed 1 movie record(s) from history

    ----------------------------------------------------------------------

    "The Matrix" (1999) - 3 plays -> 2 plays
            Mar 30, 1999 10:00 PM NZST (1999-03-30T10:00:00+00:00)
            Aug 20, 2011 12:04 PM NZST (2011-08-20T00:04:30+00:00)

    Remove 1 duplicate history record(s) for "The Matrix" (1999)? [yes]: <ENTER>
    Removed 1 movie record(s) from history

    ----------------------------------------------------------------------

    Done
