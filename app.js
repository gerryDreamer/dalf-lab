const $ = s => document.querySelector(s);
const app = $("#app");

// Données globales
let DATA = null;
let STATE = {
  xp: parseInt(localStorage.getItem("xp") || "0"),
  completed: JSON.parse(localStorage.getItem("completed") || "{}")
};

// Variables de session (leçon en cours)
let currentLesson = null;
let currentQuestionIndex = 0;
let currentScore = 0;
let currentSelection = null;
let validQuestions = [];
let currentFlashcardIndex = 0;

// Petit utilitaire pour sécuriser l'affichage du texte
window.escapeHtml = function(text) {
  if (!text) return "";
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
};

// Chargement des données
async function loadData() {
  app.innerHTML = '<p style="text-align:center; padding:40px; color:var(--mu)">Chargement du manuel...</p>';
  try {
    const r = await fetch("data/edito-c1.final-tree.json");
    if (!r.ok) throw new Error("Fichier introuvable (as-tu lancé les scripts de génération ?)");
    DATA = await r.json();
    window.showHome();
  } catch (e) {
    app.innerHTML = `<p style="color:red; padding:20px;">Erreur de chargement : ${e.message}</p>`;
  }
}

// --- 1. ACCUEIL (L'ARBRE) ---
window.showHome = function() {
  let html = `<header><h1>DALF Lab</h1><div class="xp">⭐ ${STATE.xp} XP</div></header><main><div class="unit-list">`;

  DATA.themes.forEach(theme => {
    // --- PARTIE MANUEL (une carte par conteneur A, B, C) ---
    const manuelConteneurs = theme.parties?.manuel?.conteneurs || [];
    manuelConteneurs.forEach(conteneur => {
      const sections = conteneur.sections || [];
      if (sections.length === 0) return;
      
      html += `<div class="unit-card">
        <div class="unit-header">
          <div><h2 class="unit-title">Thème ${theme.theme} - ${conteneur.titre || 'Conteneur ' + conteneur.lettre}</h2>
          <span class="unit-subtitle">${sections.length} sections</span></div>
        </div><div class="path-grid">`;
      
      sections.forEach((section, idx) => {
        const id = `T${theme.theme}-${conteneur.lettre}-${idx}`;
        const isDone = STATE.completed[id];
        const typeStr = (section.type || "leçon").toLowerCase();
        
        let icon = "📖";
        if (typeStr.includes("orale") || typeStr.includes("audiovisuelle")) icon = "🎧";
        if (typeStr.includes("ecrite")) icon = "✍️";
        if (typeStr.includes("orale")) icon = "🗣️";
        
        let label = typeStr.split('_')[0];
        if (label.length > 14) label = label.substring(0, 14) + "...";
        
        html += `<div class="path-bubble ${isDone ? 'completed' : ''}" 
          onclick="window.startLesson('${theme.theme}', '${conteneur.lettre}', ${idx}, 'manuel')">
          <span class="icon">${icon}</span>${label}
        </div>`;
      });
      html += `</div></div>`;
    });

    // --- PARTIE CAHIER (une carte avec les niveaux de vocab, grammaire, ABR) ---
    const cahierSections = theme.parties?.cahier?.sections || [];
    if (cahierSections.length > 0) {
      html += `<div class="unit-card" style="border-left: 6px solid #d97706;">
        <div class="unit-header">
          <div><h2 class="unit-title">Thème ${theme.theme} - Cahier</h2>
          <span class="unit-subtitle">${cahierSections.length} niveaux</span></div>
        </div><div class="path-grid">`;
      
      cahierSections.forEach((section, idx) => {
        const id = `T${theme.theme}-cahier-${idx}`;
        const isDone = STATE.completed[id];
        const typeStr = (section.type || "leçon").toLowerCase();
        
        let icon = "🃏";
        if (typeStr === "grammaire") icon = "📝";
        else if (typeStr === "a_batons_rompus") icon = "🗣️";
        else if (typeStr === "comprehension_orale") icon = "🎧";
        else if (typeStr === "comprehension_ecrite") icon = "📖";
        else if (typeStr === "production_orale") icon = "🗣️";
        else if (typeStr === "quiz_revision") icon = "🏆";
        
        let label = section.titre || typeStr.split('_')[0];
        if (label.length > 16) label = label.substring(0, 16) + "...";
        
        let style = isDone ? '' : 'background: #d97706; border-color: #fef3c7; box-shadow: 0 4px 0 #92400e;';
        
        html += `<div class="path-bubble ${isDone ? 'completed' : ''}" style="${style}"
          onclick="window.startLesson('${theme.theme}', 'cahier', ${idx}, 'cahier')">
          <span class="icon">${icon}</span>${label}
        </div>`;
      });
      html += `</div></div>`;
    }
  });
  html += `</div></main>`;
  app.innerHTML = html;
}

