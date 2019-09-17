# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : 2016-04-04
        copyright            : (C) 2016 Septima P/S
        email                : asger@septima.dk
        git sha              : $Format:%H$
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

from __future__ import unicode_literals
import configparser
import codecs
import os

metadata = None


def plugin_metadata():
    global metadata
    if metadata is None:
        config = configparser.ConfigParser()
        config.readfp(
            codecs.open(
                os.path.join(
                    os.path.dirname(__file__).replace("\\", "/"),
                    os.pardir,
                    'metadata.txt',
                ),
                'r',
                'utf8'
            )
        )
        metadata = dict(config.items('general'))
    return metadata

if __name__ == '__main__':
    print(plugin_metadata())
