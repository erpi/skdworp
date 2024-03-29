#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path as osp

HOME_DIR = '/home/skdworp/'
GIT_DIR = osp.join(HOME_DIR, 'git/skdworp')
SCRIPT_DIR = HOME_DIR

LOG_BESTAND = osp.join(SCRIPT_DIR, 'log_deelnemers.txt')
SERVICE_CREDS_BESTAND = osp.join(SCRIPT_DIR, 'service_creds.json')
CSV_BESTAND = osp.join(GIT_DIR, '_data/mm/mm2023/deelnemers.csv')
SWAR_BESTAND = osp.join(GIT_DIR, '_data/mm/mm2023/swar_import.csv')
FIDE_DB_BESTAND = osp.join(SCRIPT_DIR, 'fide.sqlite')
KBSB_DB_BESTAND = osp.join(SCRIPT_DIR, 'players.sqlite')
GIT_SSH_IDENTITY_BESTAND = osp.join(HOME_DIR, '.ssh/id_rsa')

# key van google spreadsheet met de inschrijvingen van Memorial
SPREADSHEET_KEY = ""

# lijst met fide id's van deelnemers die we niet graag hebben
ZWARTE_LIJST = []

# maximumcapaciteit 140 (tussen de 5 à 10 procent komt niet opdagen)
# we overboeken een klein beetje...
MAXIMUM_DEELNEMERS = 150

# deelname prijzen
PRIJS = 12
HALVE_PRIJS = PRIJS / 2
GRATIS = ['GM', 'IM', 'WGM']
KORTING = ['FM', 'WIM']

# ratingcategorieen
CATEGORIEEN = [1700, 1900, 2100]

# Oudste deelnemers die nog deel uitmaken van de U20 en U16
U20_JAAR = 2003
U16_JAAR = U20_JAAR + 4

MM_CSV_MAKEN = True
SWAR_INI_MAKEN = True

# Hoofding voor het import-bestand van SWAR
SWAR_INI_HOOFDING = (
    "[TOURNAMENT]\n"
    "1;8ste Memorial Debast - VSF Blitz 2023\n"
    "2;Dworpse Schaakkring\n"
    "3;Huizingen\n"
    "4;2023/09/09\n"
    "5;2023/09/09\n"
    "6;SWISS\n"
    "7;T_BLITZ\n"
    "8;13\n\n"
    "[PLAYER]\n"
    )