// --- 2. DÉMARRAGE DE LA LEÇON ---
window.startLesson = function(themeId, conteneurLettre, sectionIdx, partie) {
  const theme = DATA.themes.find(t => t.theme == themeId);
  let section;

  if (partie === "manuel") {
    const conteneur = theme.parties.manuel.conteneurs.find(c => c.lettre === conteneurLettre);
    section = conteneur.sections[sectionIdx];
    window.currentLessonId = `T${themeId}-${conteneurLettre}-${sectionIdx}`;
  } else {
    section = theme.parties.cahier.sections[sectionIdx];
    window.currentLessonId = `T${themeId}-cahier-${sectionIdx}`;
  }

  currentLesson = section;
  const typeStr = (section.type || "leçon").toLowerCase().trim();

  // --- CAS 1 : Vocabulaire avec flashcards (PRIORITÉ ABSOLUE) ---
  if (section.flashcards && section.flashcards.length > 0) {
    currentFlashcardIndex = 0;
    window.renderFlashcards(section);
    return;
  }

  // --- CAS 2 : Grammaire ---
  if (typeStr === "grammaire") {
    window.grammaireState = { etape: "echauffement" };
    window.renderGrammaire();
    return;
  }

  // --- CAS 3 : Production écrite ---
  if (typeStr === "production_ecrite") {
    window.renderProductionEcrite();
    return;
  }

  // --- CAS 4 : Production orale (écran dédié avec minuteur) ---
  if (typeStr === "production_orale") {
    window.renderProductionOrale();
    return;
  }

  // --- CAS 5 : QCM classique (À bâtons rompus, Compréhension, Quiz, Manuel) ---
  validQuestions = (section.questions || []).filter(q => 
    q.texte && q.texte.trim() !== "" && q.texte.toLowerCase() !== "undefined"
  );

  if (validQuestions.length === 0) {
    alert("Cette section ne contient aucune question valide.");
    window.showHome();
    return;
  }
  currentQuestionIndex = 0;
  currentScore = 0;
  window.renderQuestion();
}

