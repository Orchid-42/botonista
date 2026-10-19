/* Botonista offline cache. The version changes whenever the game changes. */
const CACHE='botonista-5087be65';
const FILES=["./", "index.html", "manifest.webmanifest", "icons/apple-touch-icon-puck.png", "icons/icon-192-puck.png", "icons/icon-512-puck.png"];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;
  const url=new URL(req.url);
  // fonts: keep a copy so the game looks right offline
  if(url.host.includes('fonts.googleapis.com')||url.host.includes('fonts.gstatic.com')){
    e.respondWith(caches.open(CACHE).then(c=>c.match(req).then(hit=>hit||fetch(req).then(r=>{c.put(req,r.clone());return r}).catch(()=>hit))));return}
  if(url.origin!==location.origin)return;
  // the page itself: network first so updates arrive, the saved copy when offline
  if(req.mode==='navigate'){e.respondWith(fetch(req).then(r=>{caches.open(CACHE).then(c=>c.put('index.html',r.clone()));return r}).catch(()=>caches.match('index.html')));return}
  e.respondWith(caches.match(req).then(hit=>hit||fetch(req)));
});
