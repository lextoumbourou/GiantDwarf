GiantDwarf
=========
A ridiculously simple Nagios bot for Campfire.

Usage
----
* Create settings.py

```
cp settings-default.py settings.py
```

* Configure settings.py.
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
