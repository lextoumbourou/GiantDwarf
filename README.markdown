GiantDwarf
=========
A silly little Campfire bot for Nagios.

Usage
----
* Create **settings.py**

```
cp settings-default.py settings.py
```

* Configure **settings.py**

```
TOKEN     = 'abcdefghijklmnop'
SUBDOMAIN = 'WeBuiltItButHeWontCome' # don't include .campfirenow.com 
...
```

* Run the silly thing in the background

```
python GiantDwarf.py &
```

* See what's up in Campfire

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
