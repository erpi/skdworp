#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# geschreven voor python 3

# Script zet uitslagen van Sevilla van het 'Open Rapid Tornooi' om in
# de juiste csv-bestanden voor de website.

# In Sevilla 'Rapporten'-->'XML/JSON-dump' kiezen om json-bestand aan te maken.
# Bij 'Rangsch.rondes', 'Periode rangsch.' en 'Speler histories' 'Geen' zetten.
# Bij 'Ronde histories' moet 'Alle ronden' komen
# Rechts 'XML" veranderen in 'JSON'

# Ronden die op dezelfde avond gespeeld worden moeten dezelfde datum hebben.

bestandsnaam = 'Open_Rapid_19-20.json'

import csv
import json

# json-bestand van Sevilla inlezen
with open(bestandsnaam, 'r', encoding = "ISO-8859-1") as sevilla_file:
    tornooi = json.load(sevilla_file)
    avonden = []
    avond = []
    vorige_datum = ''
    for ronde in tornooi['Group'][0]['RoundHist']:
        if (ronde['Date'] != vorige_datum) and vorige_datum:
            # nieuwe datum dus nieuwe avond
            if avond:
                avonden.append(avond)
            avond = []
        borden = []
        for bord in ronde['Game']:
            try:
                borden.append([bord['White'], bord['Black'],
                               bord['Res'][0].replace('\xbd', '0.5'),
                               bord['Res'][-1].replace('\xbd', '0.5')])
            except IndexError:
                borden.append([bord['White'], bord['Black'], '', ''])
        # bye speler ook nog toevoegen
        for afwezige in ronde['Abs']:
            if 'bye' in afwezige['Reason'].lower():
                borden.append([afwezige['Player'], 'bye', '', ''])
        if borden:
            avond.append(borden)
        vorige_datum = ronde['Date']
    if avond:
        avonden.append(avond)

# Csv-bestanden voor de website schrijven
for i, avond in enumerate(avonden):
    with open('ronde_{0}.csv'.format(i + 1), 'w', newline='') as avond_file:
        avond_writer = csv.writer(avond_file, quoting=csv.QUOTE_MINIMAL)
        avond_writer.writerow(['wit', 'zwart', 'wr', 'zr'])
        for j, ronde in enumerate(avond):
            avond_writer.writerow(['partij {0}'.format(j + 1),'','',''])
            for partij in ronde:
                avond_writer.writerow(partij)