# clubnummers met bijhorende clubnamen, gebaseerd op swar.ini
CLUBNAMEN = {
    101: "KASK",
    102: "De Wissel Veerle",
    108: "Merksem",
    109: "Borgerhout",
    114: "Mechelen",
    118: "Mat of Pat",
    121: "Turnhout",
    123: "Ekeren",
    124: "Deurne",
    128: "Beveren",
    130: "Hoboken",
    132: "Oude God Mortsel",
    134: "Schilde",
    135: "Geel",
    136: "Sint-Anneke",
    138: "Bornem",
    141: "Schoten",
    143: "Temse",
    152: "Paroza",
    153: "Rijkevorsel",
    162: "Mol",
    164: "Zoersel",
    166: "TSMechelen",
    167: "Essen",
    170: "Berchem",
    172: "Willebroek",
    174: "Brasschaat",
    175: "Halse",
    176: "Westerlo",
    177: "Oud Deurne",
    180: "St.-Amands",
    182: "Noorderwijk",
    185: "Lille",
    186: "OSK",
    187: "Wommelgem",
    188: "PVH Antwerpen",
    190: "Burcht",
    191: "KAGS Mortsel",
    192: "Lier",
    193: "Boom",
    194: "ChessLooks Lier",
    195: "Chessmates Kapellen",
    196: "De Rode Loper Antwerpen",
    201: "CREB Bruxelles",
    203: "Fous du Roy",
    204: "Excelsior",
    205: "Ukkel",
    207: "2 Fous Diogène",
    208: "Sinelnikov St Josse",
    209: "The Belgian Chess Club",
    210: "Bene-Schaak",
    226: "Europchess",
    228: "Dworp",
    229: "Woluwé",
    230: "Leuven Centraal",
    231: "Dolle Toren Leuven",
    232: "Dark Knights Louvain",
    233: "DZD Halle",
    234: "Schaakhuis Leuven",
    235: "Zichemse Schaakclub",
    236: "Schaakclub Panorama",
    238: "Zaventem",
    239: "Boitsfort",
    240: "SCRR (Brussel)",
    241: "Tervuren",
    243: "LV Leuven",
    244: "Brussels Chess Club",
    245: "Roque Anderlecht",
    249: "Ruisbroek",
    250: "jeugdschaak.be",
    253: "Dragon Bleu",
    260: "Kapelle-op-den-Bos",
    261: "Opwijk",
    263: "Aarschot",
    266: "Desperado Leuven",
    267: "Wespelaar",
    268: "Londerzeel",
    269: "Roosdaal",
    270: "Schaerbeek",
    271: "Le Prestige Bruxelles",
    272: "Tibéchecs",
    273: "Grand Roque Woluwé",
    274: "Uccle",
    278: "Le Pantin",
    285: "Bemilchess",
    288: "Capablanca",
    289: "Chant d'Oiseau",
    290: "Epicure",
    291: "Chess Square",
    299: "Ternat",
    301: "KOSK Oostende",
    302: "KISK Ieper",
    303: "KBSK Brugge",
    304: "Tielt",
    305: "Kortrijk",
    307: "Bredene",
    309: "Roeselare",
    311: "BSV",
    312: "Gistel",
    313: "Waregem",
    314: "Assebroek",
    318: "Blankenberge",
    320: "S.K. Gazel",
    321: "Fortis Bank Brugge",
    322: "Veurne",
    334: "Varsenare",
    340: "Izegem",
    351: "Knokke",
    352: "Oostende Pion 68",
    353: "Wervik",
    358: "Heist",
    359: "Nieuwpoort",
    360: "Beernem",
    361: "Poperinge",
    362: "Oostkamp",
    363: "Zwevegem",
    401: "KGSRL Gent",
    402: "Jean Jaurès Gent",
    403: "De Drie Torens Gent (old)",
    404: "De Drie Torens Gent",
    408: "Gentbrugge",
    410: "St.-Niklaas",
    417: "Aalst",
    418: "Geraardsbergen",
    422: "MSV",
    425: "Dendermonde",
    430: "Landegem",
    432: "Wetteren",
    433: "Eke-Nazareth",
    434: "Merelbeke",
    436: "LSV-Chesspirant",
    438: "Deinze",
    442: "Mariakerke",
    460: "Oudenaarde",
    461: "Generale Gent",
    462: "Zottegem",
    464: "St-Gillis-Waas",
    465: "Artevelde",
    466: "Zwijnaarde",
    470: "Onder Den Toren",
    471: "Wachtebeke",
    472: "de Mercatel",
    473: "Pion Aalter",
    474: "Latem",
    475: "Aalter",
    476: "Denderleeuw",
    477: "Chesspirant",
    478: "FCH Zottegem",
    501: "CREC Charleroi",
    505: "Carnières",
    506: "Grand-Mons",
    508: "Mouscron",
    511: "La Louvière",
    514: "Monti' Chess Club",
    518: "Soignies",
    521: "Tournai",
    523: "Binche",
    525: "Bourlette - Anderlues",
    526: "Montagnards",
    528: "Montignies",
    531: "Tour Charles-Quint",
    532: "Lobbes",
    533: "Lessines",
    537: "Quiévrain",
    538: "Gilly",
    539: "Sud-Hainaut",
    540: "Le Gazomat Gilly",
    541: "Leuze-en-Hainaut",
    542: "Merbes-le-Chateau",
    543: "Framières",
    546: "Mons-Hainaut",
    547: "Binche",
    548: "Caissa Europe",
    549: "St.-Ghislain",
    550: "Enquelinnes",
    551: "HCC Jurbise",
    552: "L'Échiquier Rebecquois",
    569: "Chess Club Zen",
    590: "Chess School Saint-Ghislain",
    601: "CRELEL Liège",
    603: "Verviers",
    604: "KSK47 Eynatten",
    607: "Rochade Eupen",
    609: "Anthisnes",
    613: "Flémalle",
    616: "Esneux",
    618: "Échiquier Mosan",
    619: "Welkenraedt",
    621: "Ans-Loncin",
    622: "Herve",
    623: "St-Vith",
    624: "Eynatten",
    625: "Raeren",
    626: "Herbesthal",
    627: "Wirtzfeld",
    631: "Blégny",
    638: "Ans",
    639: "En Passant",
    640: "Huy",
    641: "Malmedy",
    642: "Blégny",
    643: "Spa",
    644: "La Tour Blanche",
    645: "Huy Dardania",
    646: "Seraing",
    666: "Le 666",
    701: "Hasselt",
    703: "Eisden",
    704: "Bree",
    705: "MSK-Dilsen",
    707: "Tessenderlo",
    708: "Lommel",
    709: "Houthalen",
    710: "Rotem",
    712: "Landen",
    713: "Leopoldsburg",
    714: "Overpelt",
    715: "Boutersem",
    717: "Zonhoven",
    718: "Z-Z-Bolder",
    719: "Waterschei",
    724: "De Centrumpion",
    725: "Vlijtingen",
    726: "Neerpelt",
    727: "Genk",
    732: "Houthalen-Oost",
    733: "St.-Truiden",
    735: "Bilzen",
    736: "Heusden",
    737: "Paal",
    738: "Het Front Hasselt",
    739: "Ambiorix Tongeren",
    740: "Tongeren",
    741: "Bilzen",
    742: "Tongeren",
    743: "Chess Tongeren",
    749: "Munsterbilzen",
    750: "De Zandkorrel Hechtel",
    751: "SLim Houthalen-Oost",
    752: "SLim Tongeren",
    753: "SLim Houthalen",
    754: "SLim Genk",
    755: "SLim Maaseik",
    756: "SLim Dilsen",
    757: "SLim Neerpelt",
    758: "SLim Halen",
    759: "SLim Runkst",
    760: "Boseind Neerpelt",
    761: "SLim Achel",
    762: "Ter Duinen Hechtel",
    763: "SLim Bilzen",
    764: "De Zonnebloem Lummen",
    765: "De Beerring Beringen",
    766: "De Reinpad-Gelieren",
    767: "Eksel",
    768: "Helibel-Lille",
    769: "De Driesprong Geleen",
    770: "J.F. Kennedy Maastricht",
    771: "Scharn Maastricht",
    772: "Stedelijke Humaniora Dilsen",
    773: "'t Piepelke Bilzen",
    774: "PMD Diepenbeek",
    775: "Lucerna Houthalen",
    801: "Nassogne",
    807: "Trois Frontières",
    809: "Bertrix",
    810: "Marche-en-Famenne",
    811: "Arlon",
    812: "Odeigne",
    813: "Bastogne",
    814: "Etalle",
    816: "Bastogne",
    901: "Namur-Echecs",
    902: "Auvelais",
    903: "Les Coperes",
    906: "Rochefort",
    907: "Palamède",
    908: "Hastière",
    909: "Philippeville",
    910: "Ludisan",
    911: "Gembloux",
    912: "Ciney",
    951: "Lasne-Waterloo",
    952: "Wavre",
    953: "Nivelles",
    954: "Rixensart",
    955: "Dion",
    956: "Ottignies L-L-N",
    957: "Le Roquefort",
    958: "Braine-le-Château",
    959: "Fleurus",
    960: "L'Échiquier Rebecquois",
    961: "Braine Echecs",
    962: "Chess Club Brabant Est"
}
