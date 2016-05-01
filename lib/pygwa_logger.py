#!/usr/bin python
# -*- coding: utf-8 -*-
import os
import json
import logging.config
import logging

from . import projectPath


'''
    check this article
    http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
'''

def setup_logging(
    default_path=projectPath('resources/logging_config.json'), 
    default_level=logging.INFO,
    env_key='PYGWALOG_CFG'
):
    """Setup logging configuration at the start of the program

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
