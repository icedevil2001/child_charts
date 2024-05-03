import re
import json
from pathlib import Path


# length 
# https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_girls_p_0_2.xlsx
# https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_girls_p_2_5.xlsx

# bmi
# https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/body-mass-index-for-age/tab_bmi_girls_p_0_2.xlsx
# https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/body-mass-index-for-age/tab_bmi_girls_p_2_5.xlsx

# head circumference
# https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/head-circumference-for-age/tab_hcfa_girls_p_0_5.xlsx

# weight for age
# https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/tab_wfa_girls_p_0_5.xlsx


tables = {
    "bmi": [
        "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/body-mass-index-for-age/tab_bmi_girls_p_0_2.xlsx",
        "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/body-mass-index-for-age/tab_bmi_girls_p_2_5.xlsx"

    ],
    "hc": [
        "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/head-circumference-for-age/tab_hcfa_girls_p_0_5.xlsx"
    ],

    "weight": [
        "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/tab_wfa_girls_p_0_5.xlsx"
    ],
    "height": [
        "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_girls_p_0_2.xlsx",
        "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_girls_p_2_5.xlsx"
    ]
}   

# def get_gender(url: str) -> str:
#     r = re.search(r'(girls|boys)', url)
#     if r:
#         return r.group(1)
#     raise ValueError(f"Gender not found from {url}")


def get_age_range(url: str) -> str:
    r = re.search(r'p_(\d+_\d+)', url)
    if r:
        return r.group(1)
    raise ValueError(f"Age not found from {url}")

# def get_metric(url: str) -> str:
#     r  = re.search(r'tab_(\w+)_', url)
#     if r:
#         return r.group(1)
#     raise ValueError(f"Metric not found from {url}")

def description_metric(url: str, metric) -> dict:
    age_range = get_age_range(url)
    description = {
        "bmi": f"WHO Growth Tables percentile for body mass index for age {age_range} years",
        "hc": f"WHO Growth Tables for head circumference for age {age_range} years",
        "weight": f"WHO Growth Tables for weight for age {age_range} years",
        "height": f"WHO Growth Tables for length/height for age {age_range} years"
    }
    return description[metric]

def get_metadata(url: str) -> dict:
    ## tab_bmi_girls_p_0_2.xlsx 
    filename = url.split('/')[-1]
    tab, metric, gender, *_ = filename.split('_')
    age_range = get_age_range(url)
    return {
        "metric": metric,
        "gender": gender,
        "age_range": age_range
    }

    

def build_dataset(tables: str) -> dict:
    data = []
    
    for metric, urls in tables.items():
        for url in urls:
            for gender in ['girls','boys']:
                url = url.replace('girls', gender)
                meta =  get_metadata(url)
                data.append({
                    "url": url,
                    "description": description_metric(url, metric)
                }|meta)
    return data

def main():
    base_path = Path(__file__).parent   
    data = build_dataset(tables)
    with open(base_path/ 'WHO_growth_tables.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()
    
