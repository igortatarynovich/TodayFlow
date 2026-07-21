// Service Worker для TodayFlow PWA
const CACHE_NAME = 'todayflow-v2';
const RUNTIME_CACHE = 'todayflow-runtime-v2';

// Only static marketing/shell URLs — never personalized app surfaces.
const PRECACHE_URLS = [
  '/',
];

const NEVER_CACHE_PATH_PREFIXES = [
  '/today',
  '/profile',
  '/account',
  '/onboarding',
  '/auth',
  '/login',
  '/signup',
  '/compatibility',
  '/practices',
  '/journal',
  '/tracking',
  '/maps',
  '/morning-ritual',
  '/natal-chart',
  '/weekly',
  '/habits',
  '/challenges',
  '/questions',
  '/api/',
  '/_next/',
];

function shouldBypassCache(request, url) {
  if (request.method !== 'GET') return true;
  if (url.origin !== self.location.origin) return true;
  if (request.headers.has('Authorization')) return true;
  if (url.searchParams.has('_rsc')) return true;
  return NEVER_CACHE_PATH_PREFIXES.some(
    (prefix) => url.pathname === prefix || url.pathname.startsWith(prefix + '/') || url.pathname.startsWith(prefix)
  );
}

// Установка Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(PRECACHE_URLS).catch((err) => {
          console.warn('[SW] Некоторые ресурсы не удалось закешировать:', err);
        });
      })
      .then(() => self.skipWaiting())
  );
});

// Активация Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE;
          })
          .map((cacheName) => {
            return caches.delete(cacheName);
          })
      );
    })
    .then(() => self.clients.claim())
  );
});

// Перехват запросов (Network First; personalized routes are network-only)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  if (shouldBypassCache(event.request, url)) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const responseToCache = response.clone();
        if (response.status === 200 && event.request.method === 'GET') {
          caches.open(RUNTIME_CACHE).then((cache) => {
            cache.put(event.request, responseToCache).catch(() => {});
          });
        }
        return response;
      })
      .catch(async () => {
        const cachedResponse = await caches.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }

        if (event.request.mode === 'navigate') {
          const cached = await caches.match('/');
          if (cached) return cached;
        }

        return new Response('Офлайн режим', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({
            'Content-Type': 'text/plain'
          })
        });
      })
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
