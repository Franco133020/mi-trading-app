self.addEventListener('install', (e) => {
  console.log('[Service Worker] Instalado');
});

self.addEventListener('fetch', (e) => {
  e.respondWith(fetch(e.request));
});

self.addEventListener('push', (e) => {
  const data = e.data ? e.data.json() : {};
  const title = data.title || '🚨 Alerta Trading Bot';
  const options = {
    body: data.body || 'Señal detectada en tu estrategia',
    icon: 'https://assets.parqet.com/logos/symbol/UBER?format=jpg',
    vibrate: [200, 100, 200],
    sound: 'default'
  };
  e.waitUntil(self.registration.showNotification(title, options));
});
