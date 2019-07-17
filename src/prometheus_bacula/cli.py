import argparse
import logging
import datetime
import prometheus_bacula.reader
import prometheus_bacula.collector
from http.server import HTTPServer
from prometheus_client import MetricsHandler

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', '-p', default=8000, type=int)
    p.add_argument('--min-interval', type=int, default=5, help='Minimum time to refresh metrics')
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--debug', '-d', action='store_true')

    p.add_argument('--sql-host', action='store_true', default='localhost')
    p.add_argument('--sql-user', action='store_true', default='bacula')
    p.add_argument('--sql-db', action='store_true', default='bacula')
    p.add_argument('--sql-password', action='store_true', default='bacula')

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
