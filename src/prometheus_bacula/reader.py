import pymysql.cursors
import contextlib
import datetime
import logging

def timestamp_or_none(v):
    return v.timestamp() if v else None

class Reader(object):

    _connection = None
    _last_connection_ping = None

    level_map = {
        'I': { 'id': 1, 'name': 'Incremental'},
        'F': { 'id': 2, 'name': 'Full'},
        '':  { 'id': 0, 'name': 'None'}
    }

    def __init__(
        self, min_con_check_interval=None,
        sql_host='localhost', sql_user='bacula', sql_db='bacula',
        sql_password='bacula'
    ):
        super(Reader, self).__init__()

        self.logger = logging.getLogger(self.__class__.__name__)

        self._status_map = {}
        self._min_connection_check_interval = datetime.timedelta(seconds=5) if min_con_check_interval is None else min_con_check_interval

        self._sql_credentials = {
            'host': sql_host,
            'user': sql_user,
            'password': sql_password,
            'db': sql_db
        }

    @property
    def connection(self):
        if self._connection:
            
            if datetime.datetime.now() - self._last_connection_ping > self._min_connection_check_interval:
                self.logger.debug("Pinging SQL")
                self._connection.ping(reconnect=True)
                self._last_connection_ping = datetime.datetime.now()

            return self._connection
        
        self._connection = pymysql.connect(
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            **self._sql_credentials
        )

        self._last_connection_ping = datetime.datetime.now()
        
        return self._connection

    @property
    def status_map(self):
        if self._status_map:
            return self._status_map
        
        with self.connection.cursor() as cursor:
            cursor.execute('select JobStatus, JobStatusLong from Status')
            results = cursor.fetchall()
        
        out = {}
        for i, o in enumerate(results):
            out[o['JobStatus']] = {
                'id': i,
                'name': o['JobStatusLong'].decode()
            }
        
        self._status_map = out
        
        return self._status_map

    def _job_model_to_dist(self, model):
        return {
            "id": model["JobId"],
            "name": model["Name"].decode(),
            "schedule_time": timestamp_or_none(model["SchedTime"]),
            "start_time": timestamp_or_none(model["StartTime"]),
            "end_time": timestamp_or_none(model["EndTime"]),
            "real_end_time": timestamp_or_none(model["RealEndTime"]),
            "files": model["JobFiles"],
            "status": self.status_map[model["JobStatus"].decode()]["id"],
            "bytes": model["JobBytes"],
            "level": self.level_map[model["Level"].decode()]["id"]
        }

    def list_global_finished_jobs(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'select j.JobId, j.Name, j.SchedTime, j.StartTime, j.EndTime, j.RealEndTime, j.JobFiles, j.JobStatus, j.JobBytes, j.Level from Job as j inner join (select max(JobId) as JobId from Job group by Name) i on (j.JobId = i.JobId)',
            )
            results = cursor.fetchall()
        
        for r in results:
            yield self._job_model_to_dist(r)

    # def list_last_finished_jobs(self, limit = 20):
    #     with self.connection.cursor() as cursor:
    #         cursor.execute(
    #             'select Job, JobId, Name, StartTime, EndTime, JobFiles, JobStatus, JobBytes, Level from Job order by JobId desc limit %s',
    #             (limit,)
    #         )
    #         results = cursor.fetchall()

    #     for r in results:
    #         yield self._job_model_to_dist(r)
    
    def get_global_stats(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Name, SUM(JobBytes) AS Size FROM Job GROUP BY Name LIMIT 50000")
            results = cursor.fetchall()
        
        global_size = {}
        for r in results:
            global_size[r['Name'].decode()] = int(r['Size'])
        
        return {
            'disk_used_per_job': global_size
        }

    # def list_media(self):
    #     with self.connection.cursor() as cursor:
    #         cursor.execute("select VolumeName, PoolId, FirstWritten, LastWritten, LabelDate, VolJobs, VolFiles, VolBytes, VolStatus, MaxVolBytes from Media")
    #         # left join Pool
    #         results = cursor.fetchall()
    #         #{'VolumeName': b'Mig-0317', 'PoolId': 2, 'FirstWritten': datetime.datetime(2019, 2, 4, 2, 39, 54), 'LastWritten': datetime.datetime(2019, 2, 4, 3, 51, 25), 'LabelDate': datetime.datetime(2019, 2, 4, 2, 39, 54), 'VolJobs': 1, 'VolFiles': 7, 'VolBytes': 34359736126, 'VolStatus': 'Full', 'MaxVolBytes': 34359738368, 'MaxVolFiles': 0}
    #     for r in results:
    #         yield {
    #             'name': r['VolumeName'].decode()
    #         }

    def close(self):
        self.connection.close()
