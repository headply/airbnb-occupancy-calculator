#!/usr/bin/env python3
"""Airbnb occupancy, ADR, RevPAR and revenue for a market: per-listing CSV plus a market summary."""
import argparse, csv, json, os, sys
from apify_client import ApifyClient

def run_actor(actor, run_input):
    """Run an Apify Actor and return its dataset items. Needs APIFY_TOKEN in the environment."""
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first (free account: https://console.apify.com/sign-up, "
                 "token: https://console.apify.com/settings/integrations).")
    client = ApifyClient(token)
    print(f"Running {actor} ...", file=sys.stderr)
    run = client.actor(actor).call(run_input=run_input)
    # apify-client 3.x returns a Run object, older versions a dict
    field = lambda snake, camel: (run.get(camel) if isinstance(run, dict) else getattr(run, snake, None)) if run else None
    status = getattr(field("status", "status"), "value", field("status", "status"))
    if status != "SUCCEEDED":
        sys.exit(f"Run did not succeed: {status}. Open https://console.apify.com/actors/runs for the log.")
    return list(client.dataset(field("default_dataset_id", "defaultDatasetId")).iterate_items())


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}", file=sys.stderr)

import statistics


def pct(values, q):
    v = sorted(x for x in values if x is not None)
    return v[min(len(v) - 1, int(q * len(v)))] if v else None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("location", help='e.g. "Nashville, Tennessee"')
    p.add_argument("--max-listings", type=int, default=100)
    p.add_argument("--out", default="occupancy.csv")
    a = p.parse_args()
    items = run_actor("headply/airbnb-occupancy-revenue-estimator",
                      {"search": [a.location], "maxListings": a.max_listings, "includeOccupancy": True})
    rows = []
    for it in items:
        o = it.get("occupancy") or {}
        d30, d365 = o.get("next30Days") or {}, o.get("next365Days") or {}
        rows.append({"name": it.get("name"), "url": it.get("url"), "roomInfo": it.get("roomInfo"), "rating": it.get("rating"),
                     "reviews": it.get("reviewsCount"), "adr": o.get("adr"), "occupancy30d": d30.get("occupancyPct"),
                     "occupancy365d": d365.get("occupancyPct"), "revpar365d": d365.get("revpar"),
                     "revenue365d": d365.get("estimatedRevenue"), "confidence": o.get("confidence")})
    write_csv(a.out, rows, list(rows[0]) if rows else ["name"])
    adr = [r["adr"] for r in rows]; occ = [r["occupancy365d"] for r in rows]; rev = [r["revenue365d"] for r in rows]
    if rows:
        print(f"\n{a.location}: {len(rows)} listings")
        print(f"  median ADR            ${statistics.median([x for x in adr if x] or [0]):,.0f}")
        print(f"  median occupancy 365d {statistics.median([x for x in occ if x is not None] or [0]):.1f}%")
        print(f"  revenue 365d  p25 ${pct(rev, .25) or 0:,.0f}   median ${pct(rev, .5) or 0:,.0f}   p75 ${pct(rev, .75) or 0:,.0f}")


if __name__ == "__main__":
    main()
