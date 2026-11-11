/* Guardia di accesso al portale DPC.
   Il consenso all'accettazione delle condizioni e' memorizzato in localStorage e, in alternativa,
   in un cookie (copertura di browser/modalita' in cui lo storage non e' disponibile).
   La sessione corrente puo' comunque superare la guardia tramite il frammento '#consenso=1'
   impostato dal pulsante ACCETTO: evita il ciclo di reindirizzamento quando lo storage e' negato.
   La splash e la pagina di disclaimer restano sempre accessibili. */
(function () {
    "use strict";
    var CHIAVE = "dpc-consenso";
    var CONSENTITO = ["index.html", "disclaimer.html", ""];
    var ANNO = 60 * 60 * 24 * 365;

    function pagina() {
        var p = window.location.pathname.split("/").pop();
        return p || "index.html";
    }
    function cookieConsentito() {
        try {
            return document.cookie.split(";").some(function (c) {
                return c.trim().indexOf(CHIAVE + "=1") === 0;
            });
        } catch (e) {
            return false;
        }
    }
    function accettato() {
        try {
            if (window.localStorage.getItem(CHIAVE) === "1") { return true; }
        } catch (e) { /* storage non disponibile: si prosegue con il cookie */ }
        return cookieConsentito();
    }
    function registra() {
        try {
            window.localStorage.setItem(CHIAVE, "1");
        } catch (e) { /* storage non disponibile */ }
        try {
            document.cookie = CHIAVE + "=1;path=/;max-age=" + ANNO + ";SameSite=Lax";
        } catch (e) { /* cookie non disponibili */ }
    }
    function consensoNellaSessione() {
        var q = (window.location.hash || "") + (window.location.search || "");
        return /(^|[#&?])consenso=1(&|$)/.test(q);
    }

    window.DPC = {
        accettato: accettato,
        registra: registra,
        chiave: CHIAVE,
        vaiAlPortale: function () {
            registra();
            window.location.href = "index_list.html#consenso=1";
        }
    };

    if (accettato()) { return; }
    if (consensoNellaSessione()) { registra(); return; }
    if (CONSENTITO.indexOf(pagina()) === -1) {
        window.location.replace("index.html");
    }
})();
