export async function onRequest(context) {
  const url = new URL(context.request.url);

  const key = url.pathname.slice(1); 

  if (!key || key === "index.html") {
    return context.next();
  }

  const object = await context.env.POKEMON_BUCKET.get(key);
  
  if (object === null) {
    return new Response("The file listed could not be found. Please try to access a different file. (Format: {dex_number}_{name}.png)", { status: 404 });
  }

  
  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set('Cache-Control', 'public, max-age=31536000, immutable'); // Cache for 1 year

  return new Response(object.body, { headers });
}