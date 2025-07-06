# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import asyncio
import argparse
import logging
import os
import sys

from . import config, constants, errors, server

debug = os.environ.get("EPR_DEBUG", False)
level = logging.INFO
if debug:
    sys.excepthook = errors.debug_except_hook
    level = logging.DEBUG
log_format = "%(asctime)s %(name)s:[%(levelname)s] %(message)s"
logging.basicConfig(stream=sys.stderr, level=level, format=log_format)
logger = logging.getLogger(__name__)


class CmdLine(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="EPR MCP Server",
            usage="""eprmcp <command> [<args>]

            eprmcp commands are:
                start   start the EPR MCP server

            """,
        )

        parser.add_argument("command", help="Subcommand to run")
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logger.error("Unrecognized command")
            parser.print_help()
            sys.exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def start(self):
        """
        start the EPR MCP server
        """
        parser = argparse.ArgumentParser(description="start the EPR MCP Server\n")
        parser.add_argument(
            "--token",
            dest="epr_api_token",
            action="store",
            default=os.environ.get("EPR_API_TOKEN"),
            help="EPR Access Token",
        )
        parser.add_argument(
            "--url",
            dest="epr_url",
            action="store",
            default=os.environ.get("EPR_URL", "http://localhost:8042"),
            help="EPR Server URL",
        )
        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            default=False,
            help="Turn debug on",
        )

        args = vars(parser.parse_args(sys.argv[2:]))
        url = args["epr_url"]
        token = args["epr_api_token"]
        cfg = config.Config(url=url, token=token)

        cfg.debug = args["debug"]

        return server.run(cfg)

    def version(self):
        """
        Prints version of epr-mcp
        """
        print(constants.info())


def main():
    CmdLine()


if __name__ == "__main__":
    sys.exit(main())
