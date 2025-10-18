#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Word matching package"""

from .word import process
from .io import save_outputs
from .settings import DEFAULT_CONFIG

__all__ = ["process", "save_outputs", "DEFAULT_CONFIG"]
