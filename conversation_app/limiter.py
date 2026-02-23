#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 21:58:36 2026

@author: hounsousamuel
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from config import LIMIT

LIMITER = Limiter(key_func=get_remote_address)
LIMITE_STR = f"{LIMIT}/minute"
LIMITE_MSG_STR = f"{LIMIT + 5}/minute"