// --- 3. MOTEUR DE QUESTION (QCM) ---
window.renderQuestion = function() {
  if (currentQuestionIndex >= validQuestions.length) {
    window.completeLesson();
    return;
  }

  const q = validQuestions[currentQuestionIndex];
  const total = validQuestions.length;
  const progress = (currentQuestionIndex / total) * 100;

  let html = `<div class="player-screen">
    <div class="progress-bar"><i style="width:${progress}%"></i></div>
    <button class="sec" onclick="window.showHome()" style="align-self:flex-start; margin-bottom:20px;">✕ Quitter</button>`;

  // CORRECTIF : On affiche le texte dès qu'il existe, peu importe le type
  if (currentLesson.texte_lecture && currentLesson.texte_lecture.trim() !== "") {
    html += `<div style="background:var(--cd); padding:15px; border-radius:8px; border:1px solid var(--ln); margin-bottom:20px; max-height:200px; overflow-y:auto;">
      <p style="font-size:0.9rem; margin:0; font-family:Georgia, serif;">${window.escapeHtml(currentLesson.texte_lecture)}</p>
    </div>`;
  }

  if (currentLesson.audio && currentLesson.audio !== "Non spécifié") {
    html += `<div style="background:var(--cd); padding:15px; border-radius:8px; border:1px solid var(--ln); margin-bottom:20px;">
      <p style="font-size:0.9rem; margin:0 0 10px 0;"><b>🎧 Écoutez l'audio :</b></p>
      <audio controls style="width:100%;">
        <source src="audios/${currentLesson.audio}" type="audio/mpeg">
      </audio>
    </div>`;
  }

  html += `<div class="question-text">${currentQuestionIndex + 1}. ${window.escapeHtml(q.texte)}</div>`;

  if (q.choix && q.choix.length > 0) {
    html += `<div class="options-grid">
      ${q.choix.map((c, j) => `<div class="option-btn" id="opt-${j}" onclick="window.selectOption(${j})">${window.escapeHtml(c)}</div>`).join('')}
    </div>`;
  } else {
    let indices = "";
    if (q.indices && q.indices.length > 0) {
       indices = `<div style="background:#fffaf0; padding:15px; border-radius:8px; margin-bottom:15px; border-left:4px solid #d97706;">
          <p style="margin:0 0 5px 0; font-weight:bold; color:#b45309;">💡 Indices pour vous aider :</p>
          <ul style="margin:0; padding-left:20px; font-size:0.9rem;">${q.indices.map(i => `<li>${window.escapeHtml(i)}</li>`).join('')}</ul>
       </div>`;
    }
    html += `${indices}
    <textarea class="editor-area" placeholder="Rédigez votre réponse, vos idées ou vos arguments ici..."></textarea>`;
  }

  html += `<div id="feedback" style="min-height: 60px; margin-top:20px;"></div>
    <button id="btn-action" class="btn-primary" onclick="window.checkAnswer()">Vérifier</button>
  </div>`;

  app.innerHTML = html;
  currentSelection = null;
}

window.selectOption = function(index) {
  currentSelection = index;
  document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
  document.getElementById(`opt-${index}`).classList.add('selected');
}

// --- 4. VÉRIFICATION DE LA RÉPONSE ---
window.checkAnswer = function() {
  const q = validQuestions[currentQuestionIndex];
  const btn = document.getElementById("btn-action");
  const fb = document.getElementById("feedback");

  if (btn.textContent === "Continuer") {
    currentQuestionIndex++;
    window.renderQuestion();
    return;
  }

  if (q.choix && q.choix.length > 0) {
    if (currentSelection === null) return; 
    const isCorrect = (currentSelection === q.bonne);
    
    document.querySelectorAll('.option-btn').forEach((b, i) => {
      b.style.pointerEvents = "none";
      if (i === q.bonne) b.classList.add("correct");
      else if (i === currentSelection) b.classList.add("incorrect");
    });

    if (isCorrect) {
      currentScore++;
      fb.innerHTML = `<div class="fb g">✅ Excellent !</div>`;
    } else {
      fb.innerHTML = `<div class="fb b">❌ La bonne réponse était : ${window.escapeHtml(q.choix[q.bonne])}</div>`;
    }
  } else {
    fb.innerHTML = `<div class="fb g">✅ Réponse enregistrée. (Correction IA à venir).</div>`;
  }

  btn.textContent = "Continuer";
};

