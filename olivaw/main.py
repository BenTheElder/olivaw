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
import threading
from datetime import datetime
# third-party libraries
from flask import Flask, request
# application imports
import olivaw.tasks as tasks
import olivaw.telegram as telegram
from olivaw.settings import secrets
from olivaw.schedule import Scheduler

# pylint: disable=I0011,invalid-name
app = Flask(__name__.split('.')[0])
scheduler = Scheduler()


@app.before_first_request
def init():
    """initialize the server"""
    sched_thread = threading.Thread(target=scheduler.run)
    sched_thread.daemon = True
    sched_thread.start()

@app.route('/')
def hello():
    """Handle Unknown Routes."""
    print("/ | hit.")
    url = 'http://telegram.me/%s' % (secrets["telegram.bot_name"])
    return 'Nothing to see here. <a href="%s">%s</a>' % (url, url)

@app.route(secrets['telegram.webhook_path'], methods=['GET', 'POST'])
def telegram_webhook():
    """handle telegram webhook hits"""
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
        start_time = datetime.utcfromtimestamp(int(job["timestamp"]))
        scheduler.add_job(start_time, job)
        telegram.send_reply(secrets['telegram.bot_key'], msg, reply)
    return ''

@app.errorhandler(500)
def server_error(e):
    """500 error page handler"""
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

def main():
    """entry point for server"""
    try:
        telegram.set_webhook(secrets["telegram.bot_key"], secrets["telegram.webhook_address"])
    except:
        logging.exception('An error occured when setting the webhook.')
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

if __name__ == '__main__':
    main()
