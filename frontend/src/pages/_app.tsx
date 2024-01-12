import type { AppProps } from 'next/app'

import '@/styles/globals.css'
import NavbarLeft from '@/nav/NavbarLeft';
import NavbarTop from '@/nav/NavbarTop';

export default function MyApp({ Component, pageProps, router }: AppProps) {
  console.log("router.pathname", router.pathname)
  if (router.pathname.search('/overlays/') >= 0)
    return <Component {...pageProps} />;

  const topNavbarHeight = 40;
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Sidebar */}
      <aside className="border-r border-gray-200">
        <NavbarLeft /> {/* Your left navbar component */}
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Navbar */}
        <header>
          <NavbarTop height={topNavbarHeight} /> {/* Your top navbar component */}
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <Component {...pageProps} />
        </main>
      </div>
    </div>
  );
}
