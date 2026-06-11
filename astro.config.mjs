// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import cloudflare from '@astrojs/cloudflare';

// Astro configuration - Triggering deployment rebuild
export default defineConfig({
  site: 'https://www.globalformulation.com',
  trailingSlash: 'always',
  output: 'server',
  adapter: cloudflare({
    platformProxy: { enabled: true },
  }),
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
