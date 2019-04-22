# -*- coding: utf-8 -*-

"""Top-level package for color_bucket_logger."""

__author__ = """Adrian Likins"""
__email__ = 'adrian@likins.com'
__version__ = '0.1.0'

from .formatter import ColorFormatter, add_default_record_attrs
from . import other_module

__all__ = ['ColorFormatter', 'add_default_record_attrs', 'other_module']
