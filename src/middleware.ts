export async function onRequest(context: any, next: any) {
  const response = await next();

  // Only rewrite references in local development mode
  if (import.meta.env.DEV) {
    try {
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("text/html")) {
        const html = await response.text();
        // Rewrite cdn.globalaerosols.com to relative paths for local serving from public/
        const rewrittenHtml = html.replace(/https:\/\/cdn\.globalaerosols\.com/g, "");
        
        // Clone headers to bypass Cloudflare Worker's immutable headers guard
        const newHeaders = new Headers(response.headers);
        
        return new Response(rewrittenHtml, {
          status: response.status,
          headers: newHeaders
        });
      }
    } catch (err) {
      console.error("[Middleware Error]: Failed to read or rewrite response text.", err);
    }
  }

  return response;
}
