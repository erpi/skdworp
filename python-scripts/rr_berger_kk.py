#!/usr/bin/env python

import json
import re
from collections import OrderedDict

playernames = [
    "Stijn Bertrand",
    "Yves Baert",
    "Diederik Lot",
    "Geert Verrijken",
    "Serge Vanderwaeren",
    "Geert Maeckelbergh",
    "Niels Palmans",
    "Eddy Pletinckx",
    "Bernard Malfliet",
    "Filip Van de Velde",
    "Peter De Bosscher",
    "Eric Cornelis",
    "Walter De Reymaeker",
    "Bye"
    ]

dates = [
    "06-10-2017",
    "20-10-2017",
    "17-11-2017",
    "01-12-2017",
    "15-12-2017",
    "19-01-2018",
    "02-02-2018",
    "02-03-2018",
    "16-03-2018",
    "20-04-2018",
    "04-05-2018",
    "01-06-2018",
    "15-06-2018"
    ]

nr_players = len(playernames)
half = nr_players / 2
players = range(1, nr_players + 1)
nr_rounds = nr_players - 1
table = []

#make Berger round robin table
#first round
round = zip(players[:half], players[half:][::-1])
table.append(round)
#next rounds
for r in range(nr_rounds - 1):
    round = []
    # first board
    if r % 2:
        round.append(((table[-1][0][1] + half) % nr_rounds, players[-1]))
    else:
        round.append((players[-1], (table[-1][0][0] + half) % nr_rounds))
    # next boards
    for w,b in table[-1][1:]:
        round.append(((w + half) % nr_rounds, (b + half) % nr_rounds))
    table.append(round)
# change all zeros in berger table to 'next to last player number'
for ro in range(nr_rounds):
    for bo in range(half):
        w, b = table[ro][bo]
        if not w:
            table[ro][bo] = (nr_rounds, b)
        elif not b:
            table[ro][bo] = (w, nr_rounds)

# make json string with dates and playernames
l = []
for i, r in enumerate(table):
    round = OrderedDict([("ronde", "ronde %d" % (i + 1,)), ("datum", dates[i])])
    boards = []
    for w, b in r:
        boards.append(OrderedDict([("wr", ""), ("zr", ""), ("wit", playernames[w - 1]), ("zwart", playernames[b - 1])]))
    round["partijen"] = boards
    l.append(round)
json_string = json.dumps(l, indent=2, separators=(',', ': '))

# remove a lot of whitespace and newlines with regular expression
p = re.compile(r'''
    (\{)\s+
    ("wr":\s"",)\s+
    ("zr":\s"",)\s+
    ("wit":\s"[a-z ]+",)\s+
    ("zwart":\s"[a-z ]+")\s+
    (\})
    ''', re.VERBOSE)
json_string = p.sub(r'\1\2 \3 \4 \5\6', json_string)

# write json string to file
with open('kk1718.json', 'w') as f:
    f.write(json_string)
