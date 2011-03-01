#!/usr/bin/env python

'''
simple shortcut for running nosetests via python
replacement for *.bat or *.sh wrappers
'''

import os
import sys
from os.path import join, pardir, abspath, dirname

import nose


# django settings module
DJANGO_SETTINGS_MODULE = 'settings'

# inject current dir to pythonpath
p = abspath(join( dirname(__file__), pardir))
if p not in sys.path:
    sys.path.insert(0, p)

# django needs this env variable
os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE

# TODO: ugly hack to inject django plugin to nose.run
#
#
for i in ['--with-django',]:
    if i not in sys.argv:
        sys.argv.insert(1, i)
#
nose.run_exit(
    defaultTest=dirname(__file__),
)

