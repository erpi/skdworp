---
layout: default
title: Tornooiarchief
description: Tornooiarchief van de Dworpse Schaakkring.
permalink: /archief/
last_modified_at: 2017-01-18
---
## klubkampioenschap

- [2015 - 2016](/archief/klubkampioenschap-1516/)
- [2014 - 2015](/archief/klubkampioenschap-1415/)

## prijs van de inzet

- [2015 - 2016](/archief/inzet-1516/)
- [2014 - 2015](/archief/inzet-1415/)

## nationale interclubs

{% assign archief_ni = site.archief_ni | sort: "beginjaar" %}
{% for archief in archief_ni reversed %}
- [{{ archief.beginjaar }} - {{ archief.beginjaar | plus: 1 }}]({{ archief.url }}){% endfor %}

## snelschaak

- [2015 - 2016](/archief/snelschaak-1516/)
- [2014 - 2015](/archief/snelschaak-1415/)
