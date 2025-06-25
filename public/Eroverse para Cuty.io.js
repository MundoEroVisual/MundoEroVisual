// ==UserScript==
// @name         Eroverse: Auto Cuty.io Clicker
// @namespace    Eroverse Scripts
// @version      1.0
// @description  Automatiza el clic en el botón de continuar en cuty.io solo tras interacción humana (indetectable)
// @match        *://*.cuty.io/*
// @match        *://cuty.io/*
// @match        *://*.cuttty.com/*
// @match        *://cuttty.com/*
// @grant        none
// @run-at       document-end
// ==/UserScript==
(function() {
    'use strict';
    // Marca de agua visual Eroverse
    function mostrarMarcaEroverse() {
        if (document.getElementById('eroverse-watermark')) return;
        const marca = document.createElement('div');
        marca.id = 'eroverse-watermark';
        Object.assign(marca.style, {
            position: 'fixed',
            bottom: '10px',
            right: '20px',
            background: 'rgba(30,0,60,0.7)',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: '18px',
            fontFamily: 'monospace',
            padding: '6px 18px',
            borderRadius: '8px',
            zIndex: 99999,
            pointerEvents: 'none',
            boxShadow: '0 2px 8px #0008',
            letterSpacing: '2px',
            userSelect: 'none',
        });
        marca.textContent = 'Eroverse';
        document.body.appendChild(marca);
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

    ready(() => {
        mostrarMarcaEroverse();
        // Observa cambios en el DOM para detectar botones dinámicos
        const observer = new MutationObserver(() => {
            intentarUniversal();
        });
        observer.observe(document.body, {childList: true, subtree: true});
        // También ejecuta al inicio
        intentarUniversal();
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
        // Paso 1: Click en Continuar, Verificar, o similares (forzar habilitación si está deshabilitado)
        let btn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'))
            .find(el => el.offsetParent && /continuar|continue|siguiente|next|go|proceed|skip|get link|free access|descargar|download|obtener vínculo|obtener vinculo|obtener enlace|get url|get vinculo|click here to continue|click to verify|verify|verificar|check|comprobar/i.test((el.innerText || el.value || '').trim()));
        if (btn) {
            if (btn.disabled) btn.disabled = false;
            btn.removeAttribute('disabled');
            btn.click();
            return;
        }
        // Paso 2: Intentar hacer click en el checkbox de reCAPTCHA o botones de captcha si existen
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
            .find(el => el.offsetParent && /captcha|i am human|soy humano|no soy robot|i'm not a robot|verificar|verify|check|comprobar|continue|continuar/i.test((el.innerText || el.value || '').trim()));
        if (captchaBtn && !captchaClicked) {
            captchaBtn.disabled = false;
            captchaBtn.removeAttribute('disabled');
            captchaBtn.click();
            captchaClicked = true;
        }
        if (captchaFrame || captchaBtn) {
            // Tras resolver captcha, intenta hacer click en botones de verificación
            setTimeout(() => {
                let verifyBtn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'))
                    .find(el => el.offsetParent && /verify|verificar|check|comprobar|click to verify|click here to continue|i am human|soy humano|i'm not a robot|no soy robot|captcha|continue|continuar/i.test((el.innerText || el.value || '').trim()));
                if (verifyBtn) {
                    verifyBtn.disabled = false;
                    verifyBtn.removeAttribute('disabled');
                    verifyBtn.click();
                }
            }, 800);
            return;
        }
        // Paso 3: Click en Ir/Ir al enlace/final (forzar habilitación si está deshabilitado)
        let irBtn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'))
            .find(el => el.offsetParent && /ir|go|get link|descargar|download|final|continue|next|skip|free access|obtener vínculo|obtener vinculo|obtener enlace|get url|get vinculo|click here to continue|click to verify|verify|verificar|check|comprobar/i.test((el.innerText || el.value || '').trim()));
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
    }
})();
