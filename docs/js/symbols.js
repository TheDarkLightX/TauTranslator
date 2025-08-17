// Client-only Symbol Language: mapping + palette augmentation
// Stores everything in localStorage. No network calls.

(function(){
  const STORAGE_KEY = 'tau_symbol_map_v1';
  const DEFAULT_MAPPINGS = [
    { id:'always', display:'🔁', canonical:'always ( )', scope:'tce', wordBoundary:false },
    { id:'and', display:'∧', canonical:' and ', scope:'tce', wordBoundary:true },
    { id:'or', display:'∨', canonical:' or ', scope:'tce', wordBoundary:true },
    { id:'not', display:'¬', canonical:'!', scope:'tce', wordBoundary:true },
    { id:'implies', display:'→', canonical:' -> ', scope:'tce', wordBoundary:true },
    { id:'forall', display:'∀', canonical:'all', scope:'tce', wordBoundary:true },
    { id:'exists', display:'∃', canonical:'ex', scope:'tce', wordBoundary:true },
    { id:'eq', display:'⩵', canonical:' = ', scope:'tce', wordBoundary:false },
    { id:'true', display:'⊤', canonical:'T', scope:'tce', wordBoundary:true },
    { id:'false', display:'⊥', canonical:'F', scope:'tce', wordBoundary:true },
    { id:'t', display:'⏱️', canonical:'[t]', scope:'tce', wordBoundary:false },
    { id:'tprev', display:'⏮️', canonical:'[t-1]', scope:'tce', wordBoundary:false }
  ];

  function $(id){ return document.getElementById(id); }

  function loadMap(){
    try{ const raw = localStorage.getItem(STORAGE_KEY); if(raw){ return JSON.parse(raw); } }catch{}
    return { version:1, name:'Default', mappings: DEFAULT_MAPPINGS.slice() };
  }
  function saveMap(map){ try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(map)); }catch{} }

  function buildRegexEntry(m){
    // Escape display text for regex
    const esc = m.display.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pat = m.wordBoundary ? `\\b${esc}\\b` : esc;
    return new RegExp(pat, 'g');
  }

  function compile(map){
    const forward = []; // display -> canonical (any)
    const reverse = []; // canonical -> display (any)
    const forwardBy = { tce:[], tau:[], both:[] };
    const reverseBy = { tce:[], tau:[], both:[] };
    // Sort by display length desc to prefer longest-first
    const ms = (map.mappings||[]).slice().sort((a,b)=> (b.display.length - a.display.length));
    for(const m of ms){
      const e = { r: buildRegexEntry(m), to: m.canonical, scope:(m.scope||'both') };
      forward.push(e);
      (forwardBy[e.scope]||forwardBy.both).push(e);
    }
    // Reverse: prefer longer canonical first
    const ms2 = (map.mappings||[]).slice().sort((a,b)=> (b.canonical.length - a.canonical.length));
    for(const m of ms2){
      const esc = m.canonical.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const e = { r: new RegExp(esc, 'g'), to: m.display, scope:(m.scope||'both') };
      reverse.push(e);
      (reverseBy[e.scope]||reverseBy.both).push(e);
    }
    return { forward, reverse, forwardBy, reverseBy };
  }

  function applyForward(text, compiled, scope){
    let t = String(text||'');
    const list = scope && compiled.forwardBy[scope] ? compiled.forwardBy[scope] : compiled.forward;
    for(const e of list){ t = t.replace(e.r, e.to); }
    return t;
  }
  function applyReverse(text, compiled, scope){
    let t = String(text||'');
    const list = scope && compiled.reverseBy[scope] ? compiled.reverseBy[scope] : compiled.reverse;
    for(const e of list){ t = t.replace(e.r, e.to); }
    return t;
  }

  // Hook into existing UI
  const map = loadMap();
  let compiled = compile(map);

  // Expose minimal API on window for other scripts
  window.__tau_symbols = {
    getMap: ()=>JSON.parse(JSON.stringify(map)),
    setMap: (m)=>{ Object.assign(map, m); saveMap(map); compiled = compile(map); renderPalette(); },
    toCanonical: (text, scope)=>applyForward(text, compiled, scope),
    toDisplay: (text, scope)=>applyReverse(text, compiled, scope)
  };

  // Wrap send flows if present
  function wrapRun(){
    const run = document.getElementById('runMid');
    if(!run) return;
    const orig = run.onclick;
    run.onclick = async (ev)=>{
      try{
        if(typeof window.getEditorText === 'function'){
          const raw = window.getEditorText();
          // Determine scope: infer from op/lang in page
          let scope = 'tce';
          try{
            const op = document.getElementById('op')?.value || 'p2s';
            if(op==='tce2tau' || op==='validate') scope='tce';
            else if(op==='s2p'){
              const txt = (typeof window.getEditorText==='function')? window.getEditorText() : '';
              const isTau = /(\[.*?\])/.test(txt) || /\bmodule\b/.test(txt);
              scope = isTau ? 'tau' : 'tce';
            } else if(op==='p2s') scope='tce';
          }catch{}
          const canonical = window.__tau_symbols.toCanonical(raw, scope);
          if(canonical !== raw && window.editor){
            window.editor.setValue(canonical);
          }
        }
      }catch{}
      return orig ? orig.call(run, ev) : undefined;
    };
  }

  function wrapOutputs(){
    const orig = window.setOutputs;
    if(typeof orig !== 'function') return;
    window.setOutputs = function(args){
      try{
        if(args && typeof args.tce === 'string'){ args.tce = window.__tau_symbols.toDisplay(args.tce, 'tce'); }
        if(args && typeof args.tau === 'string'){ args.tau = window.__tau_symbols.toDisplay(args.tau, 'tau'); }
      }catch{}
      return orig.apply(null, [args]);
    };
  }

  function renderPalette(){
    // Augment chat drawer area: add custom symbols row if present
    const drawer = document.getElementById('chatDrawer'); if(!drawer) return;
    const containerId = 'customSymbolRow';
    let row = document.getElementById(containerId);
    if(!row){
      const parent = drawer.querySelector('div[style*="border-top"] > div');
      if(!parent) return;
      row = document.createElement('div'); row.id = containerId;
      row.style.display = 'flex'; row.style.gap = '6px'; row.style.flexWrap = 'wrap'; row.style.marginTop = '6px';
      parent.appendChild(row);
    }
    row.innerHTML = '';
    const ms = (map.mappings||[]).slice(0, 24);
    for(const m of ms){
      const b = document.createElement('button'); b.className = 'btn'; b.textContent = m.display; b.title = `${m.display} → ${m.canonical}`;
      b.addEventListener('click', ()=>{
        const inp = document.getElementById('chatInput'); if(!inp) return; inp.value = (inp.value||'') + m.display; inp.focus();
      });
      row.appendChild(b);
    }
  }

  // Mini panel in Settings to export/import
  function injectSettings(){
    const adv = document.getElementById('controlsAdv'); if(!adv) return;
    const details = document.createElement('details');
    const sum = document.createElement('summary'); sum.textContent = 'Symbol Language (local)';
    details.appendChild(sum);
    const box = document.createElement('div'); box.style.display='flex'; box.style.flexDirection='column'; box.style.gap='6px'; box.style.marginTop='6px';
    const help = document.createElement('small'); help.textContent = 'Define custom symbols/emoji → canonical tokens. Stored locally; export/import packs as JSON.';
    const ta = document.createElement('textarea'); ta.id='symbolMapBox'; ta.style.minHeight='120px'; ta.style.background='#1a2238'; ta.style.color='#e8e8e8'; ta.style.border='1px solid #2a3350'; ta.style.borderRadius='8px'; ta.style.padding='8px';
    ta.value = JSON.stringify(map, null, 2);
    const row = document.createElement('div'); row.style.display='flex'; row.style.gap='6px';
    const btnSave = document.createElement('button'); btnSave.className='btn'; btnSave.textContent='Save'; btnSave.onclick=()=>{ try{ const m=JSON.parse(ta.value); window.__tau_symbols.setMap(m); alert('Saved'); }catch(e){ alert('Invalid JSON: '+e.message); } };
    const btnExport = document.createElement('button'); btnExport.className='btn'; btnExport.textContent='Export JSON'; btnExport.onclick=()=>{ const blob=new Blob([ta.value],{type:'application/json'}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='symbol_map.json'; document.body.appendChild(a); a.click(); a.remove(); };
    const btnImport = document.createElement('button'); btnImport.className='btn'; btnImport.textContent='Import JSON'; btnImport.onclick=()=>{ const i=document.createElement('input'); i.type='file'; i.accept='.json'; i.onchange=()=>{ const f=i.files&&i.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>{ try{ ta.value = String(r.result||''); const m=JSON.parse(ta.value); window.__tau_symbols.setMap(m); alert('Imported'); }catch(e){ alert('Invalid JSON: '+e.message); } }; r.readAsText(f); }; i.click(); };
    row.append(btnSave, btnExport, btnImport);
    box.append(help, ta, row); details.appendChild(box); adv.appendChild(details);
  }

  // Initialize
  wrapRun(); wrapOutputs(); renderPalette(); injectSettings();
})();


