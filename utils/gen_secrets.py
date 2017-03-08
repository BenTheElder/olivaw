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
try:
   input = raw_input
except NameError:
   pass
from os import path
self_path = path.dirname(__file__)
secrets_path = path.join(self_path, "..", "secrets.cfg")
url = input("Enter the relative path (eg '/foo') for the telegram webhook: ")
host = input("Enter the host address (eg 'https://foo.appspot.com'): ")
bot = input("Enter the telegram bot api key: ")
with open(secrets_path, "w") as f:
    f.write("# AUTOMATICALLY GENERATED DO NOT EDIT!\n")
    f.write("# DO NOT CHECK INTO GIT.\n")
    f.write("\n")
    f.write("# Telegram Secrets.\n[telegram]")
    f.write("telegram_webhook_path = %s\n"%(url))
    f.write("telegram_webhook_address = '%s%s'\n"%(host, url))
    f.write("telegram_bot_key = '%s'\n"%(bot))
