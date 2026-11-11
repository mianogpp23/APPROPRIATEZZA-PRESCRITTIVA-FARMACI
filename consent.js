/* Guardia di accesso al portale DPC.
   Il consenso all'accettazione delle condizioni e' memorizzato in localStorage;
   senza consenso le pagine interne reindirizzano alla splash (index.html).
   La splash e la pagina di disclaimer restano sempre accessibili. */
(function () {
    "use strict";
    var CHIAVE = "dpc-consenso";
    var CONSENTITO = ["index.html", "disclaimer.html", ""];
    function pagina() {
        var p = window.location.pathname.split("/").pop();
        return p || "index.html";
    }
    function accettato() {
        try {
            return window.localStorage.getItem(CHIAVE) === "1";
        } catch (e) {
            return false;
        }
    }
    function registra() {
        try {
            window.localStorage.setItem(CHIAVE, "1");
        } catch (e) {
            /* modalita' privata: si prosegue comunque nella sessione */
        }
    }
    window.DPC = {
        accettato: accettato,
        registra: registra,
        chiave: CHIAVE,
        vaiAlPortale: function () {
            registra();
            window.location.href = "index_list.html";
        }
    };
    if (accettato()) { return; }
    if (CONSENTITO.indexOf(pagina()) === -1) {
        window.location.replace("index.html");
    }
})();
