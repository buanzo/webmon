#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo 'Buanzo' Busleiman

import os
import sys
import argparse
import time
from pprint import pprint
from Executor.core import ExecutorCore
from Executor.plugin import load_plugins, ExecutorPluginBase

VERSION = '0.1.0'

if __name__ == "__main__":
    print('>>> Webmon Executor <<<')
    defc = '{}/executor.conf'.format(os.getcwd())
    parser = argparse.ArgumentParser()
    parser.add_argument("--version",
                        help="Show version and paths",
                        action="store_true")
    parser.add_argument("-l", "--list",
                        help="List available plugins",
                        action="store_true")
    args = parser.parse_args()
    if args.version:
        print('version: {}'.format(VERSION))
        sys.exit(0)
    excore = ExecutorCore()
    if excore is None:
        print("Executor: Cannot instantiate ExecutorCore()")
        sys.exit(1)

    # Load plugins. Plugins may use sys.exit(255) on error
    plugins = load_plugins()

    if args.list is True:
        ExecutorPluginBase.prettyPrint()
        sys.exit(0)

    # TODO: Implement initial runtime checks here. exit on errors.

    # Still alive? then call ExecutorCore.main()
    try:
        while True:
            ret = excore.main(plugins=plugins)
            if ret is True:  # Just main exiting for normal reasons
                print("Executor: reached 100 runs. Restarting main().")
                time.sleep(1)
            else:
                print("Executor: main() exited. Should not happen.")
                print("Waiting for five seconds for main() restart")
                time.sleep(5)
            print("Restarting...")
    except KeyboardInterrupt:
        print("\nCTRL-C. Exiting....")
