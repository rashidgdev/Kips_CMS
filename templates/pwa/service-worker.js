// Minimal service worker - exists to satisfy browsers' PWA installability
// requirement (a registered service worker with a fetch handler). Does not
// implement offline caching - every request just passes straight through
// to the network. Offline support is a separate, larger feature.

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    event.respondWith(fetch(event.request));
});
