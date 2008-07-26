from setuptools import setup

setup(
    name='Emergent',
    version='1.1',
    description='A humble attempt at creating emergent behavior',
    author='Carlo Cabanilla',
    author_email='carlo.cabanilla@gmail.com',
    url='http://syntacticbayleaves.com',
    packages=['emergent'],
    scripts=['bin/emergent'],
    test_suite='nose.collector',
)

