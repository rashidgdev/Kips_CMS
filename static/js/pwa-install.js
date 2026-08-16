/**
 * Registers the service worker and drives the custom "Install App" modal,
 * replacing the browser's own install mini-infobar with a KIPS-branded one.
 *
 * Dismissing the modal hides it for the rest of this browser tab session
 * (sessionStorage - cleared when the tab/browser closes, so it reappears on
 * the next visit) but never again once the app is actually installed
 * (localStorage - permanent).
 *
 * Plain script, no build step - matches the rest of this project's
 * frontend (static/js/core/api.js, crud.js).
 */
(function () {
    'use strict';

    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
            navigator.serviceWorker.register('/sw.js').catch(function () {
                // Non-fatal - the site still works without a service worker,
                // it just won't be installable.
            });
        });
    }

    const DISMISSED_KEY = 'pwaInstallDismissed';
    const INSTALLED_KEY = 'pwaInstalled';

    function isStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    }

    let deferredPrompt = null;

    window.addEventListener('beforeinstallprompt', function (event) {
        event.preventDefault();

        if (isStandalone() || localStorage.getItem(INSTALLED_KEY) || sessionStorage.getItem(DISMISSED_KEY)) {
            return;
        }

        deferredPrompt = event;
        const modal = document.getElementById('pwa-install-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    });

    window.addEventListener('appinstalled', function () {
        localStorage.setItem(INSTALLED_KEY, '1');
        const modal = document.getElementById('pwa-install-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
        deferredPrompt = null;
    });

    document.addEventListener('DOMContentLoaded', function () {
        const modal = document.getElementById('pwa-install-modal');
        if (!modal) {
            return;
        }

        const installButton = document.getElementById('pwa-install-button');
        const dismissButton = document.getElementById('pwa-install-dismiss');

        if (installButton) {
            installButton.addEventListener('click', function () {
                modal.classList.add('hidden');
                if (!deferredPrompt) {
                    return;
                }
                deferredPrompt.prompt();
                deferredPrompt.userChoice.finally(function () {
                    deferredPrompt = null;
                });
            });
        }

        if (dismissButton) {
            dismissButton.addEventListener('click', function () {
                modal.classList.add('hidden');
                sessionStorage.setItem(DISMISSED_KEY, '1');
            });
        }
    });
})();
