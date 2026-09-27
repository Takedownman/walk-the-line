# walk-the-line

https://walk-the-line-oedkeafud8tqreunvmrx8b.streamlit.app/

Walk the line. Count the posts. Price the job.

A field estimator for fence work. Stake a property line in local feet or drop pins off a satellite map, mark the gates, and get a materials ticket, crew hours, and a priced quote. Privacy, chain-link, or vinyl.

The engine is one Python file and uses only the standard library. The Streamlit page is a thin face on that engine so the same math can run in a browser.

It does **not** stream live satellite video. Satellite mode is map clicks → latitude/longitude → local feet. That is how commercial takeoff tools work.

## Features

- Tape a run from ordered points (`x,y` in feet or `lat,lon` from a map)
- Subtract gate openings from net length
- Build a yard ticket: posts, rails, concrete, brackets, screws
- Add style-specific material: pickets, chain-link fabric, or vinyl panels
- Estimate crew hours from a feet-per-hour pace
- Price materials, labor, overhead, and markup
- Print a quote you can save and send
- Swap the shop name so any company can put it on the page

## Repo layout
walk-the-line/
├── fence_estimator.py    engine + terminal app
├── streamlit_app.py      browser UI
├── requirements.txt      streamlit
└── README.md
text## Requirements

- Python 3.10 or newer
- Terminal app: nothing else
- Browser app: `streamlit`

```bash
pip install -r requirements.txt
 contains:
textstreamlit>=1.32.0
Run the terminal app
Bashpython fence_estimator.py
python fence_estimator.py demo
Interactive prompts:

Shop name on the quote
Customer
Site
Style — privacy / chain_link / vinyl
Height in feet
Points from — feet or satellite
Each point
Gates as point_index,width_ft (index 0 is the first point)
Crew dollars per hour
Markup (0.30 is 30%)

Feet mode — one x,y per point. First stake is usually 0,0.
text0,0
120,0
120,40
200,40
Satellite mode — one lat,lon per point. In Google Maps, right-click a corner and copy the coordinates.
text30.1765,-85.8059
30.1765,-85.8053
30.1766,-85.8053
30.1766,-85.8049
Gates
text0,4
2,10
That is a 4 ft gate on the first point and a 10 ft gate on the third point.
The quote is printed in the terminal and written to quote_<customer>_<date>.txt.
Run the browser app
Bashstreamlit run streamlit_app.py
Same inputs, form layout. Button is Write the job. The quote, tape, net run, and total show on the page.
Deploy a live demo

Push this repo to GitHub.
Open https://share.streamlit.io and sign in with GitHub.
New app → this repository → main file .
Deploy.

You get a public URL you can put on a resume or send to a shop.
How the math works

walk_the_line sums segment lengths between stakes and subtracts gate widths.
pull_the_ticket places a post every 8 ft (change POST_EVERY), two rails per span, two bags of concrete per hole, then style extras.
crew_time divides net feet by a pace table (PACE).
settle_the_books applies supplier costs (YARD), labor rate, overhead, and markup.

Satellite pins are flattened first:

First pin is origin (0, 0)
Later pins become east/north feet with a great-circle span (span_ft)
Those local stakes go into walk_the_line unchanged

On a flat lot this is usually within a couple percent of a wheel tape. Trees, overhangs, and sloppy clicks are the real error. Walk the line once before you order material.
Tune it to a real shop
Edit the top of :








































NameMeaningDefaultYARDWhat the supplier chargesplaceholder dollarsPACENet feet a two-person crew hangs per hour15 / 25 / 12POST_EVERYPost spacing8 ftCREW_RATEDollars per crew hour45MARKUPProfit on subtotal + overhead0.30OVERHEADBurden on materials + labor0.10
Change those before a real quote. The shipped numbers are placeholders, not a bid.
Privacy picket count assumes a 5.5 in slat and about 1 in gap (~6.5 in on center). Adjust that line in pull_the_ticket if the shop hangs a different pattern.
Quote page

Shop name you type in
Customer, site, date
Style and height
Tape and net run
What leaves the yard
Crew hours and headcount
Materials, labor, overhead, profit, total
Good for 30 days. Deposit locks the date.

No login. No vendor lock.
What this is not

Not a CAD or survey instrument
Not a substitute for walking a government site before you order
Not connected to accounting, invoicing, or dispatch
Not a live satellite feed

Those can sit on top of this engine later. The engine stays small on purpose.
License
Use it, fork it, put a shop name on the quote. Keep the price book honest.
textGitHub repo subtitle:

`Walk the line. Count the posts. Price the job. Takeoff from feet or satellite pins — privacy, chain-link, or
