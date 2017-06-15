#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `color_debug` package."""

import pytest

import logging

from color_debug import color_debug


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_find_format_attrs():
    format_string = 'foo %(process)d blip'
    res = color_debug.find_format_attrs(format_string)
    assert ('%(process)d', 'process') in res


def test_init(response):
    """Just init the class"""
    formatter = color_debug.ColorFormatter()
    assert isinstance(formatter, color_debug.ColorFormatter)


def test_null_handler(response):
    nh = logging.NullHandler()
    formatter = color_debug.ColorFormatter()
    nh.setFormatter(formatter)
