# Central module for configuration, with command-line and json too.

import datetime
import argparse
import json

import sys
import logging as log
import os
from os.path import dirname, join, realpath

# put our configuration values in this module object, so other modules can see them just by importing.
this = sys.modules[__name__]


def initialize():
    parser = argparse.ArgumentParser(
        description='Generate a "DataBook". See https://github.com/normanlorrain/DataBook.'
    )
    parser.add_argument("root", help="root of document project")
    parser.add_argument("output", help="destination filename")
    args = parser.parse_args()
    log.debug(f"arguments: {args}")

    this.root = os.path.abspath(args.root)
    this.build = join(this.root, ".build")
    this.buildRef = join(this.root, ".build-ref")
    this.output = os.path.abspath(args.output)
    log.debug(f"Initializing with root: {this.root}")
    log.debug(f"                        {this.build},")
    log.debug(f"                        {this.buildRef}")
    log.debug(f"                        {this.output}")

    os.chdir(this.root)
    loadConfiguration(this)
    log.debug(f"Initialized")

    this.datestamp = str(datetime.date.today())

    # our latex template is in the same dir as this file
    this.template = os.path.join(os.path.dirname(__file__), "template.tex")


def loadConfiguration(container):
    configName = os.path.join(this.root, "configuration.json")

    with open(configName) as json_data:
        for key, value in json.load(json_data).items():
            setattr(container, key, value)
