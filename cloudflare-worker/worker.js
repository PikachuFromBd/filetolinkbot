// FileToLink V3 — Cloudflare Worker Proxy
// This worker acts as a permanent proxy URL for the backend VPS.
// When VPS IP changes, just update the BACKEND_ORIGIN variable below.
// User-facing links NEVER change because they use the worker URL.

// ============================================
// ⚙️ CONFIGURATION — Update this when VPS changes
// ============================================
const BACKEND_ORIGIN = "http://YOUR_VPS_IP:8080";
// Example: const BACKEND_ORIGIN = "http://123.456.789.10:8080";
// Example: const BACKEND_ORIGIN = "https://yourdomain.com";
// ============================================

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Build the backend URL preserving path + query
    const backendUrl = BACKEND_ORIGIN + url.pathname + url.search;

    // Forward all headers from the original request
    const headers = new Headers(request.headers);
    headers.set("X-Forwarded-For", request.headers.get("CF-Connecting-IP") || "");
    headers.set("X-Forwarded-Proto", url.protocol.replace(":", ""));
    headers.set("X-Real-IP", request.headers.get("CF-Connecting-IP") || "");

    try {
      const response = await fetch(backendUrl, {
        method: request.method,
        headers: headers,
        body: request.method !== "GET" && request.method !== "HEAD"
          ? request.body
          : undefined,
      });

      // Clone response headers
      const responseHeaders = new Headers(response.headers);

      // Add CORS headers
      responseHeaders.set("Access-Control-Allow-Origin", "*");
      responseHeaders.set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
      responseHeaders.set("Access-Control-Allow-Headers", "Range");

      // For streaming responses, pipe the body directly
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });
    } catch (error) {
      return new Response(
        JSON.stringify({
          error: "Backend server is temporarily unavailable",
          message: "Please try again later",
        }),
        {
          status: 502,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  },
};
