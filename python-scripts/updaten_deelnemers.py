#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import csv
import logging
import sys
import sqlite3
import pygsheets  # versie 1.1.4 nodig, nieuwer zal niet werken
from pygsheets.custom_types import HorizontalAlignment
import inspect
import io
import time
# gedefiniëerde bestandsnamen in constanten-module
from constanten import log_bestand, service_creds_bestand, csv_bestand
from constanten import swar_bestand, fide_db_bestand, git_ssh_identity_bestand
from constanten import git_dir, spreadsheet_key, zwarte_lijst, swar_hoofding
from constanten import u20_jaar, maximum_deelnemers, kbsb_db_bestand
# Change the current working directory.
# When run from the scheduler, the cwd is /root but we don't have read
# permission for that folder. If we don't change it, python exits with an
# OSError when we import Git. (Synology NAS)
import os
from constanten import home_dir
os.chdir(home_dir)
from git import Repo, Git

# script geschreven voor Python versie 2.7
if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    sys.exit("This script requires Python version 2.7; you're runnning " +
             ".".join(str(x) for x in sys.version_info))

# clubnummers met bijhorende clubnamen, gebaseerd op swar.ini
clubnamen = {
    101: u"KASK",
    102: u"De Wissel Veerle",
    108: u"Merksem",
    109: u"Borgerhout",
    114: u"Mechelen",
    118: u"Mat of Pat",
    121: u"Turnhout",
    123: u"Ekeren",
    124: u"Deurne",
    128: u"Beveren",
    130: u"Hoboken",
    132: u"Oude God Mortsel",
    134: u"Schilde",
    135: u"Geel",
    136: u"Sint-Anneke",
    138: u"Bornem",
    141: u"Schoten",
    143: u"Temse",
    152: u"Paroza",
    153: u"Rijkevorsel",
    162: u"Mol",
    164: u"Zoersel",
    166: u"TSMechelen",
    167: u"Essen",
    170: u"Berchem",
    172: u"Willebroek",
    174: u"Brasschaat",
    175: u"Halse",
    176: u"Westerlo",
    177: u"Oud Deurne",
    180: u"St.-Amands",
    182: u"Noorderwijk",
    185: u"Lille",
    186: u"OSK",
    187: u"Wommelgem",
    188: u"PVH Antwerpen",
    190: u"Burcht",
    191: u"KAGS Mortsel",
    192: u"Lier",
    193: u"Boom",
    194: u"ChessLooks Lier",
    201: u"CREB Bruxelles",
    203: u"Fous du Roy",
    204: u"Excelsior",
    205: u"Ukkel",
    207: u"2 Fous Diogène",
    208: u"Sinelnikov St Josse",
    209: u"Anderlecht",
    210: u"Bene-Schaak",
    226: u"Europchess",
    228: u"Dworp",
    229: u"Woluwé",
    230: u"Leuven Centraal",
    231: u"Dolle Toren Leuven",
    232: u"Dark Knights Louvain",
    233: u"Halle",
    234: u"Schaakhuis Leuven",
    235: u"Zichemse Schaakclub",
    238: u"Zaventem",
    239: u"Boitsfort",
    240: u"SCRR (Brussel)",
    241: u"Tervuren",
    243: u"LV Leuven",
    244: u"Brussels Chess Club",
    245: u"Roque Anderlecht",
    249: u"Ruisbroek",
    250: u"jeugdschaak.be",
    253: u"Dragon Bleu",
    260: u"Kapelle-op-den-Bos",
    261: u"Opwijk",
    263: u"Aarschot",
    266: u"Desperado Leuven",
    267: u"Wespelaar",
    268: u"Londerzeel",
    269: u"Roosdaal",
    270: u"Schaerbeek",
    271: u"Le Prestige Bruxelles",
    272: u"Tibéchecs",
    273: u"Grand Roque Woluwé",
    274: u"Uccle",
    278: u"Le Pantin",
    285: u"Bemilchess",
    288: u"Capablanca",
    289: u"Chant d'Oiseau",
    290: u"Epicure",
    291: u"Chess Square",
    299: u"Ternat",
    301: u"KOSK Oostende",
    302: u"KISK Ieper",
    303: u"KBSK Brugge",
    304: u"Tielt",
    305: u"Kortrijk",
    307: u"Bredene",
    309: u"Roeselare",
    311: u"BSV",
    312: u"Gistel",
    313: u"Waregem",
    314: u"Assebroek",
    318: u"Blankenberge",
    320: u"S.K. Gazel",
    321: u"Fortis Bank Brugge",
    322: u"Veurne",
    334: u"Varsenare",
    340: u"Izegem",
    351: u"Knokke",
    352: u"Oostende Pion 68",
    353: u"Wervik",
    358: u"Heist",
    359: u"Nieuwpoort",
    360: u"Beernem",
    361: u"Poperinge",
    362: u"Oostkamp",
    363: u"Zwevegem",
    401: u"KGSRL Gent",
    402: u"Jean Jaurès Gent",
    403: u"De Drie Torens Gent (old)",
    404: u"De Drie Torens Gent",
    408: u"Gentbrugge",
    410: u"St.-Niklaas",
    417: u"Aalst",
    418: u"Geraardsbergen",
    422: u"MSV",
    425: u"Dendermonde",
    430: u"Landegem",
    432: u"Wetteren",
    433: u"Eke-Nazareth",
    434: u"Merelbeke",
    436: u"LSV-Chesspirant",
    438: u"Deinze",
    442: u"Mariakerke",
    460: u"Oudenaarde",
    461: u"Generale Gent",
    462: u"Zottegem",
    464: u"St-Gillis-Waas",
    465: u"Artevelde",
    466: u"Zwijnaarde",
    470: u"Onder Den Toren",
    471: u"Wachtebeke",
    472: u"Mercatel",
    473: u"Pion Aalter",
    474: u"Latem",
    475: u"Aalter",
    476: u"Denderleeuw",
    477: u"Chesspirant",
    478: u"FCH Zottegem",
    501: u"CREC Charleroi",
    505: u"Carnières",
    506: u"Grand-Mons",
    508: u"Mouscron",
    511: u"La Louvière",
    514: u"Fontaine-L'Evêque",
    518: u"Soignies",
    521: u"Tournai",
    523: u"Binche",
    525: u"Bourlette - Anderlues",
    526: u"Montagnards",
    528: u"Montignies",
    531: u"Tour Charles-Quint",
    532: u"Lobbes",
    533: u"Lessines",
    537: u"Quiévrain",
    538: u"Gilly",
    539: u"Sud-Hainaut",
    540: u"Le Gazomat Gilly",
    541: u"Leuze-en-Hainaut",
    542: u"Merbes-le-Chateau",
    543: u"Framières",
    546: u"Mons-Hainaut",
    547: u"Binche",
    548: u"Caissa Europe",
    549: u"St.-Ghislain",
    550: u"Enquelinnes",
    551: u"HCC Jurbise",
    552: u"L'Échiquier Rebecquois",
    569: u"Chess Club Zen",
    590: u"Chess School Saint-Ghislain",
    601: u"CRELEL Liège",
    603: u"Verviers",
    604: u"KSK47 Eynatten",
    607: u"Rochade Eupen",
    609: u"Anthisnes",
    613: u"Flémalle",
    616: u"Esneux",
    618: u"Échiquier Mosan",
    619: u"Welkenraedt",
    621: u"Ans-Loncin",
    622: u"Herve",
    623: u"St-Vith",
    624: u"Eynatten",
    625: u"Raeren",
    626: u"Herbesthal",
    627: u"Wirtzfeld",
    631: u"Blégny",
    638: u"Ans",
    639: u"En Passant",
    640: u"Huy",
    641: u"Malmedy",
    642: u"Blégny",
    643: u"Spa",
    644: u"La Tour Blanche",
    645: u"Huy Dardania",
    646: u"Seraing",
    666: u"Le 666",
    701: u"Hasselt",
    703: u"Eisden",
    704: u"Bree",
    705: u"MSK-Dilsen",
    707: u"Tessenderlo",
    708: u"Lommel",
    709: u"Houthalen",
    710: u"Rotem",
    712: u"Landen",
    713: u"Leopoldsburg",
    714: u"Overpelt",
    715: u"Boutersem",
    717: u"Zonhoven",
    718: u"Z-Z-Bolder",
    719: u"Waterschei",
    724: u"De Centrumpion",
    725: u"Vlijtingen",
    726: u"Neerpelt",
    727: u"Genk",
    732: u"Houthalen-Oost",
    733: u"St.-Truiden",
    735: u"Bilzen",
    736: u"Heusden",
    737: u"Paal",
    738: u"Het Front Hasselt",
    739: u"Ambiorix Tongeren",
    740: u"Tongeren",
    741: u"Bilzen",
    749: u"Munsterbilzen",
    750: u"De Zandkorrel Hechtel",
    751: u"SLim Houthalen-Oost",
    752: u"SLim Tongeren",
    753: u"SLim Houthalen",
    754: u"SLim Genk",
    755: u"SLim Maaseik",
    756: u"SLim Dilsen",
    757: u"SLim Neerpelt",
    758: u"SLim Halen",
    759: u"SLim Runkst",
    760: u"Boseind Neerpelt",
    761: u"SLim Achel",
    762: u"Ter Duinen Hechtel",
    763: u"SLim Bilzen",
    764: u"De Zonnebloem Lummen",
    765: u"De Beerring Beringen",
    766: u"De Reinpad-Gelieren",
    767: u"Eksel",
    768: u"Helibel-Lille",
    769: u"De Driesprong Geleen",
    770: u"J.F. Kennedy Maastricht",
    771: u"Scharn Maastricht",
    772: u"Stedelijke Humaniora Dilsen",
    773: u"'t Piepelke Bilzen",
    774: u"PMD Diepenbeek",
    801: u"Nassogne",
    807: u"Trois Frontières",
    809: u"Bertrix",
    810: u"Marche-en-Famenne",
    811: u"Arlon",
    812: u"Odeigne",
    813: u"Bastogne",
    814: u"Etalle",
    901: u"Namur-Echecs",
    902: u"Auvelais",
    903: u"Les Coperes",
    906: u"Rochefort",
    907: u"Palamède",
    908: u"Hastière",
    909: u"Philippeville",
    910: u"Ludisan",
    911: u"Gembloux",
    912: u"Ciney",
    951: u"Lasne-Waterloo",
    952: u"Wavre",
    953: u"Nivelles",
    954: u"Rixensart",
    955: u"Dion",
    956: u"Ottignies L-L-N",
    957: u"Le Roquefort",
    958: u"Braine-le-Château",
    959: u"Fleurus",
    960: u"L'Échiquier Rebecquois",
    961: u"Braine Echecs"
}

