#!/usr/bin/env python
'''
Copyright 2016-2017 Benjamin Elder (BenTheElder) All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
# stdlib imports
from __future__ import print_function
import logging
from datetime import datetime
from datetime import timedelta
import time
import sched
# third-party libraries
from flask import Flask, request
from google.cloud import datastore
# application imports
import olivaw.tasks as tasks
import olivaw.telegram as telegram
from olivaw.settings import secrets

# pylint: disable=I0011,invalid-name
app = Flask(__name__.split('.')[0])
datastore_client = datastore.Client()
scheduler = sched.scheduler(time.time, time.sleep)


@app.route('/')
def hello():
    """Handle Unknown Routes."""
    print("/ | hit.")
    return 'Nothing to see here.'

def do_jobs(deadline=None):
    try:
        jobs_iter = datastore_client.query(kind="Job", order=["timestamp"]).fetch()
    except:
        return 0
    pages = jobs_iter.pages
    try:
        jobs = next(pages)
    except StopIteration:
        return 0
    n_done = 0
    while deadline is None or datetime.utcnow() < deadline:
        for job in jobs:
            timestamp = datetime.utcfromtimestamp(int(job['timestamp']))
            if timestamp <= datetime.utcnow():
                if tasks.do_job(dict(job)):
                    datastore_client.delete(job.key)
                    n_done += 1
        try:
            jobs = next(pages)
        except StopIteration:
            break
    return n_done

@app.route('/_ah/health')
def health():
    deadline = datetime.now() + timedelta(seconds=1)
    print("/_ah/health | hit.")
    n_done = do_jobs(deadline=deadline)
    reply = 'Done. (jobs: %d)' %(n_done)
    print ("/_ah/health | %s"%(reply))
    return reply

@app.route('/triggers/cron')
def cron():
    print("/triggers/cron | hit.")
    n_done = do_jobs()
    reply = 'Done. (jobs: %d)' %(n_done)
    print ("/triggers/cron | %s"%(reply))
    return reply

@app.route(secrets['telegram.webhook_path'], methods=['GET', 'POST'])
def webhook():
    print('telegram_webhook | data: %s'%(request.data))
    json = request.get_json(force=True, silent=True)
    if not json:
        return ''
    print("telegram_webhook | json: %s"%(json))
    update = telegram.Update(json)
    if not update.message or not update.message.text:
        return ''
    msg = update.message
    is_reminder_request, job, reply = tasks.parse_reminder(msg)
    print("reminder: ", is_reminder_request, job, reply)
    if is_reminder_request:
        key = datastore_client.key('Job', job["timestamp"])
        entity = datastore.Entity(key=key)
        for k in job:
            entity[k] = job[k]
        datastore_client.put(entity)
        telegram.send_reply(secrets['telegram.bot_key'], msg, reply)
    return ''

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

def main():
    try:
        telegram.set_webhook(secrets["telegram.bot_key"], secrets["telegram.webhook_address"])
    except:
        logging.exception('An error occured when setting the webhook.')
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

if __name__ == '__main__':
    main()
