#!/usr/bin/env python3
"""Shared layout helpers for Streamlit pages."""
import streamlit as st


def apply_fullscreen_layout(*, hide_header: bool = True, tight_padding: bool = True) -> None:
    """Inject compact CSS so pages feel closer to a fullscreen app."""
    styles = ["""<style>"""]
    if hide_header:
        styles.append(".stApp header {display: none;}")
    if tight_padding:
        styles.append(
            ".block-container {padding-top: 1.2rem; padding-bottom: 1.5rem; max-width: 1200px;}"
        )
    styles.append("body {background-color: #f8fafc;}")
    styles.append("</style>")
    st.markdown("\n".join(styles), unsafe_allow_html=True)

