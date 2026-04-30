# Browser extension (planned)

A 50-line Plasmo extension is the cleanest way to get one-click "save current
tab" on every desktop browser. Until that lands, you can pin a bookmarklet:

```javascript
javascript:(()=>{const u=encodeURIComponent(location.href),t=encodeURIComponent(document.title||'');open(`https://YOUR-PWA.vercel.app/share?url=${u}&title=${t}`,'_blank');})();
```

Drag the bookmarklet to your bookmarks bar; clicking it on any page opens the
share landing page which immediately POSTs to `/api/ingest`.
