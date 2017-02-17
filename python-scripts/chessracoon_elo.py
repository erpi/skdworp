#!/usr/bin/env python
# -*- coding: utf-8 -*-
# geschreven voor python 2.7

import argparse
import urllib2
import json
import time
import os


stamnummer = 228
url_json = "http://chessraccoon.skoudegod.be/getplayers.php?f=json&c={0}".format(stamnummer)
cur_dir = os.path.abspath(os.curdir)
elo_dir = os.path.join(cur_dir, "..", "_data", "elo", str(stamnummer))
elo_dir = os.path.normpath(elo_dir)
try:
    os.makedirs(elo_dir)
except OSError:
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="download elo-gegevens via http://chessraccoon.skoudegod.be/")
    parser.add_argument("-m", "--maand", type=int, choices=[1, 7],
        help="maand van publicatie, '1' voor januari (standaard) en '7' voor juli")
    parser.add_argument("-j", "--jaar", type=int,
        help="jaartal voor elo (2 cijfers), bv. 93")
    parser.add_argument("-c", "--club", type=int,
        help="stamnummer van de club, standaard is 228")
    parser.add_argument("-a", "--alles", action="store_true",
        help="download alle jaren")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="geef ook output in de console")
    args = parser.parse_args()

    for jaar in range(1989, 2017):
        for maand in ("01", "04", "07", "10"):
            # 2 publicaties per jaar vanaf juli 1990
            # 4 publicaties per jaar vanaf oktober 2013
            if jaar < 2013:
                if maand in ("04", "10"):
                    continue
                if jaar == 1989 and maand == "07":
                    continue
            elif jaar == 2013 and maand == "04":
                continue
            url = url_json + "&p={0}{1}".format(str(jaar)[-2:], maand)
            print url
            page = urllib2.urlopen(url)
            json_data = page.read()
            page.close()
            if json_data:
                bestandsnaam = os.path.join(elo_dir, "elo_{0}_{1}.json".format(jaar, maand))
                with open(bestandsnaam, "w") as f:
                    f.write(json_data)
                print bestandsnaam, "okay!"
            # we proberen vriendelijk te zijn voor 'de overkant'
            time.sleep(10)
