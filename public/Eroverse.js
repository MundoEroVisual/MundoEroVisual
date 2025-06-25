// ==UserScript==
// @name         Eroverse: Auto Universal Shortlink Clicker
// @namespace    Eroverse Scripts
// @version      2.4
// @description  Automatiza los clics y ayuda con captchas en acortadores populares (marca de agua Eroverse)
// @match        *://*.adf.ly/*
// @match        *://adf.ly/*
// @match        *://*.linkvertise.com/*
// @match        *://linkvertise.com/*
// @match        *://*.shrinkme.io/*
// @match        *://shrinkme.io/*
// @match        *://*.exe.io/*
// @match        *://exe.io/*
// @match        *://*.ouo.io/*
// @match        *://ouo.io/*
// @match        *://*.shorte.st/*
// @match        *://shorte.st/*
// @match        *://*.linktl.com/*
// @match        *://linktl.com/*
// @match        *://*.adshrink.it/*
// @match        *://adshrink.it/*
// @match        *://*.shrinkearn.com/*
// @match        *://shrinkearn.com/*
// @match        *://*.clicksfly.com/*
// @match        *://clicksfly.com/*
// @match        *://*.cpmlink.net/*
// @match        *://cpmlink.net/*
// @match        *://*.urlshortx.com/*
// @match        *://urlshortx.com/*
// @match        *://*.bitlymonetize.com/*
// @match        *://bitlymonetize.com/*
// @match        *://*.adpay.link/*
// @match        *://adpay.link/*
// @match        *://*.clk.sh/*
// @match        *://clk.sh/*
// @match        *://*.linkrex.net/*
// @match        *://linkrex.net/*
// @match        *://*.up-4ever.org/*
// @match        *://up-4ever.org/*
// @match        *://*.boost.ink/*
// @match        *://boost.ink/*
// @match        *://*.payout.link/*
// @match        *://payout.link/*
// @match        *://*.smoner.com/*
// @match        *://smoner.com/*
// @match        *://*.droplink.co/*
// @match        *://droplink.co/*
// @match        *://*.adurl.io/*
// @match        *://adurl.io/*
// @match        *://*.shrink.pe/*
// @match        *://shrink.pe/*
// @match        *://*.uiz.io/*
// @match        *://uiz.io/*
// @match        *://*.themezon.net/*
// @match        *://themezon.net/*
// @match        *://*.mrproblogger.com/*
// @match        *://en.mrproblogger.com/*
// @match        *://*.cuttty.com/*
// @match        *://cuttty.com/*
// @match        *://*.wordcount.im/*
// @match        *://wordcount.im/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

/* === MEJORAS EROVERSE UNIVERSAL ===
1. Soporte AJAX/SPA
2. Manipulación avanzada de temporizadores
3. Panel flotante de estado
4. Pausa/Reanuda automatización
5. Randomización de clics
6. Más tipos de captcha
7. Lista de dominios personalizable
8. Actualización remota de dominios (estructura)
9. Consola de logs y modo debug
10. Menú de usuario/configuración rápida
*/

// === BLOQUEO PARA CUTY.IO Y VARIANTES ===
if (/cuty\.io|cutyio\.com|cuttty\.com|cutty\.io|cuttyio\.com|cutty\.com|cuttty\.io|cutttyio\.com/i.test(location.hostname)) {
    if (!document.getElementById('eroverse-cutty-blocked')) {
        const msg = document.createElement('div');
        msg.id = 'eroverse-cutty-blocked';
        Object.assign(msg.style, {
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%,-50%)',
            background: '#2a0033',
            color: '#fff',
            fontFamily: 'monospace',
            fontSize: '22px',
            padding: '30px 50px',
            borderRadius: '12px',
            zIndex: 999999,
            boxShadow: '0 2px 16px #000a',
            textAlign: 'center',
        });
    }
    return;
}

