import { MetadataRoute } from 'next';
import { routing } from '@/i18n/routing';

export default function sitemap(): MetadataRoute.Sitemap {
    const defaultPages = [
        { url: '', changeFrequency: 'weekly' as const, priority: 1 },
        { url: '/payment', changeFrequency: 'monthly' as const, priority: 0.8 },
        { url: '/login', changeFrequency: 'monthly' as const, priority: 0.5 },
    ];

    const baseUrl = 'https://odoox.recognate.in';
    const sitemapEntries: MetadataRoute.Sitemap = [];

    for (const page of defaultPages) {
        for (const locale of routing.locales) {
            sitemapEntries.push({
                url: `${baseUrl}/${locale}${page.url}`,
                lastModified: new Date(),
                changeFrequency: page.changeFrequency,
                priority: page.priority,
                alternates: {
                    languages: {
                        'en': `${baseUrl}/en${page.url}`,
                        'es': `${baseUrl}/es${page.url}`,
                        'fr': `${baseUrl}/fr${page.url}`,
                        'de': `${baseUrl}/de${page.url}`,
                    }
                }
            });
        }
    }

    return sitemapEntries;
}
