#!/usr/bin/env python
# -*- coding: utf-8 -*-
# geschreven voor python 2.7

import os

bestanden = os.listdir("/home/pieter/git/skdworp/_data/elo/c228/")
bestanden.sort()
maanden = {'01': 'januari', '04': 'april', '07': 'juli', '10': 'oktober'}
for n, bestand in enumerate(bestanden):
    jaar = bestand[4:8]
    maand = bestand[9:11]

    html_string = (
        "---\n"
        "title: elolijst {0} {1}\n"
        "datafile: elo_{1}_{2}\n"
        "rangschikking: {3}\n"
        "---\n"
        ).format(maanden[maand], jaar, maand, n)

    bestandsnaam = "{0}{1}.html".format(jaar[2:], maand)
    with open(bestandsnaam, 'w') as f:
        f.write(html_string)
