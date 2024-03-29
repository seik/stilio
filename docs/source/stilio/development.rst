.. _development:

Development
===========

To help with the development process a compose file is provided. This compose file only 
executes the ``frontend`` and ``postgres`` services. The ``crawler`` service is not 
executed to avoid saturating the network of the dev machine. 

Launch
------

::

    docker-compose -f dev.yml up

A volume is linked to the folder contained the code, so there is no need to restart the
docker-compose to apply changes.

Fake data
---------

In order to create fake data, with the postgres service running (previous step),
execute this command::

    docker-compose -f dev.yml run --rm frontend python -m "stilio.persistence.populate"

Some notes
----------

If you install a new package using ``poetry`` a build is required to install the package
in the container::

    docker-compose -f dev.yml build

