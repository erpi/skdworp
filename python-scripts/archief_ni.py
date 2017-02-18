#!/usr/bin/env python
# -*- coding: utf-8 -*-
# geschreven voor python 2.7

for jaar1 in range(1989, 2016):
    jaar2 = jaar1 + 1

    html_string = (
        "---\n"
        "title: Nationale Interclubs {0} - {1}\n"
        "beginjaar: {0}\n"
        "---\n"
        ).format(jaar1, jaar2)

    bestandsnaam = "../_archief_ni/interclubs-{0}{1}.html".format(str(jaar1)[2:], str(jaar2)[2:])
    with open(bestandsnaam, 'w') as f:
        f.write(html_string)
