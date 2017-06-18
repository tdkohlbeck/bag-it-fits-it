# bag-it-fits-it
## An archiving and metadata-scraping tool
---

## Table of Contents

- Prerequisites
	- Python
		- [Installing Python (Windows)](#python-install-windows)
		- [Installing Python (MacOS)](#python-install-macos)
	- Java
		- Installing Java (Windows) (TODO)
		- Installing Java (MacOS) (TODO)
 	- FITS (TODO?)
- [Setup](#setup)
- [How to Use](#how-to-use)

---

### [Installing Python (Windows)](#python-install-windows)

First check if Python is already set up on your computer by running "python -V" in your Command Prompt.
```
C:\Users\Me>python -V
Python 3.6.1

C:\Users\Me>
```
If this command does not print a python version:

1. Navigate to http://python.org/downloads and download the latest Python 3.x.x release (not 2.7.x)
2. Run the install file, select "Add Python 3.6 to PATH", and complete installation process
3. open a Command Prompt and

---

### [Installing Python (MacOS)](#python-install-macos)

Python should come pre-installed on MacOS. To double check, run "python -V" in a terminal:
```sh
$ python -V
Python x.x.x
$
```

---

### [Setup](#setup)

1. Git clone or download/unzip `bag-it-fits-it` directory to desired location
2. Download/unzip the latest release of [FITS](https://projects.iq.harvard.edu/fits/downloads)
3. rename the fits directory from `fits-x.x.x` (where x.x.x is the most recent version) to `fits`
4. move the `fits` directory into the `bag-it-fits-it` directory (i.e. `path/to/bag-it-fits-it/fits/`)

---

### [How to Use](#how-to-use)

1. Navigate to the `bag-it-fits-it` directory in the terminal/Command Prompt

```sh
~ $ cd path/to/bag-it-fits-it
~/path/to/bag-it-fits-it $
```

2. Run `bag-it-fits-it.py` using two additional arguments
	- the directory to bag 'n fits
	- the location to place the report and bags

```sh
~/bag-it-fits-it $ bag-it-fits-it.py path/to/bag path/to/output
```
