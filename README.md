# Meta-ad-library-API-Python
This is a more versatile fork from https://github.com/facebookresearch/Ad-Library-API-Script-Repository
allowing the user to write the url parameters into the CLI args,
and so when Meta updates their API, the user can change their parameters without needing new python code to be developed to handle that

To run look at this example:
```shell
python fb_ads_library_api_cli.py -t <token> -f "id,ad_creation_time,ad_creative_bodies" -p "search_terms=<YOUR SEARCH TERM>&ad_reached_countries=<CA>&ad_active_status=ALL&ad_delivery_date_max=<date until>" save_to_csv output.csv 
```
