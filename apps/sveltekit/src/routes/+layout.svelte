<script>
  // basic global wrapper
  // Default lab API base for local dev; page lets users override
  if (typeof window !== 'undefined') {
    try {
      if (!localStorage.getItem('tau_api_base')) {
        localStorage.setItem('tau_api_base', 'http://127.0.0.1:8010')
      }
    } catch {}
  }
</script>

<slot />

<style>
  :global(html, body, #svelte) { height: 100%; }
  :global(body) { margin:0 }
</style>


