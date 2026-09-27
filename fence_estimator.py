#!/usr/bin/env python3
"""
fence_estimator.py

Walk the line. Count the posts. Price the job.
Stakes can be local feet (x,y) or satellite pins (lat,lon).

    python fence_estimator.py
    python fence_estimator.py demo
"""

from __future__ import annotations

import math
import sys
from datetime import date
from typing import Dict, List, Optional, Tuple

Stake = Tuple[float, float]
Pin = Tuple[float, float]
Opening = Tuple[int, float]

POST_EVERY = 8.0
EARTH_FT = 20_902_231.0

YARD = {
    "posts_4x4_8ft": 18.00,
    "rails_2x4_8ft": 6.00,
    "concrete_80lb_bags": 6.00,
    "brackets": 2.00,
    "screw_boxes": 15.00,
    "gates": 250.00,
    "picket_boxes": 90.00,
    "fabric_rolls_50ft": 120.00,
    "tension_bars": 25.00,
    "vinyl_panels_6ft": 80.00,
}

PACE = {
    "privacy": 15.0,
    "chain_link": 25.0,
    "vinyl": 12.0,
}

CREW_RATE = 45.0
MARKUP = 0.30
OVERHEAD = 0.10


def span_ft(a: Pin, b: Pin) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 2 * EARTH_FT * math.asin(min(1.0, math.sqrt(h)))


def stakes_from_pins(pins: List[Pin]) -> List[Stake]:
    if not pins:
        return []
    origin = pins[0]
    stakes: List[Stake] = [(0.0, 0.0)]
    for pin in pins[1:]:
        east = span_ft(origin, (origin[0], pin[1]))
        north = span_ft(origin, (pin[0], origin[1]))
        if pin[1] < origin[1]:
            east = -east
        if pin[0] < origin[0]:
            north = -north
        stakes.append((round(east, 2), round(north, 2)))
    return stakes


def walk_the_line(stakes: List[Stake], openings: Optional[List[Opening]] = None) -> Dict:
    if len(stakes) < 2:
        return {"error": "Need two stakes before you can measure anything."}
    tape = 0.0
    for a, b in zip(stakes, stakes[1:]):
        tape += math.hypot(b[0] - a[0], b[1] - a[1])
    openings = openings or []
    eaten = sum(width for _, width in openings)
    return {
        "tape_ft": round(tape, 1),
        "net_ft": round(tape - eaten, 1),
        "gate_count": len(openings),
        "gate_widths": [w for _, w in openings],
    }


