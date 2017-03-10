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
from __future__ import print_function
import json
from datetime import datetime, timedelta
import threading

import parsedatetime as pdt

import olivaw.telegram as telegram
from olivaw.settings import secrets
from olivaw.compat import queue

def do_job(job):
    print("do_job | job: %s"%(job))
    timestamp = job["timestamp"]
    data = json.loads(job["data"])
    if data["type"] == "reminder":
        try:
            cid = data["chat_id"]
            message = "Reminder: %s"%(data["reminder"])
            telegram.send_message(secrets['telegram.bot_key'], cid, message)
        except:
            pass
    return True


def start_job_runner():
    job_runner = threading.Thread(target=run_jobs_forever)
    job_runner.daemon = True
    job_runner.start()
    return job_runner



def parse_reminder(msg):
    reminder_command = "/reminder"
    text = msg.text
    print("parse_reminder, text: %s"%(text))
    if not text.startswith(reminder_command):
        return False, None, None
    parts = text[len(reminder_command):].split(",")
    print("parse_reminder, parts: %s"%(parts))
    if len(parts) != 2:
        return False, None, None
    message, time_text = parts[0], parts[1]
    source_time = datetime.utcnow()
    if msg.date:
        source_time = datetime.utcfromtimestamp(int(msg.date))
    time_struct, _ = pdt.Calendar().parse(time_text, sourceTime=source_time)
    time = datetime(*time_struct[:6])
    job = {
        "data": json.dumps({
            "type": "reminder",
            "reminder": message,
            "chat_id": msg.chat_id()
        }),
        "timestamp": str(int((time - datetime(1970, 1, 1)) / timedelta(seconds=1))),
    }
    reply = "Set reminder for %s UTC."%(str(time))
    return True, job, reply
