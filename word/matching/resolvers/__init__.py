#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resolvers short-circuit matches before LLM invocation."""

from .exact_matcher import ExactMatchResolver

__all__ = ["ExactMatchResolver"]
