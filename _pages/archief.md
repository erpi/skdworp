---
layout: default
title: Tornooiarchief
description: Tornooiarchief van de Dworpse Schaakkring.
permalink: /archief/
last_modified_at: 2017-02-20
---
## klubkampioenschap

- [2015 - 2016](/archief/klubkampioenschap-1516/)
- [2014 - 2015](/archief/klubkampioenschap-1415/)

## prijs van de inzet

{% assign archief_inzet = site.inzet | sort: "beginjaar" %}
{% for archief in archief_inzet reversed %}
- [{{ archief.beginjaar }} - {{ archief.beginjaar | plus: 1 }}]({{ archief.url }}){% endfor %}

## nationale interclubs

{% assign archief_ni = site.interclubs | sort: "beginjaar" | pop %}
{% for archief in archief_ni reversed %}
- [{{ archief.beginjaar }} - {{ archief.beginjaar | plus: 1 }}]({{ archief.url }}){% endfor %}

## snelschaak

{% assign archief_ss = site.snelschaak | sort: "beginjaar" | pop %}
{% for archief in archief_ss reversed %}
- [{{ archief.beginjaar }} - {{ archief.beginjaar | plus: 1 }}]({{ archief.url }}){% endfor %}

## memorial

{% assign archief_mm = site.memorial | sort: "jaar" %}
{% for archief in archief_mm reversed %}
- [{{ archief.jaar }}]({{ archief.url }}){% endfor %}
