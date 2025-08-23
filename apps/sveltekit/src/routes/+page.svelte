<script>
  import { onMount } from 'svelte'
  import { EditorView, keymap, drawSelection, highlightActiveLine } from '@codemirror/view'
  import { EditorState } from '@codemirror/state'
  import { defaultHighlightStyle, syntaxHighlighting } from '@codemirror/language'
  import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
  import { autocompletion } from '@codemirror/autocomplete'

  let apiBase = ''
  let byok = ''
  let reasons = ''
  let outView = 'tau'
  let outTau = ''
  let outTce = ''
  let outExplanation = ''
  let inFallback
  let outFallback
  let cmInEl
  let cmOutEl
  let inView = null
  let outViewInst = null
  const SAMPLE = 'If a payment is approved then the order is shipped.'
  let showExamples = false
  let showSettings = false
  let showAssist = false
  let chatInput = ''
  let chatThread = []
  const EXAMPLES = [
    { id:'p2s_basic_1', title:'Payment approved → order shipped', text:'If a payment is approved then the order is shipped.' },
    { id:'privacy_invariant', title:'Privacy: never send private data', text:'Never send private data over the network.' }
  ]

  function save(k,v){ try{ localStorage.setItem(k,v) }catch{}
  }
  function load(k, d=''){ try{ return localStorage.getItem(k) || d }catch{ return d } }
  function base(){ const v = apiBase.trim(); if(!v) throw new Error('Set API base'); return v.replace(/\/$/,'') }

  async function post(path, body){
    const url = base() + path
    const headers = { 'Content-Type':'application/json' }
    if(byok && load('tau_privacy_mode','0')!=='1'){ headers['X-OpenRouter-Key'] = byok }
    try{ window.__tau_last_call = { url, path, headers: {...headers}, body: JSON.parse(JSON.stringify(body)) } }catch{}
    const res = await fetch(url, { method:'POST', headers, body: JSON.stringify(body) })
    if(!res.ok) throw new Error('HTTP '+res.status)
    return await res.json()
  }

  async function runTranslate(){
    reasons = ''
    const input = (inView ? inView.state.doc.toString() : ((inFallback && inFallback.value)||'')).trim()
    if(!input){ reasons = 'Enter input'; return }
    const body = { prompt: input, mode:'assist' }
    try{
      const r = await post('/llm/prompt-to-spec', body)
      outTau = r.tau || ''
      outTce = r.tce || ''
      outExplanation = r.explanation || ''
      outView = outTau?.trim() ? 'tau' : (outTce?.trim()? 'tce' : 'expl')
      updateOut()
    }catch(e){ reasons = String((e && e.message) ? e.message : e) }
  }

  async function chatSend(){
    const text = (chatInput||'').trim(); if(!text) return;
    chatThread = [...chatThread, {role:'user', content:text}]
    chatInput = ''
    try{
      const payload = { threadId:null, messages: chatThread.map(m=>({role:m.role, content:m.content})), mode:'assist' }
      try{ window.__tau_last_call = { path:'/llm/chat', body: payload } }catch{}
      const r = await post('/llm/chat', payload)
      chatThread = [...chatThread, {role:'assistant', content: r.reply||''}]
      if(r.tce || r.tau){ outTce = r.tce||''; outTau = r.tau||''; outView = outTau? 'tau' : (outTce? 'tce' : outView); updateOut() }
    }catch(e){ chatThread = [...chatThread, {role:'assistant', content: 'Error: '+String((e&&e.message)?e.message:e)}] }
  }

  function loadExample(ex){ if(!ex) return; const v = ex.text||''; if(inView){ inView.dispatch({ changes:{ from:0, to: inView.state.doc.length, insert: v } }) } else if(inFallback){ inFallback.value = v } }
  function runExample(ex){ loadExample(ex); runTranslate() }

  function updateOut(){
    const v = outView==='tau' ? outTau : (outView==='tce'? outTce : outExplanation)
    try{
      if(!outViewInst){ return }
      outViewInst.dispatch({ changes:{ from:0, to: outViewInst.state.doc.length, insert: v||'' } })
    }catch{ if(outFallback) outFallback.value = v||'' }
  }

  onMount(()=>{
    apiBase = load('tau_api_base','https://tau-translator-api.fly.dev')
    byok = load('tau_byok_openrouter','')
    try{
      const initialDoc = ((inFallback && inFallback.value) || SAMPLE)
      inView = new EditorView({
        state: EditorState.create({
          doc: initialDoc,
          extensions: [
            history(), keymap.of([...defaultKeymap, ...historyKeymap]),
            drawSelection(), highlightActiveLine(), syntaxHighlighting(defaultHighlightStyle),
            autocompletion()
          ]
        }),
        parent: cmInEl
      })
      cmInEl.style.display = ''
      if(inFallback){ inFallback.value = initialDoc; inFallback.style.display = 'none' }
    }catch{}
    try{
      outViewInst = new EditorView({
        state: EditorState.create({
          doc: '',
          extensions: [ EditorView.editable.of(false), drawSelection(), highlightActiveLine(), syntaxHighlighting(defaultHighlightStyle) ]
        }),
        parent: cmOutEl
      })
      cmOutEl.style.display = ''
      if(outFallback) outFallback.style.display = 'none'
    }catch{}
    try{ window.TAU_UI_READY = true }catch{}
  })
