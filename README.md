# RefHar

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Requirements

| Software  | Version    | 
|-----------------|--------------------------------------|
| python  | \>= 3.6.0     | 
| pip  | \>= 21.1.3  |

The program relies on [myTypeset](https://github.com/MartinPaulEve/meTypeset) to parse the documents.

```
git clone https://github.com/MartinPaulEve/meTypeset.git
```

## Installation

Download source and create virtual environment:

```
git clone https://github.com/biblhertz/RefHar.git
cd RefHar
python -m venv venv
```

From within the `RefHar` directory:

run the following in bash if you' re installing on Linux/Unix:

```
source venv/bin/activate
```

run the following in powershell if you' re installing on Windows:
(one must change the execution policy to allow the script to run, [see more](https://superuser.com/questions/106360/how-to-enable-execution-of-powershell-scripts))
```
.\venv\Scripts\Activate.ps1 
```

Now make sure `pip` is installed:

```
python -m pip install --upgrade pip
python -m pip --version
```

Install all requirements using pip:

```
pip install -r requirements.txt
```

## Setup
Before running the program you must change the following in `config.ini`:
* Set `ProjectRoot` variable to the full path of the directory where the `RefHar` source is located
  * in a Linux/Unix system: `ProjectRoot = /home/<user>/RefHar`
  * in a Windows system: `ProjectRoot = C:\Users\<user>\Documents\RefHar`
* Set `Workspace` to any system folder that the user has read/write access.
  * in a Linux/Unix system: `Workspace = /home/<user>/workspace` or `Workspace = /tmp/workspace`
  * in a Windows system: `Workspace = C:\Users\<user>\Documents\workspace`
* Set `MeTypesetPath` to the full path to `bin\meTypeset.py` file of the meTypeset project you have already cloned 
  * in a Linux/Unix system: `MeTypesetPath = /home/<user>/meTypeset/bin/meTypeset.py`
  * in a Windows system: `MeTypesetPath = C:\Users\<user>\Documents\meTypeset\bin\meTypeset.py`

### Using custom configuration file
You can specify a different configuration filename than `config.ini` by setting the environment variable `REFCY_CONF`, so you can keep the supplied file as a reference.
For example, on *nix systems:

    export REFCY_CONF=my.config.ini

## Run Standalone

From within the `RefHar` directory run:

```
flask run
```

## Run tests

From within the `RefHar` directory run:

```
python -m unittest discover
```

## Using Docker
### Development

In order to develop the application using docker  run:
```
docker-compose -f docker-compose.yml up -d
```
### Production

In order to deploy the application to production using [gunicorn](https://gunicorn.org/) run:

```
docker-compose -f docker-compose-production.yml up -d
```

One should consider setting the environment variable `REFCY_SECRET_KEY` in order to encrypt the users' sessions.

## Usage Rights

RefHar depends on meTypeset, which is under the GNU General Public License version 2, and x3ml, which is under the Apache License 2.0. For rights compatibility, it is available under the GNU General Public License 3.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

See [LICENSE](LICENSE) file for the full GPLv3 text.
