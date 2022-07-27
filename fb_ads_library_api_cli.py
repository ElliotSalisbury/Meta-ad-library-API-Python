#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import sys

from fb_ads_library_api import FbAdsLibraryTraversal
from fb_ads_library_api_operators import get_operators, save_to_csv

def get_parser():
    parser = argparse.ArgumentParser(
        description="The Facebook Ads Library API CLI Utility"
    )
    parser.add_argument(
        "-t",
        "--access-token",
        help="The Facebook developer access token",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--fields",
        help="Fields to retrieve from the Ad Library API",
        default="id,ad_creation_time,ad_creative_bodies,ad_creative_link_captions,ad_creative_link_titles,ad_creative_link_descriptions,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,bylines,currency,delivery_by_region,demographic_distribution,estimated_audience_size,impressions,page_id,page_name,publisher_platforms,spend",
        type=validate_fields_param,
    )
    parser.add_argument(
        "-p",
        "--parameters",
        help="search parameters to filter the results from the Ad Library API",
        required=True,
        type=validate_parameters_param,
    )
    parser.add_argument("--batch-size", type=int, help="Batch size")
    parser.add_argument(
        "--retry-limit",
        type=int,
        help="When an error occurs, the script will abort if it fails to get the same batch this amount of times",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        help="How many requests per hour can be made on this token",
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    actions = ",".join(get_operators().keys())
    parser.add_argument(
        "action", help="Action to take on the ads, possible values: %s" % actions
    )
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="The parameter for the specific action"
    )
    return parser


def validate_country_param(country_input):
    if not country_input:
        return ""
    country_codes = list(filter(lambda x: x.strip(), country_input.split(",")))

    return ",".join(country_codes)


def validate_fields_param(fields_input):
    if not fields_input:
        return False
    fields_list = list(
        filter(lambda x: x, map(lambda x: x.strip(), fields_input.split(",")))
    )
    if not fields_list:
        raise argparse.ArgumentTypeError("Fields cannot be empty")
    return ",".join(fields_list)

def validate_parameters_param(fields_input):
    if not fields_input:
        return False

    fields_dict = {p[0]:p[1] for p in [p_pair.split("=") for p_pair in fields_input.split("&")]}

    if not fields_dict:
        raise argparse.ArgumentTypeError("parameters cannot be empty")
    return fields_dict

def main():
    parser = get_parser()
    opts = parser.parse_args()

    api = FbAdsLibraryTraversal(opts.access_token, opts.fields, opts.parameters)

    if opts.retry_limit:
        api.retry_limit = opts.retry_limit
    if opts.rate_limit:
        api.rate_limit = opts.rate_limit

    generator_ad_archives = api.generate_ad_archives()
    if opts.action in get_operators():
        if opts.action == "save_to_csv":
            save_to_csv(
                generator_ad_archives, opts.args, opts.fields, is_verbose=opts.verbose
            )
        else:
            get_operators()[opts.action](
                generator_ad_archives, opts.args, is_verbose=opts.verbose
            )
    else:
        print("Invalid 'action' value: %s" % opts.action)
        sys.exit(1)


if __name__ == "__main__":
    main()