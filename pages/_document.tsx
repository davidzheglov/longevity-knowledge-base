import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* Tailwind Play CDN for quick styling without installing */}
        <script src="https://cdn.tailwindcss.com"></script>
        <script dangerouslySetInnerHTML={{ __html: `
          tailwind.config = {
            theme: {
              extend: {
                colors: {
                  primary: '#7c3aed',
                  accent: '#06b6d4',
                  glass: 'rgba(255,255,255,0.06)'
                },
                borderRadius: {
                  'xl': '1rem'
                }
              }
            }
          }
        ` }} />
      </Head>
      <body className="antialiased bg-gradient-to-br from-gray-900 via-slate-900 to-black text-slate-100">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
