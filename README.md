# stilio
[![Build Status](https://travis-ci.org/seik/stilio.svg?branch=master)](https://travis-ci.org/seik/stilio)
[![Code style: black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/github/license/seik/stilio)](https://github.com/seik/stilio/blob/master/LICENSE)



## Goals

- Completely written in python.
- Fast. But __*never*__ trade code readability for speed.
- Easy set up.

### FAQ

> The crawler speed is not so good.

Try to run this commands if you are on linux:

    iptables -I OUTPUT -t raw -p udp --sport PORT_NUMBER -j NOTRACK
    iptables -I PREROUTING -t raw -p udp --dport PORT_NUMBER -j NOTRACK