stilio
======

.. image:: https://travis-ci.org/seik/stilio.svg?branch=master
   :target: https://travis-ci.org/seik/stilio
.. image:: https://readthedocs.org/projects/stilio/badge/?version=latest
   :target: https://stilio.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/badge/code_style-black-000000.svg
   :target: https://github.com/ambv/black
.. image:: https://img.shields.io/github/license/seik/stilio
   :target: https://github.com/seik/stilio/blob/master/LICENSE

Goals
-----

-  Completely written in python.
-  Fast. But ***never*** trade code readability for speed.
-  Easy set up.

FAQ
~~~

    The crawler speed is not so good.

Try to run this commands if you are on linux:

::

    iptables -I OUTPUT -t raw -p udp --sport PORT_NUMBER -j NOTRACK
    iptables -I PREROUTING -t raw -p udp --dport PORT_NUMBER -j NOTRACK
