#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import json
import math
import re
import time

import requests


def get_ad_archive_id(data):
    """
    Extract ad_archive_id from ad_snapshot_url
    """
    return re.search(r"/\?id=([0-9]+)", data["ad_snapshot_url"]).group(1)


class FbAdsLibraryTraversal:
    def __init__(
            self,
            access_token,
            fields,
            search_parameters,
            page_limit=2000,
            retry_limit=3,
            rate_limit=200,
    ):
        self.page_count = 0
        self.access_token = access_token
        self.fields = fields
        self.parameters = search_parameters
        self.page_limit = page_limit
        self.retry_limit = retry_limit
        self.rate_limit = rate_limit


    def generate_ad_archives(self):
        default_api_version = "v12.0"

        next_page_url = f"https://graph.facebook.com/{default_api_version}/ads_archive?access_token={self.access_token}&fields={self.fields}&limit={self.page_limit}"

        for param_name in self.parameters:
            param_value = self.parameters[param_name]
            next_page_url += f"&{param_name}={param_value}"

        return self._get_ad_archives_from_url(
            next_page_url=next_page_url, retry_limit=self.retry_limit, rate_limit=self.rate_limit
        )

    def _get_ad_archives_from_url(self,
            next_page_url, retry_limit=3, rate_limit=200
    ):
        last_error_url = None
        last_retry_count = 0
        sleep_time = math.ceil((60*60) / rate_limit)

        while next_page_url is not None:
            response = requests.get(next_page_url)
            response_data = json.loads(response.text)
            if "error" in response_data:
                if response_data["error"]["type"] == "OAuthException" and response_data["error"]["code"] == 190:
                    new_access_token = input("Token has expired, generate a new one and copy it in here:")
                    next_page_url = next_page_url.replace(self.access_token, new_access_token)
                    self.access_token = new_access_token

                if next_page_url == last_error_url:
                    # failed again
                    if last_retry_count >= retry_limit:
                        raise Exception(
                            "Error message: [{}], failed on URL: [{}]".format(
                                json.dumps(response_data["error"]), next_page_url
                            )
                        )
                else:
                    last_error_url = next_page_url
                    last_retry_count = 0
                last_retry_count += 1
                time.sleep(sleep_time)
                continue

            data = list(response_data["data"])
            if len(data) == 0:
                # there is no data
                next_page_url = None
                break
            yield data

            time.sleep(sleep_time)

            if "paging" in response_data:
                next_page_url = response_data["paging"]["next"]
            else:
                next_page_url = None

    def generate_ad_archives_from_url(self, failure_url):
        """
        if we failed from error, later we can just continue from the last failure url
        """
        return self._get_ad_archives_from_url(failure_url)