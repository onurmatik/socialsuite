import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-social-suite',
    version='0.1',
    packages=[
        'logs',
        'profiles',
        'streams',
        'tokens',
        'tweets',
    ],
    install_requires=[
        'Django',
        'twython',
        'requests[security]',
        'Unidecode',
    ],
    include_package_data=True,
    license='BSD License',
    description='A Django app to fetch and manage tweets.',
    long_description=README,
    url='https://www.example.com/',
    author='@onurmatik',
    author_email='onurmatik@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
