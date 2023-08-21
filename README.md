# What is this?

These are the Python scripts that I've been using to create these two area charts of [TOP500](https://wikipedia.org/wiki/TOP500) supercomputers for use on Wikipedia:

https://commons.wikimedia.org/wiki/File:Processor_families_in_TOP500_supercomputers.svg

![procfam](https://upload.wikimedia.org/wikipedia/commons/e/ef/Processor_families_in_TOP500_supercomputers.svg)

https://commons.wikimedia.org/wiki/File:Countries_with_TOP500_supercomputers.svg

![countries](https://upload.wikimedia.org/wikipedia/commons/a/a6/Countries_with_TOP500_supercomputers.svg)

# Requirements

Requires Python 3.5+ and a valid user account on top500.org. First, create a file called `top500.ini` in
the source directory containing your username and password for the site:

```
[DEFAULT]
username = MyUsername
password = "MyPassword123!"
```

# Running

You can skip `top500.py` if you want to use the cached/already-downloaded biannual lists
in `TOP500_history.csv`:

```
$ pip3 install -r requirements.txt
$ ./get-country-lists.sh    # Fetch country name mapping (country-{en,fr,es}.csv)
$ ./top500.py               # Download and combine latest biannual spreadsheets from top500.org
$ ./top500_plot.py          # Create PNG- and SVG-format plots using TOP500_history.csv
```

# With Nix

This repository provides a [Nix](https://nixos.org) environment. You can run the scripts as:

```
$ nix develop --command python3 top500.py
$ nix develop --command python3 top500_plot.py
```

# License

GPLv3 or later
