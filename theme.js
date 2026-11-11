/* DPC — switch dei temi del sito.
   Applica l'attributo data-theme su <html> e lo salva in localStorage. */
(function () {
    "use strict";

    var THEMES = [
        { id: "chiaro",    label: "Chiaro",    sw: "linear-gradient(135deg,#f8fafc,#0284c7)" },
        { id: "ambra",     label: "Ambra",     sw: "linear-gradient(135deg,#fdfaf3,#b45309)" },
        { id: "ghiaccio",  label: "Ghiaccio",  sw: "linear-gradient(135deg,#eaf4fb,#0b6fa4)" },
        { id: "grafite",   label: "Grafite",   sw: "linear-gradient(135deg,#1c1c1f,#d4d4d8)" },
        { id: "caldo",     label: "Caldo",     sw: "linear-gradient(135deg,#fff8ed,#c2410c)" }
    ];

    var KEY = "dpc-tema";
    var DEFAULT = "chiaro";

    function saved() {
        /* tema salvato alla scelta precedente; se non e' piu' valido (es. un tema
           rimosso) si riparte dal tema predefinito */
        try {
            var v = window.localStorage.getItem(KEY);
            return THEMES.some(function (x) { return x.id === v; }) ? v : null;
        } catch (e) {
            return null;
        }
    }

    function current() {
        var t = document.documentElement.getAttribute("data-theme");
        if (THEMES.some(function (x) { return x.id === t; })) { return t; }
        return saved() || DEFAULT;
    }

    function apply(id) {
        if (!THEMES.some(function (x) { return x.id === id; })) { id = DEFAULT; }
        document.documentElement.setAttribute("data-theme", id);
        try { localStorage.setItem(KEY, id); } catch (e) { /* storage non disponibile */ }
        propagate(id);
        var lbl = document.getElementById("ts-label");
        if (lbl) {
            var found = THEMES.filter(function (x) { return x.id === id; })[0];
            lbl.textContent = found ? found.label : id;
        }
        Array.prototype.forEach.call(document.querySelectorAll("#theme-switch .ts-item"), function (b) {
            b.classList.toggle("active", b.getAttribute("data-theme") === id);
            var c = b.querySelector(".ts-check");
            if (c) { c.textContent = b.getAttribute("data-theme") === id ? "✓" : ""; }
        });
    }

    /* propaga il tema agli iframe (stessa origine): senza questo la pagina incorporata
       resterebbe nel tema precedente finche' non viene ricaricata */
    function propagate(id) {
        Array.prototype.forEach.call(document.querySelectorAll("iframe"), function (f) {
            try {
                var d = f.contentDocument;
                if (d && d.documentElement) {
                    d.documentElement.setAttribute("data-theme", id);
                }
            } catch (e) { /* iframe non ancora caricato o origine diversa */ }
        });
    }

    function build() {
        if (document.getElementById("theme-switch")) { return; }
        var box = document.createElement("div");
        box.id = "theme-switch";
        box.innerHTML =
            '<button class="ts-btn" type="button" aria-haspopup="true" aria-expanded="false">' +
            '<span class="ts-dot"></span><span id="ts-label">Tema</span>' +
            '<span aria-hidden="true">▾</span></button>' +
            '<div class="ts-menu" role="menu"></div>';

        var menu = box.querySelector(".ts-menu");
        THEMES.forEach(function (t) {
            var b = document.createElement("button");
            b.className = "ts-item";
            b.type = "button";
            b.setAttribute("data-theme", t.id);
            b.setAttribute("role", "menuitem");
            b.innerHTML = '<span class="ts-sw" style="background:' + t.sw + '"></span>' +
                          '<span>' + t.label + '</span><span class="ts-check"></span>';
            b.addEventListener("click", function (e) {
                e.stopPropagation();
                apply(t.id);
                box.classList.remove("open");
                box.querySelector(".ts-btn").setAttribute("aria-expanded", "false");
            });
            menu.appendChild(b);
        });

        var btn = box.querySelector(".ts-btn");
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            var open = box.classList.toggle("open");
            btn.setAttribute("aria-expanded", open ? "true" : "false");
        });
        document.addEventListener("click", function () {
            box.classList.remove("open");
            btn.setAttribute("aria-expanded", "false");
        });

        document.body.appendChild(box);

        Array.prototype.forEach.call(document.querySelectorAll("iframe"), function (f) {
            f.addEventListener("load", function () { propagate(current()); });
        });

        apply(current());
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", build);
    } else {
        build();
    }
})();
