# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from importlib import metadata

__title__ = "epr-mcp"
__version__ = metadata.version(__title__)
__build__ = "1"
__author__ = "Brett Smith"
__license__ = "Apache 2.0"
__version_info__ = tuple(__version__.split("."))


def info():
    """Return the package name and version as two lines of text.

    Examples:
        >>> info().splitlines()[0]
        'epr-mcp'
    """
    return f"{__title__}\n{__version__}"
