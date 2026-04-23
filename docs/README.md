# Talon
A suite of tools to programmatically interact with the underlying Map Dragon API

Talon is a CLI tool that interacts with the underlying API beneath the web application, MapDragon. 

## Requirements
Most of the work is done by the API, however, there are a few requirements. 
- Python >= 3.10
- requests
- rich
- PyYAML

## Installation
The easiest way to install it will be through pip either:

Clone the repository directly to your machine using the standard git clone.
```bash
git clone {{repo}}.git
```

Or, if you want to skip cloning:
```bash
pip install git+{{repo}}
```

## Usage
As with most of our CLI tools, you can use the builtin --help functionality.

```bash
talon -h
```

### Application Options
Because this uses subparsers, the application args must be passed before you specify the command. Those can be found below: 

| Flags | Type/options | Description | Default |
| ----- | ------------ | ----------- | ------- |
| -h, --help | | show this help message and exit | | 
| -log --log-level | NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL | INFO |
| --host | {varies} | MapDragon host short cut as defined in ~/.mdhosts |
| -md-url | {Application URL} | MapDragon URL or locutus api URL | |

#### host vs md-url
The host option is just a way to avoid having to remember what the different URLs are. Users may define as many hosts in the file, ~/.mdhosts file (see below for details). The keys for each are then provided as options for this argument. 

talon will not proceed if you provide both a URL and a host. 

### Defining a ~/.mdhosts file
This is ultimately just a yaml file that (currently) contains only a single relevant property that can have as many options as needed: 

```yaml
hosts:
  dev: http://my-dev-map-dragon.com
  uat: https://uat.mappy.com/api
```

Users can provide either the Map Dragon URL or the locutus 'api' path (if you are interacting with a backend only application, obviously that is your only option)

# Available Commands
- [sideload](sideload.md)
