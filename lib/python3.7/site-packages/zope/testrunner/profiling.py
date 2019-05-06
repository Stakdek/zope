##############################################################################
#
# Copyright (c) 2004-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Profiler support for the test runner
"""
import cProfile
import glob
import os
import pstats
import tempfile

import zope.testrunner.feature

available_profilers = {}



class CProfiler(object):
    """cProfiler"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.profiler = cProfile.Profile()
        self.enable = self.profiler.enable
        self.disable = self.profiler.disable

    def finish(self):
        self.profiler.dump_stats(self.filepath)

    def loadStats(self, prof_glob):
        stats = None
        for file_name in glob.glob(prof_glob):
            if stats is None:
                stats = pstats.Stats(file_name)
            else:
                stats.add(file_name)
        return stats

available_profilers['cProfile'] = CProfiler


class Profiling(zope.testrunner.feature.Feature):

    def __init__(self, runner):
        super(Profiling, self).__init__(runner)
        self.active = bool(self.runner.options.profile)
        self.profiler = self.runner.options.profile

    def global_setup(self):
        self.prof_prefix = 'tests_profile.'
        self.prof_suffix = '.prof'
        self.prof_glob = os.path.join(self.runner.options.prof_dir,
                                      self.prof_prefix + '*' + self.prof_suffix)
        # if we are going to be profiling, and this isn't a subprocess,
        # clean up any stale results files
        if not self.runner.options.resume_layer:
            for file_name in glob.glob(self.prof_glob):
                os.unlink(file_name)
        # set up the output file
        self.oshandle, self.file_path = tempfile.mkstemp(
            self.prof_suffix, self.prof_prefix, self.runner.options.prof_dir)
        self.profiler = available_profilers[self.runner.options.profile](self.file_path)

        # Need to do this rebinding to support the stack-frame annoyance with
        # hotshot.
        self.late_setup = self.profiler.enable
        self.early_teardown = self.profiler.disable

    def global_teardown(self):
        self.profiler.finish()
        # We must explicitly close the handle mkstemp returned, else on
        # Windows this dies the next time around just above due to an
        # attempt to unlink a still-open file.
        os.close(self.oshandle)
        if not self.runner.options.resume_layer:
            self.profiler_stats = self.profiler.loadStats(self.prof_glob)
            self.profiler_stats.sort_stats('cumulative', 'calls')

    def report(self):
        if not self.runner.options.resume_layer:
            self.runner.options.output.profiler_stats(self.profiler_stats)
