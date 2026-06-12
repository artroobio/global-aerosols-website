export async function onRequest(context: any, next: any) {
  const response = await next();

  // Detect if requested from a local address
  let isLocal = false;
  try {
    const url = new URL(context.request.url);
    const host = url.hostname.toLowerCase();
    isLocal = host === "localhost" || 
              host === "127.0.0.1" || 
              host === "[::1]" || 
              host.startsWith("192.168.") || 
              host.startsWith("10.") || 
              host.startsWith("172.");
  } catch (e) {
    // Fallback to DEV flag if parsing fails
  }

  // Rewrite references in local development mode or when running on localhost
  if (import.meta.env.DEV || isLocal) {
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
