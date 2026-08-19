import type { Metadata } from "next";
import { getMessages, getTranslations } from 'next-intl/server';
import { NextIntlClientProvider } from 'next-intl';
import { routing } from '@/i18n/routing';
import { notFound } from 'next/navigation';
import "../globals.css";

// Dynamic metadata based on locale
export async function generateMetadata({
  params: paramsPromise
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const params = await paramsPromise;
  const locale = params.locale;
  const t = await getTranslations({locale, namespace: 'Index'});

  return {
    title: t('title'),
    description: t('description'),
    keywords: ["Odoo", "Claude", "AI", "MCP", "Model Context Protocol", "ERP Integration", "Generative AI", "Anthropic"],
    authors: [{ name: "OdooX Team" }],
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
    openGraph: {
      title: t('title'),
      description: t('description'),
      url: `https://odoox.com/${locale}`,
      siteName: "OdooX",
      images: [
        {
          url: "https://odoox.com/og-image.jpg",
          width: 1200,
          height: 630,
          alt: "OdooX AI Gateway Dashboard",
        },
      ],
      locale: locale === 'en' ? 'en_US' : locale, // Add mappings if needed
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: t('title'),
      description: t('description'),
      images: ["https://odoox.com/og-image.jpg"],
    },
    alternates: {
      canonical: `https://odoox.com/${locale}`,
      languages: {
        'en': 'https://odoox.com/en',
        'es': 'https://odoox.com/es',
        'fr': 'https://odoox.com/fr',
        'de': 'https://odoox.com/de',
      },
    },
    icons: {
      icon: [
        { url: '/favicon.ico', sizes: 'any' },
        { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
        { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
        { url: '/android-chrome-192x192.png', sizes: '192x192', type: 'image/png' },
        { url: '/android-chrome-512x512.png', sizes: '512x512', type: 'image/png' },
      ],
      apple: [
        { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
      ],
    },
    manifest: '/site.webmanifest',
  };
}

export default async function LocaleLayout({
  children,
  params: paramsPromise
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>
}) {
  const params = await paramsPromise;
  const locale = params.locale;
  // Ensure that the incoming `locale` is valid
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  // Providing all messages to the client side
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
