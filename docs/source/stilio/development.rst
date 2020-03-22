.. _development:

Development
===========

To help with the development process a compose file is provided. This compose file only 
executes the ``frontend`` and ``postgres`` services. The ``crawler`` service is not 
executed to avoid saturating the network of the dev machine. 

Fake data
---------

In order to create fake data, with the postgres service running,
execute this command::

    docker-compose -f dev.yml run --rm frontend python -m "stilio.persistence.populate"

This command also initializes the DB, an action that is normally executed by the
crawling component.

Launch
------

After creating the fake data::

    docker-compose -f dev.yml up

A volume is linked to the folder contained the code, so there is no need to restart the
docker-compose to apply changes.

Some notes
----------

If you install a new package using ``poetry`` a build is required to install the package
in the container::

    docker-compose -f dev.yml build

