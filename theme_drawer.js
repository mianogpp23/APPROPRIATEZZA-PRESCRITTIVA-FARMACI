/* ═══════════════════════════════════════════════════════════════════════
   Drawer per pillole operative - info-fab e toggle
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
    "use strict";

    function toggleInfoDrawer() {
        var drawer = document.getElementById("info-drawer");
        if (!drawer) return;
        drawer.classList.toggle("open");
    }

    function closeDrawerOnOutsideClick() {
        document.addEventListener("click", function(e) {
            var drawer = document.getElementById("info-drawer");
            if (!drawer || !drawer.classList.contains("open")) return;
            var fab = e.target.closest(".info-fab");
            var closeBtn = e.target.closest(".drawer-close");
            var drawerContent = e.target.closest(".drawer-content");
            if (!fab && !closeBtn && !drawerContent) {
                drawer.classList.remove("open");
            }
        });
    }

    /* Chiudi drawer con ESC */
    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            var drawer = document.getElementById("info-drawer");
            if (drawer && drawer.classList.contains("open")) {
                drawer.classList.remove("open");
            }
        }
    });

    /* Inizializza drawer se presente nella pagina */
    function buildDrawer() {
        var fab = document.querySelector(".info-fab");
        if (!fab) return;

        /* Event listener per il FAB */
        fab.addEventListener("click", function(e) {
            e.stopPropagation();
            toggleInfoDrawer();
        });

        closeDrawerOnOutsideClick();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", buildDrawer);
    } else {
        buildDrawer();
    }
})();
