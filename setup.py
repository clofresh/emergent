from setuptools import setup

setup(
    name='Emergent',
    version='1.0',
    description='A humble attempt at creating emergent behavior',
    author='Carlo Cabanilla',
    author_email='carlo.cabanilla@gmail.com',
    url='http://syntacticbayleaves.com',
    package_dir={'emergent': 'lib/emergent'},
    packages=['emergent'],
    scripts=['bin/emergent']
)

