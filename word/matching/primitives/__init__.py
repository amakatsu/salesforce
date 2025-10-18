#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Primitive building blocks used by matching components."""

from .candidates import Candidate, top_k_candidates, phrase_candidates
from .component_matcher import ComponentMatchResult, ComponentMatcher

__all__ = [
    "Candidate",
    "top_k_candidates",
    "phrase_candidates",
    "ComponentMatchResult",
    "ComponentMatcher",
]
