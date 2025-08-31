export function cm_slugifyWords(text){
  const stop = ['the','a','an','to','and','or','of','for','in','on','over','under','with','without','if','then','when','whenever','must','should','never','not','cannot'];
  const words = (String(text||'').toLowerCase().match(/[a-z0-9]+/g)||[]).filter(w=>!stop.includes(w));
  return words.join('_') || 'predicate';
}

export function cm_localP2S(prompt, constraints){
  const raw = String(prompt||'').trim(); const low = raw.toLowerCase();
  const hasIf = /\bif\b/i.test(low); const hasThen = /\bthen\b/i.test(low); const hasNever = /\bnever\b|\bcannot\b|\bmust not\b/i.test(low);
  let tce = ''; let tceEnglish = '';
  if(hasIf){
    let cond = raw.split(/\bif\b/i)[1] || raw; cond = cond.trim();
    let lhs = cond; let rhs = '';
    if(hasThen){ const parts = cond.split(/\bthen\b/i); lhs = (parts[0]||'').trim(); rhs = (parts[1]||'').trim(); }
    const lhsPred = cm_slugifyWords(lhs); const rhsPred = rhs ? cm_slugifyWords(rhs) : 'action';
    tce = `always (${lhsPred} -> ${rhsPred})`;
    tceEnglish = `At all times, if ${lhs.replace(/[.]+$/,'')} then ${rhs || 'the action occurs'}.`;
  } else if(hasNever){
    const pred = cm_slugifyWords(low.replace(/\bnever\b|\bcannot\b|\bmust not\b/ig,'').trim());
    tce = `always (not ${pred || 'send_data_over_network'})`;
    tceEnglish = `At all times, no data is sent over the network.`;
  } else {
    const pred = cm_slugifyWords(low);
    tce = `always (${pred})`;
    const sentence = raw.replace(/[.]+$/,'');
    tceEnglish = `At all times, ${sentence}.`;
  }
  if(constraints && constraints.forbid_colon){ tce = tce.replace(/:/g,' '); }
  if(constraints && constraints.require_prefix && !tce.toLowerCase().startsWith(constraints.require_prefix.toLowerCase())){ tce = `${constraints.require_prefix}${tce}`; }
  if(constraints && constraints.require_closing_paren && /always \(/i.test(tce) && !/\)$/.test(tce)){ tce += ')'; }
  return { tau: tce, tce: tceEnglish, explanation: '', reasons: ['Local fallback (offline)'], success: true, errors: [] };
}

export function cm_localValidate(tce){
  const txt = String(tce||''); const valid = /^\s*always\s*\(/i.test(txt) && (txt.split('(').length===txt.split(')').length);
  return { valid, errors: valid?[]:['Local validator: expected always(...) and balanced parentheses'] };
}

export function cm_localS2P(spec){
  const s = String(spec||''); const txt = s.replace(/\s+/g,' ');
  const explanation = `In plain English: ${txt.includes('->')? 'if the condition holds then the consequence holds' : txt}`;
  return { explanation, intent: 'causal', refined_prompt: '', refined_options: [] };
}

export function cm_localTce2Tau(text){
  const raw = String(text||'').trim(); const low = raw.toLowerCase();
  const hasIf = /\bif\b/i.test(low); const hasThen = /\bthen\b/i.test(low);
  if(hasIf){
    let cond = raw.split(/\bif\b/i)[1] || raw; cond = cond.trim();
    let lhs = cond; let rhs = '';
    if(hasThen){ const parts = cond.split(/\bthen\b/i); lhs = (parts[0]||'').trim(); rhs = (parts[1]||'').trim(); }
    const lhsPred = cm_slugifyWords(lhs); const rhsPred = rhs ? cm_slugifyWords(rhs) : 'action';
    return { tau: `always (${lhsPred} -> ${rhsPred})`, errors: [], success: true };
  }
  const pred = cm_slugifyWords(low);
  return { tau: `always (${pred})`, errors: [], success: true };
}

export function cm_localChat(messages){
  try{
    const last = Array.isArray(messages) && messages.length ? messages[messages.length-1] : null;
    const user = last && last.role==='user' ? last.content : '';
    const reply = user ? `Offline assistant (local): I received your message: "${String(user).slice(0,200)}". Try Prompt→Spec or Spec→Prompt for offline deterministic help.` : 'Offline assistant (local) available. Try Prompt→Spec or Spec→Prompt.';
    return { reply };
  }catch{ return { reply: 'Offline assistant (local).' }; }
}