// --- 5. MOTEUR DE FLASHCARDS ---
window.renderFlashcards = function(section) {
  const cards = section.flashcards;
  if (!cards || cards.length === 0) {
    alert("Aucune flashcard générée pour cette section.");
    window.showHome();
    return;
  }

  if (currentFlashcardIndex >= cards.length) {
    window.completeLesson();
    return;
  }

  const card = cards[currentFlashcardIndex];
  const progress = (currentFlashcardIndex / cards.length) * 100;

  app.innerHTML = `<div class="player-screen">
    <div class="progress-bar"><i style="width:${progress}%"></i></div>
    <button class="sec" onclick="window.showHome()" style="align-self:flex-start; margin-bottom:20px;">✕ Quitter</button>
    <h2 style="margin-top:20px;">🃏 ${window.escapeHtml(section.titre || 'Flashcards')}</h2>
    <p style="text-align:center; color:var(--mu);">Carte ${currentFlashcardIndex + 1} sur ${cards.length}</p>
    
    <div id="flashcard" class="flashcard" onclick="window.flipCard(this)">
      <div class="front">
        <div>
          <p style="font-size:1rem; color:var(--mu); margin-bottom:10px;">${window.escapeHtml(card.categorie || "")}</p>
          ${card.image_url ? `<img class="card-image" src="${card.image_url}" alt="${window.escapeHtml(card.recto)}" onerror="this.style.display='none'">` : ""}
          <p style="font-size:2rem; margin: 8px 0;">${window.escapeHtml(card.recto)}</p>
          <p style="font-size:0.8rem; color:var(--mu); margin-top:16px;">(Cliquez pour retourner)</p>
        </div>
      </div>
      <div class="back">
        <div>
          <p style="font-size:1.5rem; color:white;">${window.escapeHtml(card.verso)}</p>
        </div>
      </div>
    </div>

    <button id="btn-next-card" class="btn-primary" style="display:none; margin-top:20px;" onclick="window.nextCard()">Carte suivante</button>
  </div>`;
}

window.flipCard = function(el) {
  el.classList.toggle("flipped");
  document.getElementById("btn-next-card").style.display = "block";
}

window.nextCard = function() {
  currentFlashcardIndex++;
  window.renderFlashcards(currentLesson);
}

// --- 6. MOTEUR GRAMMAIRE ---
window.renderGrammaire = function() {
  const g = currentLesson;
  const etape = window.grammaireState.etape;

  const etapes = ["echauffement", "fonctionnement", "entrainement"];
  const labels = {
    echauffement: "1. Échauffement",
    fonctionnement: "2. Règle",
    entrainement: "3. Entraînement"
  };
  const idxEtape = etapes.indexOf(etape);
  const progress = ((idxEtape + 1) / etapes.length) * 100;

  let contenu = "";

  // ÉTAPE 1 : ÉCHAUFFEMENT
  if (etape === "echauffement") {
    const e = g.echauffement;
    let texte = "";
    if (typeof e === "string") texte = e;
    else if (e && e.consigne) texte = e.consigne;
    else if (e && e.texte) texte = e.texte;
    
    contenu = `
      <h2 style="margin-top:20px;">🔥 Échauffement</h2>
      <p style="color:var(--mu); font-size:0.9rem;">Notion : <b>${window.escapeHtml(g.notion || "")}</b></p>
      ${texte ? `<div style="background:var(--cd); padding:15px; border-radius:10px; border:1px solid var(--ln); margin:20px 0;">
        <p style="margin:0; font-size:1.1rem; line-height:1.6;">${window.escapeHtml(texte)}</p>
      </div>` : ""}
    `;
  }

  // ÉTAPE 2 : RÈGLE
  if (etape === "fonctionnement") {
    const f = g.fonctionnement;
    let texte = "";
    if (typeof f === "string") texte = f;
    else if (f && f.regle) texte = f.regle;
    else if (f && f.texte) texte = f.texte;
    
    contenu = `
      <h2 style="margin-top:20px;">📝 Règle de grammaire</h2>
      <p style="color:var(--mu); font-size:0.9rem;">Notion : <b>${window.escapeHtml(g.notion || "")}</b></p>
      ${texte ? `<div style="background:var(--ac-light); padding:15px; border-radius:10px; border-left:4px solid var(--ac); margin:20px 0;">
        <p style="margin:0; font-size:1rem; line-height:1.6;">${window.escapeHtml(texte)}</p>
      </div>` : "<p style='color:var(--mu);'>Aucune règle détaillée disponible.</p>"}
    `;
  }

  // ÉTAPE 3 : ENTRAÎNEMENT
  if (etape === "entrainement") {
    if (g.exercices_qcm && g.exercices_qcm.length > 0) {
      validQuestions = g.exercices_qcm;
      currentQuestionIndex = 0;
      currentScore = 0;
      window.renderQuestion(); 
      return;
    }

    if (g.questions && g.questions.length > 0) {
      validQuestions = g.questions;
      currentQuestionIndex = 0;
      currentScore = 0;
      window.renderQuestion(); 
      return;
    }

    const e = g.entrainement;
    let exercices = [];
    if (typeof e === "string") exercices = [e];
    else if (Array.isArray(e)) exercices = e;
    else if (e && e.exercices) exercices = e.exercices;
    else if (e && e.consigne) exercices = [e.consigne];
    else if (e && e.texte) exercices = [e.texte];

    contenu = `
      <h2 style="margin-top:20px;">🎯 Entraînement</h2>
      <p style="color:var(--mu); font-size:0.9rem;">Notion : <b>${window.escapeHtml(g.notion || "")}</b></p>
    `;

    if (exercices.length > 0) {
      contenu += `<div style="display:flex; flex-direction:column; gap:12px; margin-top:20px;">`;
      exercices.forEach((ex, i) => {
        let txt = typeof ex === "string" ? ex : (ex.texte || ex.consigne || "");
        contenu += `<div style="background:var(--cd); padding:15px; border-radius:10px; border:1px solid var(--ln); font-size:1rem; line-height:1.5;">
          ${exercices.length > 1 ? `<b>${i+1}.</b> ` : ""}${window.escapeHtml(txt)}
        </div>`;
      });
      contenu += `</div>`;
    } else {
      contenu += `<p style="color:var(--mu);">Exercices à venir.</p>`;
    }
  }

  let btnLabel = "Suivant";
  let btnAction = "window.grammaireNext()";
  if (etape === "entrainement") {
    btnLabel = "Terminer";
    btnAction = "window.completeLesson()";
  }

  app.innerHTML = `<div class="player-screen">
    <div class="progress-bar"><i style="width:${progress}%"></i></div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
      <button class="sec" onclick="window.showHome()">✕ Quitter</button>
      <span style="color:var(--mu); font-size:0.9rem;">${labels[etape]}</span>
    </div>
    ${contenu}
    <button class="btn-primary" style="margin-top:30px;" onclick="${btnAction}">${btnLabel}</button>
  </div>`;
};

