#!/usr/bin/env python
# -*- coding: utf-8 -*-
# geschreven voor python 2.7

# Script zet uitslagen van PairTwo van het 'Open Rapid Tornooi' om in
# de juiste csv-bestanden voor de website.
# In PairTwo 'bestanden'-->'CSV-Rapport' kiezen om CSV-bestand aan te maken.
# Ronden die op dezelfde avond gespeeld worden moeten dezelfde datum hebben.
# In PairTwo 'Tornooi'-->'Data ronden' kiezen om eventueel data juist te zetten.

import csv

bestandsnaam = 'Open Rapid 2017-2018.csv'

# Csv-bestand van PairTwo inlezen
with open(bestandsnaam, 'rb') as p2_file:
    p2_reader = csv.reader(p2_file, delimiter=';')
    datum_avond = ''
    avonden = []
    avond = []
    ronde = []
    for row in p2_reader:
        if row[0][0:5] == 'Ronde':
            if ronde:
                avond.append(ronde)
            ronde = []
            if row[1] != datum_avond:
                # nieuwe avond
                datum_avond = row[1]
                if avond:
                    avonden.append(avond)
                avond = []
        elif datum_avond:
            if row[0] == '-':
                # afwezige speler
                pass
            elif row[2] == 'Bye':
                # speler zonder tegenstander
                ronde.append([row[1].replace('Van De Velde', 'Van de Velde'), 'bye', '', ''])
            else:
                # normale partij
                wit = row[1].replace('Van De Velde', 'Van de Velde')
                zwart = row[3].replace('Van De Velde', 'Van de Velde')
                wres = row[2][0].replace('\xbd', '0.5')
                zres = row[2][2].replace('\xbd', '0.5')
                ronde.append([wit, zwart, wres, zres])
    if ronde:
        avond.append(ronde)
    if avond:
        avonden.append(avond)

# Csv-bestanden voor de website schrijven
for i, avond in enumerate(avonden):
    with open('ronde_{0}.csv'.format(i + 1), 'wb') as avond_file:
        avond_writer = csv.writer(avond_file, quoting=csv.QUOTE_MINIMAL)
        avond_writer.writerow(['wit', 'zwart', 'wr', 'zr'])
        for j, ronde in enumerate(avond):
            avond_writer.writerow(['partij {0}'.format(j + 1),'','',''])
            for partij in ronde:
                avond_writer.writerow(partij)