# initialiseer log-object
fh = logging.FileHandler(log_bestand)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(fh)


class spreadsheet(object):
    """google spreadsheet met alle inschrijvingen"""

    def __init__(self, key, credentials, db):
        """key: unieke naam van de spreadsheet
        credentials: toegangssleutel
        db: de spelersdb van kbsb en fide
        We checken ook of de kolommen vd spreadsheet nog de juiste hoofding
        hebben en/of aanwezig zijn.
        """
        self.__client = pygsheets.authorize(service_account_file=credentials)
        self.__spreadsheet = self.__client.open_by_key(key)
        self.__wks = self.__spreadsheet.sheet1
        self.__db = db
        # we maken een dictionary met het kolomnummer voor elke kolomnaam
        self._kolomnummers = {}
        for nummer, naam in enumerate(
                self.__wks.get_row(1, include_tailing_empty=False), start=1):
            self._kolomnummers[naam] = nummer
        # controleren of alle kolommen aanwezig zijn in de spreadsheet
        for kolom in [
                'achternaam', 'voornaam', 'fide_id', 'stamnr', 'aanwezig',
                'betaald', 'bedrag', 'jaar', 'titel', 'elo', 'elo soort',
                'clubnr', 'svb', 'nat', 'nat_fide', 'e-mailadres', 'Tijdstempel',
                'cat', 'u16', 'vrouw'
        ]:
            try:
                self._kolomnummers[kolom]
            except KeyError:
                raise Exception(
                    'Kolom "{0}" niet ingetroffen in de google spreadsheet'.
                    format(kolom))

    def deelnemers_vervolledigen(self):
        """
        """
        deelnemers = self.__wks.get_all_records()
        for row, dlnr in enumerate(deelnemers, start=2):
            # we zijn geïnteresseerd in alle info van een deelnemer in de
            # spreadsheet met uitzondering van tijdstempel en e-mailadres
            sp = speler(
                naam=u'{0}, {1}'.format(
                    dlnr.get('achternaam', ''), dlnr.get('voornaam', '')),
                stam=dlnr.get('stamnr'),
                fid=dlnr.get('fide_id'),
                aanwezig=dlnr.get('aanwezig', ''),
                betaald=dlnr.get('betaald', ''),
                bedrag=dlnr.get('bedrag'),
                jaar=dlnr.get('jaar'),
                titel=dlnr.get('titel', ''),
                clubnr=dlnr.get('clubnr'),
                nat=dlnr.get('nat', ''),
                nat_fide=dlnr.get('nat_fide', ''),
                vrouw=dlnr.get('vrouw', ''))
            sp.elo = (dlnr.get('elo'), dlnr.get('elo soort', ''))
            if sp.is_nieuw:
                # een nieuwe inschrijving in de spreadsheet
                self.rij_layouten(row)
                # er zijn 3 goede scenario's:
                # 1. een juist fide id zonder een kbsb stamnummer
                # 2. een juist fide id met het bijhorende juiste kbsb stamnr
                # 3. een fide id met waarde 0 en een bestaand kbsb stamnummer
                if self.__db.geldige_fide_id(sp.fide_id):
                    if not sp.stamnr:
                        # scenario 1
                        # we zoeken het ontbrekende stamnummer van de kbsb op
                        # het kan uiteraard ook een buitenlander zijn
                        sp.stamnr = self.__db.get_stamnummer(sp.fide_id)
                        sp_db = self.__db.get_speler(sp.fide_id, sp.stamnr)
                        sp.updaten(sp_db)
                        self.rij_updaten(row, sp, dlnr)
                    elif self.__db.get_fide_id(sp.stamnr) == sp.fide_id:
                        # scenario 2
                        # stamnummer en fide id komen overeen
                        sp_db = self.__db.get_speler(sp.fide_id, sp.stamnr)
                        sp.updaten(sp_db)
                        self.rij_updaten(row, sp, dlnr)
                    else:
                        # fide id en stamnummer komen niet overeen
                        sp.auto_afwezig('nummers?')
                        self.cell_aanwezig_updaten(row, sp)
                elif (sp.fide_id == 0) and self.__db.geldig_kbsb_stamnummer(
                        sp.stamnr):
                    # scenario 3
                    # lid van de kbsb die nog geen fide id heeft gekregen
                    # misschien is er toch een fide id?
                    sp.fide_id = self.__db.get_fide_id(sp.stamnr)
                    if not sp.fide_id:
                        # controleren of de speler wel actief is bij de kbsb
                        if not self.__db.actief_kbsb_stamnummer(sp.stamnr):
                            sp.auto_afwezig('geen lid kbsb')
                    sp_db = self.__db.get_speler(sp.fide_id, sp.stamnr)
                    sp.updaten(sp_db)
                    self.rij_updaten(row, sp, dlnr)
                else:
                    # fide id en/of stamnummer is waardeloos
                    sp.auto_afwezig('nummers?')
                    self.cell_aanwezig_updaten(row, sp)
            else:
                # een oude inschrijving in de spreadsheet
                # enkel eventueel gewijzigde gegevens updaten
                if not sp.fide_id:
                    # misschien is er ondertussen wel een fide id?
                    sp.fide_id = self.__db.get_fide_id(sp.stamnr)
                if not sp.stamnr:
                    # misschien ondertussen toch aangesloten bij de kbsb?
                    sp.stamnr = self.__db.get_stamnummer(sp.fide_id)
                sp_db = self.__db.get_speler(sp.fide_id, sp.stamnr)
                if sp_db:
                    sp.updaten(sp_db)
                    self.rij_updaten(row, sp, dlnr)

    def rij_layouten(self, rij):
        """past achtergrond en horizontale alignment aan van de rij
        """
        # deze methode kan ongetwijfeld op veel betere wijze geschreven worden
        # licht paarse achtergrond
        cell = self.__wks.cell((rij, self._kolomnummers['Tijdstempel']))
        cell.color = (0xd9/255, 0xd2/255, 0xe9/255, 0)
        time.sleep(2)
        # licht gele achtergrond
        for k in ['achternaam', 'voornaam', 'e-mailadres', 'fide_id', 'stamnr']:
            cell = self.__wks.cell((rij, self._kolomnummers[k]))
            cell.color = (0xff/255, 0xf2/255, 0xcc/255, 0)
            time.sleep(2)
        # licht groene achtergrond
        for k in ['aanwezig', 'betaald']:
            cell = self.__wks.cell((rij, self._kolomnummers[k]))
            cell.color = (0xd9/255, 0xea/255, 0xd3/255, 0)
            time.sleep(2)
        # licht blauwe achtergrond
        for k in ['bedrag', 'jaar', 'titel', 'elo', 'elo soort', 'clubnr',
                  'svb', 'nat', 'nat_fide', 'cat', 'u16', 'vrouw']:
            cell = self.__wks.cell((rij, self._kolomnummers[k]))
            cell.color = (0xcf/255, 0xe2/255, 0xf3/255, 0)
            time.sleep(2)
        # horizontale alignment
        # rechts
        #cell = self.__wks.cell((rij, self._kolomnummers['Tijdstempel']))
        #cell.horizontal_alignment = HorizontalAlignment.RIGHT
        # midden
        for k in ['fide_id', 'stamnr', 'aanwezig', 'betaald', 'bedrag', 'jaar',
                  'titel', 'elo', 'elo soort', 'clubnr', 'svb', 'nat',
                  'nat_fide', 'cat', 'u16', 'vrouw'
        ]:
            cell = self.__wks.cell((rij, self._kolomnummers[k]))
            cell.fetch()
            time.sleep(2)
            cell.horizontal_alignment = HorizontalAlignment.CENTER
            time.sleep(2)

    def cell_aanwezig_updaten(self, rij, speler):
        """Updatet enkel de cell 'aanwezig' in een rij.
        """
        self.__wks.update_value((rij, self._kolomnummers['aanwezig']),
                               speler.aanwezig)
        time.sleep(2)

    def rij_updaten(self, rij, speler, dlnr):
        """Updatet de cellen 'fide_id', 'stamnr', 'aanwezig', 'betaald',
        'bedrag', 'jaar', 'titel', 'clubnr', 'svb', 'nat', 'nat_fide', 'cat', 
        'u16', 'vrouw' in een rij indien 'speler' nieuwere waarden heeft.
        """
        # speler.__dict__ bevat niet de properties zoals 'aanwezig'
        # vandaar dat we getmembers gebruiken
        speler = dict(inspect.getmembers(speler))
        for k in [
                'fide_id', 'stamnr', 'aanwezig', 'betaald', 'bedrag', 'jaar',
                'titel', 'clubnr', 'svb', 'nat', 'nat_fide', 'cat', 'u16', 'vrouw'
        ]:
            if speler[k] != dlnr.get(k):
                self.__wks.update_value((rij, self._kolomnummers[k]), speler[k])
                # google spreadsheets hebben last van lees/schrijf quota
                time.sleep(2)
        # elo en elo soort apart
        for e, k in zip(speler['elo'], ('elo', 'elo soort')):
            if e != dlnr.get(k):
                self.__wks.update_value((rij, self._kolomnummers[k]), e)
                time.sleep(2)

    def maak_csv_bestand_met_deelnemers(self, bestand):
        """creëert een csv-bestand voor de website
        met naam, titel, elo, clubnaam van elke aanwezige deelnemer
        """
        with open(bestand, 'w') as f:
            # in volgende 2 sets houden we fide id's en stamnummers van de
            # deelnemers bij, zodanig dat een deelnemer maximaal 1 keer in
            # het csv-bestand kan komen
            fide_ids = set()
            stamnummers = set()
            writer = csv.writer(f)
            writer.writerow(['achternaam', 'voornaam', 'titel', 'elo', 'club'])
            deelnemers = self.__wks.get_all_records()
            for deelnemer in deelnemers:
                fid = deelnemer.get('fide_id')
                stam = deelnemer.get('stamnr')
                if (deelnemer.get('aanwezig') in ('ja', 'ja (auto)')
                        and fid not in fide_ids and stam not in stamnummers):
                    if fid:  # geen lege of null-waarden toevoegen
                        fide_ids.add(fid)
                    if stam:
                        stamnummers.add(stam)
                    deelnemer = [
                        unicode(k).encode('utf-8') for k in [
                            deelnemer.get('achternaam', ''),
                            deelnemer.get('voornaam', ''),
                            deelnemer.get('titel', ''),
                            deelnemer.get('elo'),
                            clubnamen.get(deelnemer.get('clubnr'), '')
                        ]
                    ]
                    writer.writerow(deelnemer)

    def maak_csv_bestanden_met_deelnemers(self, bestand_website, bestand_swar):
        """creëert 2 csv-bestanden (het tweede eerder een soort van ini). 
        Het eerste voor de website met naam, titel, elo en clubnaam van elke 
        aanwezige deelnemer. Het tweede voor het paringsprogramma SWAR met een 
        lijst van deelnemers in chronologische volgorde van inschrijving.
        """
        f_web = open(bestand_website, 'w')
        writer = csv.writer(f_web)
        f_swar = io.open(bestand_swar, 'w', encoding='iso8859_15', newline='\r\n')
        # hoofding bestanden schrijven
        writer.writerow(['achternaam', 'voornaam', 'titel', 'elo', 'club'])
        f_swar.write(swar_hoofding)
        # in volgende 2 sets houden we fide id's en stamnummers van de
        # deelnemers bij, zodanig dat een deelnemer maximaal 1 keer in
        # de bestanden kan komen
        fide_ids = set()
        stamnummers = set()
        # itereren over alle rijen in de spreadsheet
        deelnemers = self.__wks.get_all_records()
        i = 0
        for deelnemer in deelnemers:
            fid = deelnemer.get('fide_id')
            stam = deelnemer.get('stamnr')
            if (deelnemer.get('aanwezig') in ('ja', 'ja (auto)')
                and i < maximum_deelnemers
                    and fid not in fide_ids and stam not in stamnummers):
                i = i + 1
                if fid:  # geen lege of null-waarden toevoegen
                    fide_ids.add(fid)
                if stam:
                    stamnummers.add(stam)
                deelnemer = [
                    unicode(k).encode('utf-8') for k in [
                        deelnemer.get('achternaam', ''),
                        deelnemer.get('voornaam', ''),
                        deelnemer.get('titel', ''),
                        deelnemer.get('elo'),
                        clubnamen.get(deelnemer.get('clubnr'), '')
                    ]
                ]
                writer.writerow(deelnemer)
                if stam:
                    f_swar.writelines([unicode(stam), u'\n'])
                elif fid:
                    f_swar.writelines([unicode(fid), u'\n'])
        # afronden
        f_web.close()
        f_swar.close()


