#!/usr/bin/env python
# -*- coding: utf-8 -*-
# geschreven voor python 2.7

for jaar1 in (range(1988,1996) + range(2010, 2016)):
    jaar2 = jaar1 + 1

    html_string = (
        "---\n"
        "title: Nationale Interclubs {0} - {1}\n"
        "beginjaar: {0}\n"
        "noindex: true\n"
        "sitemap: false\n"
        "---\n"
        ).format(jaar1, jaar2)

    bestandsnaam = "../_interclubs/interclubs-{0}{1}.html".format(str(jaar1)[2:], str(jaar2)[2:])
    with open(bestandsnaam, 'w') as f:
        f.write(html_string)