// === 1. Soporte AJAX/SPA ===
(function() {
    // Detecta cambios de URL (pushState/hashchange)
    let lastUrl = location.href;
    setInterval(() => {
        if (location.href !== lastUrl) {
            lastUrl = location.href;
            if (window.eroversePanel) window.eroversePanel.mostrar('Cambio de URL detectado, re-ejecutando bypass...');
            setTimeout(() => {
                intentarUniversal();
                clickBotonUniversal();
            }, 500);
        }
    }, 500);
    window.addEventListener('hashchange', () => {
        if (window.eroversePanel) window.eroversePanel.mostrar('Cambio de hash detectado, re-ejecutando bypass...');
        setTimeout(() => {
            intentarUniversal();
            clickBotonUniversal();
        }, 500);
    });
    // Intercepta AJAX/fetch
    const origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        this.addEventListener('load', function() {
            setTimeout(() => {
                intentarUniversal();
                clickBotonUniversal();
            }, 500);
        });
        origOpen.apply(this, arguments);
    };
    if (window.fetch) {
        const origFetch = window.fetch;
        window.fetch = function() {
            return origFetch.apply(this, arguments).then(res => {
                setTimeout(() => {
                    intentarUniversal();
                    clickBotonUniversal();
                }, 500);
                return res;
            });
        };
    }
})();

// === 2. Manipulación avanzada de temporizadores ===
(function() {
    const origSetTimeout = window.setTimeout;
    const origSetInterval = window.setInterval;
    window.setTimeout = function(fn, t) {
        if (typeof t === 'number' && t > 1000) t = 200 + Math.random()*200;
        return origSetTimeout(fn, t);
    };
    window.setInterval = function(fn, t) {
        if (typeof t === 'number' && t > 1000) t = 500 + Math.random()*500;
        return origSetInterval(fn, t);
    };
})();

// === 3. Panel flotante de estado ===
(function() {
    if (window.eroversePanel) return;
    const panel = document.createElement('div');
    panel.id = 'eroverse-panel';
    Object.assign(panel.style, {
        position: 'fixed',
        top: '10px',
        left: '10px',
        background: 'rgba(30,0,60,0.85)',
        color: '#fff',
        fontFamily: 'monospace',
        fontSize: '15px',
        padding: '8px 18px',
        borderRadius: '8px',
        zIndex: 99999,
        boxShadow: '0 2px 8px #0008',
        minWidth: '180px',
        userSelect: 'none',
        transition: 'opacity 0.3s',
        opacity: 0.95
    });
    panel.textContent = 'Eroverse: Bypass activo';
    document.body.appendChild(panel);
    window.eroversePanel = {
        mostrar: function(msg) {
            panel.textContent = 'Eroverse: ' + msg;
            panel.style.opacity = 1;
            setTimeout(() => { panel.style.opacity = 0.7; }, 3000);
        },
        setEstado: function(msg) {
            panel.textContent = 'Eroverse: ' + msg;
        }
    };
})();

// === 4. Pausa/Reanuda automatización ===
// (Eliminado por solicitud del usuario)

// === 5. Randomización de clics ===
function eroverseClick(el) {
    if (!el) return;
    setTimeout(() => {
        el.click();
    }, 100 + Math.random()*300);
}

// === 6. Más tipos de captcha ===
function detectarOtrosCaptchas() {
    // hCaptcha
    if (document.querySelector('iframe[src*="hcaptcha"]')) {
        if (window.eroversePanel) window.eroversePanel.mostrar('hCaptcha detectado, resuélvelo');
    }
    // FunCaptcha
    if (document.querySelector('iframe[src*="funcaptcha"]')) {
        if (window.eroversePanel) window.eroversePanel.mostrar('FunCaptcha detectado, resuélvelo');
    }
}

// === 7. Lista de dominios personalizable ===
function getDominiosPersonalizados() {
    try {
        return JSON.parse(localStorage.getItem('eroverseDominios')||'[]');
    } catch { return []; }
}
function addDominioPersonalizado(dominio) {
    let doms = getDominiosPersonalizados();
    if (!doms.includes(dominio)) doms.push(dominio);
    localStorage.setItem('eroverseDominios', JSON.stringify(doms));
}
function removeDominioPersonalizado(dominio) {
    let doms = getDominiosPersonalizados();
    doms = doms.filter(d => d!==dominio);
    localStorage.setItem('eroverseDominios', JSON.stringify(doms));
}

