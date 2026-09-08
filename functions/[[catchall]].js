export async function onRequest(context) {
  const url = new URL(context.request.url);
  const key = url.pathname.slice(1); 

  
  if (!key || key === "index.html") {
    return context.next();
  }

  const cache = caches.default;
  

  let response = await cache.match(context.request);
  if (response) {
    return response;
  }


  const object = await context.env.POKEMON_BUCKET.get(key);
  
  if (object === null) {
    return new Response(
      "The file listed could not be found. Please try to access a different file. (Format: {dex_number}_{name}.png)", 
      { status: 404 }
    );
  }


  const headers = new Headers();
  object.writeHttpMetadata(headers);


  headers.set('Cache-Control', 'public, max-age=31536000, s-maxage=31536000, immutable');
  if (object.httpEtag) {
    headers.set('ETag', object.httpEtag);
  }


  response = new Response(object.body, { 
    status: 200,
    headers 
  });


  context.waitUntil(cache.put(context.request, response.clone()));

  
  return response;
}