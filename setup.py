import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pcassandra',
    version='0.0.2',
    packages=[
        'pcassandra',
        'pcassandra.management',
        'pcassandra.management.commands',
        'pcassandra.dj18',
        'pcassandra',
        'pcassandra',
    ],
    include_package_data=True,
    license='BSD License',
    description='Utilities to use Cassandra with Django',
    long_description=README,
    url='https://github.com/hgdeoro/pcassandra',
    author='Horacio G. de Oro',
    author_email='hgdeoro@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
