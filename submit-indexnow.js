import { readFileSync, existsSync, readdirSync } from 'fs';
import { join } from 'path';

const HOST = 'www.globalaerosols.com';
const KEY = 'f7ca96b9b81b4e0b9a7c8bbfe79e77b0';
const KEY_LOCATION = `https://${HOST}/${KEY}.txt`;

async function getUrls() {
  const urls = new Set();

  // Find and parse all sitemap-*.xml files in dist/client (excluding sitemap-index.xml)
  const clientDir = join(process.cwd(), 'dist', 'client');
  if (existsSync(clientDir)) {
    try {
      const files = readdirSync(clientDir);
      for (const file of files) {
        if (file.startsWith('sitemap-') && file.endsWith('.xml') && file !== 'sitemap-index.xml') {
          const sitemapPath = join(clientDir, file);
          console.log(`Parsing sitemap file: ${file}`);
          const content = readFileSync(sitemapPath, 'utf8');
          const matches = content.matchAll(/<loc>(https:\/\/[^<]+)<\/loc>/g);
          for (const match of matches) {
            urls.add(match[1]);
          }
        }
      }
    } catch (err) {
      console.warn('Error reading or parsing sitemaps from dist/client:', err.message);
    }
  } else {
    console.warn(`Client build directory not found at: ${clientDir}`);
  }

  return Array.from(urls);
}

async function run() {
  const urlList = await getUrls();
  if (urlList.length === 0) {
    console.log('No URLs found to submit.');
    return;
  }

  console.log(`Submitting ${urlList.length} URLs to IndexNow...`);

  try {
    const res = await fetch('https://api.indexnow.org/indexnow', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: JSON.stringify({
        host: HOST,
        key: KEY,
        keyLocation: KEY_LOCATION,
        urlList,
      }),
    });

    if (res.ok) {
      console.log(`✅ IndexNow submission successful! (Status: ${res.status})`);
    } else {
      const text = await res.text();
      console.error(`❌ IndexNow submission failed: ${res.status} - ${text}`);
    }
  } catch (err) {
    console.error('❌ IndexNow submission error:', err);
  }
}

run();
