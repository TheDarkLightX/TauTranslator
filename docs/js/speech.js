// Client-only Speech-to-Text (Web Speech API) for Prompt/Chat
// No audio leaves the device. If unsupported, UI disables mic.

(function(){
  const hasSpeech = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  let rec = null; let listening = false;
  const STORAGE_KEY = 'tau_stt_lang_v1';

  function $(id){ return document.getElementById(id); }

  function ensureMicButtons(){
    // Add mic next to chat input
    const chatRow = (function(){
      const d = document.getElementById('chatDrawer'); if(!d) return null;
      const rows = d.querySelectorAll('div[style*="display:flex"][style*="gap:8px"]');
      return rows && rows[rows.length-1] ? rows[rows.length-1] : null;
    })();
    if(chatRow && !document.getElementById('chatMic')){
      const b = document.createElement('button'); b.className='btn'; b.id='chatMic'; b.textContent='🎙️'; b.title='Voice input (client-only)';
      if(!hasSpeech){ b.disabled=true; b.title='Voice input not supported by this browser'; }
      b.addEventListener('click', ()=>toggleChatRec());
      chatRow.insertBefore(b, chatRow.querySelector('#chatSend'));
    }
    // Inject language selector in Advanced settings
    ensureLangSelector();
  }

  function startRec(onText){
    if(!hasSpeech || listening) return;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    rec = new SR(); rec.lang = (loadLang() || navigator.language || 'en-US'); rec.interimResults = true; rec.continuous = true;
    let lastFinal = '';
    rec.onresult = (e)=>{
      let interim=''; let finalText='';
      for(let i=e.resultIndex; i<e.results.length; i++){
        const res = e.results[i];
        if(res.isFinal){ finalText += res[0].transcript; }
        else { interim += res[0].transcript; }
      }
      if(finalText && finalText!==lastFinal){ lastFinal = finalText; onText(finalText, false); }
      if(interim){ onText(interim, true); }
    };
    rec.onerror = ()=>stopRec();
    rec.onend = ()=>{ listening=false; updateMicUI(false); };
    rec.start(); listening = true; updateMicUI(true);
  }
  function stopRec(){ try{ if(rec){ rec.stop(); } }catch{} listening=false; updateMicUI(false); }

  function updateMicUI(active){ const b=$('chatMic'); if(!b) return; b.textContent = active? '🛑' : '🎙️'; b.title = active? 'Stop voice' : 'Voice input (client-only)'; }

  function toggleChatRec(){
    if(listening) return stopRec();
    const inp = $('chatInput'); if(!inp) return;
    let lastInterim='';
    startRec((text, interim)=>{
      if(interim){ lastInterim = text; inp.placeholder = '🎤 ' + text; }
      else { inp.value = (inp.value||'') + (text.endsWith(' ')? text : text+' '); inp.placeholder='Ask about your spec or request a change...'; }
    });
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    ensureMicButtons();
  });

  function loadLang(){ try{ return localStorage.getItem(STORAGE_KEY) || ''; }catch{ return ''; } }
  function saveLang(v){ try{ localStorage.setItem(STORAGE_KEY, v||''); }catch{} }
  function ensureLangSelector(){
    const adv = document.getElementById('controlsAdv'); if(!adv) return;
    if(document.getElementById('sttLangRow')) return;
    const det = document.createElement('details');
    const sum = document.createElement('summary'); sum.textContent='Voice (client-only)'; det.appendChild(sum);
    const row = document.createElement('div'); row.id='sttLangRow'; row.style.display='flex'; row.style.gap='8px'; row.style.marginTop='6px';
    const label = document.createElement('label'); label.textContent='STT Language'; label.style.display='flex'; label.style.flexDirection='column';
    const sel = document.createElement('select'); sel.id='sttLang'; sel.style.minWidth='180px';
    const langs = [
      'en-US','en-GB','es-ES','es-MX','fr-FR','de-DE','it-IT','pt-PT','pt-BR','ja-JP','ko-KR','zh-CN','zh-TW','ru-RU','ar-SA'
    ];
    const cur = loadLang() || (navigator.language||'en-US');
    langs.forEach(l=>{ const o=document.createElement('option'); o.value=l; o.textContent=l; if(l===cur) o.selected=true; sel.appendChild(o); });
    label.appendChild(sel);
    const note = document.createElement('small'); note.textContent = hasSpeech? 'Uses Web Speech API; no audio leaves your device.' : 'Web Speech API not supported in this browser.';
    row.appendChild(label); row.appendChild(note); det.appendChild(row); adv.appendChild(det);
    sel.addEventListener('change', ()=> saveLang(sel.value));
  }
})();


