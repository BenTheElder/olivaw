import threading
from datetime import datetime

from olivaw.compat import queue

# TODO: specify job format
# TODO: hooks for persisting jobs
# TODO: start_time format

class Sheduler(object):
    def __init__(self):
        self._cond = threading.Condition()
        self._wait_time = 1.
        self._job_queue = queue.PriorityQueue()

    def run(self):
        while True:
            # wait for a job to be ready
            self._cond.wait_for(self.job_ready(), timeout=self._wait_time)
            # fetch the first job
            try:
                start_time, job = self._job_queue.get()
            except queue.Empty:
                continue
            # run all ready jobs
            job_done = False
            while start_time <= datetime.utcnow():
                # run job
                # TODO: how should we handle this?
                try:
                    job[0](job[1:])
                    job_done = True
                except:
                    pass
                try:
                    start_time, job = self._job_queue.get()
                    job_done = False
                except queue.Empty:
                    break
            # if we reached a job that isn't ready, put it back
            if not job_done:
                self._job_queue.put_nowait((start_time, job))

    def job_ready(self):
        # get first job in queue
        try:
            start_time, job = self._job_queue.get()
        except queue.Empty:
            return False
        # put job back in queue
        self._job_queue.put_nowait((start_time, job))
        # return wether it is time to do job
        return start_time <= datetime.utcnow()

    def add_job(self, start_time, job):
        # add job to queue
        self._job_queue.put_nowait((start_time, job))
        # alert runner that there is a job
        self._cond.acquire()
        self._cond.notify()
        self._cond.release()

