// @ts-check
import { defineConfig, envField } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import cloudflare from '@astrojs/cloudflare';

// Astro configuration - Triggering deployment rebuild
export default defineConfig({
  site: 'https://www.globalaerosols.com',
  trailingSlash: 'always',
  output: 'static',
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'hover',
  },
  adapter: cloudflare({
    platformProxy: { enabled: true },
  }),
  env: {
    schema: {
      RESEND_API_KEY: envField.string({ context: 'server', access: 'secret', optional: true }),
      RESEND_SENDER_EMAIL: envField.string({ context: 'server', access: 'secret', optional: true }),
      CONTACT_EMAIL_RECIPIENT: envField.string({ context: 'server', access: 'secret', optional: true }),
    },
  },
  integrations: [
    sitemap({
      filter: (page) =>
        !page.includes('/admin/') &&
        !page.includes('/login/') &&
        !page.includes('/dashboard/') &&
        !page.includes('/cart/') &&
        !page.includes('/checkout/') &&
        !page.includes('/store/search/'),
    }),
  ],
});
