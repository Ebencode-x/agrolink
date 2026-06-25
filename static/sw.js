const CACHE_NAME = 'agrolink-v2';
const OFFLINE_URL = '/offline';

const PRECACHE_URLS = [
  '/',
  '/offline',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Acha requests zisizo GET zipite kawaida
  if (event.request.method !== 'GET') return;

  // Acha cross-origin requests (fonts, CDN) zipite bila SW kuzigusa
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  // Acha API calls zipite moja kwa moja
  if (url.pathname.startsWith('/api/')) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Cache only valid responses
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() =>
        caches.match(event.request).then(cached => {
          if (cached) return cached;
          // Kama ni page request, rudisha offline page
          if (event.request.destination === 'document') {
            return caches.match(OFFLINE_URL);
          }
          // Kwa resources nyingine rudisha 404 badala ya undefined
          return new Response('Not found', { status: 404 });
        })
      )
  );
});