class speler(object):
    def __init__(self,
                 naam='',
                 stam=None,
                 fid=None,
                 clubnr=None,
                 jaar=None,
                 titel='',
                 nat='',
                 nat_fide='',
                 federatie='',
                 elo_kbsb=0,
                 elo_fide=0,
                 elo_blitz=0,
                 vrouw='',
                 betaald='',
                 aanwezig='',
                 bedrag=None):
        self.naam = naam
        self.stamnr = stam
        self.fide_id = fid
        self.clubnr = clubnr
        self.jaar = jaar
        self.titel = titel
        self.nat = nat
        self.nat_fide = nat_fide
        self.federatie = federatie
        self.elo_kbsb = elo_kbsb
        self.elo_fide = elo_fide
        self.elo_blitz = elo_blitz
        self.vrouw = vrouw
        self.betaald = betaald
        self.aanwezig = aanwezig
        self.bedrag = bedrag

    def updaten(self, sp):
        # op aanwezig/afwezig zetten
        # vervelend geval?
        if self.fide_id in zwarte_lijst:
            self.auto_afwezig('zwarte lijst')
        # controleer correctheid van de spelersnaam
        elif self.naam.strip().lower() == sp.naam.strip().lower():
            # alles correct, dus we kunnen aanwezigheid op 'ja' zetten
            self.auto_aanwezig()
        else:
            # misschien indicatie spelersnaam komt niet overeen met fide id
            # en/of stamnummer. Of gewoon een spellingsfout?
            self.auto_afwezig('naam?')

        # waarden kopiëren
        self.clubnr = sp.clubnr
        self.jaar = sp.jaar
        self.titel = sp.titel
        self.nat = sp.nat
        self.nat_fide = sp.nat_fide
        self.federatie = sp.federatie
        self.vrouw = sp.vrouw
        self.elo_kbsb = sp.elo_kbsb
        self.elo_fide = sp.elo_fide
        self.elo_blitz = sp.elo_blitz

    def auto_aanwezig(self):
        if not self.aanwezig:
            self.aanwezig = 'ja (auto)'

    def auto_afwezig(self, reden):
        if not self.aanwezig:
            self.aanwezig = 'nee ({0})'.format(reden)

    @property
    def aanwezig(self):
        return self._aanwezig

    @aanwezig.setter
    def aanwezig(self, value):
        if isinstance(value, basestring):
            value = value.lower()
        if value in ('ja', 'j', 'yes', 'y'):
            self._aanwezig = 'ja'
        elif value in ('nee', 'n', 'no'):
            self._aanwezig = 'nee'
        else:
            self._aanwezig = value

    @property
    def is_nieuw(self):
        return not any([
            self.jaar, self.clubnr, self.titel, self.nat, self.nat_fide,
            self.elo_kbsb, self.elo_fide, self.elo_blitz, self.vrouw
        ])

    @property
    def svb(self):
        # Leden van clubs in Vlaans-Brabant zijn lid van SVB
        if self.clubnr in (228, 230, 231, 233, 234, 235, 240, 260, 261):
            return 'ja'
        # Leden van Brusselse clubs aangesloten bij VSF zijn lid van SVB
        elif self.clubnr in (201, 204, 207, 209, 226, 229, 239, 244, 278, 289) and self.federatie == 'V':
            return 'ja'
        else:
            return ''

    @property
    def elo(self):
        if self.elo_blitz:
            return (self.elo_blitz, 'blitz')
        elif self.elo_fide:
            return (self.elo_fide, 'fide')
        else:
            return (self.elo_kbsb, 'nationaal')

    @elo.setter
    def elo(self, value):
        if isinstance(value[1], basestring):
            soort = value[1].lower()
        try:
            if soort == 'nationaal':
                self.elo_kbsb = value[0]
            elif soort == 'fide':
                self.elo_fide = value[0]
            elif soort == 'blitz':
                self.elo_blitz = value[0]
        except IndexError:
            pass

    @property
    def bedrag(self):
        if self._bedrag:
            return self._bedrag
        elif self.titel in ['GM', 'IM', 'WGM']:
            return 0
        elif (self.titel in ['FM', 'WIM']) or (self.jaar in range(u20_jaar, 2025)):
            return 5
        else:
            return 10

    @bedrag.setter
    def bedrag(self, value):
        self._bedrag = value

    @property
    def betaald(self):
        if self._betaald:
            return self._betaald
        elif self.bedrag == 0:
            return 'ja'
        else:
            return 'nee'

    @betaald.setter
    def betaald(self, value):
        if isinstance(value, basestring):
            value = value.lower()
        if value in ('ja', 'j', 'yes', 'y'):
            self._betaald = 'ja'
        elif value in ('nee', 'n', 'no'):
            self._betaald = 'nee'
        else:
            self._betaald = value

    @property
    def clubnaam(self):
        return clubnamen.get(self.clubnr, '')

    @property
    def cat(self):
        elo = self.elo[0]
        if elo < 1400:
            return -1400
        elif elo < 1600:
            return -1600
        elif elo < 1800:
            return -1800
        elif elo < 2000:
            return -2000
        elif elo < 2200:
            return -2200
        else:
            return ''

    @property
    def u16(self):
        if self.jaar in range(u20_jaar + 4, 2025):
            return 'ja'
        else:
            return ''

    @property
    def vrouw(self):
        return self._vrouw

    @vrouw.setter
    def vrouw(self, value):
        if isinstance(value, basestring):
            value = value.lower()
        if value in ('ja', 'f'):
            self._vrouw = 'ja'
        else:
            self._vrouw = ''
        
    