// === 8. Actualización remota de dominios (estructura) ===
async function actualizarDominiosRemotos() {
    // Solo estructura, puedes implementar fetch real a un JSON remoto
    // let resp = await fetch('https://tusitio.com/eroverse-dominios.json');
    // let nuevos = await resp.json();
    // localStorage.setItem('eroverseDominios', JSON.stringify(nuevos));
}

// === 9. Consola de logs y modo debug ===
window.eroverseDebug = false;
function eroverseLog() {
    if (window.eroverseDebug) console.log('[Eroverse]', ...arguments);
}

// === 10. Menú de usuario/configuración rápida ===
if (typeof GM_registerMenuCommand === 'function') {
    GM_registerMenuCommand('Activar/Desactivar debug', () => {
        window.eroverseDebug = !window.eroverseDebug;
        alert('Debug ' + (window.eroverseDebug ? 'activado' : 'desactivado'));
    });
    GM_registerMenuCommand('Añadir dominio actual', () => {
        addDominioPersonalizado(location.hostname);
        alert('Dominio añadido: ' + location.hostname);
    });
    GM_registerMenuCommand('Quitar dominio actual', () => {
        removeDominioPersonalizado(location.hostname);
        alert('Dominio quitado: ' + location.hostname);
    });
    GM_registerMenuCommand('Actualizar dominios remotos', () => {
        actualizarDominiosRemotos();
        alert('Actualización remota (estructura) ejecutada');
    });
}

