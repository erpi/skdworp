$(document).ready(function(){
    var ssTabel, namen = [], rooster = [['naam']];
    function ssRondeWinnaarsAanduiden() {
        var kolom, rij, j, cell, uitslag, hoogste, winnaars,
            body = ssTabel[0].tBodies[0],
            aantalRijen = body.rows.length,
            aantalKolommen = ssTabel[0].rows[0].cells.length;
        for (kolom = 2; kolom < aantalKolommen - 1; kolom++) {
            hoogste = -999;
            winnaars = [];
            for (rij = 0; rij < aantalRijen; rij++) {
                cell = body.rows[rij].cells[kolom];
                uitslag = parseFloat(cell.innerHTML);
                if (isFinite(uitslag)) {
                    if (uitslag > hoogste) {
                        hoogste = uitslag;
                        winnaars = [cell];
                    } else if (uitslag == hoogste) {
                        winnaars.push(cell);
                    }
                }
            }
            for (j = 0; j < winnaars.length; j++) {
                winnaars[j].className += ' dworp';
            }
        }
    }
    function ssUitslagenDoorstrepen() {
        var i, beginKolom, uitslagen;
        if (ssTabel[0].rows[0].cells[2].innerHTML.toLowerCase() != 'av') {
            beginKolom = 2;
        } else {
            // uitslagen av tellen niet mee en dienen niet doorstreept te worden
            beginKolom = 3;
        }
        $('.ss-stand > tbody  > tr').each(function() {
            uitslagen = [];
            $(this).children('td').slice(beginKolom, -1).each(function(index, td) {
                var uitslag = [parseFloat($(td).html()), td];
                if (isFinite(uitslag[0])) {
                    uitslagen.push(uitslag);
                }
            });
            if (uitslagen.length > 5) {
                uitslagen.sort(function(a, b) {return b[0] - a[0];});
                for (i = 5; i < uitslagen.length; i++) {
                    $(uitslagen[i][1]).addClass('doorstreept');
                }
            }
        });
    }
    function ssRondeAvAanduiden() {
        var kolom, rij, avHoofding,
            body = ssTabel[0].tBodies[0],
            aantalRijen = body.rows.length;
        avHoofding = ssTabel[0].rows[0].cells[2]
        if (avHoofding.innerHTML.toLowerCase() == 'av') {
            avHoofding.innerHTML = 'av*';
            avHoofding.className += ' schuin';
            for (rij = 0; rij < aantalRijen; rij++) {
                body.rows[rij].cells[2].className += ' schuin grijs';
            }
        }
    }
    function ssUitslagenInlezen() {
        var i, mogelijkeRonden = ["av", "sep", "okt", "nov", "dec", "jan",
            "feb", "maa", "apr", "mei", "jun"];
        function indexNaam(naam) {
            var i;
            //naam = naam.toLowerCase();
            i = namen.indexOf(naam);
            if (i == -1) {
                // naam zit nog niet in de array 'namen'
                i = namen.push(naam) - 1;
                // rooster groter maken met een extra rij op het einde
                rooster.push(new Array(rooster[0].length));
                rooster[i + 1][0] = naam;
            }
            return i;
        }
        for (i = 0; i < mogelijkeRonden.length; i++ ) {
            ronde = mogelijkeRonden[i];
            $('#' + ronde + ' tbody  > tr').each(function() {
                if (rooster[0].slice(-1)[0] != ronde) {
                    // nieuwe ronde
                    rooster[0].push(ronde);
                    for (j = 1; j < rooster.length; j++ ) {
                        // extra kolom toevoegen aan rooster
                        rooster[j].length = rooster[0].length;
                    }
                }
                tds = $(this).children('td');
                spelerIndex = indexNaam(tds.eq(1).html());
                res = parseFloat(tds.eq(tds.length - 1).html());
                if (isFinite(res)) {
                    rooster[spelerIndex + 1][rooster[0].length - 1] = Math.round(res);
                }
            });
        }
    }
    function ssTotalenBerekenen() {
        var rij, kolom, beginKolom, uitslagen, totaal;
        beginKolom = 1;
        if (rooster[0][1] == "av") {beginKolom = 2;}
        for (rij = 1; rij < rooster.length; rij++ ) {
            uitslagen = [];
            for (kolom = beginKolom; kolom < rooster[0].length; kolom++) {
                uitslag = rooster[rij][kolom];
                if (isFinite(uitslag)) {uitslagen.push(uitslag);}
            }
            if (uitslagen.length > 5) {
                uitslagen.sort(function(a, b) {return b - a;});
            }
            totaal = uitslagen.slice(0, 5).reduce(
                function(tot, res) {return tot + res;}, 0);
            rooster[rij].push(Math.round(totaal));
        }
        rooster[0].push('totaal');
    }
    function ssSorteerRooster() {
        var i, j, hoogsteRij, maxTotaal, totaal, tempRij;
        for (i = 1; i < rooster.length; i++) {
            hoogsteRij = i;
            maxTotaal = rooster[i].slice(-1)[0];
            for (j = i + 1; j < rooster.length; j++) {
                totaal = rooster[j].slice(-1)[0];
                if (totaal > maxTotaal) {
                    hoogsteRij = j;
                    maxTotaal = totaal;
                }
            }
            // verwissel rij 'i' met rij 'hoogsteRij' in rooster
            tempRij = rooster[i];
            rooster[i] = rooster[hoogsteRij];
            rooster[hoogsteRij] = tempRij;
        }
        //console.log(rooster);
    }
    function ssHtmlRooster() {
        // rooster array omzetten in html-tabel
        // gebaseerd op _includes/table-eindstand.html
        var i, j, tabel, left, res;
        tabel = '<thead><tr>';
        for (i = 0; i < rooster[0].length; i++) {
            tabel += '<th>' + ((i < 2) ? '<span class="sr-only">' : '')  +
                     rooster[0][i] + ((i < 2) ? '</span>' : '' + '</th>');
        }
        tabel += '</tr></thead><tbody>';
        for (i = 1; i < rooster.length; i++) {
            tabel += '<tr' + ((rooster[i][1].indexOf('worp') != -1) ? ' class="dworp"' : '') + '>';
            for (j = 0; j < rooster[i].length; j++) {
                left = (j == 1) ? ' class="alignleft"' : '';
                res = (rooster[i][j] !== undefined) ? rooster[i][j] : '';
                tabel += '<td' + left + '>' + res + '</td>';
            }
            tabel += '</tr>';
        }
        tabel += '</tbody>';
        return tabel;
    }
    function ssRoosterVervolledigen() {
        var i;
        // eertste kolom met rangnummers toevoegen
        rooster[0].unshift('nummer');
        for (i = 1; i < rooster.length; i++) {
            if (rooster[i].slice(-1)[0] != rooster[i - 1].slice(-1)[0]) {
                rooster[i].unshift(i);
            } else {
                // totaal speler is gelijk aan totaal van vorige speler
                rooster[i].unshift('');
            }
        }
    }
    // Tabel met tussenstand dynamisch genereren
    ssTabel = document.getElementsByClassName("ss-tussenstand");
    if (ssTabel[0]) {
        ssUitslagenInlezen();
        ssTotalenBerekenen();
        ssSorteerRooster();
        ssRoosterVervolledigen();
        ssTabel[0].innerHTML = ssHtmlRooster();
    }
    // Eind- en tussenstanden snelschaak extra opmaken
    ssTabel = document.getElementsByClassName("ss-stand");
    if (ssTabel[0]) {
        ssRondeWinnaarsAanduiden();
        ssUitslagenDoorstrepen();
        ssRondeAvAanduiden();
    }
});
