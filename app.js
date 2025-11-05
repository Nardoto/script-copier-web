// ========================================
// SCRIPT COPIER WEB - Main Application
// Portado de ScriptCopier_UNIVERSAL.py
// ========================================

class ScriptCopierApp {
    constructor() {
        this.projects = {};
        this.currentProject = null;
        this.copyHistory = this.loadHistory();
        this.directoryHandle = null; // Handle para acesso direto à pasta
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFromLocalStorage();
        this.updateRefreshButtonVisibility();
        this.checkSavedDirectory();
    }

    setupEventListeners() {
        // Upload button - agora usa File System Access API
        document.getElementById('uploadButton').addEventListener('click', () => {
            this.selectDirectory();
        });

        // Refresh button - recarrega arquivos da pasta
        document.getElementById('refreshButton').addEventListener('click', () => {
            if (this.directoryHandle) {
                this.readDirectoryFiles(this.directoryHandle);
            }
        });

        // Fallback para navegadores sem suporte
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                this.switchTab(button.dataset.tab);
            });
        });

        // YouTube save button
        document.getElementById('saveYoutubeData')?.addEventListener('click', () => {
            this.saveYoutubeData();
        });

        // Status buttons
        document.querySelectorAll('.status-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.status-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // Modal copy button
        document.getElementById('modalCopyButton')?.addEventListener('click', () => {
            this.copyCurrentSection();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
            if (e.ctrlKey && e.key === 'c' && !window.getSelection().toString()) {
                // Implementar copiar seção atual se necessário
            }
        });
    }

    // ========================================
    // FILE SYSTEM ACCESS API (Acesso Direto à Pasta)
    // ========================================

    async selectDirectory() {
        // Verifica se o navegador suporta File System Access API
        if (!('showDirectoryPicker' in window)) {
            this.showToast('⚠️ Navegador não suporta acesso direto. Use upload de pasta.', 'error');
            document.getElementById('fileInput').click();
            return;
        }

        try {
            // Solicita acesso à pasta
            const dirHandle = await window.showDirectoryPicker({
                mode: 'read',
                startIn: 'documents'
            });

            this.directoryHandle = dirHandle;
            await this.saveDirectoryHandle(dirHandle);

            this.showToast(`📁 Pasta "${dirHandle.name}" selecionada!`, 'success');
            this.updateRefreshButtonVisibility();

            // Lê todos os arquivos da pasta
            await this.readDirectoryFiles(dirHandle);

        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('Erro ao selecionar pasta:', err);
                this.showToast('Erro ao acessar pasta', 'error');
            }
        }
    }

    async checkSavedDirectory() {
        const savedHandle = await this.loadDirectoryHandle();

        if (!savedHandle) return;

        try {
            // Verifica se ainda tem permissão
            const permission = await savedHandle.queryPermission({ mode: 'read' });

            if (permission === 'granted') {
                this.directoryHandle = savedHandle;
                this.showToast(`✅ Pasta "${savedHandle.name}" reconectada!`, 'success');
                this.updateRefreshButtonVisibility();
                await this.readDirectoryFiles(savedHandle);
            } else if (permission === 'prompt') {
                // Pede permissão novamente
                const newPermission = await savedHandle.requestPermission({ mode: 'read' });
                if (newPermission === 'granted') {
                    this.directoryHandle = savedHandle;
                    this.updateRefreshButtonVisibility();
                    await this.readDirectoryFiles(savedHandle);
                }
            }
        } catch (err) {
            console.log('Pasta salva não está mais acessível');
            await this.clearSavedDirectory();
        }
    }

    async readDirectoryFiles(dirHandle) {
        this.showToast('Lendo arquivos da pasta...', 'info');

        const projectMap = {};

        // Percorre todas as entradas (pastas e arquivos)
        for await (const entry of dirHandle.values()) {
            // Se for uma subpasta
            if (entry.kind === 'directory') {
                const projectName = entry.name;
                const files = [];

                // Lê arquivos dentro da subpasta
                for await (const fileEntry of entry.values()) {
                    if (fileEntry.kind === 'file' && fileEntry.name.endsWith('.txt')) {
                        const file = await fileEntry.getFile();
                        const content = await file.text();

                        files.push({
                            name: file.name,
                            content: content,
                            size: file.size,
                            relativePath: `${projectName}/${file.name}`
                        });
                    }
                }

                if (files.length > 0) {
                    projectMap[projectName] = {
                        name: projectName,
                        files: files,
                        path: projectName
                    };
                }
            }
            // Se for arquivo .txt direto na raiz
            else if (entry.kind === 'file' && entry.name.endsWith('.txt')) {
                const file = await entry.getFile();
                const content = await file.text();

                const projectName = dirHandle.name;

                if (!projectMap[projectName]) {
                    projectMap[projectName] = {
                        name: projectName,
                        files: [],
                        path: ''
                    };
                }

                projectMap[projectName].files.push({
                    name: file.name,
                    content: content,
                    size: file.size,
                    relativePath: file.name
                });
            }
        }

        // Parse sections for each project
        Object.values(projectMap).forEach(project => {
            project.sections = this.parseAllSections(project);
            this.projects[project.name] = project;
        });

        this.saveToLocalStorage();
        this.renderProjects();

        const projectCount = Object.keys(projectMap).length;
        const fileCount = Object.values(projectMap).reduce((sum, p) => sum + p.files.length, 0);
        this.showToast(`${projectCount} projeto(s) • ${fileCount} arquivo(s) lidos!`, 'success');
    }

    async saveDirectoryHandle(dirHandle) {
        try {
            const db = await this.openDatabase();
            const tx = db.transaction('handles', 'readwrite');
            await tx.objectStore('handles').put(dirHandle, 'rootDirectory');
            await tx.done;
        } catch (err) {
            console.error('Erro ao salvar handle:', err);
        }
    }

    async loadDirectoryHandle() {
        try {
            const db = await this.openDatabase();
            const tx = db.transaction('handles', 'readonly');
            const handle = await tx.objectStore('handles').get('rootDirectory');
            await tx.done;
            return handle;
        } catch (err) {
            console.error('Erro ao carregar handle:', err);
            return null;
        }
    }

    async clearSavedDirectory() {
        try {
            const db = await this.openDatabase();
            const tx = db.transaction('handles', 'readwrite');
            await tx.objectStore('handles').delete('rootDirectory');
            await tx.done;
        } catch (err) {
            console.error('Erro ao limpar handle:', err);
        }
    }

    async openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('ScriptCopierDB', 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('handles')) {
                    db.createObjectStore('handles');
                }
            };
        });
    }

    updateRefreshButtonVisibility() {
        const refreshButton = document.getElementById('refreshButton');
        const uploadButton = document.getElementById('uploadButton');

        if (this.directoryHandle) {
            refreshButton.style.display = 'inline-flex';
            uploadButton.textContent = 'Alterar Pasta';
        } else {
            refreshButton.style.display = 'none';
            uploadButton.textContent = 'Selecionar Pasta';
        }
    }

    // ========================================
    // FILE UPLOAD & PARSING (Fallback)
    // ========================================

    async handleFileUpload(files) {
        if (files.length === 0) return;

        this.showToast('Processando estrutura de pastas...', 'info');

        // Group files by project (actual folder structure)
        const projectMap = {};

        for (const file of files) {
            // Only process .txt files
            if (!file.name.endsWith('.txt')) continue;

            // Extract project name from file path
            const projectName = this.extractProjectNameFromPath(file.webkitRelativePath || file.name);

            if (!projectName) continue;

            // Create project if doesn't exist
            if (!projectMap[projectName]) {
                projectMap[projectName] = {
                    name: projectName,
                    files: [],
                    path: this.extractProjectPath(file.webkitRelativePath)
                };
            }

            // Read file content
            const content = await this.readFile(file);

            projectMap[projectName].files.push({
                name: file.name,
                content: content,
                size: file.size,
                relativePath: file.webkitRelativePath
            });
        }

        // Parse sections for each project
        Object.values(projectMap).forEach(project => {
            project.sections = this.parseAllSections(project);
            this.projects[project.name] = project;
        });

        this.saveToLocalStorage();
        this.renderProjects();

        const projectCount = Object.keys(projectMap).length;
        const fileCount = Object.values(projectMap).reduce((sum, p) => sum + p.files.length, 0);
        this.showToast(`${projectCount} projeto(s) • ${fileCount} arquivo(s) carregados!`, 'success');
    }

    extractProjectNameFromPath(path) {
        if (!path) return null;

        // Path format: "RootFolder/ProjectFolder/file.txt"
        // We want "ProjectFolder"
        const parts = path.split('/');

        if (parts.length < 2) {
            // No subfolder, use root as project name
            return parts[0] || 'Projeto Principal';
        }

        // Get the folder name (second to last part, before filename)
        return parts[parts.length - 2];
    }

    extractProjectPath(path) {
        if (!path) return '';
        const parts = path.split('/');
        parts.pop(); // Remove filename
        return parts.join('/');
    }

    readFile(file) {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.readAsText(file, 'UTF-8');
        });
    }

    // ========================================
    // SECTION PARSING (Portado do Python)
    // ========================================

    parseAllSections(project) {
        const sections = [];

        project.files.forEach(file => {
            const fileSections = this.detectSections(file.content, file.name);
            sections.push(...fileSections);
        });

        return sections;
    }

    detectSections(text, filename) {
        // Padrões de seção (portados de ScriptCopier_UNIVERSAL.py)
        const patterns = [
            { regex: /^HOOK\s*\(.*?\).*?$/gm, type: 'HOOK' },
            { regex: /^ATO\s+[IVXLCDM]+\s*[-–]\s*(.+?)(?:\s*▓▓▓)?$/gm, type: 'ATO' },
            { regex: /^ACT\s+[IVXLCDM]+\s*[-–]\s*(.+?)(?:\s*▓▓▓)?$/gm, type: 'ACT' },
            { regex: /^CONCLUS[ÃA]O\s*(?:[-–]\s*(.+?))?(?:\s*▓▓▓)?$/gm, type: 'CONCLUSÃO' },
            { regex: /^CHAPTER\s+\w+\s*[-–]\s*(.+)$/gm, type: 'CHAPTER' },
            { regex: /^SCENE\s+\d+\s*[-–]\s*(.+)$/gm, type: 'SCENE' },
            { regex: /^OPENING\s*[-–]?\s*(.*)$/gm, type: 'OPENING' },
            { regex: /^CENA\s+\d+\s*[-–]\s*(.+)$/gm, type: 'CENA' },
            { regex: /^#{1,3}\s*(.+)$/gm, type: 'HEADING' }
        ];

        const sections = [];
        const matches = [];

        // Find all section markers
        patterns.forEach(({ regex, type }) => {
            let match;
            regex.lastIndex = 0;
            while ((match = regex.exec(text)) !== null) {
                matches.push({
                    type,
                    title: match[0].trim(),
                    index: match.index
                });
            }
        });

        // Sort by position
        matches.sort((a, b) => a.index - b.index);

        // Extract text between sections
        for (let i = 0; i < matches.length; i++) {
            const current = matches[i];
            const next = matches[i + 1];

            const startPos = current.index;
            const endPos = next ? next.index : text.length;

            let sectionText = text.substring(startPos, endPos).trim();

            // Remove the title from the text
            sectionText = sectionText.substring(current.title.length).trim();

            // Count words and characters
            const wordCount = sectionText.split(/\s+/).filter(w => w.length > 0).length;
            const charCount = sectionText.length;

            sections.push({
                id: `${filename}_${i}`,
                type: current.type,
                title: current.title,
                text: sectionText,
                filename,
                wordCount,
                charCount,
                position: i + 1
            });
        }

        return sections;
    }

    // ========================================
    // CLIPBOARD & COPY HISTORY
    // ========================================

    async copyToClipboard(text, sectionId, sectionTitle) {
        try {
            await navigator.clipboard.writeText(text);

            // Update copy history
            this.updateCopyHistory(sectionId, sectionTitle);

            this.showToast('✓ Texto copiado!', 'success');
            this.updateSectionUI(sectionId);

            return true;
        } catch (err) {
            console.error('Erro ao copiar:', err);
            this.showToast('Erro ao copiar texto', 'error');
            return false;
        }
    }

    updateCopyHistory(sectionId, sectionTitle) {
        const now = new Date().toISOString();

        if (!this.copyHistory[this.currentProject]) {
            this.copyHistory[this.currentProject] = {};
        }

        if (!this.copyHistory[this.currentProject][sectionId]) {
            this.copyHistory[this.currentProject][sectionId] = {
                title: sectionTitle,
                primeira_copia: now,
                ultima_copia: now,
                contador: 1
            };
        } else {
            this.copyHistory[this.currentProject][sectionId].ultima_copia = now;
            this.copyHistory[this.currentProject][sectionId].contador++;
        }

        this.saveHistory();
    }

    getCopyInfo(sectionId) {
        if (!this.currentProject || !this.copyHistory[this.currentProject]) {
            return null;
        }
        return this.copyHistory[this.currentProject][sectionId];
    }

    // ========================================
    // UI RENDERING
    // ========================================

    renderProjects() {
        const projectList = document.getElementById('projectList');
        const emptyState = document.querySelector('.empty-state');
        const tabsContainer = document.getElementById('tabsContainer');

        if (Object.keys(this.projects).length === 0) {
            projectList.style.display = 'none';
            emptyState.style.display = 'block';
            tabsContainer.style.display = 'none';
            return;
        }

        emptyState.style.display = 'none';
        projectList.style.display = 'grid';
        tabsContainer.style.display = 'block';

        projectList.innerHTML = Object.entries(this.projects).map(([name, project]) => {
            const fileCount = project.files.length;
            const sectionCount = project.sections.length;
            const isActive = this.currentProject === name;

            return `
                <div class="project-card ${isActive ? 'active' : ''}" onclick="app.selectProject('${name}')">
                    <h3>${name}</h3>
                    <div class="file-count">${fileCount} arquivo(s) • ${sectionCount} seção(ões)</div>
                    <div class="status-indicator">📄</div>
                </div>
            `;
        }).join('');

        // Select first project if none selected
        if (!this.currentProject && Object.keys(this.projects).length > 0) {
            this.selectProject(Object.keys(this.projects)[0]);
        }
    }

    selectProject(projectName) {
        this.currentProject = projectName;
        this.renderProjects();
        this.renderSections();
        this.renderFiles();
    }

    renderSections() {
        const sectionsList = document.getElementById('sectionsList');
        if (!this.currentProject) {
            sectionsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Selecione um projeto</p>';
            return;
        }

        const project = this.projects[this.currentProject];
        if (!project.sections || project.sections.length === 0) {
            sectionsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Nenhuma seção detectada</p>';
            return;
        }

        sectionsList.innerHTML = project.sections.map(section => {
            const copyInfo = this.getCopyInfo(section.id);
            const isCopied = copyInfo !== null;

            return `
                <div class="section-card ${isCopied ? 'copied' : ''}" onclick="app.openSectionModal('${section.id}')">
                    <div class="section-info">
                        <h3>${section.title}</h3>
                        <div class="section-meta">
                            <span>${section.wordCount} palavras</span>
                            <span>${section.charCount} caracteres</span>
                            ${isCopied ? `<span class="copy-badge">Copiado ${copyInfo.contador}x</span>` : ''}
                        </div>
                    </div>
                    <div class="section-action">
                        ${isCopied ? '✓' : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    renderFiles() {
        const filesList = document.getElementById('filesList');
        if (!this.currentProject) {
            filesList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Selecione um projeto</p>';
            return;
        }

        const project = this.projects[this.currentProject];
        filesList.innerHTML = project.files.map(file => {
            const sizeKB = (file.size / 1024).toFixed(1);
            return `
                <div class="file-item">
                    <div class="file-name">📄 ${file.name}</div>
                    <div class="file-size">${sizeKB} KB</div>
                </div>
            `;
        }).join('');
    }

    updateSectionUI(sectionId) {
        // Re-render to show updated copy status
        this.renderSections();
    }

    // ========================================
    // MODAL
    // ========================================

    openSectionModal(sectionId) {
        const section = this.findSection(sectionId);
        if (!section) return;

        document.getElementById('modalSectionTitle').textContent = section.title;
        document.getElementById('modalSectionText').textContent = section.text;

        const copyInfo = this.getCopyInfo(sectionId);
        const copyCount = document.getElementById('modalCopyCount');

        if (copyInfo) {
            const lastCopy = new Date(copyInfo.ultima_copia).toLocaleString('pt-BR');
            copyCount.textContent = `Copiado ${copyInfo.contador}x • Última vez: ${lastCopy}`;
        } else {
            copyCount.textContent = 'Nunca copiado';
        }

        // Store current section for copy button
        this.currentModalSection = section;

        document.getElementById('sectionModal').classList.add('active');
    }

    closeModal() {
        document.getElementById('sectionModal').classList.remove('active');
        this.currentModalSection = null;
    }

    async copyCurrentSection() {
        if (!this.currentModalSection) return;

        const success = await this.copyToClipboard(
            this.currentModalSection.text,
            this.currentModalSection.id,
            this.currentModalSection.title
        );

        if (success) {
            // Update modal copy info
            const copyInfo = this.getCopyInfo(this.currentModalSection.id);
            const copyCount = document.getElementById('modalCopyCount');
            const lastCopy = new Date(copyInfo.ultima_copia).toLocaleString('pt-BR');
            copyCount.textContent = `Copiado ${copyInfo.contador}x • Última vez: ${lastCopy}`;
        }
    }

    findSection(sectionId) {
        if (!this.currentProject) return null;
        const project = this.projects[this.currentProject];
        return project.sections.find(s => s.id === sectionId);
    }

    // ========================================
    // TAB MANAGEMENT
    // ========================================

    switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');
    }

    // ========================================
    // YOUTUBE DATA
    // ========================================

    saveYoutubeData() {
        if (!this.currentProject) return;

        const youtubeData = {
            titles: document.getElementById('titles').value,
            description: document.getElementById('description').value,
            thumbnail: document.getElementById('thumbnail').value,
            status: document.querySelector('.status-btn.active')?.dataset.status || 'new'
        };

        this.projects[this.currentProject].youtubeData = youtubeData;
        this.saveToLocalStorage();
        this.showToast('Informações salvas!', 'success');
    }

    // ========================================
    // STORAGE
    // ========================================

    saveToLocalStorage() {
        try {
            localStorage.setItem('scriptCopier_projects', JSON.stringify(this.projects));
        } catch (e) {
            console.error('Erro ao salvar:', e);
        }
    }

    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('scriptCopier_projects');
            if (saved) {
                this.projects = JSON.parse(saved);
                this.renderProjects();
            }
        } catch (e) {
            console.error('Erro ao carregar:', e);
        }
    }

    saveHistory() {
        try {
            localStorage.setItem('scriptCopier_history', JSON.stringify(this.copyHistory));
        } catch (e) {
            console.error('Erro ao salvar histórico:', e);
        }
    }

    loadHistory() {
        try {
            const saved = localStorage.getItem('scriptCopier_history');
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            console.error('Erro ao carregar histórico:', e);
            return {};
        }
    }

    // ========================================
    // TOAST NOTIFICATIONS
    // ========================================

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// ========================================
// GLOBAL FUNCTIONS (for onclick handlers)
// ========================================

function closeModal() {
    app.closeModal();
}

// ========================================
// INITIALIZE APP
// ========================================

let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ScriptCopierApp();
    console.log('Script Copier Web initialized ✓');
});