(function() {
    'use strict';
    // Marca de agua visual Eroverse + botones personalizados
    function mostrarMarcaEroverse() {
        if (document.getElementById('eroverse-watermark')) return;
        // Contenedor para botones y marca
        const cont = document.createElement('div');
        cont.id = 'eroverse-watermark-container';
        Object.assign(cont.style, {
            position: 'fixed',
            bottom: '10px',
            right: '20px',
            zIndex: 99999,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            gap: '6px',
        });
        // Botón página
        const btnWeb = document.createElement('a');
        btnWeb.href = 'https://eroverse.glitch.me/index.html/';
        btnWeb.target = '_blank';
        btnWeb.textContent = '🌐 Mi página';
        Object.assign(btnWeb.style, {
            background: 'linear-gradient(90deg,#6a11cb,#2575fc)',
            color: '#fff',
            fontWeight: 'bold',
            fontFamily: 'monospace',
            fontSize: '15px',
            padding: '4px 16px',
            borderRadius: '7px',
            textDecoration: 'none',
            marginBottom: '0px',
            boxShadow: '0 2px 8px #0005',
            transition: 'background 0.2s',
        });
        btnWeb.onmouseover = () => btnWeb.style.background = 'linear-gradient(90deg,#2575fc,#6a11cb)';
        btnWeb.onmouseout = () => btnWeb.style.background = 'linear-gradient(90deg,#6a11cb,#2575fc)';
        // Botón YouTube
        const btnYT = document.createElement('a');
        btnYT.href = 'https://youtube.com/@eroverse18?si=SW5u7yqk00-qYhmL';
        btnYT.target = '_blank';
        btnYT.textContent = '▶️ Mi canal';
        Object.assign(btnYT.style, {
            background: 'linear-gradient(90deg,#ff512f,#dd2476)',
            color: '#fff',
            fontWeight: 'bold',
            fontFamily: 'monospace',
            fontSize: '15px',
            padding: '4px 16px',
            borderRadius: '7px',
            textDecoration: 'none',
            marginBottom: '0px',
            boxShadow: '0 2px 8px #0005',
            transition: 'background 0.2s',
        });
        btnYT.onmouseover = () => btnYT.style.background = 'linear-gradient(90deg,#dd2476,#ff512f)';
        btnYT.onmouseout = () => btnYT.style.background = 'linear-gradient(90deg,#ff512f,#dd2476)';
        // Marca de agua
        const marca = document.createElement('div');
        marca.id = 'eroverse-watermark';
        Object.assign(marca.style, {
            background: 'rgba(30,0,60,0.7)',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: '18px',
            fontFamily: 'monospace',
            padding: '6px 18px',
            borderRadius: '8px',
            pointerEvents: 'none',
            boxShadow: '0 2px 8px #0008',
            letterSpacing: '2px',
            userSelect: 'none',
        });
        marca.textContent = 'Eroverse';
        // Ensamblar
        cont.appendChild(btnWeb);
        cont.appendChild(btnYT);
        cont.appendChild(marca);
        document.body.appendChild(cont);
    }

    // Notificación visual para captcha
    function notificarCaptcha() {
        if (document.getElementById('eroverse-captcha-notif')) return;
        const notif = document.createElement('div');
        notif.id = 'eroverse-captcha-notif';
        Object.assign(notif.style, {
            position: 'fixed',
            top: '60px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#222',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: '20px',
            fontFamily: 'monospace',
            padding: '14px 28px',
            borderRadius: '10px',
            zIndex: 99999,
            boxShadow: '0 2px 8px #0008',
            opacity: 0.97,
        });
        notif.textContent = 'Resuelve el captcha (No soy robot) para continuar';
        document.body.appendChild(notif);
        setTimeout(() => { notif.remove(); }, 6000);
    }

    // Espera a que el DOM esté listo
    function ready(fn) {
        if (document.readyState !== 'loading') fn();
        else document.addEventListener('DOMContentLoaded', fn);
    }

    // Función robusta para presionar botones/enlaces antes y después del captcha
    function clickBotonUniversal() {
        // Antes del captcha: intenta presionar cualquier botón/enlace relevante
        let btn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a'))
            .find(el => el.offsetParent && /continuar|continue|next|go|go to url|proceed|skip|get linkc|get link|get access|free access|descargar|download|obtener vínculo|obtener vinculo|obtener enlace|get url|get vinculo|click here to continue|click to verify|verify|verificar|check|comprobar|unlock|visit link|skip ad|ir al enlace|acceder|acceso/i.test((el.innerText || el.value || '').trim()));
        if (btn) {
            if (btn.disabled) btn.disabled = false;
            btn.removeAttribute('disabled');
            btn.click();
        }
        // Observa si aparece un nuevo <a> relevante tras el clic (por ejemplo, después del captcha)
        const observerA = new MutationObserver(() => {
            let aBtn = Array.from(document.querySelectorAll('a'))
                .find(el => el.offsetParent && /get link|go to link|proceed to link|visit link|go to destination|ir al destino|ir al enlace|click here to continue|continuar|continue|next|skip|go|ir|final|descargar|download/i.test((el.innerText || el.value || '').trim()));
            if (aBtn && !aBtn.disabled && !aBtn.hasAttribute('disabled')) {
                aBtn.click();
                observerA.disconnect();
            }
        });
        observerA.observe(document.body, {childList: true, subtree: true, attributes: true, characterData: true});
    }

    ready(() => {
        mostrarMarcaEroverse();
        const observer = new MutationObserver(() => {
            intentarUniversal();
            clickBotonUniversal();
        });
        observer.observe(document.body, {childList: true, subtree: true});
        intentarUniversal();
        clickBotonUniversal();
    });

    function intentarUniversal() {
        // Paso 0: Si hay un contador visible de 12 segundos, intenta acelerarlo
        let timer = document.querySelector('span, div, p, b, strong');
        if (timer && /1[012] ?s(ec(ondos|onds)?)?/i.test(timer.textContent)) {
            // Busca input hidden o variable de tiempo y ponlo a 0 si es posible
            let inputs = document.querySelectorAll('input[type="hidden"], input[type="text"], input[type="number"]');
            for (let inp of inputs) {
                if (/time|timer|count|seg|wait/i.test(inp.name || inp.id || '')) {
                    inp.value = 0;
                }
            }
            // Intenta modificar variables globales de tiempo
            for (let key in window) {
                if (/time|timer|count|seg|wait/i.test(key) && typeof window[key] === 'number') {
                    window[key] = 0;
                }
            }
        }
        // Elimina cualquier botón que mencione descarga directa
        Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a'))
            .filter(el => /descarga directa|direct download|download direct/i.test((el.innerText || el.value || '').trim()))
            .forEach(el => el.remove());
        // Paso 1: Click en Verificar, o similares (forzar habilitación si está deshabilitado)
        let btn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a'))
            .find(el => el.offsetParent && /continue|siguiente|next|go|go to url|proceed|skip|get linkc|get link|get access|free access|descargar|download|obtener vínculo|obtener vinculo|obtener enlace|get url|get vinculo|click here to continue|click to verify|verify|verificar|check|comprobar|unlock|visit link|skip ad|ir al enlace|acceder|acceso/i.test((el.innerText || el.value || '').trim()));
        if (btn) {
            if (btn.disabled) btn.disabled = false;
            btn.removeAttribute('disabled');
            btn.click();
            // Observa si aparece un nuevo <a> relevante tras el clic (por ejemplo, después del captcha)
            const observerA = new MutationObserver(() => {
                let aBtn = Array.from(document.querySelectorAll('a'))
                    .find(el => el.offsetParent && /get link|go to link|proceed to link|visit link|go to destination|ir al destino|ir al enlace|click here to continue|continuar|continue|next|skip|go|ir|final|descargar|download/i.test((el.innerText || el.value || '').trim()));
                if (aBtn && !aBtn.disabled && !aBtn.hasAttribute('disabled')) {
                    aBtn.click();
                    observerA.disconnect();
                }
            });
            observerA.observe(document.body, {childList: true, subtree: true, attributes: true, characterData: true});
            return;
        }
        // Paso 2: Intentar hacer click en el checkbox de reCAPTCHA o botones de captcha si existen
        // Si hay mensaje de captcha, enfoca el captcha y notifica
        if (document.body.innerText.match(/por favor marque el captcha|please check the captcha|captcha para pasar/i)) {
            let captchaFrame = document.querySelector('iframe[src*="recaptcha"]');
            if (captchaFrame) {
                notificarCaptcha();
                captchaFrame.scrollIntoView({behavior: "smooth", block: "center"});
                captchaFrame.focus();
            }
        }
        let captchaFrame = document.querySelector('iframe[src*="recaptcha"]');
        let captchaClicked = false;
        if (captchaFrame) {
            notificarCaptcha();
            try {
                const frameWin = captchaFrame.contentWindow;
                const frameDoc = captchaFrame.contentDocument || frameWin.document;
                // Busca el checkbox dentro del iframe
                const checkbox = frameDoc.querySelector('.recaptcha-checkbox-border, #recaptcha-anchor');
                if (checkbox) {
                    checkbox.click();
                    captchaClicked = true;
                } else {
                    captchaFrame.scrollIntoView({behavior: "smooth", block: "center"});
                    captchaFrame.focus();
                }
            } catch (e) {
                captchaFrame.scrollIntoView({behavior: "smooth", block: "center"});
                captchaFrame.focus();
            }
        }
        // También intenta hacer click en botones de captcha fuera de iframes
        let captchaBtn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'))
            .find(el => el.offsetParent && /captcha|i am human|soy humano|no soy robot|i'm not a robot|verificar|verify|check|comprobar|continue/i.test((el.innerText || el.value || '').trim()));
        if (captchaBtn && !captchaClicked) {
            captchaBtn.disabled = false;
            captchaBtn.removeAttribute('disabled');
            captchaBtn.click();
            captchaClicked = true;
        }
        if (captchaFrame || captchaBtn) {
            // Tras resolver captcha, observa y haz clic en cualquier botón relevante apenas esté disponible
            const tryClickRelevant = () => {
                let continuarBtn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a'))
                    .find(el => el.offsetParent && /continuar|click here to continue|get link|go to link|obtener enlace|proceed to link|visit link|go to destination|ir al destino|ir al enlace|acceder|acceso|continue|next|skip|go|ir|final|descargar|download/i.test((el.innerText || el.value || '').trim()));
                if (continuarBtn && !continuarBtn.disabled && !continuarBtn.hasAttribute('disabled')) {
                    continuarBtn.click();
                    return true;
                }
                // Si aparece un <a> relevante tras el captcha
                let aBtn = Array.from(document.querySelectorAll('a'))
                    .find(el => el.offsetParent && /get link|go to link|proceed to link|visit link|go to destination|ir al destino|ir al enlace|click here to continue|continuar|continue|next|skip|go|ir|final|descargar|download/i.test((el.innerText || el.value || '').trim()));
                if (aBtn && !aBtn.disabled && !aBtn.hasAttribute('disabled')) {
                    aBtn.click();
                    return true;
                }
                return false;
            };
            // Intento inmediato
            if (tryClickRelevant()) return;
            // Observa cambios en el DOM y atributos para hacer clic apenas esté disponible
            const observer = new MutationObserver(() => {
                if (tryClickRelevant()) observer.disconnect();
            });
            observer.observe(document.body, {childList: true, subtree: true, attributes: true, characterData: true});
            return;
        }
        // Paso 3: Click en Ir/Ir al enlace/final (forzar habilitación si está deshabilitado)
        let irBtn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a'))
            .find(el => el.offsetParent && /ir|go|go to url|get linkc|get link|get access|descargar|download|final|next|skip|skip ad|free access|obtener vínculo|obtener vinculo|obtener enlace|get url|get vinculo|click here to continue|click to verify|verify|verificar|check|comprobar|unlock|visit link|acceder|acceso/i.test((el.innerText || el.value || '').trim()));
        if (irBtn) {
            if (irBtn.disabled) irBtn.disabled = false;
            irBtn.removeAttribute('disabled');
            irBtn.click();
            return;
        }
        // Paso extra: Click en el contador si el texto lo indica (ej: "Click on the Counter if it STOPS")
        let counterBtn = Array.from(document.querySelectorAll('span, div, p, b, strong, a'))
            .find(el => el.offsetParent && /click (on|en) (the )?counter|clic(kea)? (en )?el contador|haz click en el contador|counter if it stops/i.test((el.innerText || el.value || '').trim()));
        if (counterBtn) {
            counterBtn.click();
            return;
        }
        // Paso extra robusto: Forzar clic en el contador si es botón o elemento clickable con temporizador
        let counterBtn2 = Array.from(document.querySelectorAll('button, a, span, div, p, , strong'))
            .find(el => el.offsetParent &&
                (/click (on|en) (the )?counter|clic(kea)? (en )?el contador|haz click en el contador|counter if it stops|su enlace está casi listo|segundos|seconds/i.test((el.innerText || el.value || '').trim()) ||
                (el.className && /count|timer|wait|next|skip/i.test(el.className))));
        if (counterBtn2) {
            // Si está deshabilitado, forzar habilitación
            if (counterBtn2.disabled) counterBtn2.disabled = false;
            counterBtn2.removeAttribute('disabled');
            counterBtn2.style.pointerEvents = 'auto';
            // Si tiene un temporizador, observar hasta que cambie
            if (counterBtn2.innerText.match(/\d+\s*(segundos|seconds|s)/i) || counterBtn2.className.match(/count|timer|wait/i)) {
                const obs = new MutationObserver(() => {
                    if (!counterBtn2.disabled && !counterBtn2.hasAttribute('disabled')) {
                        counterBtn2.click();
                        obs.disconnect();
                    }
                });
                obs.observe(counterBtn2, {childList: true, subtree: true, attributes: true, characterData: true});
            } else {
                counterBtn2.click();
            }
            return;
        }
    }
})();