import '../styles/globals.css';
import Layout from '../components/Layout';
import { ThemeProvider } from '../context/ThemeContext'; // Import ThemeProvider

function MyApp({ Component, pageProps }) {
  return (
    <ThemeProvider> {/* Wrap application with ThemeProvider */}
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </ThemeProvider>
  );
}

export default MyApp;
