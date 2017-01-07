//https://github.com/twbs/bootstrap/issues/2415
//https://github.com/jquery/jquery/issues/2885
//http://stackoverflow.com/questions/7862233/twitter-bootstrap-tabs-go-to-specific-tab-on-page-reload-or-hyperlink


    var gotoHashTab = function (customHash) {
        var hash = customHash || location.hash;
        var hashPieces = hash.split('?'),
            activeTab = $('[href*=\\' + hashPieces[0] + ']');
        activeTab && activeTab.tab('show');
    }

    // onready go to the tab requested in the page hash
    gotoHashTab();

    // when the nav item is selected update the page hash
    $('.nav a').on('shown', function (e) {
        window.location.hash = e.target.hash;
    })

    // when a link within a tab is clicked, go to the tab requested
    $('.tab-pane a').click(function (event) {
        if (event.target.hash) {
            gotoHashTab(event.target.hash);
        }
    });
