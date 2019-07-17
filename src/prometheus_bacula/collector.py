import logging
import datetime
from prometheus_client import Gauge, CollectorRegistry

class UpdatingRegistryCollector(CollectorRegistry):
    def collect(self, *args, **kwargs):
        self.on_collect()
        return super(UpdatingRegistryCollector, self).collect(*args, **kwargs)

    def on_collect(self):
        pass


class MetricsContainer(object):
    def __init__(self, reader):
        super(MetricsContainer, self).__init__()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.reader = reader
        self.registry = UpdatingRegistryCollector()
        self.registry.on_collect = self.update

        self.min_delay_time = datetime.timedelta(seconds=5)
        self.last_update = None

        self.m_finished_job_start = Gauge('bacula_finished_job_start_seconds', 'Job real start time', registry=self.registry, labelnames=["name"])
        self.m_finished_job_end = Gauge('bacula_finished_job_end_seconds', 'Job end time', registry=self.registry, labelnames=["name"])
        self.m_finished_files = Gauge('bacula_finished_job_files_count', 'Number of files fetched in job', registry=self.registry, labelnames=["name"])
        self.m_finished_size = Gauge('bacula_finished_job_size_bytes', 'Size of job data', registry=self.registry, labelnames=["name"])
        self.m_finished_status = Gauge('bacula_finished_job_status', 'Job status', registry=self.registry, labelnames=["name"])
        self.m_finished_level = Gauge('bacula_finished_job_level', 'Job level', registry=self.registry, labelnames=["name"])
        self.m_finished_id = Gauge('bacula_finished_job_id', 'Job id', registry=self.registry, labelnames=["name"])

        self.m_job_bytes_total = Gauge('bacula_job_bytes_total', 'Total size of job', registry=self.registry, labelnames=["name"])
    
    def update(self):
        if self.last_update is not None and (datetime.datetime.now() - self.last_update) <= self.min_delay_time:
            return
        
        self.logger.info("Updating metrics")
        for job in self.reader.list_global_finished_jobs():
            labels = [job["name"]]
            self.m_finished_job_start.labels(*labels).set(job["start_time"])
            self.m_finished_job_end.labels(*labels).set(job["end_time"])
            self.m_finished_files.labels(*labels).set(job["files"])
            self.m_finished_size.labels(*labels).set(job["bytes"])
            self.m_finished_status.labels(*labels).set(job["status"])
            self.m_finished_level.labels(*labels).set(job["level"])
            self.m_finished_id.labels(*labels).set(job["id"])
        
        stats = self.reader.get_global_stats()
        for k,v in stats['disk_used_per_job'].items():
            self.m_job_bytes_total.labels(k).set(v)

        self.last_update = datetime.datetime.now()
