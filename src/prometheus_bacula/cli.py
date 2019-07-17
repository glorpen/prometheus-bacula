import os
import argparse
import logging
import datetime
import prometheus_bacula.reader
import prometheus_bacula.collector
from http.server import HTTPServer
from prometheus_client import MetricsHandler

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', '-p', default=int(os.environ.get('METRICS_PORT', 8000)), type=int)
    p.add_argument('--min-interval', type=int, default=int(os.environ.get('MIN_INTERVAL', 5)), help='Minimum time to refresh metrics, in seconds')
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--debug', '-d', action='store_true')

    p.add_argument('--sql-host', action='store_true', default=os.environ.get('SQL_HOST', 'localhost'), help="Bacula SQL host to connect to")
    p.add_argument('--sql-user', action='store_true', default=os.environ.get('SQL_USER', 'bacula'), help="SQL user with read access to bacula DB")
    p.add_argument('--sql-db', action='store_true', default=os.environ.get('SQL_DB', 'bacula'), help="Bacula SQL database name")
    p.add_argument('--sql-password', action='store_true', default=os.environ.get('SQL_PASSWORD', 'bacula'), help="Password for SQL user")

    ns = p.parse_args()
    level = logging.ERROR
    if ns.verbose:
        level = logging.INFO
    if ns.debug:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    r = prometheus_bacula.reader.Reader(
        datetime.timedelta(seconds=ns.min_interval),
        sql_db=ns.sql_db,
        sql_host=ns.sql_host,
        sql_password=ns.sql_password,
        sql_user=ns.sql_user
    )
    
    c = prometheus_bacula.collector.MetricsContainer(r)
    c.update()
    h = HTTPServer(('', ns.port), MetricsHandler.factory(c.registry))
    h.serve_forever()
