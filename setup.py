import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pcassandra',
    version='0.0.6.dev',
    packages=[
        'pcassandra',
        'pcassandra.dj18',
        'pcassandra.dj18.auth',
        'pcassandra.dj18.session',
        'pcassandra.management',
        'pcassandra.management.commands',
    ],
    include_package_data=True,
    license='BSD License',
    description='Utilities to use Cassandra with Django',
    long_description=README,
    url='https://github.com/hgdeoro/pcassandra',
    author='Horacio G. de Oro',
    author_email='hgdeoro@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    ],
)
