import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'RecordExpress',
    version = '0.0',
    packages = ['collection_record'],
    include_package_data = True,
    dependency_links = ['https://github.com/cdlib/RecordExpress.git',
        'https://github.com/drewyeaton/django-sortable/archive/master.zip#egg=django-sortable', #pypi package currently broken - 2013/09
        ], 
    license = 'BSD License - see LICENSE file', 
    description = 'A lightweight EAD creator',
    long_description = README,
    author = 'Mark Redar',
    author_email = 'mark.redar@ucop.edu',
    classifiers = [
        'Environment :: Web Environment',
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        'django==1.4, ==1.5',
        'django-dublincore>=0.1',
#        'django-sortable',
        'BeautifulSoup',
        'webtest',
        'django-webtest'
        ],
)

