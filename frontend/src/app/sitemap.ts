import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
    const defaultPages = [
        { url: '', changeFrequency: 'weekly' as const, priority: 1 },
        { url: '/payment', changeFrequency: 'monthly' as const, priority: 0.8 },
        { url: '/login', changeFrequency: 'monthly' as const, priority: 0.5 },
    ];

    const baseUrl = 'https://odoox.recognate.in';
    const sitemapEntries: MetadataRoute.Sitemap = [];

    for (const page of defaultPages) {
        sitemapEntries.push({
            url: `${baseUrl}${page.url}`,
            lastModified: new Date(),
            changeFrequency: page.changeFrequency,
            priority: page.priority,
        });
    }

    return sitemapEntries;
}
