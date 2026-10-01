/**
 * Adversarial Hangman - Service Worker
 * Enables 100% offline gameplay including complete dictionary pre-caching.
 */

const CACHE_NAME = 'hangman-pwa-v1.0.0';
const CORE_ASSETS = [
  './',
  './index.html',
  './style.css',
  './script.js',
  './dict.txt',
  './favicon.svg',
  './icon-192.png',
  './icon-512.png',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        CORE_ASSETS.map((assetUrl) =>
          cache.add(assetUrl).catch((err) => {
            console.warn(`[SW] Pre-cache failed for ${assetUrl}:`, err);
          })
        )
      );
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Cross-origin fallback for external fonts or fallback dictionary
  if (url.origin !== self.location.origin) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request).catch(() => new Response('')))
    );
    return;
  }

  // Network-first for HTML/JS/CSS to pick up updates seamlessly, fallback to cache
  const isNavigation = event.request.mode === 'navigate';
  const isCode = event.request.destination === 'script' ||
                 url.pathname.endsWith('.js') ||
                 url.pathname.endsWith('.html');

  if (isNavigation || isCode) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const clone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return networkResponse;
        })
        .catch(() => caches.match(event.request).then((cached) => cached || caches.match('./index.html')))
    );
    return;
  }

  // Cache-first for dict.txt, images, and fonts with network update
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200) {
          return networkResponse;
        }
        const clone = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return networkResponse;
      }).catch(() => caches.match('./index.html'));
    })
  );
});
