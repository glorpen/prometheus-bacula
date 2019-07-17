=========================
Bacula Prometheus Metrics
=========================

-----
Usage
-----

.. sourcecode:: shell

    # docker run --rm -it glorpen/prometheus-bacula --help

    usage: prometheus-bacula [-h] [--port PORT] [--min-interval MIN_INTERVAL]
                            [--verbose] [--debug] [--sql-host] [--sql-user]
                            [--sql-db] [--sql-password]

    optional arguments:
    -h, --help            show this help message and exit
    --port PORT, -p PORT
    --min-interval MIN_INTERVAL
                            Minimum time to refresh metrics, in seconds
    --verbose, -v
    --debug, -d
    --sql-host            Bacula SQL host to connect to
    --sql-user            SQL user with read access to bacula DB
    --sql-db              Bacula SQL database name
    --sql-password        Password for SQL user

App defaults:

- ``port``: 8000
- ``min-interval``: 5
- ``sql-host``: localhost
- ``sql-user``: bacula
- ``sql-db``: bacula
- ``sql-password``: bacula

---------------------
Environment variables
---------------------

Each env variable has corresponding console option.

- METRICS_PORT
- MIN_INTERVAL
- SQL_HOST
- SQL_USER
- SQL_DB
- SQL_PASSWORD

-------
Metrics
-------

- bacula_finished_job_start_seconds
- bacula_finished_job_end_seconds
- bacula_finished_job_files_count
- bacula_finished_job_size_bytes
- bacula_finished_job_status
- bacula_finished_job_level
- bacula_finished_job_id
- bacula_job_bytes_total
