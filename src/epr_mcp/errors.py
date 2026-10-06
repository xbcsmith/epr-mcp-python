# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0


import pdb
import traceback


class BaseError(Exception):
    """Base Error Class"""


class RunCmdError(BaseError):
    """Raised when a command fails to run"""


class CmdMissingError(BaseError):
    """Raised when a command is missing"""


class FileNotFoundError(BaseError):
    """Raised when a file is not found"""


class InvalidKeyError(BaseError):
    """An invalid key was specified"""


class KeyNotFoundError(BaseError):
    """The specified key was not found"""


class NotImplemented(BaseError):
    """function not implemented"""


class EPRError(Exception):
    """Base Error for EPR"""

    message = "An error occurred with the request to EPR"

    def __init__(self, message=None):
        if message:
            self.message += ": " + message
        super().__init__(message)


class GraphQLError(EPRError):
    """Raised when a graphql request fails"""

    message = "Error making GraphQL request to EPR"


def debug_except_hook(type, value, tb):
    """Print an uncaught exception and open a post-mortem debugger.

    Installed as ``sys.excepthook`` when debugging is on. Do not use it with the stdio
    transport: the debugger reads from stdin, which carries the MCP protocol.

    Args:
        type: The exception class.
        value: The exception instance.
        tb: The traceback.
    """
    print(f"epr python hates {type.__name__}")
    print(str(type))

    traceback.print_exception(type, value, tb)
    pdb.post_mortem(tb)
