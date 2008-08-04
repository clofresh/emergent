from distutils.core import setup
import os
from warnings import warn

metadata = dict(
    name='Emergent',
    version='1.1',
    description='A humble attempt at creating emergent behavior',
    author='Carlo Cabanilla',
    author_email='carlo.cabanilla@gmail.com',
    url='http://syntacticbayleaves.com',
    packages=['emergent'],
    scripts=['bin/emergent'],
)

try:
    import nose
    metadata['test_suite'] = 'nose.collector'
except:
    warn("nose not found. Can't run test suite", ImportWarning)    

if os.name == 'nt':
    try:
        import py2exe
        metadata['console'] = ['bin/emergent']
    except ImportError:
        warn("py2exe not found. Can't bundle Windows executable", ImportWarning)
    

setup(**metadata)
