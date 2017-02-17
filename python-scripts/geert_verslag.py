#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, datetime, os, codecs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="maak .md bestand in _post-directory")
    parser.add_argument("file", help="bestand verkregen via staticman")
    args = parser.parse_args()
    # inlezen
    try:
        output = u"---\n"
        with open(args.file, "r") as sm_file:
            for line in sm_file:
                if line.startswith("tag: "):
                    tag = line[7:].rstrip()
                elif line.startswith("author: "):
                    auteur = line[8:].rstrip()
                elif line.startswith("ni_ronde: "):
                    ronde = line[11:].rstrip()[:-1]
                elif line.startswith("verslag: "):
                    verslag = line[10:].rstrip()[:-1].replace('\\r\\n', '\n')
                    continue
                elif line.startswith(("_id: ", "date: ")):
                    continue
                output += line.rstrip().decode("utf-8") + "\n"
        output += u'description: ""\n'
        output += u"---\n"
    except IOError:
        print "bestand niet gevonden"
    # schrijven
    try:
        cur_dir = os.path.abspath(os.curdir)
        bestandsnaam = "{0}-{1}-r{2}-verslag-{3}.md".format(
            datetime.date.today().isoformat(), tag, ronde, auteur)
        bestand = os.path.join(cur_dir, "..", "_posts", bestandsnaam)
        bestand = os.path.normpath(bestand)
        print bestand
        print output
        with codecs.open(bestand, 'w', encoding="utf-8") as md_file:
            md_file.write(output)
            md_file.write(verslag.replace('\r\n', '\n').decode("utf-8"))
    except IOError:
        print "bestand '{0}' kan niet geschreven worden".format(bestand)
