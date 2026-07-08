// Service Worker для TodayFlow PWA
const CACHE_NAME = 'todayflow-v1';
const RUNTIME_CACHE = 'todayflow-runtime-v1';

// Ресурсы для кеширования при установке
const PRECACHE_URLS = [
  '/',
  '/dashboard',
  '/practices',
  '/journal'
];

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

// Перехват запросов (Network First стратегия)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Пропускаем не-GET, сторонние домены, API и служебные Next.js-запросы.
  if (
    event.request.method !== 'GET' ||
    url.origin !== self.location.origin ||
    url.pathname.startsWith('/api/') ||
    url.pathname.startsWith('/_next/') ||
    url.searchParams.has('_rsc')
  ) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Клонируем ответ для кеша
        const responseToCache = response.clone();
        
        // Кешируем успешные ответы (только GET запросы, не API)
        if (response.status === 200 && event.request.method === 'GET' && !event.request.url.includes('/api/')) {
          caches.open(RUNTIME_CACHE).then((cache) => {
            cache.put(event.request, responseToCache).catch(() => {
              // Игнорируем ошибки кеширования
            });
          });
        }
        
        return response;
      })
      .catch(async () => {
        // Если сеть недоступна, пытаемся получить из кеша
        const cachedResponse = await caches.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }
        
        // Если это навигационный запрос и нет в кеше, возвращаем базовую страницу
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

// Обработка сообщений от клиента
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
