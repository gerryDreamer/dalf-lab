// Changer le numéro de version à chaque mise à jour de l'appli pour renouveler le cache.
const C = "dalf-v8", A = [...] // Change v7 en v8 ou v9
const A = [
  "./",
  "index.html",
  "app.css",
  "app.js",
  "manifest.json",
  "icon-192.png",
  "icon-512.png",
  "data/edito-c1.lecons.json",
  "profiles/edito-c1.json",
  "profiles/cosmopolite-5.json"
];

self.addEventListener("install", e =>
  e.waitUntil(
    caches.open(C).then(c => c.addAll(A)).then(() => self.skipWaiting())
  )
);

self.addEventListener("activate", e =>
  e.waitUntil(
    caches.keys()
      .then(k => Promise.all(k.filter(x => x !== C).map(x => caches.delete(x))))
      .then(() => self.clients.claim())
  )
);

self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET") return;
  const u = new URL(r.url);
  const ok = u.origin === location.origin || u.hostname === "cdnjs.cloudflare.com";
  if (!ok) return;

  const keep = n => {
    if (n && n.ok) {
      const cp = n.clone();
      caches.open(C).then(c => c.put(r, cp));
    }
    return n;
  };

  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then(keep).catch(() => caches.match("index.html")));
    return;
  }
  e.respondWith(caches.match(r).then(h => h || fetch(r).then(keep)));
});
