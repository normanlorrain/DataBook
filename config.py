# Central module for configuration, with command-line and json too.

import argparse
import datetime
import json
import os
import sys
from os.path import dirname, join, realpath

import log

# put our configuration values in this module object, so other modules can see them just by importing.


class _Config:

    def __init__(self):
        print('configuration initializing')
        parser = argparse.ArgumentParser(
            description='Generate a "DataBook". See https://github.com/normanlorrain/DataBook.'
        )
        parser.add_argument("root", help="root of document project")
        parser.add_argument("output", help="destination filename")
        args = parser.parse_args()
        log.debug(f"arguments: {args}")

        self.root = os.path.abspath(args.root)
        self.build = join(self.root, ".build")
        self.buildRef = join(self.root, ".build-ref")
        self.output = os.path.abspath(args.output)
        log.debug(f"Initializing with root: {self.root}")
        log.debug(f"                        {self.build},")
        log.debug(f"                        {self.buildRef}")
        log.debug(f"                        {self.output}")

        os.chdir(self.root)
        self.loadConfiguration()
        log.debug(f"Initialized")

        self.datestamp = str(datetime.date.today())

        # our latex template is in the same dir as this file
        self.template = os.path.join(os.path.dirname(__file__), "template.tex")

    def loadConfiguration(self):
        configName = os.path.join(self.root, "configuration.json")

        with open(configName) as json_data:
            for key, value in json.load(json_data).items():
                setattr(self, key, value)

config = _Config()
