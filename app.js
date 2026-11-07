// ═════════════════════════════════════════════════════════════
//  DALF Lab — app.js  (1/3 : état, helpers, données)
// ═════════════════════════════════════════════════════════════

const PV = {
  gemini:     { n:"Google Gemini",             u:"",                                m:"gemini-flash-latest" },
  mistral:    { n:"Mistral",                   u:"https://api.mistral.ai/v1",       m:"mistral-small-latest" },
  groq:       { n:"Groq",                      u:"https://api.groq.com/openai/v1",  m:"llama-3.3-70b-versatile" },
  openrouter: { n:"OpenRouter",                u:"https://openrouter.ai/api/v1",    m:"" },
  deepseek:   { n:"DeepSeek",                  u:"https://api.deepseek.com",        m:"deepseek-chat" },
  autre:      { n:"Autre (compatible OpenAI)", u:"",                                m:"" }
};

const DEFAULTS = { xp:0, done:{}, ok:{}, txt:"", hl:{}, w:{}, m:{}, res:[], gen:[], ai:null, xo:0 };
let S = Object.assign({}, DEFAULTS);
try { Object.assign(S, JSON.parse(localStorage.getItem("dalf1") || "{}")); } catch (e) {}
if (!Array.isArray(S.gen)) S.gen = [];
if (!Array.isArray(S.res)) S.res = [];
if (S.ai && typeof S.ai !== "object") S.ai = null;
const save = () => { try { localStorage.setItem("dalf1", JSON.stringify(S)); } catch (e) {} };

