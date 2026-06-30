"""
LinkedIn location data — countries and cities with geoIds.
geoId is LinkedIn's internal numeric location identifier.

⚠️  IMPORTANT — GeoID Reliability:
LinkedIn's guest API (jobs-guest) is primarily designed for US/UK markets.
For other regions, even with the correct geoId, the API may return irrelevant
results or fall back to a default region.

Reliability tiers:
  ✅ RELIABLE   — guest API works consistently (US, UK, Canada, Australia)
  ⚠️ PARTIAL    — works sometimes, may return mixed/wrong results (Europe, India, Gulf)
  ❌ UNRELIABLE — guest API largely ignores geoId, returns default region results

To find the CORRECT geoId for any location:
    python find_geoid.py "Pakistan"
    python find_geoid.py "Karachi"

Or manually:
    1. Open linkedin.com/jobs in Chrome
    2. Open DevTools → Network tab
    3. Search for jobs with your location selected
    4. Find the seeMoreJobPostings request → check the geoId param
"""

# Reliability markers per region — shown in the UI
RELIABILITY = {
    "Remote / Worldwide":   "✅",
    "United States":        "✅",
    "Canada":               "✅",
    "United Kingdom":       "✅",
    "Australia":            "✅",
    "Germany":              "⚠️",
    "Netherlands":          "⚠️",
    "France":               "⚠️",
    "Spain":                "⚠️",
    "Sweden":               "⚠️",
    "Switzerland":          "⚠️",
    "India":                "❌",
    "Singapore":            "⚠️",
    "Japan":                "⚠️",
    "South Korea":          "⚠️",
    "Brazil":               "⚠️",
    "Saudi Arabia":         "❌",   # tested — returns UK jobs
    "United Arab Emirates": "❌",   # same guest API limitation as Saudi Arabia
    "Qatar":                "❌",
    "Kuwait":               "❌",
    "Bahrain":              "❌",
    "Oman":                 "❌",
    "Jordan":               "❌",
    "Egypt":                "❌",
    "Turkey":               "⚠️",
    "Pakistan":             "❌",
    "Bangladesh":           "❌",
    "Sri Lanka":            "❌",
    "Nigeria":              "❌",
    "South Africa":         "❌",
    "Kenya":                "❌",
    "Malaysia":             "❌",
    "Philippines":          "❌",
}

RELIABILITY_NOTES = {
    "✅": "Guest API works reliably for this region.",
    "⚠️": "Results may include jobs from other countries. Verify geoId with find_geoid.py",
    "❌": "LinkedIn's guest API does not reliably support this region. Results will likely show jobs from US/UK instead. Use LinkedIn directly or a paid API.",
}

# Structure:
# LOCATIONS = {
#   "Country Name": {
#       "geoId": "...",          ← country-level geoId
#       "cities": {
#           "City Name": "...",  ← city-level geoId
#       }
#   }
# }
# ⚠️ GeoIds below are estimates — verify with: python find_geoid.py <location>