def pull_the_ticket(net_ft: float, style: str, gates: int = 0) -> Dict[str, int]:
    posts = int(net_ft // POST_EVERY) + 1
    spans = max(posts - 1, 0)
    extras: Dict[str, int] = {}
    if style == "privacy":
        slats = int(net_ft * 12 / 6.5)
        extras = {"pickets": slats, "picket_boxes": (slats + 49) // 50}
    elif style == "chain_link":
        extras = {
            "fabric_rolls_50ft": (int(net_ft) + 49) // 50,
            "tension_bars": posts,
        }
    elif style == "vinyl":
        extras = {"vinyl_panels_6ft": (int(net_ft) + 5) // 6}
    return {
        "posts_4x4_8ft": posts,
        "rails_2x4_8ft": spans * 2,
        "concrete_80lb_bags": posts * 2,
        "brackets": posts * 2,
        "screw_boxes": max(1, posts // 10),
        "gates": gates,
        **extras,
    }


def crew_time(net_ft: float, style: str, hands: int = 2) -> Dict:
    hours = net_ft / PACE.get(style, 15.0)
    return {"hours": round(hours, 1), "hands": hands, "days": round(hours / 8.0, 1)}


def settle_the_books(
    ticket: Dict[str, int],
    hours: float,
    rate: float = CREW_RATE,
    markup: float = MARKUP,
    overhead: float = OVERHEAD,
) -> Dict[str, float]:
    materials = sum(qty * YARD.get(sku, 0.0) for sku, qty in ticket.items())
    labor = hours * rate
    sub = materials + labor
    burden = sub * overhead
    keep = (sub + burden) * markup
    return {
        "materials": round(materials, 2),
        "labor": round(labor, 2),
        "overhead": round(burden, 2),
        "profit": round(keep, 2),
        "total": round(sub + burden + keep, 2),
    }


def write_the_job(
    shop: str,
    customer: str,
    site: str,
    stakes: List[Stake],
    style: str,
    height: float,
    openings: Optional[List[Opening]] = None,
    rate: float = CREW_RATE,
    markup: float = MARKUP,
) -> Dict:
    line = walk_the_line(stakes, openings)
    if "error" in line:
        return line
    ticket = pull_the_ticket(line["net_ft"], style, gates=line["gate_count"])
    time = crew_time(line["net_ft"], style)
    books = settle_the_books(ticket, time["hours"], rate, markup)
    return {
        "shop": shop,
        "customer": customer,
        "site": site,
        "style": style,
        "height": height,
        "line": line,
        "ticket": ticket,
        "time": time,
        "books": books,
        "when": date.today().isoformat(),
    }


def write_the_job_from_pins(
    shop: str,
    customer: str,
    site: str,
    pins: List[Pin],
    style: str,
    height: float,
    openings: Optional[List[Opening]] = None,
    rate: float = CREW_RATE,
    markup: float = MARKUP,
) -> Dict:
    return write_the_job(
        shop, customer, site, stakes_from_pins(pins), style, height, openings, rate, markup
    )


def print_the_job(job: Dict) -> str:
    line, time, books = job["line"], job["time"], job["books"]
    out = [
        "=" * 62,
        f"{job['shop'].upper()}  —  JOB ESTIMATE",
        "=" * 62,
        f"Customer:  {job['customer']}",
        f"Site:      {job['site']}",
        f"Date:      {job['when']}",
        f"Style:     {job['style'].replace('_', ' ').title()}   Height: {job['height']} ft",
        "-" * 62,
        f"Tape:          {line['tape_ft']} ft",
        f"Net run:       {line['net_ft']} ft",
        f"Gates:         {line['gate_count']}  {line['gate_widths']}",
        "-" * 62,
        "LEAVING THE YARD",
    ]
    for sku, qty in job["ticket"].items():
        out.append(f"  {sku.replace('_', ' '):<28} {qty}")
    out += [
        "-" * 62,
        f"Crew: {time['hours']} hrs, {time['hands']} hands, ~{time['days']} days",
        "-" * 62,
        f"Materials:   ${books['materials']:>10,.2f}",
        f"Labor:       ${books['labor']:>10,.2f}",
        f"Overhead:    ${books['overhead']:>10,.2f}",
        f"Profit:      ${books['profit']:>10,.2f}",
        "=" * 62,
        f"TOTAL:       ${books['total']:>10,.2f}",
        "=" * 62,
        "Good for 30 days. Deposit locks the date.",
    ]
    return "\n".join(out)


def stash(job: Dict, path: Optional[str] = None) -> str:
    text = print_the_job(job)
    if path is None:
        tag = "".join(c if c.isalnum() else "_" for c in job["customer"])
        path = f"quote_{tag}_{job['when']}.txt"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    return path


def _ask(prompt: str, default=None, cast=str):
    hint = f" [{default}]" if default is not None else ""
    raw = input(f"{prompt}{hint}: ").strip()
    if not raw and default is not None:
        return default
    try:
        return cast(raw)
    except ValueError:
        print(f"  skip — using {default}")
        return default


def _read_pair(label: str, kind: str) -> Tuple[float, float]:
    while True:
        raw = input(f"  {label}: ").strip()
        try:
            a, b = raw.split(",")
            return float(a), float(b)
        except ValueError:
            print(f"    format: {kind}")


def interactive() -> None:
    print("=" * 62)
    print("Walk the line. Price the job.")
    print("=" * 62)
    shop = _ask("Shop name on the quote", "Fence Estimate")
    customer = _ask("Customer")
    site = _ask("Site")
    style = _ask("Style  privacy / chain_link / vinyl", "privacy")
    height = _ask("Height ft", 6, float)
    mode = _ask("Points from  feet / satellite", "feet").lower()
    n = _ask("How many points", 4, int)
    if mode.startswith("s"):
        print("Each pin as lat,lon   example  30.158, -85.660")
        pins = [_read_pair(f"pin {i + 1}", "lat,lon") for i in range(n)]
        stakes = stakes_from_pins(pins)
        print("Local feet from first pin:")
        for i, s in enumerate(stakes):
            print(f"  stake {i}: {s}")
    else:
        print("Each stake as x,y in feet   example  0,0")
        stakes = [_read_pair(f"stake {i + 1}", "x,y") for i in range(n)]
    n_gates = _ask("How many gates", 0, int)
    openings: List[Opening] = []
    for i in range(n_gates):
        while True:
            raw = input(f"  gate {i + 1}  point_index,width_ft: ").strip()
            try:
                idx, w = raw.split(",")
                openings.append((int(idx), float(w)))
                break
            except ValueError:
                print("    index,width")
    rate = _ask("Crew $/hr", CREW_RATE, float)
    markup = _ask("Markup  0.30 = 30%", MARKUP, float)
    job = write_the_job(shop, customer, site, stakes, style, height, openings, rate, markup)
    if "error" in job:
        print(job["error"])
        return
    print()
    print(print_the_job(job))
    print(f"\nWrote {stash(job)}")


def demo() -> None:
    feet = [(0.0, 0.0), (120.0, 0.0), (120.0, 40.0), (200.0, 40.0)]
    openings = [(0, 4.0), (2, 10.0)]
    origin = (30.1765, -85.8059)
    pins = [
        origin,
        (30.1765, -85.8059 + 120 / 364000),
        (30.1765 + 40 / 364000, -85.8059 + 120 / 364000),
        (30.1765 + 40 / 364000, -85.8059 + 200 / 364000),
    ]
    print("--- local feet ---")
    job = write_the_job(
        "Gulf Coast Fence Co", "Marisol Vega", "1420 Oak Ridge Dr, Tampa FL",
        feet, "privacy", 6, openings, rate=50.0, markup=0.35,
    )
    print(print_the_job(job))
    stash(job)
    print()
    print("--- satellite pins ---")
    job = write_the_job_from_pins(
        "Gulf Coast Fence Co", "Marisol Vega", "1420 Oak Ridge Dr, Tampa FL",
        pins, "privacy", 6, openings, rate=50.0, markup=0.35,
    )
    print(print_the_job(job))
    stash(job)
    print()
    for style, height in (("chain_link", 4), ("vinyl", 6)):
        job = write_the_job(
            "Gulf Coast Fence Co", "Marisol Vega", "1420 Oak Ridge Dr, Tampa FL",
            feet, style, height, openings, rate=50.0, markup=0.35,
        )
        print(print_the_job(job))
        print()
        stash(job)
    print("Demo quotes written.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        interactive()