const $ = s => document.querySelector(s);
const app = $("#app");
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const nz = s => s.toLowerCase()
  .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
  .replace(/œ/g, "oe").replace(/æ/g, "ae").replace(/ß/g, "ss")
  .replace(/[’‘]/g, "'")
  .replace(/[^a-z0-9' ]/g, " ")
  .replace(/\s+/g, " ").trim();

function ok(u, a) {
  const x = nz(u);
  return a.split(" / ").some(b => {
    const y = nz(b);
    if (x === y) return true;
    const p = y.split(" "), q = x.split(" ");
    if (p.length < 7) return false;
    const i = p.filter(w => q.includes(w)).length;
    return 2 * i / (p.length + q.length) >= .85;
  });
}

let L = [], LK = [], TK = [], TP = [], KD = {}, CN = [];
let DATA_READY = false;

async function loadData() {
  try {
    const r = await fetch("data/edito-c1.lecons.json", { cache: "no-cache" });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const j = await r.json();
    L = j.lecons || []; LK = j.liens || []; TK = j.taches || [];
    TP = j.sujets_ia || []; KD = j.types_ia || {}; CN = j.connecteurs || [];
  } catch (e) {
    console.error("Chargement des données impossible :", e);
  }
  DATA_READY = true;
}

const PFS = {};
const PROFILE_IDS = ["edito-c1", "cosmopolite-5"];
const PROFILES_READY = Promise.all(PROFILE_IDS.map(id =>
  fetch("profiles/" + id + ".json")
    .then(r => r.ok ? r.json() : null)
    .then(j => { if (j) PFS[id] = j; })
    .catch(() => {})
));



// ═════════════════════════════════════════════════════════════
//  DALF Lab — app.js  (2/3 : navigation et onglets)
// ═════════════════════════════════════════════════════════════

function home(t) {
  t = t || "l";
  if (!DATA_READY) {
    app.innerHTML = '<p class="mu">Chargement…</p>';
    loadData().then(() => home(t));
    return;
  }
  const TABS = [["l","Leçons"],["t","Lire"],["w","Écrire"],["r","Liens"],["i","Import"]];
  const body =
    t === "l" ? lessons() :
    t === "t" ? reader()  :
    t === "w" ? writer()  :
    t === "i" ? importer() :
    t === "x" ? extra()   :
                links();
  app.innerHTML =
    '<div class="hd"><div><h1>Édito C1, thème 1</h1><span class="mu">Justice, quelles alternatives ?</span></div><div class="xp">' + S.xp + ' XP</div></div>' +
    '<nav>' + TABS.map(([k, l]) => '<button class="' + (t === k ? "on" : "") + '" onclick="App.home(\'' + k + '\')">' + l + '</button>').join("") + '</nav>' +
    body +
    '<p class="note">Prototype : tes résultats restent dans ce navigateur.</p>';
}

function lessons() { return lessons0() + xcard(); }

function opn() {
  return L.every(l => (S.done[l.id] || 0) >= Math.ceil(l.q.length * .7));
}

function lessons0() {
  return L.map((l, i) =>
    '<button class="card" onclick="App.start(' + i + ')"><b>' + esc(l.t) + '</b><small>' + esc(l.s) + '</small><span>' +
    (S.done[l.id] != null ? "Meilleur score : " + S.done[l.id] + "/" + l.q.length : "Commencer") + '</span></button>'
  ).join("");
}

function xcard() {
  const okk = opn() || S.xo;
  const g = S.gen.map((l, i) =>
    '<button class="card" onclick="App.startG(' + i + ')"><b>' + esc(l.t) + '</b><small>' + esc(l.s) + '</small><span>Commencer</span></button>'
  ).join("");
  return (g ? '<h3>Leçons générées par l’IA</h3>' + g : "") +
    '<button class="card" onclick="App.home(\'x\')"><b>Études extra avec l’IA</b><small>' +
    (okk ? "Crée des exercices à partir des sujets du manuel." : "Se débloque quand toutes les leçons sont réussies à 70 % ou plus.") +
    '</small><span>' + (okk ? "Ouvrir" : "Voir") + '</span></button>';
}

let cur, qi, sc, ans, lock = false;

function start(i)  { cur = L[i];     qi = 0; sc = 0; lock = false; show(); }
function startG(i) { cur = S.gen[i]; qi = 0; sc = 0; lock = false; show(); }

function show() {
  if (qi >= cur.q.length) {
    S.done[cur.id] = Math.max(S.done[cur.id] || 0, sc);
    S.xp += sc * 10; save();
    app.innerHTML = '<div class="end"><h2>Leçon terminée</h2><p>' + sc + ' sur ' + cur.q.length + ', +' + (sc * 10) + ' XP</p><button class="pri" onclick="App.home()">Revenir aux leçons</button></div>';
    return;
  }
  const q = cur.q[qi]; ans = null; lock = false;
  app.innerHTML =
    '<button class="x" aria-label="Quitter" onclick="App.home()">✕</button>' +
    '<div class="bar"><i style="width:' + (qi / cur.q.length * 100) + '%"></i></div>' +
    '<small>' + esc(cur.s) + '</small><h2>' + esc(q[1]) + '</h2>' +
    (q[0] === "c"
      ? '<div class="opts">' + q[2].map((o, j) => '<button class="opt" onclick="App.pick(' + j + ',this)">' + esc(o) + '</button>').join("") + '</div>'
      : '<input id="in" type="text" autocomplete="off" placeholder="Écris ta réponse" onkeydown="if(event.key===\'Enter\')App.check()">') +
    '<div id="fb"></div><div id="rs">' + rl() + '</div>' +
    '<button id="go" class="pri" onclick="App.check()">Vérifier</button>';
}

function pick(j, b) {
  if (lock) return;
  ans = j;
  document.querySelectorAll(".opt").forEach(o => o.classList.remove("sel"));
  b.classList.add("sel");
}

function check() {
  if (lock) { qi++; show(); return; }
  const q = cur.q[qi];
  let g, c;
  if (q[0] === "c") {
    if (ans == null) return;
    g = ans === q[3]; c = q[2][q[3]];
  } else {
    const v = $("#in").value;
    if (!v.trim()) return;
    g = ok(v, q[2]); c = q[2];
  }
  lock = true;
  if (g) sc++;
  if (q[0] === "c") {
    document.querySelectorAll(".opt").forEach((o, j) => {
      o.disabled = true;
      if (j === q[3]) o.classList.add("good");
      else if (j === ans) o.classList.add("bad");
    });
  } else { $("#in").disabled = true; }
  const f = $("#fb");
  f.className = "fb " + (g ? "g" : "b");
  f.innerHTML = (g ? "Correct." : "Pas tout à fait.") +
    (q[0] === "t" ? '<small>Corrigé : ' + esc(c) + '</small>' : (g ? "" : '<small>Réponse attendue : ' + esc(c) + '</small>'));
  $("#go").textContent = "Continuer";
  $("#rs").innerHTML = rl();
}

function rl() {
  const a = S.res.filter(r => r.l === cur.id && (!r.q || r.q === qi + 1) && (lock || r.t !== "corrige"));
  if (!a.length) return "";
  return '<details class="rs"><summary>Ressources de cette étape (' + a.length + ')</summary>' +
    a.map(r => '<p><b>' + (TY[r.t] || r.t) + '</b>' + (r.r ? " : " + esc(r.r) : "") + (r.ia ? " (généré par l’IA)" : "") + '<br>' + esc(r.x).replace(/\n/g, "<br>") + '</p>').join("") +
    '</details>';
}

function reader() {
  const ps = S.txt.split(/\n+/).map(s => s.trim()).filter(Boolean);
  if (!ps.length) {
    return '<p class="mu">Colle ici un texte de ton manuel.</p>' +
      '<textarea id="tx" aria-label="Texte du manuel" placeholder="Colle le texte ici"></textarea>' +
      '<button class="pri" onclick="App.sv()">Enregistrer le texte</button>';
  }
  return '<p class="mu">' + ps.length + ' paragraphes. Touche un paragraphe pour le surligner.</p>' +
    ps.map((p, i) => '<div class="p ' + (S.hl[i] ? "h" : "") + '" onclick="App.hl(' + i + ')"><b>§' + (i + 1) + '</b><span>' + esc(p) + '</span></div>').join("") +
    '<button class="sec" onclick="App.sv2()">Remplacer le texte</button>';
}
function sv()  { S.txt = $("#tx").value; S.hl = {}; save(); home("t"); }
function sv2() { S.txt = ""; S.hl = {}; save(); home("t"); }
function hl(i) { S.hl[i] = !S.hl[i]; save(); const el = document.querySelectorAll(".p")[i]; if (el) el.classList.toggle("h"); }

const O = {};
function stats(id) {
  const k = TK.find(x => x.id === id);
  if (!k) return "";
  const t = S.w[id] || "";
  const w = (t.match(/\S+/g) || []).length;
  const lo = Math.round(k.n * .9), hi = Math.round(k.n * 1.1);
  const n = " " + nz(t) + " ";
  const u = CN.filter(c => n.includes(" " + nz(c) + " "));
  const pa = t.split(/\n+/).filter(s => s.trim()).length;
  let h = '<div class="wc ' + (w >= lo && w <= hi ? "in" : "out") + '">' + w + ' mots (cible : ' + lo + ' à ' + hi + ')</div><small>' + pa + ' paragraphe' + (pa > 1 ? "s" : "") + ', connecteurs : ' + (u.length ? u.join(", ") : "aucun") + '</small><br>';
  if (!k.m) h += '<small>Le manuel ne fournit pas de corrigé pour cet essai.</small>';
  else if (w < k.n / 2) h += '<small>Le corrigé s’ouvre quand tu as écrit au moins la moitié des mots.</small>';
  else {
    h += '<button class="sec" onclick="App.mo(\'' + id + '\')">' + (O[id] ? "Masquer" : "Voir") + ' le corrigé</button>';
    if (O[id]) h += '<textarea aria-label="Corrigé" oninput="S.m[\'' + id + '\']=this.value;save()">' + esc(S.m[id] || "") + '</textarea>';
  }
  return h + '<br><button class="sec" disabled>Correction par l’IA (appli complète)</button>';
}
function wr(id) { S.w[id] = $("#w-" + id).value; save(); const el = $("#i-" + id); if (el) el.innerHTML = stats(id); }
function mo(id) { O[id] = !O[id]; const el = $("#i-" + id); if (el) el.innerHTML = stats(id); }
function writer() {
  return TK.map(k =>
    '<section class="card2"><h3>' + esc(k.t) + '</h3><small>' + esc(k.s) + '</small><p>' + esc(k.c) + '</p>' +
    '<textarea id="w-' + k.id + '" aria-label="' + esc(k.t) + '" placeholder="Écris ton texte ici" oninput="App.wr(\'' + k.id + '\')">' + esc(S.w[k.id] || "") + '</textarea>' +
    '<div id="i-' + k.id + '">' + stats(k.id) + '</div></section>'
  ).join("");
}

function links() {
  return '<p class="mu">Liens détectés. Touche une ligne pour la valider.</p>' +
    LK.map((c, i) =>
      '<section class="card2"><h3>' + esc(c.h) + '</h3><small>' + esc(c.f) + '</small>' +
      c.r.map((r, j) => {
        const k = i + "-" + j;
        return '<button class="row ' + (S.ok[k] ? "v" : "") + '" onclick="App.tg(\'' + k + '\')"><span>' + esc(r[0]) + '<em>' + esc(r[1]) + '</em></span><b>' + (S.ok[k] ? "✓ validé" : "Confiance " + esc(r[2]).toLowerCase()) + '</b></button>';
      }).join("") +
      '</section>'
    ).join("");
}
function tg(k) { S.ok[k] = !S.ok[k]; save(); home("r"); }


// ═════════════════════════════════════════════════════════════
//  DALF Lab — app.js  (3/3 : import, IA, démarrage)
// ═════════════════════════════════════════════════════════════

let IM = null, PF = null;
const TY = { transcription:"Transcription", corrige:"Corrigé", texte:"Texte du manuel", note:"Note" };
let IT = "f";

function importer() {
  return '<nav><button class="' + (IT === "f" ? "on" : "") + '" onclick="App.IT=\'f\';App.home(\'i\')">Importer un fichier</button><button class="' + (IT === "a" ? "on" : "") + '" onclick="App.IT=\'a\';App.home(\'i\')">Ajouter à la main</button></nav>' +
    (IT === "a" ? adder() : impF());
}

function impF() {
  return '<p class="mu">Choisis le PDF du manuel, puis tes fichiers audio et vidéo. Rien n’est envoyé.</p>' +
    '<p class="mu">Profil du manuel</p><select id="pf" onchange="App.PF=App.PFS[this.value]||null"><option value="">Détection automatique</option>' +
    Object.keys(PFS).map(k => '<option value="' + k + '"' + (PF && PF.id === k ? " selected" : "") + '>' + esc(PFS[k].titre) + '</option>').join("") +
    '</select><p class="mu">PDF</p><input id="fp" type="file" accept="application/pdf" multiple>' +
    '<p class="mu">Audio et vidéo</p><input id="fm" type="file" accept="audio/*,video/*" multiple>' +
    '<button class="pri" onclick="App.runImp()">Analyser</button><div id="im">' + (IM ? imHtml() : "") + '</div>';
}

function adder() {
  const o = Object.keys(TY).map(k => '<option value="' + k + '">' + TY[k] + '</option>').join("");
  const ls = '<option value="0">Aucune (général)</option>' + L.map(l => '<option value="' + l.id + '">' + esc(l.t) + '</option>').join("");
  return '<p class="mu">Ajoute à la main transcription, corrigé, texte ou note.</p>' +
    '<p class="mu">Type</p><select id="xt">' + o + '</select>' +
    '<p class="mu">Étape</p><select id="xl">' + ls + '</select>' +
    '<p class="mu">Numéro de question (facultatif)</p><input id="xq" type="number" min="1">' +
    '<p class="mu">Référence (facultatif)</p><input id="xr" type="text" placeholder="ex. livre p. 14">' +
    '<p class="mu">Texte</p><textarea id="xx" aria-label="Texte de la ressource"></textarea>' +
    '<p class="mu">Ou depuis un PDF (pages de … à …)</p><input id="xf" type="file" accept="application/pdf">' +
    '<input id="xa" type="number" min="1" placeholder="page de"><br><br><input id="xb" type="number" min="1" placeholder="page à">' +
    '<button class="sec" onclick="App.fromPdf()">Lire le texte du PDF</button>' +
    '<button class="pri" onclick="App.addRes()">Enregistrer</button>' +
    '<h3>Ressources ajoutées (' + S.res.length + ')</h3>' +
    S.res.map((r, i) =>
      '<div class="row"><span>' + (TY[r.t] || r.t) + (r.r ? " : " + esc(r.r) : "") + '<em>' +
      (r.l ? esc((L.find(l => l.id === r.l) || { t: "" }).t) : "général") + (r.q ? ", question " + r.q : "") +
      ', ' + r.x.length + ' caractères</em></span><b><button class="sec" onclick="App.dl(' + i + ')">Supprimer</button></b></div>'
    ).join("");
}
function addRes() {
  const x = $("#xx").value.trim();
  if (!x) { $("#xx").focus(); return; }
  if (x.length > 150000) { alert("Texte trop long (150 000 caractères max)."); return; }
  S.res.push({ t:$("#xt").value, l:+$("#xl").value, q:+$("#xq").value || 0, r:$("#xr").value.trim(), x });
  save(); home("i");
}
function dl(i) { if (!confirm("Supprimer ?")) return; S.res.splice(i, 1); save(); home("i"); }

async function fromPdf() {
  const f = $("#xf").files[0];
  if (!f) return;
  if (!window.pdfjsLib) { alert("pdf.js non chargé."); return; }
  pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
  try {
    const d = await pdfjsLib.getDocument({ data: await f.arrayBuffer() }).promise;
    const a = +$("#xa").value || 1;
    const b = Math.min(+$("#xb").value || a, d.numPages);
    const t = [];
    for (let i = a; i <= b; i++) t.push(seg((await (await d.getPage(i)).getTextContent()).items).join("\n"));
    $("#xx").value = t.join("\n\n");
  } catch (e) { alert("Lecture impossible : " + e.message); }
}

function seg(I) {
  const L = [];
  I.forEach(x => {
    if (!x.str) return;
    const y = x.transform[5], h = Math.abs(x.transform[3]) || 10;
    let r = L.find(q => Math.abs(q.y - y) <= h * .4);
    if (!r) { r = { y, a: [] }; L.push(r); }
    r.a.push({ s: x.str, x: x.transform[4], w: x.width, h });
  });
  const out = [];
  L.sort((a, b) => b.y - a.y).forEach(r => {
    r.a.sort((p, q) => p.x - q.x);
    let cur = "", end = null, h = 10;
    r.a.forEach(t => {
      if (end != null) {
        const g = t.x - end;
        if (g > h * 1.5) { out.push(cur); cur = ""; }
        else if (g > h * .15 && !/\s$/.test(cur) && !/^\s/.test(t.s)) cur += " ";
      }
      cur += t.s; end = t.x + t.w; h = t.h;
    });
    out.push(cur);
  });
  return out.map(s => s.replace(/\s+/g, " ").trim()).filter(Boolean);
}

async function runImp() {
  const out = $("#im"), pf = [...$("#fp").files], mf = [...$("#fm").files];
  if (!pf.length) { out.textContent = "Choisis d’abord un PDF."; return; }
  if (!window.pdfjsLib) { out.textContent = "pdf.js non chargé."; return; }
  pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
  const P = [];
  try {
    for (const f of pf) {
      const d = await pdfjsLib.getDocument({ data: await f.arrayBuffer() }).promise;
      for (let i = 1; i <= d.numPages; i++) {
        out.textContent = f.name + " : page " + i + " / " + d.numPages;
        const c = await (await d.getPage(i)).getTextContent(), it = seg(c.items);
        P.push({ f:f.name, n:i, it, num:it.filter(s => /^\d{1,2}$/.test(s)) });
      }
    }
  } catch (e) { out.textContent = "Lecture impossible : " + e.message; return; }
  IM = analyse(P, mf.map(f => f.name));
  out.innerHTML = imHtml();
}

function analyse(P, fl) {
  const R = { ent: [], cor: [], med: [] };
  P.forEach(p => {
    const z = p.it.map(nz), h = r => z.some(s => r.test(s));
    p.k = h(/\baudios?\b/) && h(/\btranscriptions?\b/) ? "audio" :
          h(/\bvideos?\b/) && h(/\btranscriptions?\b/) ? "video" :
          h(/^corriges?$/) ? "corrige" : "livre";
  });
  P.forEach(p => {
    if (p.k === "corrige") p.it.forEach(s => {
      const m = s.match(/^Page\s+(\d+),\s*(.+)$/);
      if (m) R.cor.push({ page:+m[1], s:m[2], pdf:p.n });
    });
  });
  R.diag = D(P);
  return R;
}
function D(P) {
  const f = {};
  P.forEach(p => {
    const d = f[p.f] = f[p.f] || { pages:0, avecTexte:0, types:{} };
    d.pages++;
    if (p.it.length) d.avecTexte++;
    d.types[p.k] = (d.types[p.k] || 0) + 1;
  });
  return f;
}
function imHtml() {
  const R = IM;
  return '<h3>Fichiers lus</h3>' +
    Object.keys(R.diag || {}).map(k =>
      '<div class="row"><span>' + esc(k) + '<em>' + R.diag[k].pages + ' pages, ' + R.diag[k].avecTexte + ' avec du texte</em></span></div>'
    ).join("") +
    '<h3>Résumé</h3><p class="mu">Corrigés : ' + R.cor.length + '</p>' +
    '<h3>Données détectées (JSON)</h3><textarea readonly onclick="this.select()">' + esc(JSON.stringify(R)) + '</textarea>';
}

// ─── IA ───
function extra() {
  const c = S.ai || { p:"gemini", u:"", m:PV.gemini.m, key:"" };
  const b = '<button class="sec" onclick="App.home(\'l\')">← Leçons</button>';
  if (!opn() && !S.xo) {
    return b + '<p class="mu">Se débloque quand toutes les leçons sont réussies à 70 % ou plus.</p>' +
      '<button class="pri" onclick="S.xo=1;save();App.home(\'x\')">Ouvrir quand même</button>';
  }
  return b + '<h2>Études extra avec l’IA</h2>' +
    '<details class="rs"><summary>Réglages de l’IA</summary>' +
    '<p class="mu">Fournisseur</p><select id="ap" onchange="App.apc(this.value)">' +
    Object.keys(PV).map(k => '<option value="' + k + '"' + (c.p === k ? " selected" : "") + '>' + PV[k].n + '</option>').join("") +
    '</select><p class="mu">URL API</p><input id="au" type="text" value="' + esc(c.u || "") + '">' +
    '<p class="mu">Modèle</p><input id="am" type="text" value="' + esc(c.m || "") + '">' +
    '<p class="mu">Clé API (reste sur cet appareil)</p><input id="ak" type="password" value="' + esc(c.key || "") + '">' +
    '<button class="sec" onclick="App.asv()">Enregistrer et tester</button><div id="at2" class="mu"></div></details>' +
    '<p class="mu">Sujet</p><select id="gs">' + TP.map(t => '<option>' + esc(t) + '</option>').join("") + '</select>' +
    '<p class="mu">Type</p><select id="gk">' + Object.keys(KD).map(k => '<option value="' + k + '">' + KD[k] + '</option>').join("") + '</select>' +
    '<button class="pri" onclick="App.gen()">Générer</button><div id="gout"></div>';
}
function apc(v) { $("#au").value = PV[v].u; $("#am").value = PV[v].m; }
async function asv() {
  const c = { p:$("#ap").value, u:$("#au").value.trim(), m:$("#am").value.trim(), key:$("#ak").value.trim() };
  if (c.p !== "gemini" && (!c.u || !c.m)) { $("#at2").textContent = "URL et modèle requis."; return; }
  S.ai = c; save();
  const o = $("#at2"); o.textContent = "Test…";
  try {
    const r = await ai("Réponds uniquement par le mot OK.");
    o.textContent = "Connexion réussie : " + r.slice(0, 40);
  } catch (e) { o.textContent = "Échec : " + e.message; }
}
async function ai(p) {
  const c = S.ai || {};
  if (!c.key) throw new Error("Ajoute ta clé API.");
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), 60000);
  try {
    if (c.p === "gemini") {
      const r = await fetch("https://generativelanguage.googleapis.com/v1beta/models/" + encodeURIComponent(c.m) + ":generateContent", {
        method: "POST", headers: { "Content-Type": "application/json", "x-goog-api-key": c.key },
        body: JSON.stringify({ contents: [{ parts: [{ text: p }] }] }), signal: ctl.signal
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error && j.error.message || r.status);
      if (!j.candidates?.[0]?.content?.parts) throw new Error(j.promptFeedback?.blockReason || "Réponse vide");
      return j.candidates[0].content.parts.map(x => x.text).join("");
    }
    const r = await fetch(c.u.replace(/\/$/, "") + "/chat/completions", {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer " + c.key },
      body: JSON.stringify({ model: c.m, messages: [{ role: "user", content: p }] }), signal: ctl.signal
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error && (j.error.message || j.error) || r.status);
    return j.choices[0].message.content;
  } finally { clearTimeout(t); }
}
function gen() {
  $("#gout").textContent = "Génération…";
  const s = $("#gs").value, k = $("#gk").value;
  ai("Tu es professeur de FLE, niveau C1. Sujet : " + s + ". Réponds en français.")
    .then(r => { $("#gout").textContent = r; })
    .catch(e => { $("#gout").textContent = "Échec : " + e.message; });
}

// ─── Pont global pour les onclick inline ───
window.App = {
  home, start, startG, pick, check, sv, sv2, hl, wr, mo, tg,
  importer, fromPdf, addRes, dl, runImp,
  extra, apc, asv, gen,
  get IT() { return IT; }, set IT(v) { IT = v; },
  get PF() { return PF; }, set PF(v) { PF = v; },
  PFS
};
window.save = save;
window.S = S;

// ─── Service worker ───
if ("serviceWorker" in navigator) {
  addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js")
      .then(() => console.log("✅ SW enregistré"))
      .catch(e => console.warn("⚠️ SW:", e));
  });
}

// ─── Démarrage ───
(async () => {
  await loadData();
  home();
})();


