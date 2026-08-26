import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
    const defaultPages = [
        { url: '', changeFrequency: 'daily' as const, priority: 1.0 },
        { url: '/payment', changeFrequency: 'weekly' as const, priority: 0.9 },
        { url: '/login', changeFrequency: 'monthly' as const, priority: 0.7 },
        { url: '/production-planning', changeFrequency: 'weekly' as const, priority: 0.8 },
        { url: '/llms.txt', changeFrequency: 'daily' as const, priority: 0.9 },
        { url: '/llms-full.txt', changeFrequency: 'daily' as const, priority: 0.9 },
    ];

    const baseUrl = 'https://odoox.recognate.in';
    const sitemapEntries: MetadataRoute.Sitemap = [];

    for (const page of defaultPages) {
        sitemapEntries.push({
            url: `${baseUrl}${page.url}`,
            lastModified: new Date(),
            changeFrequency: page.changeFrequency,
            priority: page.priority,
            alternates: {
                languages: {
                    'en-US': `${baseUrl}${page.url}`,
                    'en-GB': `${baseUrl}${page.url}`,
                    'en-IN': `${baseUrl}${page.url}`,
                    'de-DE': `${baseUrl}${page.url}`,
                    'fr-FR': `${baseUrl}${page.url}`,
                    'x-default': `${baseUrl}${page.url}`,
                }
            }
        });
    }

    return sitemapEntries;
}
