/* ══════════════════════════════════════════════════════════════
   DSP LAB — Main Application Logic
   ══════════════════════════════════════════════════════════════ */

const DSPLab = {
    currentPage: 'dashboard',
    partResults: {},
    allParams: {},
    defaultParams: {},
    paramSchemas: {},
    isRunning: false,

    // ── Initialization ───────────────────────────────────────
    async init() {
        this.setupNavigation();
        this.setupModal();
        await this.loadAllParameters();
        await this.loadProjectInfo();
        this.showPage('dashboard');
    },

    // ── Navigation ───────────────────────────────────────────
    setupNavigation() {
        document.querySelectorAll('.nav-item[data-page]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.showPage(item.dataset.page);
            });
        });
    },

    showPage(pageId) {
        document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

        const page = document.getElementById('page-' + pageId);
        if (page) {
            page.classList.add('active');
            this.currentPage = pageId;
        }

        const navItem = document.querySelector(`.nav-item[data-page="${pageId}"]`);
        if (navItem) navItem.classList.add('active');

        // Load part-specific content
        const partMatch = pageId.match(/^part(\d)$/);
        if (partMatch) {
            this.loadPartPage(parseInt(partMatch[1]));
        }
        if (pageId === 'history') this.loadExperimentHistory();
    },

    // ── Load All Parameters ──────────────────────────────────
    async loadAllParameters() {
        try {
            const resp = await fetch('/api/parameters/all');
            const data = await resp.json();
            for (const [part, info] of Object.entries(data)) {
                const pn = parseInt(part);
                this.paramSchemas[pn] = info.parameters;
                this.defaultParams[pn] = { ...info.defaults };
                this.allParams[pn] = { ...info.defaults };
            }
        } catch (e) {
            console.error('Failed to load parameters:', e);
        }
    },

    // ── Project Info ─────────────────────────────────────────
    async loadProjectInfo() {
        try {
            const resp = await fetch('/api/project-info');
            const data = await resp.json();
            const statusEl = document.getElementById('dashboard-status');
            if (statusEl) {
                let completed = 0, total = 6;
                for (const [num, info] of Object.entries(data.parts)) {
                    if (info.has_outputs) completed++;
                }
                document.getElementById('stat-total').textContent = total;
                document.getElementById('stat-completed').textContent = completed;
                document.getElementById('stat-failed').textContent = '0';
                document.getElementById('stat-data').textContent =
                    (data.data_files.audio ? '✓' : '✗') + ' Audio  ' +
                    (data.data_files.image ? '✓' : '✗') + ' Image';
            }
        } catch (e) {
            console.error('Failed to load project info:', e);
        }
    },

    // ── Run All Parts ────────────────────────────────────────
    async runAll() {
        if (this.isRunning) return;
        this.isRunning = true;

        const btn = document.getElementById('btn-run-all');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Running All Experiments...';

        const progressBox = document.getElementById('run-all-progress');
        progressBox.style.display = 'block';

        try {
            const paramsPayload = {};
            for (let p = 1; p <= 6; p++) {
                if (this.allParams[p]) paramsPayload[p] = this.allParams[p];
            }

            // Run parts sequentially via API
            const allResults = [];
            for (let partNum = 1; partNum <= 6; partNum++) {
                document.getElementById('progress-text').textContent = `Running Part ${partNum} of 6...`;
                document.getElementById('progress-bar').style.width = `${((partNum - 1) / 6) * 100}%`;
                this.updatePipelineStatus(partNum, 'running');

                const resp = await fetch(`/api/run/${partNum}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ params: this.allParams[partNum] || {} }),
                });

                const result = await resp.json();
                allResults.push(result);
                this.partResults[partNum] = result;

                this.updatePipelineStatus(partNum, result.status);
                document.getElementById('progress-bar').style.width = `${(partNum / 6) * 100}%`;
            }

            document.getElementById('progress-text').textContent = 'All experiments completed!';
            document.getElementById('progress-bar').style.width = '100%';

            // Update stats
            let completed = allResults.filter(r => r.status === 'completed').length;
            let failed = allResults.filter(r => r.status === 'failed').length;
            document.getElementById('stat-completed').textContent = completed;
            document.getElementById('stat-failed').textContent = failed;

            const totalTime = allResults.reduce((s, r) => s + (r.duration || 0), 0);
            document.getElementById('stat-time').textContent = totalTime.toFixed(1) + 's';

            this.showToast('All experiments completed!', 'success');
        } catch (e) {
            this.showToast('Execution failed: ' + e.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🚀 RUN ALL EXPERIMENTS';
            this.isRunning = false;
        }
    },

    updatePipelineStatus(partNum, status) {
        const stage = document.getElementById(`pipeline-stage-${partNum}`);
        if (stage) {
            stage.className = `pipeline-stage ${status}`;
            const badge = stage.querySelector('.status-badge');
            if (badge) {
                badge.className = `status-badge ${status}`;
                badge.innerHTML = `<span class="status-dot"></span> ${status}`;
            }
        }
    },

    // ── Run Single Part ──────────────────────────────────────
    async runPart(partNum) {
        if (this.isRunning) {
            this.showToast('Another experiment is running.', 'info');
            return;
        }
        this.isRunning = true;

        const btn = document.getElementById(`btn-run-part-${partNum}`);
        if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Running...'; }

        const statusEl = document.getElementById(`part${partNum}-status`);
        if (statusEl) statusEl.innerHTML = '<span class="status-badge running"><span class="status-dot"></span> RUNNING</span>';

        try {
            const resp = await fetch(`/api/run/${partNum}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ params: this.allParams[partNum] || {} }),
            });

            const result = await resp.json();
            this.partResults[partNum] = result;

            if (statusEl) {
                statusEl.innerHTML = `<span class="status-badge ${result.status}"><span class="status-dot"></span> ${result.status.toUpperCase()}</span>
                    <span style="color:var(--text-muted);font-size:12px;margin-left:8px;">${result.duration}s</span>`;
            }

            // Render results
            this.renderPartResults(partNum, result);
            this.showToast(`Part ${partNum} ${result.status}`, result.status === 'completed' ? 'success' : 'error');

        } catch (e) {
            this.showToast('Error: ' + e.message, 'error');
            if (statusEl) statusEl.innerHTML = '<span class="status-badge failed"><span class="status-dot"></span> FAILED</span>';
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = `▶ Run Part ${partNum}`; }
            this.isRunning = false;
        }
    },

    // ── Load Part Page ───────────────────────────────────────
    async loadPartPage(partNum) {
        this.renderPartParams(partNum);
        // Load existing outputs
        try {
            const resp = await fetch(`/api/outputs/${partNum}`);
            const data = await resp.json();
            if (data.files && data.files.length > 0) {
                this.renderOutputs(partNum, data.files);
            }
        } catch (e) {
            console.error(`Failed to load outputs for part ${partNum}:`, e);
        }
    },

    // ── Render Parameters ────────────────────────────────────
    renderPartParams(partNum) {
        const container = document.getElementById(`part${partNum}-params`);
        if (!container) return;

        const schema = this.paramSchemas[partNum];
        const defaults = this.defaultParams[partNum];
        const current = this.allParams[partNum];
        if (!schema) return;

        let html = '<div class="params-grid">';
        for (const [key, s] of Object.entries(schema)) {
            const val = current[key] !== undefined ? current[key] : defaults[key];
            const isModified = JSON.stringify(val) !== JSON.stringify(defaults[key]);
            const modClass = isModified ? 'modified' : '';

            html += `<div class="param-item ${modClass}" id="param-${partNum}-${key}">`;
            html += `<div class="form-label">
                        <span>${s.label}</span>
                        <span class="default-val">Default: ${this.formatParamValue(defaults[key])}</span>
                     </div>`;

            if (s.type === 'int' || s.type === 'float') {
                const step = s.step || (s.type === 'float' ? 0.01 : 1);
                html += `<div class="slider-row">
                    <input type="range" min="${s.min}" max="${s.max}" step="${step}"
                           value="${val}"
                           id="input-${partNum}-${key}"
                           oninput="DSPLab.updateParam(${partNum},'${key}',this.value,${s.type === 'float'})">
                    <span class="slider-value" id="val-${partNum}-${key}">${val}</span>
                </div>`;
            } else if (s.type === 'tuple_int' || s.type === 'tuple_float') {
                const valStr = Array.isArray(val) ? val.join(', ') : val.toString();
                html += `<input type="text" class="form-control" value="${valStr}"
                           id="input-${partNum}-${key}"
                           onchange="DSPLab.updateTupleParam(${partNum},'${key}',this.value)">`;
            }

            html += `<div class="param-help">${s.help || ''}</div>`;
            html += '</div>';
        }
        html += '</div>';

        html += `<div style="margin-top:16px;display:flex;gap:10px;">
            <button class="btn btn-secondary btn-sm" onclick="DSPLab.resetParams(${partNum})">
                ↺ Reset to Original Defaults
            </button>
        </div>`;

        container.innerHTML = html;
    },

    formatParamValue(val) {
        if (Array.isArray(val) || (typeof val === 'object' && val !== null)) {
            return Array.isArray(val) ? val.join(', ') : JSON.stringify(val);
        }
        return String(val);
    },

    updateParam(partNum, key, value, isFloat = false) {
        const numVal = isFloat ? parseFloat(value) : parseInt(value);
        this.allParams[partNum][key] = numVal;

        const valEl = document.getElementById(`val-${partNum}-${key}`);
        if (valEl) valEl.textContent = isFloat ? numVal.toFixed(3) : numVal;

        const container = document.getElementById(`param-${partNum}-${key}`);
        const isModified = numVal !== this.defaultParams[partNum][key];
        if (container) container.classList.toggle('modified', isModified);
    },

    updateTupleParam(partNum, key, value) {
        try {
            const vals = value.split(',').map(v => parseInt(v.trim()));
            this.allParams[partNum][key] = vals;
        } catch (e) {
            this.showToast('Invalid tuple format. Use comma-separated integers.', 'error');
        }
    },

    resetParams(partNum) {
        this.allParams[partNum] = { ...this.defaultParams[partNum] };
        this.renderPartParams(partNum);
        this.showToast(`Part ${partNum} parameters reset to defaults`, 'info');
    },

    // ── Render Part Results ──────────────────────────────────
    renderPartResults(partNum, result) {
        // Console output
        const console = document.getElementById(`part${partNum}-console`);
        if (console) {
            let content = result.stdout || '';
            if (result.error) content += '\n\n' + result.error;
            console.textContent = content;
        }

        // Metrics
        const metricsEl = document.getElementById(`part${partNum}-metrics`);
        if (metricsEl && result.metrics && Object.keys(result.metrics).length > 0) {
            let html = '<table class="metrics-table"><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>';
            for (const [key, val] of Object.entries(result.metrics)) {
                html += `<tr><td>${key}</td><td>${val}</td></tr>`;
            }
            html += '</tbody></table>';
            metricsEl.innerHTML = html;
        }

        // Output files
        if (result.outputs && result.outputs.length > 0) {
            const files = result.outputs.map(path => {
                const name = path.split(/[/\\]/).pop();
                return {
                    name,
                    path,
                    type: this.getFileType(name),
                    url: `/api/file/${partNum}/${name}`,
                };
            });
            this.renderOutputs(partNum, files);
        }
    },

    // ── Render Outputs ───────────────────────────────────────
    renderOutputs(partNum, files) {
        const gallery = document.getElementById(`part${partNum}-gallery`);
        if (!gallery) return;

        const images = files.filter(f => f.type === 'image');
        const audios = files.filter(f => f.type === 'audio');

        let html = '';

        // Audio players
        if (audios.length > 0) {
            html += '<div style="margin-bottom:16px;">';
            for (const f of audios) {
                html += `<div class="audio-player">
                    <span class="audio-label">🔊 ${f.name}</span>
                    <audio controls src="${f.url}" preload="none"></audio>
                    <a href="${f.url}" download="${f.name}" class="download-link">⬇ Download</a>
                </div>`;
            }
            html += '</div>';
        }

        // Image gallery
        if (images.length > 0) {
            html += '<div class="results-gallery">';
            for (const f of images) {
                const ts = Date.now();
                html += `<div class="result-item">
                    <img src="${f.url}?t=${ts}" alt="${f.name}" onclick="DSPLab.openModal('${f.url}?t=${ts}')" loading="lazy">
                    <div class="result-item-footer">
                        <span>${f.name}</span>
                        <a href="${f.url}" download="${f.name}" class="download-link">⬇ Download</a>
                    </div>
                </div>`;
            }
            html += '</div>';
        }

        if (!html) {
            html = `<div class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>No Results Yet</h3>
                <p>Run this part to generate visualizations and results.</p>
            </div>`;
        }

        gallery.innerHTML = html;
    },

    getFileType(name) {
        const ext = name.split('.').pop().toLowerCase();
        if (['png', 'jpg', 'jpeg', 'bmp', 'gif'].includes(ext)) return 'image';
        if (['wav', 'mp3', 'ogg'].includes(ext)) return 'audio';
        return 'other';
    },

    // ── Image Modal ──────────────────────────────────────────
    setupModal() {
        const modal = document.getElementById('image-modal');
        if (modal) {
            modal.addEventListener('click', () => {
                modal.classList.remove('show');
            });
        }
    },

    openModal(src) {
        const modal = document.getElementById('image-modal');
        const img = document.getElementById('modal-image');
        if (modal && img) {
            img.src = src;
            modal.classList.add('show');
        }
    },

    // ── Tabs ─────────────────────────────────────────────────
    switchTab(partNum, tabName) {
        const container = document.getElementById(`page-part${partNum}`);
        if (!container) return;

        container.querySelectorAll(`.tab[data-part="${partNum}"]`).forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tabName);
        });
        container.querySelectorAll(`.tab-content[data-part="${partNum}"]`).forEach(c => {
            c.classList.toggle('active', c.dataset.tab === tabName);
        });
    },

    // ── Experiment History ────────────────────────────────────
    async loadExperimentHistory() {
        try {
            const resp = await fetch('/api/experiments');
            const data = await resp.json();
            const container = document.getElementById('experiment-list');
            if (!container) return;

            if (!data.experiments || data.experiments.length === 0) {
                container.innerHTML = `<div class="empty-state">
                    <div class="empty-icon">🧪</div>
                    <h3>No Experiments Yet</h3>
                    <p>Run experiments from the dashboard or individual parts to see history here.</p>
                </div>`;
                return;
            }

            let html = '<div class="exp-list">';
            for (const exp of data.experiments) {
                html += `<div class="exp-item">
                    <div class="exp-item-info">
                        <div class="exp-item-id">${exp.id}</div>
                        <div class="exp-item-label">${exp.label || 'Unnamed Experiment'}</div>
                        <div class="exp-item-meta">
                            ${exp.created_at} · Parts: ${exp.parts.join(', ')}
                        </div>
                    </div>
                    <span class="status-badge ${exp.status}"><span class="status-dot"></span> ${exp.status}</span>
                    <button class="btn btn-danger btn-sm" onclick="DSPLab.deleteExperiment('${exp.id}')">✕</button>
                </div>`;
            }
            html += '</div>';
            container.innerHTML = html;
        } catch (e) {
            console.error('Failed to load experiments:', e);
        }
    },

    async deleteExperiment(expId) {
        try {
            await fetch(`/api/experiments/${expId}`, { method: 'DELETE' });
            this.loadExperimentHistory();
            this.showToast('Experiment deleted', 'info');
        } catch (e) {
            this.showToast('Failed to delete experiment', 'error');
        }
    },

    async saveExperiment(label) {
        try {
            const params = {};
            for (let p = 1; p <= 6; p++) {
                params[p] = this.allParams[p];
            }
            const resp = await fetch('/api/experiments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    parts: [1, 2, 3, 4, 5, 6],
                    params,
                    label: label || `Experiment ${new Date().toLocaleString()}`,
                }),
            });
            const data = await resp.json();
            this.showToast('Experiment saved!', 'success');
            return data;
        } catch (e) {
            this.showToast('Failed to save experiment', 'error');
        }
    },

    // ── Toast Notifications ──────────────────────────────────
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span> ${message}`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    },
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => DSPLab.init());
