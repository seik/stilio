.. _development:

Development
========

To help with the development process a compose file ()
is provided. This compose file only executes the ``frontend`` and
``postgres`` services. The ``crawler`` service is not executed
since it can make development painful since it can slow your machine
due to the high amount of net interaction.

Launch
------

.. highlight:: bash
    docker-compose -f dev.yml up

A volume is linked to the folder contained the code, so
there is no need to restart the docker-compose to apply
changes.

Fake data
---------

In order to create fake data, with the postgres service running,
execute this command:

.. highlight:: bash
    docker-compose -f dev.yml run --rm frontend python -m "stilio.persistence.populate"

Some notes
----------

If you install a new package using ``pipenv`` you will need to trigger a
build to install the new package in the container:

.. highlight:: bash
    docker-compose -f dev.yml build

