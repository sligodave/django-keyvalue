import os
from setuptools import setup

from keyvalue import VERSION


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-keyvalue',
    version=".".join(map(str, VERSION)),
    description='django-keyvalue is a django app for generic Key Value '\
                            'relationships between django model instances.',
    author='David Higgins',
    author_email='sligodave@gmail.com',
    url='http://github.com/sligodave/django-keyvalue/tree/master',
    packages=['keyvalue'],
    long_description=read('README.txt'),
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
