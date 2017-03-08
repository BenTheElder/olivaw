#!/usr/bin/env python
import os

self_path = os.path.dirname(__file__)
project_path = os.path.join(self_path, "..")
os.chdir(project_path)
os.system("gcloud app deploy cron.yaml")
