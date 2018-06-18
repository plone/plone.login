# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '1.0rc1'

long_description = (
    open('README.rst').read() +
    '\n' +
    open('CONTRIBUTORS.rst').read() +
    '\n' +
    open('CHANGES.rst').read() +
    '\n'
)

setup(
    name='plone.login',
    version=version,
    description='Plone Login System',
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Framework :: Zope2',
        'Framework :: Plone',
        'Framework :: Plone :: 5.0',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    ],
    keywords='cms plone login security',
    author='The Plone Foundation',
    author_email='plone@plone.org',
    url='https://github.com/plone/plone.login',
    license='gpl',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['plone', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.app.z3cform',
        'plone.schema',
        'plone.z3cform',
        'six',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.api',
        ]
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
