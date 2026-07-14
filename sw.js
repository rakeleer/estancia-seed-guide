const CACHE_NAME = 'seed-app-v5';
const ASSETS_TO_CACHE = [
    './',
    './index.html',
    './manifest.json',
    './taxa.csv'
];

// Install Event: Save core files to cache
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Fetch Event: Serve from cache if offline
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        }).catch(() => {
            // If both cache and network fail, do nothing (or return a fallback)
        })
    );
});