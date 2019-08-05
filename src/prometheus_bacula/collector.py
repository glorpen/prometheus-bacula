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
        self.last_job_names = set()

        self._job_metrics = []

        self._create_job_metric("schedule_time", "schedule_seconds", "Job schedule time")
        self._create_job_metric("start_time", "start_seconds", "Job start time")
        self._create_job_metric("end_time", "end_seconds", "Job end time")
        self._create_job_metric("real_end_time", "real_end_seconds", "Job real end time")
        self._create_job_metric("files", "files_count", "Number of files fetched in job")
        self._create_job_metric("bytes", "size_bytes", "Size of job data")
        self._create_job_metric("status", "status", "Job status")
        self._create_job_metric("level", "level", "Job level")
        self._create_job_metric("id", "id", "Job id")

        self.m_job_bytes_total = Gauge('bacula_job_bytes_total', 'Total size of job', registry=self.registry, labelnames=["name"])
    
    def _create_job_metric(self, model_field, name, description):
        m = Gauge('bacula_finished_job_%s' % name, description, registry=self.registry, labelnames=["name"])
        def update(model):
            v = model[model_field]
            v = 'nan' if v is None else v
            m.labels(model["name"]).set(v)
        def remove(name):
            m.remove([name])
        self._job_metrics.append((update, remove))

    def update(self):
        if self.last_update is not None and (datetime.datetime.now() - self.last_update) <= self.min_delay_time:
            return
        
        self.logger.info("Updating metrics")

        job_names = set()
        for job in self.reader.list_global_finished_jobs():
            job_names.add(job["name"])
            for updater, _remover in self._job_metrics:
                updater(job)
        
        stats = self.reader.get_global_stats()
        for k,v in stats['disk_used_per_job'].items():
            self.m_job_bytes_total.labels(k).set(v)

        for i in self.last_job_names.difference(job_names):
            self.logger.debug("Removing job %s from metrics", i)
            for _updater, remover in self._job_metrics:
                remover(i)

            self.m_job_bytes_total.remove([i])
        
        self.last_job_names = job_names
        self.last_update = datetime.datetime.now()