window.grammaireNext = function() {
  const etapes = ["echauffement", "fonctionnement", "entrainement"];
  const idx = etapes.indexOf(window.grammaireState.etape);
  if (idx < etapes.length - 1) {
    window.grammaireState.etape = etapes[idx + 1];
    window.renderGrammaire();
  }
};

// --- 7. MOTEUR PRODUCTION ÉCRITE ---
window.renderProductionEcrite = function() {
  const p = currentLesson;
  const storageKey = `prod_${window.currentLessonId}`;
  const saved = localStorage.getItem(storageKey) || "";

  app.innerHTML = `<div class="player-screen">
    <div class="progress-bar"><i style="width:50%"></i></div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
      <button class="sec" onclick="window.showHome()">✕ Quitter</button>
      <span style="color:var(--mu); font-size:0.9rem;">✍️ Production écrite</span>
    </div>
    <h2 style="margin-top:20px;">✍️ ${window.escapeHtml(p.titre || "Production écrite")}</h2>
    <div style="background:var(--cd); padding:15px; border-radius:10px; border-left:4px solid var(--ac); margin:20px 0;">
      <p style="margin:0 0 6px 0; font-weight:bold; color:var(--ac);">Consigne</p>
      <p style="margin:0; line-height:1.6;">${window.escapeHtml(p.consigne || "")}</p>
    </div>
    <textarea id="prod-textarea" class="editor-area" style="min-height:280px;"
      placeholder="Rédigez votre texte ici..."
      oninput="window.saveProduction()">${window.escapeHtml(saved)}</textarea>
    <p id="prod-status" style="color:var(--mu); font-size:0.85rem; text-align:right; margin-top:-8px;">
      ${saved ? "💾 Brouillon restauré" : ""}
    </p>
    <button class="btn-primary" style="margin-top:20px;" onclick="window.completeLesson()">Terminer</button>
  </div>`;
};

