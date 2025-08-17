// Client-only Speech-to-Text (Web Speech API) for Prompt/Chat
// No audio leaves the device. If unsupported, UI disables mic.

(function(){
  const hasSpeech = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  let rec = null; let listening = false;

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
    // Add mic next to main run button row if desired (skipped to keep UI minimal)
  }

  function startRec(onText){
    if(!hasSpeech || listening) return;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    rec = new SR(); rec.lang = (navigator.language || 'en-US'); rec.interimResults = true; rec.continuous = true;
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
})();


