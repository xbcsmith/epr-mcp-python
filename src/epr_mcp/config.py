# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from dataclasses import asdict, dataclass


@dataclass
class Config:
    """Data class for Config"""

    url: str
    token: str
    debug: bool = False

    def as_dict(self):
        """Get a dictionary containing object properties"""
        return asdict(self)
