import { e as escape_html } from "../../chunks/escaping.js";
import "clsx";
import { v as pop, t as push } from "../../chunks/index.js";
const replacements = {
  translate: /* @__PURE__ */ new Map([
    [true, "yes"],
    [false, "no"]
  ])
};
function attr(name, value, is_boolean = false) {
  if (is_boolean) return "";
  const normalized = name in replacements && replacements[name].get(value) || value;
  const assignment = is_boolean ? "" : `="${escape_html(normalized, true)}"`;
  return ` ${name}${assignment}`;
}
function _page($$payload, $$props) {
  push();
  let apiBase = "";
  let byok = "";
  let reasons = "";
  $$payload.out.push(`<div class="wrap svelte-demyh7"><div class="bar svelte-demyh7"><h1>Translator (SvelteKit + CM6)</h1> <div class="stack svelte-demyh7"><small>API</small> <input${attr("value", apiBase)} placeholder="https://tau-translator-api.fly.dev" class="svelte-demyh7"/> <button class="btn svelte-demyh7">Save</button></div> <div class="stack svelte-demyh7"><small>BYOK</small> <input type="password"${attr("value", byok)} placeholder="sk-or-v1-..." class="svelte-demyh7"/> <button class="btn svelte-demyh7">Save</button></div> <button id="btnExamples" class="btn svelte-demyh7">Examples</button> <button id="btnSettings" class="btn svelte-demyh7">Settings</button> <button id="btnAssist" class="btn primary svelte-demyh7">Assist</button></div> <div class="card svelte-demyh7" style="margin-bottom:10px"><div style="display:flex; gap:10px; flex-wrap:wrap"><button id="btnTranslate" class="btn primary svelte-demyh7">Translate</button></div></div> <div class="row svelte-demyh7"><div class="card svelte-demyh7"><label for="inFallback">Input</label> <div id="cmIn" style="display:none"></div> <textarea placeholder="If a payment is approved then the order is shipped." class="svelte-demyh7">If a payment is approved then the order is shipped.</textarea></div> <div class="card svelte-demyh7"><div style="display:flex; gap:8px; align-items:center"><label>Output</label> <div style="margin-left:auto; display:flex; gap:6px"><button class="btn svelte-demyh7">Tau</button> <button class="btn svelte-demyh7">TCE</button> <button class="btn svelte-demyh7">Expl</button></div></div> <div id="cmOut" style="display:none"></div> <textarea class="mono svelte-demyh7" readonly></textarea></div></div> <div class="card svelte-demyh7" style="margin-top:14px"><label>Reasons / Errors</label> <div class="mono svelte-demyh7">${escape_html(reasons)}</div></div> `);
  {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--> `);
  {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--> `);
  {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--></div>`);
  pop();
}
export {
  _page as default
};
