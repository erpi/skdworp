#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import sys
# script geschreven voor Python versie 2.7
if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    sys.exit("This script requires Python version 2.7; you're runnning " +
             ".".join(str(x) for x in sys.version_info))

import argparse
import csv
import glob
import json
import os.path as osp

input_dir = '../_data/ni'
output_dir_csv = '../_data/inzet'
output_dir_html = '../_inzet'

def sort(spelers):
    """QuickSort algoritme, inspiratie  Stackoverflow."""

    less, equal, greater = [], [], []

    if len(spelers) > 1:
        pivot = spelers[0][-1]
        for speler in spelers:
            if speler[-1] < pivot:
                less.append(speler)
            elif speler[-1] == pivot:
                equal.append(speler)
            elif speler[-1] > pivot:
                greater.append(speler)
        return sort(greater) + equal + sort(less)
    else:
        return spelers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="maak csv-bestand met stand van de prijs van de inzet")
    parser.add_argument("seizoen", help="geef het seizoen op, bv. '1819'")
    parser.add_argument("-m", "--html", action="store_true",
                        help="maak nieuwe jekyll html-pagina")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="geef ook output in de console")
    args = parser.parse_args()

    input_dir = osp.join(input_dir, 'ni{0}'.format(args.seizoen))
    input_files = glob.glob(osp.join(input_dir, 'individueel*.json'))
    output_file_csv = osp.join(output_dir_csv,
                               'inzet{0}.csv'.format(args.seizoen))
    output_file_html = osp.join(output_dir_html,
                                'inzet-{0}.html'.format(args.seizoen))

    if input_files:
        spelers_dict = {}
        # doorloop alle json-files met individuele uitslagen
        for input_file in input_files:
            with open(input_file, 'r') as json_file:
                j = json.load(json_file)
                for round in j:
                    ronde = int(round['ronde'])
                    for board in round['borden']:
                        if 'dworp' in round['thuis']:
                            naam = board['tspeler']
                            resultaat = board['tr']
                        else:
                            naam = board['uspeler']
                            resultaat = board['ur']
                        try:
                            # verwijder eerst forfait markeringen
                            resultaat = resultaat.lower().replace('f', '')
                            resultaat = int(float(resultaat) * 2 + 1)
                        except ValueError:
                            print(('ValueError: ronde:{0}, naam:{1}, res:{2}'
                            ).format(ronde, naam, resultaat))
                        # avec petit 'd' gevallen
                        naam = naam.replace('Van De Velde', 'Van de Velde')
                        naam = naam.replace('Van Duuren', 'van Duuren')
                        try:
                            achternaam, voornaam = naam.strip().split(', ')
                            naam = u'{0} {1}'.format(voornaam, achternaam)
                        except ValueError:
                            pass
                        if 'bye' in naam.lower():
                            pass
                        elif naam in spelers_dict:
                            # bestaande speler
                            spelers_dict[naam][ronde] = resultaat
                        else:
                            # nieuwe speler 
                            l = [0] * 12
                            l[ronde] = resultaat
                            spelers_dict[naam] = l

        # bereken totaal per speler
        for naam, uitslag in spelers_dict.items():
            spelers_dict[naam][0] = sum(uitslag)

        # transformeer spelers dictionary in list
        spelers_list = []
        for naam, uitslag in spelers_dict.items():
             spelers_list.append([naam] + uitslag[1:12] + [uitslag[0]])

        # sorteer spelers lijst
        spelers_list = sort(spelers_list)

        # voeg ranking toe
        vorig_totaal = 9999
        for rang, speler in enumerate(spelers_list, start=1):
            totaal = speler[-1]
            if totaal < vorig_totaal:
                spelers_list[rang - 1] = [rang] + speler
            else:
                spelers_list[rang - 1] = [u''] + speler
            vorig_totaal = totaal

        # onderste rij met totalen, magische python zip fu
        spelers_list.append(
            [u'', u'totaal'] + [sum(x) for x in zip(*spelers_list)[2:]])

        # vervang nullen door lege strings
        spelers_list = [[u'' if x == 0 else x for x in speler]
                        for speler in spelers_list]
        
        # output naar csv-bestand
        with open(output_file_csv, 'wb') as csv_file:
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(
                ['nummer', 'naam', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
                 'r8','r9', 'r10', 'r11', 'totaal'])
            for speler in spelers_list:
                csv_writer.writerow(speler)

        # output naar html-bestand
        if args.html:
            beginjaar = int(args.seizoen[:2])
            eindjaar = int(args.seizoen[2:4])
            if beginjaar < 60:
                beginjaar += 2000
                eindjaar += 2000
            else:
                beginjaar += 1900
                eindjaar += 1900
            from collections import Counter
            c = Counter([resultaat for speler in spelers_list[:-1]
                         for resultaat in speler[2:-1]])
            verlies, remise, winst = c[1], c[2], c[3]
            totaal = verlies + remise + winst
            html_string = (
                '---\n'
                'title: Prijs van de inzet {0} - {1}\n'
                'beginjaar: {0}\n'
                '---\n'
                '<p>de club sloot de nationale interclubs af met</p>\n'
                '<ul>\n'
                '<li>{2} overwinningen ({3}%)</li>\n'
                '<li>{4} remises ({5}%)</li>\n'
                '<li>{6} nederlagen ({7}%)</li>\n'
                '</ul>\n'
                ).format(
                    beginjaar, eindjaar, winst,
                    '{0:.0f}'.format(winst / totaal * 100), remise,
                    '{0:.0f}'.format(remise / totaal * 100), verlies,
                    '{0:.0f}'.format(verlies / totaal * 100))
            with open(output_file_html, 'w') as html_file:
                html_file.write(html_string)

        # verbose: output ook naar console
        if args.verbose:
            for speler in spelers_list:
                print(speler)
            if args.html:
                print(html_string)