LOCATIONS = {

    # ── Special ───────────────────────────────────────────────────────────────
    "Remote / Worldwide": {
        "geoId": "",
        "cities": {},
    },

    # ── Middle East ───────────────────────────────────────────────────────────
    "Saudi Arabia": {
        "geoId": "101004847",
        "cities": {
            "Riyadh":       "105149807",
            "Jeddah":       "100546951",
            "Dammam":       "105921779",
            "Khobar":       "106639368",
            "Mecca":        "106691643",
            "Medina":       "105938570",
            "Tabuk":        "102229900",
            "Abha":         "107282234",
        },
    },
    "United Arab Emirates": {
        "geoId": "104305776",
        "cities": {
            "Dubai":        "106204383",
            "Abu Dhabi":    "101282772",
            "Sharjah":      "107097761",
            "Ajman":        "106546120",
            "Ras Al Khaimah": "106778479",
        },
    },
    "Qatar": {
        "geoId": "104813976",
        "cities": {
            "Doha":         "103990839",
        },
    },
    "Kuwait": {
        "geoId": "104516386",
        "cities": {
            "Kuwait City":  "105025874",
        },
    },
    "Bahrain": {
        "geoId": "100565514",
        "cities": {
            "Manama":       "104093773",
        },
    },
    "Oman": {
        "geoId": "102106391",
        "cities": {
            "Muscat":       "100363460",
        },
    },
    "Jordan": {
        "geoId": "101404627",
        "cities": {
            "Amman":        "103999498",
        },
    },
    "Egypt": {
        "geoId": "106139199",
        "cities": {
            "Cairo":        "104438076",
            "Alexandria":   "105014779",
            "Giza":         "106568682",
        },
    },
    "Turkey": {
        "geoId": "102105699",
        "cities": {
            "Istanbul":     "102988579",
            "Ankara":       "105717861",
            "Izmir":        "105814812",
        },
    },

    # ── South Asia ────────────────────────────────────────────────────────────
    "India": {
        "geoId": "102713980",
        "cities": {
            "Bangalore":    "105214831",
            "Mumbai":       "103781685",
            "Delhi":        "102713980",
            "Hyderabad":    "105556991",
            "Chennai":      "106087591",
            "Pune":         "106686106",
            "Kolkata":      "103035651",
            "Ahmedabad":    "103976443",
            "Noida":        "105214831",
            "Gurgaon":      "107290979",
        },
    },
    "Pakistan": {
        "geoId": "100600279",
        "cities": {
            "Karachi":      "104539711",
            "Lahore":       "104970196",
            "Islamabad":    "106191369",
            "Rawalpindi":   "106588359",
            "Faisalabad":   "106023698",
        },
    },
    "Bangladesh": {
        "geoId": "100547484",
        "cities": {
            "Dhaka":        "102986280",
            "Chittagong":   "105779666",
        },
    },
    "Sri Lanka": {
        "geoId": "101007782",
        "cities": {
            "Colombo":      "103043085",
        },
    },

    # ── Americas ──────────────────────────────────────────────────────────────
    "United States": {
        "geoId": "103644278",
        "cities": {
            "New York":         "105080838",
            "San Francisco":    "102277331",
            "Los Angeles":      "102448103",
            "Seattle":          "103809590",
            "Austin":           "104900716",
            "Chicago":          "103112676",
            "Boston":           "101002888",
            "Denver":           "104793856",
            "Atlanta":          "103573859",
            "Miami":            "104026800",
            "Washington DC":    "103997265",
            "Dallas":           "103644278",
            "Houston":          "100364959",
            "San Diego":        "103733491",
            "Portland":         "101862928",
        },
    },
    "Canada": {
        "geoId": "101174742",
        "cities": {
            "Toronto":      "100025096",
            "Vancouver":    "103366113",
            "Montreal":     "104311334",
            "Calgary":      "101929798",
            "Ottawa":       "101209775",
        },
    },
    "Brazil": {
        "geoId": "106057199",
        "cities": {
            "São Paulo":    "101294013",
            "Rio de Janeiro": "103988788",
            "Brasília":     "102454768",
        },
    },

    # ── Europe ────────────────────────────────────────────────────────────────
    "United Kingdom": {
        "geoId": "101165590",
        "cities": {
            "London":       "102257491",
            "Manchester":   "103735049",
            "Birmingham":   "102106047",
            "Edinburgh":    "104361854",
            "Bristol":      "104361887",
            "Leeds":        "100943803",
        },
    },
    "Germany": {
        "geoId": "101282230",
        "cities": {
            "Berlin":       "103035651",
            "Munich":       "104160803",
            "Hamburg":      "104660867",
            "Frankfurt":    "106389649",
            "Cologne":      "103035651",
        },
    },
    "Netherlands": {
        "geoId": "102890719",
        "cities": {
            "Amsterdam":    "102011674",
            "Rotterdam":    "100062277",
            "The Hague":    "104115440",
            "Utrecht":      "103025561",
        },
    },
    "France": {
        "geoId": "105015875",
        "cities": {
            "Paris":        "104246759",
            "Lyon":         "107784645",
            "Marseille":    "107228773",
        },
    },
    "Spain": {
        "geoId": "105646813",
        "cities": {
            "Madrid":       "100994331",
            "Barcelona":    "100994331",
            "Valencia":     "104438132",
        },
    },
    "Sweden": {
        "geoId": "105117694",
        "cities": {
            "Stockholm":    "106748339",
            "Gothenburg":   "104362988",
            "Malmö":        "102974008",
        },
    },
    "Switzerland": {
        "geoId": "106693272",
        "cities": {
            "Zurich":       "104113680",
            "Geneva":       "103773018",
            "Basel":        "103694623",
        },
    },

    # ── East & Southeast Asia ─────────────────────────────────────────────────
    "Singapore": {
        "geoId": "102454443",
        "cities": {
            "Singapore":    "102454443",
        },
    },
    "Australia": {
        "geoId": "101452733",
        "cities": {
            "Sydney":       "104769905",
            "Melbourne":    "101356218",
            "Brisbane":     "103999338",
            "Perth":        "106295941",
        },
    },
    "Japan": {
        "geoId": "101355337",
        "cities": {
            "Tokyo":        "103873803",
            "Osaka":        "104553297",
        },
    },
    "Malaysia": {
        "geoId": "102454932",
        "cities": {
            "Kuala Lumpur": "102747807",
            "Petaling Jaya": "102747807",
        },
    },
    "Philippines": {
        "geoId": "103121230",
        "cities": {
            "Manila":       "103995865",
            "Cebu":         "101975059",
        },
    },
    "South Korea": {
        "geoId": "105149562",
        "cities": {
            "Seoul":        "100463598",
            "Busan":        "100513609",
        },
    },

    # ── Africa ────────────────────────────────────────────────────────────────
    "Nigeria": {
        "geoId": "101331766",
        "cities": {
            "Lagos":        "103916066",
            "Abuja":        "101358378",
        },
    },
    "South Africa": {
        "geoId": "104035573",
        "cities": {
            "Johannesburg": "102140673",
            "Cape Town":    "102140678",
            "Durban":       "104479061",
        },
    },
    "Kenya": {
        "geoId": "101686862",
        "cities": {
            "Nairobi":      "105973754",
        },
    },
}


def get_reliability(country: str) -> str:
    """Returns reliability emoji for a country (✅ / ⚠️ / ❌)."""
    return RELIABILITY.get(country, "⚠️")


def get_reliability_note(country: str) -> str:
    """Returns a human-readable note about this region's reliability."""
    emoji = get_reliability(country)
    return RELIABILITY_NOTES.get(emoji, "")


def get_geo_id(country: str, city: str = "") -> str:
    """
    Return the best geoId for a country + optional city combination.
    Falls back to country geoId if city is not found.
    """
    country_data = LOCATIONS.get(country, {})
    if city and city in country_data.get("cities", {}):
        return country_data["cities"][city]
    return country_data.get("geoId", "")


def get_location_string(country: str, city: str = "") -> str:
    """
    Build the location string to send to LinkedIn's API.
    e.g. "Riyadh, Saudi Arabia" or just "Saudi Arabia"
    """
    if country == "Remote / Worldwide":
        return "Remote"
    if city:
        return f"{city}, {country}"
    return country


def all_countries() -> list[str]:
    return list(LOCATIONS.keys())


def cities_for(country: str) -> list[str]:
    return list(LOCATIONS.get(country, {}).get("cities", {}).keys())
