# Airbnb occupancy & revenue calculator (AirDNA alternative, pay per use)

Give it a city and get **occupancy rate, ADR, RevPAR and 30/90/365-day revenue for every Airbnb listing**,
computed from the live availability calendar, plus a market summary. No monthly subscription.

```bash
pip install -r requirements.txt
export APIFY_TOKEN=...        # free account: https://console.apify.com/sign-up
python occupancy.py "Nashville, Tennessee" --max-listings 200
```

### Sample (real run, Nashville)

| listing | ADR | occupancy 30d | occupancy 365d | revenue 365d |
|---|---|---|---|---|
| Ultimate Retreat! Glam Bar, Broadway | $365 | 96.7% | 64.8% | $81,440 |
| Luxury Rooftop Retreat - Hot Tub | $492 | 80.0% | 42.4% | $71,832 |
| Luxe Home w/ Hot Tub, Grill & Rooftop | $400 | 73.3% | 20.9% | $28,814 |
| The NashNest | $300 | 46.7% | 24.4% | $25,234 |

```
Nashville, Tennessee: 12 listings
  median ADR            $305
  median occupancy 365d 20.0%
  revenue 365d  p25 $7,411   median $19,011   p75 $43,800
```

## How accurate is it?

A calendar shows a night as unavailable but not whether a guest booked it or the host blocked it. The first
scan counts unavailable nights as demand (the standard single-scan method). **Re-run the same market weekly**
and the Actor separates real bookings from host blocks (`confidence` moves from `single-snapshot` to history-based).

## How it works

Runs the [Airbnb Occupancy & Revenue Estimator](https://apify.com/headply/airbnb-occupancy-revenue-estimator) on Apify:
about **$10 for a 1,000-listing market** including occupancy. Also available:
[Airbnb Scraper](https://apify.com/headply/airbnb-scraper) (listings + 12-month calendar),
[Vrbo Scraper](https://apify.com/headply/vrbo-scraper), and [Airbnb & Vrbo in one run](https://apify.com/headply/airbnb-vrbo-scraper).

MIT licensed.
