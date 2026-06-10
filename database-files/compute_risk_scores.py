#!/usr/bin/env python3
"""
Calculates percentile-based risk scores for all 27 EU countries using 2023 data rom terra_db.sql.

run: python database-files/compute_risk_scores.py
"""

# ── 2023 data from country_year_data in terra_db.sql
# (country_id, country_name, heatwave_days, dry_days, precip_days_heavy, asylum_applications, population, gdp_per_capita)

countries = [
    ( 1, 'Austria',        0,  245,  4,   59230,   9131761,  56579.50),
    ( 2, 'Belgium',        0,  197,  2,   35225,  11779946,  55291.48),
    ( 3, 'Bulgaria',       0,  251,  7,   22510,   6446596,  15853.21),
    ( 4, 'Cyprus',        29,  303,  1,   11910,   1344976,  36623.69),
    ( 5, 'Czechia',        0,  215,  3,    1405,  10864042,  31761.59),
    ( 6, 'Germany',        0,  216,  3,  351600,  83287273,  54776.77),
    ( 7, 'Denmark',        0,  221,  4,    2480,   5946952,  68043.55),
    ( 8, 'Estonia',        0,  197,  4,    3985,   1370286,  30264.01),
    ( 9, 'Spain',         19,  300,  5,  162435,  48352528,  33493.22),
    (10, 'Finland',        0,  214,  3,    5355,   5583911,  52834.29),
    (11, 'France',         0,  219,  7,  167055,  68372286,  44700.14),
    (12, 'Greece',        23,  285,  7,   64230,  10407351,  23343.71),
    (13, 'Croatia',        0,  239, 16,    1750,   3859686,  22184.23),
    (14, 'Hungary',        0,  235,  9,      30,   9592186,  22230.63),
    (15, 'Ireland',        0,  193,  7,   13275,   5311538, 106818.92),
    (16, 'Italy',          5,  246,  9,  135820,  58984216,  39277.08),
    (17, 'Lithuania',      0,  209,  2,     575,   2871585,  27786.01),
    (18, 'Luxembourg',     0,  201,  1,    2685,    666430, 133230.62),
    (19, 'Latvia',         0,  198,  2,    1700,   1883710,  22710.26),
    (20, 'Malta',         10,  308,  1,     855,    552747,  40905.81),
    (21, 'Netherlands',    0,  172,  7,   39755,  17877117,  63515.60),
    (22, 'Poland',         0,  211,  2,    9495,  36687353,  22145.27),
    (23, 'Portugal',       0,  299,  3,    2695,  10578174,  27634.62),
    (24, 'Romania',        1,  268,  3,   10095,  19061062,  18244.42),
    (25, 'Sweden',         0,  227,  1,   17040,  10536632,  54950.28),
    (26, 'Slovenia',       0,  231, 28,    7260,   2120461,  32660.48),
    (27, 'Slovakia',       0,  240,  5,     415,   5426740,  24614.87),
]

# raw value
for c in countries:
    c_id, name, hw, dry, precip, asylum, pop, gdp = c
    countries[countries.index(c)] = {
        'country_id':    c_id,
        'name':          name,
        'climate_raw':   hw + dry + precip,
        'asylum_rate':   asylum / pop,
        'vulnerability': 1 / gdp,
    }

# percentile rank
def percentile_rank(values, target):
    below = sum(1 for v in values if v < target)
    return (below / (len(values) - 1)) * 100

climate_vals = [c['climate_raw']   for c in countries]
asylum_vals  = [c['asylum_rate']   for c in countries]
vuln_vals    = [c['vulnerability'] for c in countries]

# score + level
def get_level(score):
    if score <= 25:   return 'Low'
    elif score <= 50: return 'Moderate'
    elif score <= 75: return 'High'
    else:             return 'Critical'

print(f"\n{'Country':<20} {'Climate':>8} {'Asylum':>8} {'Vuln':>8} {'Score':>8} {'Level'}")
print("-" * 65)

inserts = []
for c in countries:
    cp = percentile_rank(climate_vals, c['climate_raw'])
    ap = percentile_rank(asylum_vals,  c['asylum_rate'])
    vp = percentile_rank(vuln_vals,    c['vulnerability'])

    score = round((cp + ap + vp) / 3, 2)
    level = get_level(score)
    notes = f"climate={cp:.1f}, asylum={ap:.1f}, vulnerability={vp:.1f}"

    print(f"{c['name']:<20} {cp:>8.1f} {ap:>8.1f} {vp:>8.1f} {score:>8.1f} {level}")

    inserts.append(
        f"    ({c['country_id']}, 2023, {score}, '{level}', 'percentile', '{notes}')"
    )