class spelers_db(object):
    def __init__(self, kbsb_db, fide_db):
        self.__connection_kbsb = sqlite3.connect(kbsb_db)
        self.__cursor_kbsb = self.__connection_kbsb.cursor()
        self.__connection_fide = sqlite3.connect(fide_db)
        self.__cursor_fide = self.__connection_fide.cursor()

    def close(self):
        self.__cursor_kbsb.close()
        self.__connection_kbsb.close()
        self.__cursor_fide.close()
        self.__connection_fide.close()
        
    def geldige_fide_id(self, fid):
        """
        Geeft de waarde "True" terug als de "fide id" voorkomt in de fide-db,
        "False" indien niet.
        """
        if not fid:
            return False
        self.__cursor_fide.execute(
            'SELECT * FROM fide WHERE IdNumber=?',
            (fid, ))
        return bool(self.__cursor_fide.fetchall())

    def geldig_kbsb_stamnummer(self, stam):
        """Geeft de waarde "True" terug als het stamnummer voorkomt in de kbsb db,
        "False" indien niet.
        """
        if not stam:
            return False
        self.__cursor_kbsb.execute(
            'SELECT * FROM players WHERE IdNumber=?',
            (stam, ))
        return bool(self.__cursor_kbsb.fetchall())

    def actief_kbsb_stamnummer(self, stam):
        """Geeft "True" indien de speler momenteel is aangesloten bij de kbsb,
        "False" indien het een oude speler betreft of een nieuwe jeugdspeler.
        """
        if not stam:
            return False
        self.__cursor_kbsb.execute(
            'SELECT * FROM players WHERE IdNumber=? and Affiliated=1',
            (stam, ))
        return bool(self.__cursor_kbsb.fetchall())

    def get_fide_id(self, stam):
        """Geeft de "fide id" terug die hoort bij een kbsb-stamnummer.
        "None" indien die kbsb-speler geen "fide id" heeft.
        """
        if not stam:
            return None
        self.__cursor_kbsb.execute(
            'SELECT FideId FROM players WHERE IdNumber=?',
            (stam, ))
        try:
            return int(self.__cursor_kbsb.fetchone()[0])
        except:
            return None

    def get_stamnummer(self, fid):
        """Geeft het stamnummer van de kbsb-speler met een bepaalde "fide id",
        "None" indien geen enkele kbsb-speler die "fide id" heeft.
        """
        if not fid:
            return None
        self.__cursor_kbsb.execute(
            'SELECT IdNumber FROM players WHERE FideId=?',
            (fid, ))
        try:
            return int(self.__cursor_kbsb.fetchone()[0])
        except:
            return None

    def get_speler(self, fid=None, stam=None):
        """Geeft een speler-object terug op basis van fide id en/of stamnummer.
        Data van de kbsb heeft voorrang op die van de fide.
        """
        self.__speler = speler()
        speler_gevonden = False
        if fid and self.geldige_fide_id(fid):
            self.__data_fide_speler(fid)
            self.__speler.fide_id = fid
            speler_gevonden = True
        if stam and self.geldig_kbsb_stamnummer(stam):
            self.__data_kbsb_speler(stam)
            self.__speler.stamnr = stam
            speler_gevonden = True
        if speler_gevonden:
            return self.__speler
        else:
            return None

    def __data_fide_speler(self, fid):
        self.__cursor_fide.execute(
            '''SELECT Name, BDay, SRtng, BRtng, Tit, Fed, Sex 
            FROM fide WHERE IdNumber=?''',
            (fid, ))
        (self.__speler.naam, datum, elo_fide, elo_blitz, self.__speler.titel,
         self.__speler.nat_fide, self.__speler.vrouw
        ) = self.__cursor_fide.fetchone()
        # elo waardes kunnen 0 of None zijn. Zet deze om naar integers.
        self.__speler.elo_fide = int(elo_fide or 0)
        self.__speler.elo_blitz = int(elo_blitz or 0)
        # jaar is een datum-string, eerste 4 chars omzetten naar int.
        self.__speler.jaar = int(datum[:4])

    def __data_kbsb_speler(self, stam):
        self.__cursor_kbsb.execute(
            '''SELECT Name, Club, Birthday, Elo, NatPlayer, NatFideSign, Fed, Sex
            FROM players WHERE IdNumber=?''', (stam, ))
        (self.__speler.naam, clubnr, datum, elo_kbsb, self.__speler.nat,
         self.__speler.nat_fide, self.__speler.federatie, self.__speler.vrouw
        ) = self.__cursor_kbsb.fetchone()
        # clubnr kan de waarde 0 hebben, elo_kbsb kan 0 of None zijn.
        # Omzetten naar integer.
        self.__speler.clubnr = int(clubnr)
        self.__speler.elo_kbsb = int(elo_kbsb or 0)
        # jaar is een datum-string, eerste 4 chars omzetten naar int.
        self.__speler.jaar = int(datum[:4])


def main():
    try:
        logger.info('start sync')
        db = spelers_db(kbsb_db_bestand, fide_db_bestand)
        sp = spreadsheet(spreadsheet_key, service_creds_bestand, db)
        # data in Google Spreadsheet aanvullen
        sp.deelnemers_vervolledigen()
        repo = Repo(git_dir)
        git_ssh_cmd = 'ssh -i {0}'.format(git_ssh_identity_bestand)
        with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
            # git pull
            repo.remotes.origin.pull()
            # csv-bestand schrijven
            sp.maak_csv_bestanden_met_deelnemers(csv_bestand, swar_bestand)
            # git commit/push indien er iets veranderd is
            if repo.is_dirty():
                logger.info(repo.git.diff(unified=0))
                repo.git.add('_data/mm/mm2019/deelnemers.csv')
                repo.git.add('_data/mm/mm2019/swar_import.csv')
                repo.git.commit(m='automatische update deelnemers memorial')
                repo.remotes.origin.push()

        db.close()
        logger.info('stop sync')
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
