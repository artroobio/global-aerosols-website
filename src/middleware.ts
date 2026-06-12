import { defineMiddleware } from "astro:middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  const response = await next();

  // Only rewrite references in local development mode
  if (import.meta.env.DEV) {
    try {
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("text/html")) {
        const html = await response.text();
        // Rewrite cdn.globalaerosols.com to relative paths for local serving from public/
        const rewrittenHtml = html.replace(/https:\/\/cdn\.globalaerosols\.com/g, "");
        
        return new Response(rewrittenHtml, {
          status: response.status,
          headers: response.headers
        });
      }
    } catch (err) {
      console.error("[Middleware Error]: Failed to read or rewrite response text.", err);
    }
  }

  return response;
});
