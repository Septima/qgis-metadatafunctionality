# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : 2016-06-23
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Septima P/S
        email                : stephan@septima.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import urllib
import urllib2
import json


class TaxonClassifier(object):
    """ Class that talks to a Taxon Classifier backend """

    def __init__(self, url, taxonomy):
        self.url = url
        self.taxonomy = taxonomy

    def __str__(self):
        'TaxonClassifier - url: {url} - taxonomy: {taxonomy}'.format(
            url=self.url,
            taxonomy=self.taxonomy
        )

    def get(self, text):
        data = urllib.urlencode(
            {
                'taxonomy': self.taxonomy,
                'text': text
            },
            'utf-8'
        )
        response = urllib2.urlopen(
            urllib2.Request(self.url, data)
        ).read()

        if response.strip() == 'No result':
            return None

        return self._parse_response(json.loads(response))

    def _parse_response(self, response):
        parsed_response = []

        for elem in response:
            parsed_response.append(
                {
                    'kle': elem,
                    'title': response[elem]['title']
                }
            )

        return parsed_response
