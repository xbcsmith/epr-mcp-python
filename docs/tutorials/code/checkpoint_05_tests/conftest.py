# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Let the tests import the server that sits next to them."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
