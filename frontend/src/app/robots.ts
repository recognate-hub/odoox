import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
    return {
        rules: [
            {
                userAgent: '*',
                allow: ['/', '/llms.txt', '/llms-full.txt'],
                disallow: ['/userdashboard', '/admin', '/api/'],
            },
            {
                userAgent: ['ClaudeBot', 'Anthropic-AI', 'GPTBot', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended'],
                allow: ['/', '/llms.txt', '/llms-full.txt'],
                disallow: ['/userdashboard', '/admin', '/api/'],
            }
        ],
        sitemap: 'https://odoox.recognate.in/sitemap.xml',
        host: 'https://odoox.recognate.in',
    };
}
