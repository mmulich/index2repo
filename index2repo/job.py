# -*- coding: utf-8 -*-
"""Python package job creation and run process.

Currently implemented to integrate with Jenkins CI (jenkins-ci.org).
Later we can abstract the job process to work with other systems.
"""
import urllib
import json


class JobQueue:
    """rough implementatin of Job queuing"""

    def __init__(self, runner):
        self.runner = runner
        self._data = []

    def __call__(self):
        for data_set in self._data:
            self.runner(*data_set)

    def add(self, dir, info):
        self._data.append((dir, info,))

    def clear(self):
        self._data = []


class JenkinsCIJobRunner:
    """Job creation and processing through Jenkins CI (jenkins-ci.org)."""

    def __init__(self, url):
        self.url = url

    def __call__(self, dir, release_info):
        job_info = {}
        metadata = object()
        print("Running {0} ({1})...".format(release_info.name, release_info.version))
        return job_info, metadata

    def _has_job(self, name):
        return False

    def _create_job(self, name, type):
        url = "{0}/api/?name={1}".format(self.url, name)
        
        resp = urllib.request.
        pass

    def _update_job(self, name):
        pass

    def _get_job_status(self, name):
        return None
