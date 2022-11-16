import datetime
import os
import sys
import subprocess
from pathlib import Path

from dateutil import rrule
from dateutil.relativedelta import relativedelta

from fb_ads_library_api import FbAdsLibraryTraversal
from fb_ads_library_api_operators import save_to_csv

country_code = "CA"

token = "REPLACE WITH YOUR TOKEN"
fields = "id,ad_creation_time,ad_creative_bodies,ad_creative_link_titles,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,page_id,page_name,publisher_platforms"
static_search_params = f"search_terms=.&ad_reached_countries={country_code}&ad_active_status=ALL&"

start_date = datetime.datetime(2018,6,1)
end_date = datetime.datetime(2022,10,1)
for search_dt_start in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
    output_file = Path(f"api_search/{country_code}/{search_dt_start:%Y_%m_%d}.csv")

    if output_file.exists():
        continue
    output_file.parent.mkdir(parents=True, exist_ok=True)


    search_dt_end = search_dt_start + relativedelta(months=1)
    print(f"{search_dt_start} - {search_dt_end}")

    new_params = f"ad_delivery_date_min={search_dt_start:%Y-%m-%d}"

    if search_dt_end < datetime.datetime.now():
        new_params += f"&ad_delivery_date_max={search_dt_end:%Y-%m-%d}"
    else:
        search_dt_end = datetime.datetime.now()
        new_params += f"&ad_delivery_date_max={search_dt_end:%Y-%m-%d}"
        output_file = output_file.parent / f"{search_dt_start:%Y_%m_%d}_incomplete.csv"

    full_params = static_search_params + new_params
    parms_dict = {p[0]:p[1] for p in [p_pair.split("=") for p_pair in full_params.split("&")]}

    api = FbAdsLibraryTraversal(token, fields, parms_dict)
    generator_ad_archives = api.generate_ad_archives()
    save_to_csv(generator_ad_archives, [output_file, ], fields)

    token = api.access_token