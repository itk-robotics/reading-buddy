    /*
    Prepare html for tablet view on Pepper 18a
    Source:
    https://partner-portal.aldebaran.com/projects/knowledge-base/wiki/Adjust_tablet's_display_with_JavaScript_for_Pepper_18a
     */

    (function() {
        viewport = document.querySelector("meta[name=viewport]");
        if (viewport != null) {
          var legacyWidth = 1280;
          var windowWidth = window.screen.width;
          var scale = (windowWidth/legacyWidth).toFixed(3);
          init_str = "initial-scale=".concat(scale.toString());
          min_str = "minimum-scale=".concat(scale.toString());
          max_str = "maximum-scale=".concat(scale.toString());
          viewport.setAttribute("content", init_str.concat(",").concat(min_str).concat(",").concat(max_str));
        }
    });


    var session = null;

    document.addEventListener("DOMContentLoaded", function(event) {

        QiSession(function (s) {
            console.log("Qi session connected!");
            session = s;

            // Subscribe to the memShowFact to display fact data on tablet
            session.service("ALMemory").then(function(mem) {
                mem.subscriber("memShowString").then( function (sub) {
                    sub.signal.connect(showFactCallback);
                });
            });

            // Subscribe to the memShowFact to display fact data on tablet
            session.service("ALMemory").then(function(mem) {
                mem.subscriber("memHideString").then( function (sub) {
                    sub.signal.connect(hideFactCallback);
                });
            });

        }, function () {
            console.log("disconnected");
        });

    });


    function showFactCallback(args) {
        console.log("a new fact has been triggered:");
        console.log(args);
        document.getElementById("factBox").style.opacity="1";
        document.getElementById("factTitle").innerHTML = args;
    }


    /*
        // Open when someone clicks on the span element
    function openNav() {
        document.getElementById("factBox").style.width = "100%";
        session.service("ALMemory").then(function (mem) {
            mem.raiseEvent("memTabletEvent", "fact box opend");
        });
    }
    // Close when someone clicks on the "x" symbol inside the overlay
    */

    function hideFactCallback() {
        document.getElementById("factBox").style.opacity="0";
    }