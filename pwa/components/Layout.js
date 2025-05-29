import Link from 'next/link';
import Head from 'next/head';
import ThemeToggleButton from './ThemeToggleButton'; // Import the toggle button

const Layout = ({ children }) => {
  return (
    <>
      <Head>
        <title>Tau Translator version Omega</title>
        <meta name="description" content="Tau Translator version Omega PWA" />
        <link rel="icon" href="/favicon.ico" /> {/* Placeholder, real favicon needed */}
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0070f3" />
      </Head>
      <nav style={{ 
        background: 'var(--nav-background)', // Use CSS variable for nav background
        padding: '1rem',
        color: 'var(--nav-text-color)', // Use CSS variable for nav text
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>
          <Link href="/" style={{ color: 'var(--nav-text-color)', textDecoration: 'none' }}>
            Tau Translator version Omega
          </Link>
        </h1>
        <div style={{ display: 'flex', gap: '20px' }}>
          <Link href="/" style={{ color: 'var(--nav-text-color)', textDecoration: 'none', padding: '5px 10px' }}>File</Link>
          <span style={{ color: 'var(--nav-text-color)', opacity: 0.7, padding: '5px 10px', cursor: 'default' }}>Edit</span> {/* Placeholder */}
          <span style={{ color: 'var(--nav-text-color)', opacity: 0.7, padding: '5px 10px', cursor: 'default' }}>View</span> {/* Placeholder */}
          <Link href="/settings/llm" style={{ color: 'var(--nav-text-color)', textDecoration: 'none', padding: '5px 10px' }}>Settings</Link>
          <ThemeToggleButton />
        </div>
      </nav>
      <main className="container">
        {children}
      </main>
      <footer style={{
        textAlign: 'center',
        padding: '2rem 0',
        marginTop: '2rem',
        borderTop: '1px solid var(--border-color)'
      }}>
      </footer>
    </>
  );
};

export default Layout;
