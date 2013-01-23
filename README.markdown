GiantDwarf
=========
A simple Campfire bot written in Python 

Installation
------------
* Clone the repo

```
lex@server:~/src$ git clone git@github.com:lextoumbourou/GiantDwarf.git
```

* Install via **setup.py**

```
lex@server:~/src$ cd GiantDwarf
lex@server:~/src/GiantDwarf$ sudo python setup.py install 
```

* Copy the **example-giantdwarf.conf** to **/etc/giantdwarf/giantdwarf.conf** or to **~/.giantdwarf.conf** and configure.

```
# API authentication token (found under My Info in Campfire)
token: 'abcdefghijklmnop'

# Part of domain before .campfire.com
subdomain: 'WeBuiltItButHeWontCome' # don't include .campfirenow.com 
...
```

Usage
-----
* Run in the background

```
lex@server:~$ python giantdwarf.py &
```

* Or, as an upstart job

```
lex@server:~$ cat /etc/init/giantdwarf.conf
# Start GiantDwarf
#

description "Start GiantDwarf server"

start on startup

script
    python giantdwarf.py
end script

lex@server:~$ sudo start giantdwarf
giantdwarf start/running, process 6834
```

* See what's up in Campfire


Plugin Development
-----------------
* Coming soon

Prereqs
------
* BeautifulSoup 3

```
pip install BeautifulSoup
```

* [PyFire](https://github.com/mariano/pyfire)

License
------
MIT
