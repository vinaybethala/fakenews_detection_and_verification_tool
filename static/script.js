// Common UI handling
const showError = (msg) => {
    const alert = document.getElementById('error-alert');
    if(alert) {
        alert.textContent = msg;
        alert.classList.remove('d-none');
    }
};

const hideError = () => {
    const alert = document.getElementById('error-alert');
    if(alert) alert.classList.add('d-none');
};

// ==========================================
// Detector logic (index.html)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    const analyzeForm = document.getElementById('analyze-form');
    if(analyzeForm) {
        analyzeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideError();
            
            const text = document.getElementById('article-text').value.trim();
            if(!text) {
                showError("Please enter some text to analyze.");
                return;
            }

            const btnSpinner = document.getElementById('btn-spinner');
            const btnText = document.getElementById('btn-text');
            const analyzeBtn = document.getElementById('analyze-btn');
            const resultsSection = document.getElementById('results-section');

            // UI Loading state
            btnSpinner.classList.remove('d-none');
            btnText.textContent = "Analyzing Pipeline...";
            analyzeBtn.disabled = true;
            resultsSection.classList.add('d-none');

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });

                const data = await response.json();
                
                if(!response.ok) {
                    throw new Error(data.error || "Failed to analyze.");
                }

                // Render Results
                renderPrediction(data.prediction);
                renderExplainability(data.explainability);
                renderFactChecks(data.fact_checks);
                
                resultsSection.classList.remove('d-none');
                
            } catch (err) {
                showError(err.message);
            } finally {
                btnSpinner.classList.add('d-none');
                btnText.textContent = "Analyze Article";
                analyzeBtn.disabled = false;
            }
        });
    }
});

function renderPrediction(prediction) {
    const labelBadge = document.getElementById('verdict-label');
    const scoreText = document.getElementById('confidence-score');
    
    labelBadge.className = 'badge'; // reset
    if (prediction.label === 'FAKE') {
        labelBadge.classList.add('badge-fake');
        labelBadge.textContent = 'FAKE NEWS';
    } else {
        labelBadge.classList.add('badge-real');
        labelBadge.textContent = 'REAL NEWS';
    }
    
    scoreText.textContent = `${(prediction.confidence * 100).toFixed(1)}%`;
}

function renderExplainability(explainability) {
    const acc = document.getElementById('claims-accordion');
    acc.innerHTML = '';
    
    if(explainability.length === 0) {
        acc.innerHTML = `<div class="p-3 text-white-50">No major claims detected.</div>`;
        return;
    }

    explainability.forEach((item, index) => {
        let highlightedClaim = item.claim;
        // Highlight logic
        if(item.suspicious_words && item.suspicious_words.length > 0) {
            item.suspicious_words.forEach(word => {
                const regex = new RegExp(`(${word})`, 'gi');
                highlightedClaim = highlightedClaim.replace(regex, `<span class="highlight-suspicious">$1</span>`);
            });
        }
        
        let scoreColor = item.suspicious_score > 0.1 ? 'text-warning' : 'text-success';

        const html = `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading-${index}">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-toggle="target="#collapse-${index}">
                        Claim ${index + 1} (Score: ${item.suspicious_score})
                    </button>
                </h2>
                <div id="collapse-${index}" class="accordion-collapse collapse" data-bs-parent="#claims-accordion">
                    <div class="accordion-body">
                        <p class="mb-2 fs-5">${highlightedClaim}</p>
                        <p class="mb-0 small text-white-50"><strong class="${scoreColor}">Suspicious words detected:</strong> ${item.suspicious_words.length > 0 ? item.suspicious_words.join(', ') : 'None'}</p>
                    </div>
                </div>
            </div>
        `;
        acc.innerHTML += html;
    });
}

function renderFactChecks(factChecks) {
    const tbody = document.getElementById('factchecks-tbody');
    tbody.innerHTML = '';
    
    if(factChecks.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-white-50 py-4">No fact checks available.</td></tr>`;
        return;
    }

    factChecks.forEach(fc => {
        let verdictColor = fc.verdict.toUpperCase().includes('FALSE') ? 'text-danger fw-bold' : 
                           fc.verdict.toUpperCase().includes('TRUE') ? 'text-success fw-bold' : '';
                           
        const badgeVerdict = `<span class="${verdictColor}">${fc.verdict}</span>`;
        const link = fc.url ? `<a href="${fc.url}" target="_blank" class="text-info text-decoration-none">View Source</a>` : `<span class="text-white-50">N/A</span>`;
        
        const html = `
            <tr>
                <td>${fc.claim}</td>
                <td>${badgeVerdict}</td>
                <td>${fc.publisher}</td>
                <td>${link}</td>
            </tr>
        `;
        tbody.innerHTML += html;
    });
}


// ==========================================
// Dashboard logic (dashboard.html)
// ==========================================
async function loadMetrics() {
    try {
        const res = await fetch('/api/metrics');
        const data = await res.json();
        document.getElementById('metric-articles').textContent = data.articles;
        document.getElementById('metric-accuracy').textContent = `${(data.accuracy * 100).toFixed(0)}%`;
        document.getElementById('metric-uptime').textContent = data.uptime;
        document.getElementById('metric-users').textContent = data.users;
    } catch(err) {
        console.error("Failed to load metrics");
    }
}

async function loadSources() {
    try {
        const res = await fetch('/sources');
        const data = await res.json();
        const list = document.getElementById('sources-list');
        list.innerHTML = '';
        
        data.sources.forEach(source => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent text-white border-0 d-flex justify-content-between align-items-center px-0 py-2 border-bottom';
            li.style.borderColor = 'rgba(255,255,255,0.1) !important';
            li.innerHTML = `
                <span><i class="bi bi-shield-check text-success me-2"></i> ${source}</span>
                <button class="btn btn-sm btn-outline-danger border-0" onclick="removeSource('${source}')">Remove</button>
            `;
            list.appendChild(li);
        });
    } catch(err) {
        console.error("Failed to load sources");
    }
}

async function removeSource(source) {
    if(!confirm(`Remove ${source} from trusted sources?`)) return;
    try {
        await fetch('/sources', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({source})
        });
        loadSources();
    } catch(err) {
        alert("Failed to remove source");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const addForm = document.getElementById('add-source-form');
    if(addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('new-source-input');
            const source = input.value.trim();
            if(!source) return;
            
            try {
                await fetch('/sources', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({source})
                });
                input.value = '';
                loadSources();
            } catch(err) {
                alert("Failed to add source");
            }
        });
    }
});
