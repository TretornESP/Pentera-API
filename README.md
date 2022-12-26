# AUTOCRACKER

## Description

This program is a user's nightmare, it automatically runs pentera a pentera cracking
scenario, parses the results and forces a reset on the user's password through ldap.

## Installation

Just replicate the following folder structure:

```
./conf
./conf/conf.json
./conf/creds
./conf/creds/ad.json
./conf/creds/email.json
./conf/creds/pentera.json
```

## Config files

**conf.json**
```json
{
    "version": "1.0",
    "logfile": "log/autocracker.log",
    "_comment": "Reserved for future use"
}
```

**ad.json**
```json
{
    "user": "autocracker",
    "pass": "************",
    "server": "192.168.123.123",
    "skip": [
        "xabier-iglesias",
        "marcos-gonzalez"
    ]
}
```

**email.json**
```json
{
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "xabier.iglesias@gmail.com",
    "password": "************",
    "to": [
        "xabier.iglesias@gmail.com"
    ]
}
```

**pentera.json**
```json
{
    "ACHIEVEMENT_NAME": "Cracked user hash using GPU",
    "MAX_WAIT_MILLIS": 500000,
    "TARGET_SCENARIO": "Cracking one",
    "API_URL": "https://pentera.yoursite.com:8181/pentera/api/v1/",
    "AUTH_ID": "**************",
    "AUTH_TGT": "****************",
    "AUTH_TOKEN": "****************"
}
```

## How to run

Choose your desired run target. You can simply run it in detached mode with:

```make```

You can view live logs bu running:

```make logs```

You can also rebuild the image to apply deep changes by:

```make rebuild```


## Logging

You may specify a file inside the log folder or leave it blank
if no file is specified, **stdout** will be used instead.

## Make targets

* `make` - Same as make detached
* `make detached` - Runs in detached mode
* `make attached` - Runs in attached mode
* `make stop` - Kills a test
* `make status` - Outputs the status of the container
* `make logs` - Starts tailing logs
* `make clean` - Cleans up the container
* `make build` - Builds the container
* `make rebuild` - Builds and runs the container
* `make push` - Pushes updated code to the repo
* `make pull` - Downloads newest version and rebuilds
