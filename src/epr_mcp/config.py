# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from dataclasses import asdict, dataclass

TRANSPORTS = ("http", "stdio")


@dataclass
class Config:
    """Data class for Config"""

    url: str
    token: str | None = None
    debug: bool = False
    transport: str = "http"
    host: str = "0.0.0.0"
    port: int = 8000

    def as_dict(self):
        """Get a dictionary containing the configuration values.

        Returns:
            A dictionary with url, token, debug, transport, host, and port.

        Examples:
            >>> Config(url="http://epr").as_dict()["port"]
            8000
        """
        return asdict(self)
