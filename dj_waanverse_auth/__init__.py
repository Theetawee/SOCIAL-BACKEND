# flake8: noqa
# Copyright 2024 Waanverse Labs Inc.
r"""                                               _           _         
| |  | |                                          | |         | |        
| |  | | __ _  __ _ _ ____   _____ _ __ ___  ___  | |     __ _| |__  ___ 
| |/\| |/ _` |/ _` | '_ \ \ / / _ \ '__/ __|/ _ \ | |    / _` | '_ \/ __|
\  /\  / (_| | (_| | | | \ V /  __/ |  \__ \  __/ | |___| (_| | |_) \__ \
 \/  \/ \__,_|\__,_|_| |_|\_/ \___|_|  |___/\___| \_____/\__,_|_.__/|___/
"""

__version__ = "0.0.0-alpha.1"
__author__ = "Waanverse Labs Inc."
__email__ = "software@waanverse.com"
__description__ = "A comprehensive Waanverse Labs Inc. internal package for managing user accounts and authentication"
__maintainer__ = "Khaotungkulmethee Pattawee Drake"
__maintainer_email__ = "tawee@waanverse.com"

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Dj Waanverse Auth package initialized")
