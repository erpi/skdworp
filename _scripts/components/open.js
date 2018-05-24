/*
grotendeels gebaseerd op snelschaak.js
opSorteerRooster() en opRoosterVervolledigen() moeten nog verder aangepast worden 
*/

$(document).ready(function(){
    var opTabel, namen = [], rooster = [['naam']];
    function opRondeWinnaarsAanduiden() {
        var kolom, rij, j, cell, uitslag, hoogste, winnaars,
            body = opTabel[0].tBodies[0],
            aantalRijen = body.rows.length,
            aantalKolommen = opTabel[0].rows[0].cells.length;
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
    function opUitslagenDoorstrepen() {
        var i, uitslagen;
        $('.op-stand > tbody  > tr').each(function() {
            uitslagen = [];
            $(this).children('td').slice(2, -1).each(function(index, td) {
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
    function opUitslagenInlezen() {
        var i, mogelijkeRonden = ["ronde_1", "ronde_2", "ronde_3", "ronde_4", "ronde_5", "ronde_6",
            "ronde_7", "ronde_8", "ronde_9", "ronde_10", "ronde_11"];
        function indexNaam(naam) {
            var i;
            naam = naam.toLowerCase();
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
            kort = ronde.replace('onde_','');
            $('#' + ronde + ' tbody  > tr').each(function() {
                if (rooster[0].slice(-1)[0] != kort) {
                    // nieuwe ronde
                    rooster[0].push(kort);
                    for (j = 1; j < rooster.length; j++ ) {
                        // extra kolom toevoegen aan rooster
                        rooster[j].length = rooster[0].length;
                    }
                }
                tds = $(this).children('td');
                if (tds.length != 0) {
                    y = rooster[0].length - 1;
                    if (tds.eq(3).html().toLowerCase() == 'bye') {
                        // bye is 2 punten
                        witRes = 2;
                    } else {
                        witRes = 2 * parseFloat(tds.eq(4).html()) + 1;
                        zwartRes = 2 * parseFloat(tds.eq(6).html()) + 1;
                        zwartIndex = indexNaam(tds.eq(3).html());
                        x = zwartIndex + 1;
                        rooster[x][y] = (rooster[x][y] !== undefined) ? rooster[x][y] += zwartRes : zwartRes;
                    }
                    witIndex = indexNaam(tds.eq(1).html());
                    x = witIndex + 1;
                    rooster[x][y] = (rooster[x][y] !== undefined) ? rooster[x][y] += witRes : witRes;
                }
            });
        }
    }
    function opTotalenBerekenen() {
        var rij, kolom, uitslagen, totaal;
        for (rij = 1; rij < rooster.length; rij++ ) {
            uitslagen = [];
            for (kolom = 1; kolom < rooster[0].length; kolom++) {
                uitslag = rooster[rij][kolom];
                if (isFinite(uitslag)) {uitslagen.push(uitslag);}
            }
            uitslagen.sort(function(a, b) {return b - a;});
            totaal = uitslagen.slice(0, 5).reduce(
                function(tot, res) {return tot + res;}, 0);
            rooster[rij].push(Math.round(totaal));
            // voeg de gesorteerde uitslagen array toe aan rooster
            // gebruiken we om de spelers te sorteren
            rooster[rij].push(uitslagen);
        }
        rooster[0].push('totaal');
        rooster[0].push('uitslagen');
    }
    function opSorteerRooster() {
        var i, j, k, hoogsteRij, maxTotaal, maxUitslagen, totaal, uitslagen, beter, tempRij;
        for (i = 1; i < rooster.length; i++) {
            hoogsteRij = i;
            maxTotaal = rooster[i].slice(-2)[0];
            maxUitslagen = rooster[i].slice(-1)[0];
            for (j = i + 1; j < rooster.length; j++) {
                beter = false;
                totaal = rooster[j].slice(-2)[0];
                uitslagen = rooster[j].slice(-1)[0];
                if (totaal > maxTotaal) {
                    beter = true;
                }
                else if (totaal == maxTotaal) {
                    // eerste scheiding: deelnemer met de meeste gespeelde avonden staat eerst
                    if (uitslagen.length > maxUitslagen.length) {
                        beter = true;
                    }
                    else if (uitslagen.length == maxUitslagen.length) {
                        // tweede scheiding: beste rondescores vergelijken
                        // 'uitslagen' is een gesorteerde array van groot naar klein
                        for (k = 0; k < uitslagen.length; k++) {
                            if (uitslagen[k] < maxUitslagen[k]) {
                                break;
                            }
                            if (uitslagen[k] > maxUitslagen[k]) {
                                beter = true;
                                break;
                            }
                        }
                    }
                }
                if (beter) {
                    hoogsteRij = j;
                    maxTotaal = totaal;
                    maxUitslagen = uitslagen;
                }
            }
            // verwissel rij 'i' met rij 'hoogsteRij' in rooster
            tempRij = rooster[i];
            rooster[i] = rooster[hoogsteRij];
            rooster[hoogsteRij] = tempRij;
        }
        //console.log(rooster);
    }
    function opHtmlRooster() {
        // rooster array omzetten in html-tabel
        // gebaseerd op _includes/table-eindstand.html
        var i, j, tabel, left, res;
        tabel = '<thead><tr>';
        for (i = 0; i < rooster[0].length - 1; i++) {
            tabel += '<th>' + ((i < 2) ? '<span class="sr-only">' : '')  +
                     rooster[0][i] + ((i < 2) ? '</span>' : '' + '</th>');
        }
        tabel += '</tr></thead><tbody>';
        for (i = 1; i < rooster.length; i++) {
            tabel += '<tr' + ((rooster[i][1].indexOf('worp') != -1) ? ' class="dworp"' : '') + '>';
            for (j = 0; j < rooster[i].length - 1; j++) {
                left = (j == 1) ? ' class="alignleft"' : '';
                res = (rooster[i][j] !== undefined) ? rooster[i][j] : '';
                tabel += '<td' + left + '>' + res + '</td>';
            }
            tabel += '</tr>';
        }
        tabel += '</tbody>';
        return tabel;
    }
    function opRoosterVervolledigen() {
        var i, j, verschillend, uitslagen, vorige;
        // eertste kolom met rangnummers toevoegen
        rooster[0].unshift('nummer');
        for (i = 1; i < rooster.length; i++) {
            if (rooster[i].slice(-2)[0] != rooster[i - 1].slice(-2)[0]) {
                rooster[i].unshift(i);
            }
            else if (rooster[i].slice(-1)[0].length != rooster[i - 1].slice(-1)[0].length) {
                rooster[i].unshift(i);
            }
            else {
                verschillend = false;
                uitslagen = rooster[i].slice(-1)[0];
                vorige = rooster[i - 1].slice(-1)[0];
                for (j = 0; j < uitslagen.length; j++) {
                    if (uitslagen[j] != vorige[j]) {
                        verschillend = true;
                        break;
                    }
                }
                if (verschillend) {
                    rooster[i].unshift(i);
                } else {
                    // totaal speler is gelijk aan totaal van vorige speler
                    rooster[i].unshift('');
                }
            }
        }
    }
    // Tabel met tussenstand dynamisch genereren
    opTabel = document.getElementsByClassName("op-tussenstand");
    if (opTabel[0]) {
        opUitslagenInlezen();
        opTotalenBerekenen();
        opSorteerRooster();
        opRoosterVervolledigen();
        opTabel[0].innerHTML = opHtmlRooster();
    }
    // Eind- en tussenstanden extra opmaken
    opTabel = document.getElementsByClassName("op-stand");
    if (opTabel[0]) {
        opRondeWinnaarsAanduiden();
        opUitslagenDoorstrepen();
    }
});
