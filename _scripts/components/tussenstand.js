$(document).ready(function(){
    var kruisTabel, soort, uitslagenId, n, namen, rooster;
    function uitslagenInlezen() {
        var tds, witIndex, zwartIndex, wr, zr;
        function indexNaam(naam) {
            var i, j;
            //naam = naam.toLowerCase();
            i = namen.indexOf(naam);
            if (naam.toLowerCase() == 'bye') {
                return -1
            }
            if (i == -1) {
                // naam zit nog niet in de array 'namen'
                i = namen.push(naam) - 1;
                // rooster groter maken met een extra rij op het einde
                rooster.push(new Array(rooster.length));
                // rooster groter maken met een extra kolom op het einde van elke rij
                for (j = 0; j < rooster.length; j++) {
                    rooster[j].length = rooster.length;
                }
            }
            return i;
        }
        
        $(uitslagenId + ' > tbody  > tr').each(function() {
            tds = $(this).children('td');
            if (tds.length == 7) {
                witIndex = indexNaam(tds.eq(1).html());
                zwartIndex = indexNaam(tds.eq(3).html());
                if (witIndex != -1 && zwartIndex != -1) {
                    // geen uitslag met bye
                    wr = parseFloat(tds.eq(4).html());
                    zr = parseFloat(tds.eq(6).html());
                    if (isFinite(wr)) {
                        rooster[witIndex][zwartIndex] = wr;
                    }
                    if (isFinite(zr)) {
                        rooster[zwartIndex][witIndex] = zr;
                    }
                }
            }
        });
    }
    function roosterTotalenToevoegen() {
        // namen, aantal partijen en totaal toevoegen aan rooster
        var i, bp;
        function totaalRij(rij) {
            return rooster[rij].reduce(function(tot, res) {return tot + res;}, 0);
        }
        function totaalKolom(kolom) {
            var i, res, totaal = 0;
            for (i = 0; i < rooster.length; i++) {
                res = rooster[i][kolom];
                if (isFinite(res)) {totaal += res;}
            }
            return totaal;
        }
        function aantalRij(rij) {
            return rooster[rij].filter(function(res) {return typeof res == 'number';}).length;
        }
        function bpPerMatch() {
            return (totaalRij(0) + totaalKolom(0)) / aantalRij(0);
        }
        function mpRij(rij) {
            function mp(tot, res) {
                if (2 * res > bp) {
                    return tot + 2;
                } else if (2 * res == bp) {
                    return tot + 1;
                }
                return tot;
            }
            return rooster[rij].reduce(mp, 0);
        }
        if (soort == 'ni') {bp = bpPerMatch();
        }
        for (i = 0; i < rooster.length; i++) {
            if (soort != 'ni') {
                rooster[i].push(aantalRij(i), totaalRij(i));
            } else {
                rooster[i].push(totaalRij(i), mpRij(i));
            }
        }
        // voeg namen toe
        for (i = 0; i < rooster.length; i++) {
            rooster[i].unshift(namen[i]);
        }
        // console.log(rooster);
    }
    function sorteerRooster() {
        // rooster sorteren, eerst op totaal (kk) of mp (ni)(hoog --> laag),
        // vervolgens op aantal bij kk (laag -> hoog)
        // of vervolgens op bp bij ni (hoog -> laag)
        var i, j,
            hoogste, maxTotaal, minAantal, totaal, aantal,
            kleinerDan, groterDan, vergelijken,
            tempVar;
        kleinerDan = function(first, second) {
            return first < second;
        };
        groterDan = function(first, second) {
            return first > second;
        };
        // bij 'ni' is groter 'bp' beter, bij 'kk' is lager 'aantal' beter
        vergelijken = (soort == 'ni') ? groterDan : kleinerDan;
        for (i = 0; i < rooster.length; i++) {
            hoogste = i;
            maxTotaal = rooster[i][rooster.length + 2];
            minAantal = rooster[i][rooster.length + 1];
            for (j = i + 1; j < rooster.length; j++) {
                totaal = rooster[j][rooster.length + 2];
                aantal = rooster[j][rooster.length + 1];
                if (totaal > maxTotaal ||
                    (totaal == maxTotaal && vergelijken(aantal, minAantal))) {
                        hoogste = j;
                        maxTotaal = totaal;
                        minAantal = aantal;
                }
            }
            if (i != hoogste) {
                // verwissel rij 'i' met rij 'hoogste' in rooster
                tempVar = rooster[i];
                rooster[i] = rooster[hoogste];
                rooster[hoogste] = tempVar;
                // verwissel kolom 'i' met kolom 'hoogste'
                // i + 1 omdat de eerste kolom de namen bevat
                for (j = 0; j < rooster.length; j++) {
                    tempVar = rooster[j][i + 1];
                    rooster[j][i + 1] = rooster[j][hoogste + 1];
                    rooster[j][hoogste+1] = tempVar;
                }
            }
        }
        // console.log(rooster);
    }
    function roosterVervolledigen() {
        // hoofding, rangschikkingsnummers, kruisjes toevoegen
        var i;
        if (soort != 'ni') {
            rooster.unshift(['nummer', 'naam', '#', 'totaal']);
        } else {
            rooster.unshift(['nummer', 'naam', 'bp', 'mp']);
        }
        for (i = 1; i < rooster.length; i++) {
            rooster[0].splice(i + 1, 0, i);
            rooster[i].unshift(i);
            rooster[i][i + 1] = 'x';
        }
        // console.log(rooster);
    }
    function htmlRooster() {
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
                // the folowing line fixes "Nan" values in the table in Safari
                // NaN is the only JavaScript value that is treated as unequal to itself
                if (res !== res) {res = '';};
                tabel += '<td' + left + '>' + res + '</td>';
            }
            tabel += '</tr>';
        }
        tabel += '</tbody>';
        // console.log(tabel);
        return tabel;
    }
    kruisTabel = document.getElementsByClassName("kruis-tussenstand");
    for (n = 0; n < kruisTabel.length; n++) {
        namen = [];
        rooster = [];
        // soort van tabel: 'nn' of 'kk'
        soort = kruisTabel[n].id.substr(0, 2);
        // id van de tabel met uitslagen, bv. 'uitslag-3b'
        uitslagenId = '#uitslag-' + kruisTabel[n].id.substr(-2, 2);
        uitslagenInlezen();
        roosterTotalenToevoegen();
        sorteerRooster();
        roosterVervolledigen();
        kruisTabel[n].innerHTML = htmlRooster();
    }
});
