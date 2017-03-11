import threading
from datetime import datetime

from olivaw.compat import queue
import olivaw.tasks as tasks 

# TODO: hooks for persisting jobs
# TODO: error handling

class Scheduler(object):
    def __init__(self):
        self._cond = threading.Condition()
        self._default_wait_time = 60.
        self._job_queue = queue.PriorityQueue()

    def run(self):
        while True:
            # wait for a job to be ready
            self._cond.acquire()
            wait_time = self.next_wait_time()
            while wait_time > 0:
                self._cond.wait(timeout=wait_time)
                wait_time = self.next_wait_time()
            self._cond.release()
            # fetch the first job
            try:
                start_time, job = self._job_queue.get_nowait()
            except queue.Empty:
                continue
            # run all ready jobs
            job_done = False
            while start_time <= datetime.utcnow():
                # run job
                # TODO: how should we handle this?
                try:
                    tasks.do_job(job)
                    job_done = True
                except:
                    pass
                try:
                    start_time, job = self._job_queue.get_nowait()
                    job_done = False
                except queue.Empty:
                    break
            # if we reached a job that isn't ready, put it back
            if not job_done:
                self._job_queue.put_nowait((start_time, job))

    def next_wait_time(self):
        # get first job in queue
        try:
            start_time, job = self._job_queue.get_nowait()
        except queue.Empty:
            # if no job, return default wait time
            return self._default_wait_time
        # put job back in queue
        self._job_queue.put_nowait((start_time, job))
        # return time to next job
        return (start_time - datetime.utcnow()).total_seconds()

    def add_job(self, start_time, job):
        # add job to queue
        self._cond.acquire()
        self._job_queue.put_nowait((start_time, job))
        # alert runner that there is a job
        self._cond.notify()
        self._cond.release()
