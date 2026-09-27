#!/usr/bin/env python3
"""Thin web face for fence_estimator.py. Deploy on Streamlit Community Cloud."""

from __future__ import annotations

import streamlit as st

from fence_estimator import (
    CREW_RATE,
    MARKUP,
    print_the_job,
    stakes_from_pins,
    write_the_job,
)


def parse_pairs(blob: str):
    rows = []
    for line in blob.splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.replace(" ", "")
        a, b = line.split(",")
        rows.append((float(a), float(b)))
    return rows


def parse_gates(blob: str):
    rows = []
    for line in blob.splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.replace(" ", "")
        idx, width = line.split(",")
        rows.append((int(idx), float(width)))
    return rows


st.set_page_config(page_title="walk-the-line", layout="centered")
st.title("Walk the line. Price the job.")
st.caption("Privacy · chain-link · vinyl. Feet on the ground or pins off a satellite map.")

shop = st.text_input("Shop name on the quote", "Fence Estimate")
customer = st.text_input("Customer")
site = st.text_input("Site")

c1, c2, c3 = st.columns(3)
style = c1.selectbox("Style", ["privacy", "chain_link", "vinyl"])
height = c2.number_input("Height (ft)", min_value=3.0, max_value=12.0, value=6.0, step=0.5)
mode = c3.radio("Points from", ["feet", "satellite"], horizontal=True)

if mode == "feet":
    st.markdown("One stake per line as `x,y` in feet. First stake is usually `0,0`.")
    raw_pts = st.text_area("Stakes", "0,0\n120,0\n120,40\n200,40", height=120)
else:
    st.markdown(
        "One pin per line as `lat,lon`. "
        "Google Maps: right-click a corner → copy coordinates."
    )
    raw_pts = st.text_area(
        "Pins",
        "30.1765,-85.8059\n30.1765,-85.8053\n30.1766,-85.8053\n30.1766,-85.8049",
        height=120,
    )

st.markdown("Gates as `point_index,width_ft`. Index is 0 for the first point. Leave blank if none.")
raw_gates = st.text_area("Gates", "0,4\n2,10", height=80)

c4, c5 = st.columns(2)
rate = c4.number_input("Crew $/hr", min_value=1.0, value=float(CREW_RATE), step=1.0)
markup = c5.number_input("Markup (0.30 = 30%)", min_value=0.0, value=float(MARKUP), step=0.05)

if st.button("Write the job", type="primary"):
    try:
        pairs = parse_pairs(raw_pts)
        openings = parse_gates(raw_gates) if raw_gates.strip() else []
        stakes = stakes_from_pins(pairs) if mode == "satellite" else pairs
        job = write_the_job(
            shop, customer, site, stakes, style, height, openings, rate, markup
        )
    except Exception as exc:
        st.error(f"Could not read the line: {exc}")
    else:
        if "error" in job:
            st.error(job["error"])
        else:
            if mode == "satellite":
                st.caption("Pins flattened to local feet from the first pin.")
                st.write(stakes)
            st.code(print_the_job(job), language=None)
            books = job["books"]
            m1, m2, m3 = st.columns(3)
            m1.metric("Tape", f"{job['line']['tape_ft']} ft")
            m2.metric("Net run", f"{job['line']['net_ft']} ft")
            m3.metric("Total", f"${books['total']:,.2f}")