window.saveProduction = function() {
  const ta = document.getElementById("prod-textarea");
  const status = document.getElementById("prod-status");
  if (!ta) return;
  const key = `prod_${window.currentLessonId}`;
  localStorage.setItem(key, ta.value);
  if (status) {
    status.textContent = "💾 Enregistré à " + new Date().toLocaleTimeString();
  }
};

// --- 7b. MOTEUR PRODUCTION ORALE (avec minuteur) ---
window.renderProductionOrale = function() {
  const p = currentLesson;
  
  app.innerHTML = `<div class="player-screen">
    <div class="progress-bar"><i style="width:100%"></i></div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
      <button class="sec" onclick="window.showHome()">✕ Quitter</button>
      <span style="color:var(--mu); font-size:0.9rem;">🗣️ Production orale</span>
    </div>
    <h2 style="margin-top:20px;">🗣️ ${window.escapeHtml(p.titre || "Production orale")}</h2>
    <div style="background:var(--cd); padding:15px; border-radius:10px; border-left:4px solid #d97706; margin:20px 0;">
      <p style="margin:0 0 6px 0; font-weight:bold; color:#d97706;">Consigne</p>
      <p style="margin:0; line-height:1.6;">${window.escapeHtml(p.consigne || "Préparez votre intervention orale.")}</p>
    </div>
    <div style="text-align:center; margin:30px 0;">
      <div id="timer-display" style="font-size:4rem; font-weight:bold; color:var(--ac);">00:00</div>
      <p style="color:var(--mu); font-size:0.9rem;">Temps de préparation</p>
      <button id="btn-timer" class="btn-primary" style="margin-top:15px; max-width:200px;" onclick="window.toggleTimer()">Démarrer le minuteur</button>
    </div>
    <button class="btn-primary" style="margin-top:20px;" onclick="window.completeLesson()">Terminer</button>
  </div>`;
  
  window.timerState = { active: false, seconds: 0, interval: null };
};

window.toggleTimer = function() {
  const btn = document.getElementById("btn-timer");
  const display = document.getElementById("timer-display");
  
  if (window.timerState.active) {
    clearInterval(window.timerState.interval);
    window.timerState.active = false;
    btn.textContent = "Reprendre";
  } else {
    window.timerState.active = true;
    btn.textContent = "Pause";
    window.timerState.interval = setInterval(() => {
      window.timerState.seconds++;
      const m = String(Math.floor(window.timerState.seconds / 60)).padStart(2, '0');
      const s = String(window.timerState.seconds % 60).padStart(2, '0');
      display.textContent = `${m}:${s}`;
    }, 1000);
  }
};

// --- 8. FIN DE LEÇON ---
window.completeLesson = function() {
  currentFlashcardIndex = 0;

  let gainedXP = 20;
  let messageResultat = "Section complétée !";

  const isQcmLesson = currentLesson 
    && currentLesson.type !== "vocabulaire" 
    && currentLesson.type !== "grammaire" 
    && currentLesson.type !== "production_ecrite"
    && currentLesson.type !== "production_orale";

  if (isQcmLesson) {
    const qcmCount = validQuestions.filter(q => q.choix && q.choix.length > 0).length;
    if (qcmCount > 0) {
      gainedXP = currentScore * 10;
      messageResultat = `Tu as eu ${currentScore} bonne(s) réponse(s) sur ${qcmCount} QCM.`;
    }
  }

  STATE.xp += gainedXP;
  STATE.completed[window.currentLessonId] = true;
  localStorage.setItem("xp", STATE.xp);
  localStorage.setItem("completed", JSON.stringify(STATE.completed));

  app.innerHTML = `<div class="player-screen" style="text-align:center; justify-content:center;">
    <h1 style="font-size:4rem; margin:0;">🎉</h1>
    <h2>Leçon terminée !</h2>
    <p>${messageResultat}</p>
    <p style="color:var(--ac); font-weight:bold; font-size:1.2rem;">+${gainedXP} XP</p>
    <button class="btn-primary" style="margin-top:30px;" onclick="window.showHome()">Retour à l'accueil</button>
  </div>`;
}

// Démarrage de l'application
loadData();
