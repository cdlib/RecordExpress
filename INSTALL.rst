===================================
RecordExpress EAD Generator install
===================================

RecordExpress is a Django application for generating lightweight EAD files.


To add to existing Django projects
==================================

1. In your Django environment::

    easy_install install https://github.com/cdlib/RecordExpress.git

    or

    pip install -e git+https://github.com/cdlib/RecordExpress.git

2. Add to your settings::

    INSTALLED_APPS = (
        ...
        'dublincore',
        'collection_record',
    )

3. Sync the dbs::

    manage.py syncdb


For quick start
--------------

See QUICKSTART in `README.rst <./README.rst>`_.
