#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import sqlite3
import unicodedata
from operator import xor
import inspect
import io
import time
import os
import sys
import pygsheets  # werkt met versie 2.0.6
from pygsheets.custom_types import HorizontalAlignment
from git import Repo, Git
# gedefiniëerde bestandsnamen in constanten-module
from memorial_deelnemers_constanten import LOG_BESTAND, SERVICE_CREDS_BESTAND, CSV_BESTAND
from memorial_deelnemers_constanten import SWAR_BESTAND, FIDE_DB_BESTAND, GIT_SSH_IDENTITY_BESTAND
from memorial_deelnemers_constanten import GIT_DIR, SPREADSHEET_KEY, ZWARTE_LIJST, SWAR_INI_HOOFDING
from memorial_deelnemers_constanten import U20_JAAR, U16_JAAR, MAXIMUM_DEELNEMERS, KBSB_DB_BESTAND
from memorial_deelnemers_constanten import CATEGORIEEN, GRATIS, KORTING, PRIJS, HALVE_PRIJS
from memorial_deelnemers_constanten import MM_CSV_MAKEN, SWAR_INI_MAKEN, CLUBNAMEN

# initialiseer log-object
fh = logging.FileHandler(LOG_BESTAND)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(fh)


class Spreadsheet(object):
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
                'clubnr', 'svb', 'vsf', 'kbsb', 'nat', 'nat_fide',
                'e-mailadres', 'Tijdstempel', 'cat', 'u16', 'vrouw'
        ]:
            try:
                self._kolomnummers[kolom]
            except KeyError:
                raise Exception(
                    'Kolom "{0}" niet ingetroffen in de google spreadsheet'.
                    format(kolom))

    def deelnemers_aanvullen(self):
        """de data van nieuwe deelnemers in de spreadsheet aanvullen.
        de data van de oude deelnemers eventueel updaten.
        """
        deelnemers = self.__wks.get_all_records()
        for row, dlnr in enumerate(deelnemers, start=2):
            # we zijn geïnteresseerd in alle info van een deelnemer in de
            # spreadsheet met uitzondering van tijdstempel en e-mailadres
            sp = Speler(
                naam='{0}, {1}'.format(
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
                self.namen_en_email_opschonen(row, sp)
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
        """past achtergrond en horizontale alignment aan van de cellen in de rij
        """
        # licht paarse achtergrond
        cell = self.__wks.cell((rij, self._kolomnummers['Tijdstempel']))
        cell.color = (0xd9/255, 0xd2/255, 0xe9/255, 0)
        time.sleep(2)
        # licht gele achtergrond
        cell = pygsheets.Cell('A1')
        cell.color = (0xff/255, 0xf2/255, 0xcc/255, 0)
        cell.horizontal_alignment = HorizontalAlignment.LEFT
        pygsheets.DataRange('B{0}'.format(rij), 'D{0}'.format(rij), self.__wks).apply_format(cell)
        time.sleep(2)
        cell.horizontal_alignment = HorizontalAlignment.CENTER
        pygsheets.DataRange('E{0}'.format(rij), 'F{0}'.format(rij), self.__wks).apply_format(cell)
        time.sleep(2)
        # licht groene achtergrond
        cell.color = (0xd9/255, 0xea/255, 0xd3/255, 0)
        pygsheets.DataRange('G{0}'.format(rij), 'I{0}'.format(rij), self.__wks).apply_format(cell)
        time.sleep(2)
        # licht blauwe achtergrond
        cell.color = (0xcf/255, 0xe2/255, 0xf3/255, 0)
        pygsheets.DataRange('J{0}'.format(rij), 'V{0}'.format(rij), self.__wks).apply_format(cell)
        time.sleep(2)

    def namen_en_email_opschonen(self, rij, speler):
        """Verwijdert whitespace van namen/e-mail van deelnemers die soms via het
        inschrijfformulier wordt meegestuurd en zet de hoofdletters juist.
        Dit laatste verandert wel namen als 'Van de Velde' in 'Van De Velde', 
        maar dat nemen we er maar bij...
        """
        wijziging = False
        for k in ['achternaam', 'voornaam']:
            naam = self.__wks.get_value((rij, self._kolomnummers[k]))
            try:
                # namen met hoofdletters
                nette_naam = naam.strip().title()
                if naam != nette_naam:
                    wijziging = True
                    self.__wks.update_value((rij, self._kolomnummers[k]),
                                            nette_naam)
                    logger.info('wijzigen %s "%s" in "%s"', k, naam, nette_naam)
                    time.sleep(2)
                # bij wijziging in de spreadsheet moeten we ook de naam van de speler aanpassen
                if wijziging:
                    speler.naam = '{0}, {1}'.format(
                        self.__wks.get_value((rij, self._kolomnummers['achternaam'])),
                        self.__wks.get_value((rij, self._kolomnummers['voornaam'])))
            except AttributeError as e:
                logger.error(e)
        email = self.__wks.get_value((rij, self._kolomnummers['e-mailadres']))
        try:
            # e-mail met kleine letters
            nette_email = email.strip().lower()
            if email != nette_email:
                self.__wks.update_value((rij, self._kolomnummers['e-mailadres']),
                                        nette_email)
                logger.info('wijzigen e-mailadres "%s" in "%s"', email, nette_email)
                time.sleep(2)
        except AttributeError as e:
            logger.error(e)

    def cell_aanwezig_updaten(self, rij, speler):
        """Updatet enkel de cell 'aanwezig' in een rij.
        """
        self.__wks.update_value((rij, self._kolomnummers['aanwezig']),
                                speler.aanwezig)
        time.sleep(2)

    def rij_updaten(self, rij, speler, dlnr):
        """Updatet de cellen 'fide_id', 'stamnr', 'aanwezig', 'betaald',
        'bedrag', 'jaar', 'titel', 'clubnr', 'svb', 'vsf', 'kbsb', 'nat',
        'nat_fide', 'cat', 'u16', 'vrouw' in een rij indien 'speler' nieuwere
        waarden heeft.
        """
        # speler.__dict__ bevat niet de properties zoals 'aanwezig'
        # vandaar dat we getmembers gebruiken
        speler_dict = dict(inspect.getmembers(speler))
        if (any([xor((speler_dict[k] != dlnr.get(k)),
                     ((speler_dict[k] is None) and (dlnr.get(k) == ""))) for k in [
                         'fide_id', 'stamnr', 'aanwezig', 'betaald', 'bedrag', 'jaar',
                         'titel', 'clubnr', 'svb', 'vsf', 'kbsb', 'nat', 'nat_fide',
                         'cat', 'u16', 'vrouw']])
            or (speler.elo[0] != dlnr.get('elo'))
            or (speler.elo[1] != dlnr.get('elo soort'))):
            logger.info('rij_updaten %s', speler.naam)
            self.__wks.update_values('E{0}:V{0}'.format(rij), [[
                speler.fide_id, speler.stamnr, speler.aanwezig, speler.betaald,
                speler.bedrag, speler.jaar, speler.titel, speler.elo[0],
                speler.elo[1], speler.clubnr, speler.svb, speler.vsf, speler.kbsb,
                speler.nat, speler.nat_fide, speler.cat, speler.u16, speler.vrouw
            ]])
            # google spreadsheets hebben last van lees/schrijf quota
            time.sleep(2)

    def maak_bestanden_met_deelnemers(self, bestand_website, bestand_swar):
        """creëert 2 csv-bestanden (het tweede eerder een soort van ini).
        Het eerste voor de website met naam, titel, elo en clubnaam van elke
        aanwezige deelnemer. Het tweede voor het paringsprogramma SWAR met een
        lijst van deelnemers in chronologische volgorde van inschrijving.
        """
        if MM_CSV_MAKEN:
            f_web = open(bestand_website, 'w')
            writer = csv.writer(f_web)
            writer.writerow(['achternaam', 'voornaam', 'titel', 'elo', 'club'])
        if SWAR_INI_MAKEN:
            f_swar = io.open(bestand_swar, 'w', encoding='iso8859_15', newline='\r\n')
            f_swar.write(SWAR_INI_HOOFDING)
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
                and (i < MAXIMUM_DEELNEMERS)
                and (fid not in fide_ids) and (stam not in stamnummers)):
                i = i + 1
                if fid:  # geen lege of null-waarden toevoegen
                    fide_ids.add(fid)
                if stam:
                    stamnummers.add(stam)
                deelnemer = [str(k) for k in [
                    deelnemer.get('achternaam', ''),
                    deelnemer.get('voornaam', ''),
                    deelnemer.get('titel', ''),
                    deelnemer.get('elo'),
                    CLUBNAMEN.get(deelnemer.get('clubnr'), '')]
                ]
                if MM_CSV_MAKEN:
                    writer.writerow(deelnemer)
                if SWAR_INI_MAKEN:
                    if stam:
                        f_swar.writelines([str(stam), '\n'])
                    elif fid:
                        f_swar.writelines([str(fid), '\n'])
        # afronden
        if MM_CSV_MAKEN:
            f_web.close()
        if SWAR_INI_MAKEN:
            f_swar.close()


class Speler(object):
    def __init__(self,
                 naam='',
                 stam=None,
                 fid=None,
                 clubnr='',
                 jaar=None,
                 titel='',
                 nat='',
                 nat_fide='',
                 federatie='',
                 aangesloten=0,
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
        self.aangesloten = aangesloten
        self.elo_kbsb = elo_kbsb
        self.elo_fide = elo_fide
        self.elo_blitz = elo_blitz
        self.vrouw = vrouw
        self.betaald = betaald
        self.aanwezig = aanwezig
        self.bedrag = bedrag

    def updaten(self, speler_db):

        def zonder_accenten(naam):
            # hulpfuntie die accenten verwijdert
            return ''.join(c for c in unicodedata.normalize('NFD', naam)
                           if unicodedata.category(c) != 'Mn')

        # stap 1: op aanwezig/afwezig zetten

        naam_ss = self.naam.lower().strip()
        naam_db = speler_db.naam.lower().strip()
        # vervelend geval?
        if self.fide_id in ZWARTE_LIJST:
            self.auto_afwezig('zwarte lijst')
        # controleer correctheid van de spelersnaam
        elif naam_ss == naam_db:
            # alles correct, dus we kunnen aanwezigheid op 'ja' zetten
            self.auto_aanwezig()
        elif zonder_accenten(naam_ss) == zonder_accenten(naam_db):
            # Franstalige namen die zonder accent in de database zitten
            self.auto_aanwezig()
        else:
            # misschien indicatie spelersnaam komt niet overeen met fide id
            # en/of stamnummer. Of gewoon een spellingsfout?
            self.auto_afwezig('naam?',
                              'namen "{0}" en "{1}" komen niet overeen'.format(
                                  self.naam, speler_db.naam))

        # stao 2: waarden kopiëren
        self.clubnr = speler_db.clubnr
        self.jaar = speler_db.jaar
        self.titel = speler_db.titel
        self.nat = speler_db.nat
        self.nat_fide = speler_db.nat_fide
        self.federatie = speler_db.federatie
        self.aangesloten = speler_db.aangesloten
        self.vrouw = speler_db.vrouw
        self.elo_kbsb = speler_db.elo_kbsb
        self.elo_fide = speler_db.elo_fide
        self.elo_blitz = speler_db.elo_blitz

    def auto_aanwezig(self):
        if not self.aanwezig:
            self.aanwezig = 'ja (auto)'

    def auto_afwezig(self, reden, log=''):
        if not self.aanwezig:
            self.aanwezig = 'nee ({0})'.format(reden)
            if log:
                logger.info(log)

    @property
    def aanwezig(self):
        return self._aanwezig

    @aanwezig.setter
    def aanwezig(self, value):
        if isinstance(value, str):
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
        # Leden van Brusselse clubs aangesloten bij VSF zijn lid van SVB
        if not self.clubnr:
            return ''
        if self.vsf and self.clubnr > 200 and self.clubnr < 300:
            return 'ja'
        else:
            return ''

    @property
    def vsf(self):
        # een speler is lid van de VSF wanneer hij is aangesloten bij de KBSB en zijn
        # federatie "V" of "V*" is
        if self.federatie in ['V', 'V*'] and self.kbsb:
            return 'ja'
        else:
            return ''

    @property
    def kbsb(self):
        if self.aangesloten:
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
        if isinstance(value[1], str):
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
        elif self.titel in GRATIS:
            return 0
        elif (self.titel in KORTING) or (self.jaar in range(U20_JAAR, 2030)):
            return HALVE_PRIJS
        else:
            return PRIJS

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
        if isinstance(value, str):
            value = value.lower()
        if value in ('ja', 'j', 'yes', 'y'):
            self._betaald = 'ja'
        elif value in ('nee', 'n', 'no'):
            self._betaald = 'nee'
        else:
            self._betaald = value

    @property
    def clubnr(self):
        # enkel een clubnr wanneer aangesloten bij de KBSB
        if self.kbsb:
            return self._clubnr
        else:
            return ''

    @clubnr.setter
    def clubnr(self, value):
        self._clubnr = value

    @property
    def clubnaam(self):
        return CLUBNAMEN.get(self.clubnr, '')

    @property
    def cat(self):
        elo = self.elo[0]
        for c in CATEGORIEEN:
            if elo < c:
                return -c
        return ''

    @property
    def u16(self):
        if self.jaar in range(U16_JAAR, 2030):
            return 'ja'
        else:
            return ''

    @property
    def vrouw(self):
        return self._vrouw

    @vrouw.setter
    def vrouw(self, value):
        if isinstance(value, str):
            value = value.lower()
        if value in ('ja', 'f'):
            self._vrouw = 'ja'
        else:
            self._vrouw = ''

class SpelersDatabases(object):
    """SQLite databeses van KBSB en FIDE"""

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
        self.__speler = Speler()
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
            '''SELECT Name, Club, Birthday, Elo, NatPlayer, NatFideSign, Fed, Affiliated, Sex
            FROM players WHERE IdNumber=?''', (stam, ))
        (self.__speler.naam, clubnr, datum, elo_kbsb, self.__speler.nat,
         self.__speler.nat_fide, self.__speler.federatie,
         self.__speler.aangesloten, self.__speler.vrouw
        ) = self.__cursor_kbsb.fetchone()
        # clubnr kan de waarde 0 hebben, elo_kbsb kan 0 of None zijn.
        # Omzetten naar integer.
        self.__speler.clubnr = int(clubnr)
        self.__speler.elo_kbsb = int(elo_kbsb or 0)
        # jaar is een datum-string, eerste 4 chars omzetten naar int.
        self.__speler.jaar = int(datum[:4])


def main():
    try:
        logger.info('start - pygsheets %s - %s', pygsheets.__version__, sys.version)
        db = SpelersDatabases(KBSB_DB_BESTAND, FIDE_DB_BESTAND)
        sheet = Spreadsheet(SPREADSHEET_KEY, SERVICE_CREDS_BESTAND, db)
        # data in Google Spreadsheet aanvullen/updaten
        sheet.deelnemers_aanvullen()
        # website van de club updaten
        if MM_CSV_MAKEN or SWAR_INI_MAKEN:
            repo = Repo(GIT_DIR)
            git_ssh_cmd = 'ssh -i {0}'.format(GIT_SSH_IDENTITY_BESTAND)
            with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                # git pull
                repo.remotes.origin.pull()
                # bestanden schrijven
                sheet.maak_bestanden_met_deelnemers(CSV_BESTAND, SWAR_BESTAND)
                # git commit/push indien er iets veranderd is
                if repo.is_dirty():
                    logger.info(repo.git.diff(unified=0))
                    if MM_CSV_MAKEN:
                        repo.git.add(CSV_BESTAND)
                    if SWAR_INI_MAKEN:
                        repo.git.add(SWAR_BESTAND)
                    repo.git.commit(m='automatische update deelnemers memorial')
                    repo.remotes.origin.push()
        # script afsluiten
        db.close()
        logger.info('einde')
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
