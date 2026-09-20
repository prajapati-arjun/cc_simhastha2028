const createNextIntlPlugin = require("next-intl/plugin");

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    // Sprint 1 seed data carries image_url: null. Remote hosts are not known yet,
    // so <img> is used rather than next/image with an open remotePatterns allowlist.
    remotePatterns: [],
  },
};

module.exports = withNextIntl(nextConfig);