</script>

<div class="wrap">
  <div class="bar">
    <h1>Translator (SvelteKit + CM6)</h1>
    <div class="stack">
      <small>API</small>
      <input bind:value={apiBase} placeholder="https://tau-translator-api.fly.dev" />
      <button class="btn" on:click={() => save('tau_api_base', apiBase)}>Save</button>
    </div>
    <div class="stack">
      <small>BYOK</small>
      <input type="password" bind:value={byok} placeholder="sk-or-v1-..." />
      <button class="btn" on:click={() => save('tau_byok_openrouter', byok)}>Save</button>
    </div>
    <button id="btnExamples" class="btn" on:click={() => { showExamples = true }}>Examples</button>
    <button id="btnSettings" class="btn" on:click={() => { showSettings = !showSettings }}>Settings</button>
    <button id="btnAssist" class="btn primary" on:click={() => { showAssist = true }}>Assist</button>
  </div>

  <div class="card" style="margin-bottom:10px">
    <div style="display:flex; gap:10px; flex-wrap:wrap">
      <button id="btnTranslate" class="btn primary" on:click={runTranslate}>Translate</button>
    </div>
  </div>

  <div class="row">
    <div class="card">
      <label for="inFallback">Input</label>
      <div id="cmIn" bind:this={cmInEl} style="display:none"></div>
      <textarea bind:this={inFallback} placeholder="If a payment is approved then the order is shipped.">If a payment is approved then the order is shipped.</textarea>
    </div>
    <div class="card">
      <div style="display:flex; gap:8px; align-items:center">
        <label>Output</label>
        <div style="margin-left:auto; display:flex; gap:6px">
          <button class="btn" on:click={() => { outView='tau'; updateOut() }}>Tau</button>
          <button class="btn" on:click={() => { outView='tce'; updateOut() }}>TCE</button>
          <button class="btn" on:click={() => { outView='expl'; updateOut() }}>Expl</button>
        </div>
      </div>
      <div id="cmOut" bind:this={cmOutEl} style="display:none"></div>
      <textarea class="mono" bind:this={outFallback} readonly></textarea>
    </div>
  </div>

  <div class="card" style="margin-top:14px">
    <label>Reasons / Errors</label>
    <div class="mono">{reasons}</div>
  </div>

  {#if showExamples}
  <div class="drawer left">
    <div class="drawer-head"><strong>Examples</strong><button class="btn" on:click={() => { showExamples=false }}>Close</button></div>
    <div class="drawer-body">
      {#each EXAMPLES as ex}
        <div class="ex">
          <div class="ex-title">{ex.title}</div>
          <div class="ex-actions">
            <button class="btn" on:click={() => loadExample(ex)}>Load</button>
            <button class="btn" on:click={() => runExample(ex)}>Load + Translate</button>
          </div>
        </div>
      {/each}
    </div>
  </div>
  {/if}

  {#if showSettings}
  <div class="panel">
    <details open>
      <summary>Privacy</summary>
      <label><input type="checkbox" checked={load('tau_privacy_mode','0')==='1'} on:change={(e)=>save('tau_privacy_mode', e.currentTarget.checked?'1':'0')} /> Privacy mode (strip BYOK/grammar)</label>
    </details>
  </div>
  {/if}

  {#if showAssist}
  <div class="drawer right">
    <div class="drawer-head"><strong>Assistant</strong><button class="btn" on:click={() => { showAssist=false }}>Close</button></div>
    <div class="drawer-body" style="gap:10px">
      <div class="chat-list">
        {#each chatThread as m}
          <div class="chat-msg" data-role={m.role}><div class="who">{m.role}</div><div>{m.content}</div></div>
        {/each}
      </div>
      <div class="chat-row">
        <input id="assistInput" placeholder="Ask about your spec..." bind:value={chatInput} />
        <button id="assistSend" class="btn primary" on:click={chatSend}>Send</button>
      </div>
    </div>
  </div>
  {/if}
</div>

<style>
  :root { --bg:#0f0f1e; --card:#13132a; --fg:#e8e8e8; --muted:#a3a3a3; --b:#1f2040; --brand:#00d4ff; }
  body{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; background: linear-gradient(135deg, #0f0f1e, #1a1a2e); color: var(--fg); }
  .wrap { max-width: 1100px; margin: 28px auto; padding: 0 16px; }
  .bar { display:flex; align-items:center; gap:12px; margin-bottom:12px }
  .stack { display:flex; align-items:center; gap:8px }
  .btn { padding: 8px 10px; border-radius: 10px; border:1px solid rgba(255,255,255,0.12); background: #18203a; color: var(--fg); cursor: pointer; }
  .btn.primary { background: linear-gradient(45deg, var(--brand), #0099ff); border-color: transparent; color: #081018; font-weight: 700; }
  input, textarea { background: var(--card); color: var(--fg); border: 1px solid var(--b); border-radius: 10px; padding: 8px 10px; }
  .row { display:grid; grid-template-columns: 1fr 1fr; gap: 14px }
  .card { background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 12px }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: 13px; white-space: pre-wrap; word-break: break-word }
  .drawer { position:fixed; top:0; height:100vh; width:360px; background:#101725; border:1px solid rgba(255,255,255,0.12); box-shadow: 0 0 20px rgba(0,0,0,0.4); display:flex; flex-direction:column; z-index:9999 }
  .drawer.left { left:0 }
  .drawer.right { right:0; width:420px }
  .drawer-head { display:flex; align-items:center; justify-content:space-between; padding:10px; border-bottom:1px solid rgba(255,255,255,0.12) }
  .drawer-body { flex:1; overflow:auto; padding:10px; display:flex; flex-direction:column }
  .panel { display:flex; flex-direction:column; gap:8px; padding:10px; border:1px solid rgba(255,255,255,0.12); border-radius:12px; margin-top:10px }
  .ex { border:1px solid rgba(255,255,255,0.12); border-radius:8px; padding:8px; margin-bottom:8px }
  .ex-title { font-weight:600 }
  .ex-actions { display:flex; gap:6px; margin-top:6px }
  .chat-list { flex:1; overflow:auto; display:flex; flex-direction:column; gap:8px }
  .chat-msg { border:1px solid rgba(255,255,255,0.12); border-radius:8px; padding:8px }
  .chat-msg .who { font-weight:600; color:#00d4ff }
  .chat-row { display:flex; gap:8px }
</style>


