# masquerader-detector
A tool for detecting masqueraders using your computer.

## Installation
Clone repo:
```sh
$ git clone https://github.com/CathyMouse96/masquerader-detector.git
```

Install prerequisites:
1. Install the following packages with Homebrew (if you don't have Homebrew, you should probably [get it](https://brew.sh)):
```sh
$ brew install cairo
$ brew install gobject-introspection
```
You may also have to run the following scripts for pkg-config to find openssl, sqlite and libffi:
```sh
$ set -gx PKG_CONFIG_PATH "/usr/local/opt/openssl/lib/pkgconfig"
$ set -gx PKG_CONFIG_PATH "/usr/local/opt/sqlite/lib/pkgconfig"
$ set -gx PKG_CONFIG_PATH "/usr/local/opt/libffi/lib/pkgconfig"
```
These are the prerequisites for AppKit which we will install with pip.

2. Install the following requirements with pip (Make sure you have Python 3 installed):
```sh
$ pip3 install -r requirements.txt
```

## Usage
Collect user behavior data (requires root privileges):
```sh
$ python3 collect.py [-i <interval>] [-m <monitor_dir>] [-o <output_dir>] [-v]
```

Train model:
```sh
$ python3 train.py
```

## Troubleshooting
1. `ModuleNotFoundError: No module named 'AppKit'`
Solution: Run `pip3 install -U PyObjC` and rename `appkit` to `AppKit` in wherever your AppKit is installed (e.g. `/Library/Frameworks/Python.framework/Versions/<version>/lib/python<version>/site-packages`).