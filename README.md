## What it does

A Python dashboard built on Refinitiv's Eikon Data API that shows where a company's
ESG score actually sits relative to its peers. You enter a company (by RIC, e.g.
`BMWG.DE`), choose whether to benchmark against its industry or its home country,
and pick which score to look at — ESG Combined, ESG, or the Environmental, Social,
and Governance pillars individually. The app returns the company's absolute score,
its percentile position within that peer group, and a bar chart of every peer sorted
by score with the selected company highlighted in red.

It also lets you build your own composite: enter custom weights for E, S, and G and
the app recomputes a weighted score, so you can weight the pillars according to what
you actually care about rather than accepting the vendor's weighting.

## Approach

For a given company, the app pulls its identity and classification (common name,
TRBC industry, headquarters country) along with all five ESG scores. It then uses
Refinitiv `SCREEN()` expressions to pull the same score for every public equity
sharing that company's industry or country, producing the peer set.

Peer scores are sorted, missing values filtered out, and the target company's rank
located within the sorted list — giving both a percentile and a peer-group mean.
The sorted bar chart with a single highlighted bar was the core design decision:
a raw score of 68 is meaningless on its own, but seeing exactly where that bar falls
in a distribution of several hundred peers communicates the same information without
the user needing to interpret a number at all.

Peer companies are fetched at startup with deliberate delays between requests, since
the API rate-limits bulk score retrieval.

## Stack

Python · Refinitiv Eikon Data API · Dash + dash-bootstrap-components · Plotly · pandas · NumPy

## Notes

Built in a hackathon over a short time period. This is prototype-quality code —>
a single `main.py`, no tests, no error handling and three hardcoded companies loaded 
at startup because the API was too slow to fetch peer sets on demand.
Kept public as a record of the project rather than as an example of production work.