// ========================================
// SCRIPT COPIER WEB - Desktop Layout
// Portado de ScriptCopier_UNIVERSAL.py
// Version: 2.8.3 - Tradutor COMPLETO: scroll sincronizado, navegação entre seções, tradução de arquivo completo
// ========================================

class ScriptCopierApp {
    constructor() {
        console.log('🚀 Script Copier v2.8.3 - Tradutor completo com scroll sincronizado e arquivo completo');

        // Nova estrutura: múltiplas pastas raiz
        this.rootFolders = []; // Array de {id, name, handle, projects}
        this.currentRootFolderId = null;

        this.projects = {}; // Projetos da pasta raiz atual
        this.currentProject = null;
        this.currentSection = null;
        this.currentFile = null;
        this.copyHistory = this.loadHistory();

        // FORÇA limpeza do cache do YouTube para testar
        localStorage.removeItem('youtubeData');
        console.log('🔄 Cache do YouTube limpo!');

        this.youtubeData = this.loadYoutubeData();
        this.directoryHandle = null;

        // AI Configuration
        this.geminiApiKey = localStorage.getItem('geminiApiKey') || '';

        this.init();
    }

    async init() {
        this.setupEventListeners();

        // Carregar pastas raiz salvas
        await this.loadRootFoldersFromIndexedDB();
        this.renderRootFolderDropdown();

        // Se houver pastas raiz salvas, não carregar localStorage antigo
        if (this.rootFolders.length === 0) {
            this.loadFromLocalStorage();
            await this.checkSavedDirectory();
        } else {
            // Se houver 1 pasta, carregar automaticamente
            if (this.rootFolders.length === 1) {
                this.currentRootFolderId = this.rootFolders[0].id;
                await this.loadRootFolderProjects(this.currentRootFolderId);
                this.renderRootFolderDropdown();
            }
        }

        this.updateUI();
    }

    // ========================================
    // EVENT LISTENERS
    // ========================================

    setupEventListeners() {
        // Header buttons
        document.getElementById('helpButton').addEventListener('click', () => {
            document.getElementById('helpModal').style.display = 'block';
        });

        document.getElementById('aboutButton').addEventListener('click', () => {
            document.getElementById('aboutModal').style.display = 'block';
        });

        document.getElementById('settingsButton').addEventListener('click', () => {
            this.openSettingsModal();
        });

        // Close modals when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        });

        // Root folder management
        document.getElementById('rootFolderDropdown')?.addEventListener('change', (e) => {
            this.switchRootFolder(e.target.value);
        });

        document.getElementById('addRootFolderButton')?.addEventListener('click', () => {
            console.log('🖱️ Botão "+Nova Pasta" clicado');
            this.addNewRootFolder();
        });

        document.getElementById('removeRootFolderButton')?.addEventListener('click', () => {
            this.removeCurrentRootFolder();
        });

        document.getElementById('openFolderButton')?.addEventListener('click', () => {
            this.openProjectFolder();
        });

        document.getElementById('uploadButton').addEventListener('click', () => {
            console.log('🖱️ Botão "Selecionar Pasta" clicado');
            this.selectDirectory();
        });

        document.getElementById('refreshButton')?.addEventListener('click', () => {
            if (this.directoryHandle) {
                this.readDirectoryFiles(this.directoryHandle);
            }
        });

        document.getElementById('saveButton')?.addEventListener('click', () => {
            this.saveToLocalStorage();
            this.showToast('Estado salvo com sucesso!', 'success');
        });

        // Fallback file input
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Project dropdown
        document.getElementById('projectDropdown')?.addEventListener('change', (e) => {
            this.selectProject(e.target.value);
        });

        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                this.switchTab(button.dataset.tab);
            });
        });

        // Preview actions
        document.getElementById('copyTextButton')?.addEventListener('click', () => {
            this.copyCurrentSection();
        });

        document.getElementById('saveTextButton')?.addEventListener('click', () => {
            this.saveCurrentSection();
        });

        // File preview copy button
        document.getElementById('copyFileButton')?.addEventListener('click', () => {
            this.copyCurrentFile();
        });

        // File translation button
        document.getElementById('translateFileButton')?.addEventListener('click', () => {
            this.translateEntireFile();
        });

        // YouTube form
        document.getElementById('saveYoutubeData')?.addEventListener('click', () => {
            this.saveYoutubeData();
        });

        // Copy buttons for YouTube fields
        document.querySelectorAll('.btn-copy-icon').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.dataset.target;
                const element = document.getElementById(targetId);
                if (element) {
                    this.copyToClipboard(element.value || element.textContent);
                }
            });
        });

        // Analyze project button
        document.getElementById('analyzeProjectButton')?.addEventListener('click', () => {
            this.analyzeCurrentProject();
        });

        // Settings: API Key management
        document.getElementById('saveApiKeyButton')?.addEventListener('click', () => {
            this.saveGeminiApiKey();
        });

        document.getElementById('testApiKeyButton')?.addEventListener('click', () => {
            this.testGeminiConnection();
        });

        // AI Translator - Copy Tab
        document.getElementById('translateButton')?.addEventListener('click', () => {
            this.translateCurrentSection();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearSelection();
            }
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveToLocalStorage();
                this.showToast('Estado salvo!', 'success');
            }
        });
    }

    // ========================================
    // FILE SYSTEM ACCESS API
    // ========================================

    async selectDirectory() {
        console.log('🔍 selectDirectory() chamado');
        console.log('🌐 Navegador:', navigator.userAgent);
        console.log('📂 showDirectoryPicker disponível?', 'showDirectoryPicker' in window);

        if (!('showDirectoryPicker' in window)) {
            console.error('❌ API File System Access não disponível neste navegador');
            this.showToast('⚠️ Navegador não suporta acesso direto. Use Chrome ou Edge.', 'error');
            alert('⚠️ ATENÇÃO:\n\nEste navegador não suporta a API de acesso a pastas.\n\nPor favor, use:\n• Google Chrome\n• Microsoft Edge\n• Brave\n\nFirefox e Safari não são suportados para esta funcionalidade.');
            return;
        }

        try {
            console.log('📂 Abrindo seletor de pasta...');
            const dirHandle = await window.showDirectoryPicker({
                mode: 'read',
                startIn: 'documents'
            });

            console.log('✅ Pasta selecionada:', dirHandle.name);

            // Adicionar como nova pasta raiz
            await this.addRootFolderFromHandle(dirHandle);
        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('❌ Erro ao selecionar pasta:', err);
                this.showToast('Erro ao acessar pasta', 'error');
            } else {
                console.log('ℹ️ Usuário cancelou seleção de pasta');
            }
        }
    }

    // Adiciona nova pasta raiz (para botão "+Nova Pasta")
    async addNewRootFolder() {
        await this.selectDirectory();
    }

    // Abre pasta do projeto (limitação: navegadores não permitem abrir diretamente no Explorer)
    async openProjectFolder() {
        console.log('🖱️ Botão "Abrir Pasta" clicado');

        if (!this.currentRootFolderId) {
            this.showToast('⚠️ Nenhuma pasta raiz selecionada', 'error');
            return;
        }

        const rootFolder = this.rootFolders.find(rf => rf.id === this.currentRootFolderId);
        if (!rootFolder) {
            this.showToast('⚠️ Pasta raiz não encontrada', 'error');
            return;
        }

        // Por segurança, navegadores NÃO permitem abrir pastas no Explorer diretamente
        // Alternativa: Mostrar informações da pasta
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h2>📁 Pasta do Projeto</h2>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div style="background: var(--bg-hover); padding: 1.5rem; border-radius: var(--radius-sm); margin-bottom: 1rem;">
                        <h3 style="color: var(--accent-primary); margin: 0 0 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M3 5C3 3.89543 3.89543 3 5 3H8L10 5H15C16.1046 5 17 5.89543 17 7V15C17 16.1046 16.1046 17 15 17H5C3.89543 17 3 16.1046 3 15V5Z" stroke="currentColor" stroke-width="2"></path>
                            </svg>
                            ${rootFolder.name}
                        </h3>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">
                            Pasta raiz atual
                        </p>
                    </div>

                    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; border-radius: var(--radius-sm); margin-bottom: 1rem;">
                        <p style="margin: 0; color: #856404; font-size: 0.9rem;">
                            <strong>⚠️ Limitação do Navegador:</strong><br>
                            Por questões de segurança, navegadores não permitem abrir pastas diretamente no Windows Explorer via JavaScript.
                        </p>
                    </div>

                    <h4 style="color: var(--text-primary); margin: 1rem 0 0.5rem 0;">Como encontrar a pasta manualmente:</h4>
                    <ol style="color: var(--text-secondary); font-size: 0.9rem; padding-left: 1.5rem; margin: 0;">
                        <li style="margin-bottom: 0.5rem;">Abra o <strong>Windows Explorer</strong> (tecla Windows + E)</li>
                        <li style="margin-bottom: 0.5rem;">Procure pela pasta chamada: <code style="background: var(--bg-hover); padding: 0.2rem 0.5rem; border-radius: 3px; color: var(--accent-primary);">${rootFolder.name}</code></li>
                        <li style="margin-bottom: 0.5rem;">Ela deve estar no local onde você selecionou inicialmente</li>
                    </ol>

                    <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                        <button onclick="this.closest('.modal').remove()" class="btn-primary" style="width: 100%;">
                            ✅ Entendi
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Fechar modal ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // Adiciona pasta raiz a partir de um handle
    async addRootFolderFromHandle(dirHandle) {
        const id = Date.now().toString();
        const name = dirHandle.name;

        // Verificar se já existe
        const exists = this.rootFolders.find(rf => rf.name === name);
        if (exists) {
            this.showToast(`⚠️ Pasta "${name}" já está na lista!`, 'error');
            this.currentRootFolderId = exists.id;
            this.renderRootFolderDropdown();
            await this.loadRootFolderProjects(exists.id);
            return;
        }

        const rootFolder = {
            id,
            name,
            handle: dirHandle,
            projects: {}
        };

        this.rootFolders.push(rootFolder);
        this.currentRootFolderId = id;

        await this.saveRootFoldersToIndexedDB();
        this.renderRootFolderDropdown();
        this.showToast(`📁 Pasta "${name}" adicionada!`, 'success');

        // Carregar projetos desta pasta
        await this.loadRootFolderProjects(id);
    }

    // Remove pasta raiz atual
    async removeCurrentRootFolder() {
        if (!this.currentRootFolderId) return;

        const currentFolder = this.rootFolders.find(rf => rf.id === this.currentRootFolderId);
        if (!currentFolder) return;

        const confirmed = confirm(`Remover pasta raiz "${currentFolder.name}" da lista?\n\nIsso não apaga os arquivos do disco.`);
        if (!confirmed) return;

        this.rootFolders = this.rootFolders.filter(rf => rf.id !== this.currentRootFolderId);
        this.currentRootFolderId = null;
        this.projects = {};

        await this.saveRootFoldersToIndexedDB();
        this.renderRootFolderDropdown();
        this.updateUI();
        this.showToast(`🗑️ Pasta raiz removida da lista`, 'success');
    }

    // Troca para outra pasta raiz
    async switchRootFolder(folderId) {
        if (!folderId) return;

        this.currentRootFolderId = folderId;
        this.currentProject = null;
        this.projects = {};

        await this.loadRootFolderProjects(folderId);
    }

    // Carrega projetos de uma pasta raiz específica
    async loadRootFolderProjects(folderId) {
        const rootFolder = this.rootFolders.find(rf => rf.id === folderId);
        if (!rootFolder) return;

        this.showToast(`Carregando projetos de "${rootFolder.name}"...`, 'info');

        try {
            // Verificar permissão
            const permission = await rootFolder.handle.queryPermission({ mode: 'read' });
            if (permission !== 'granted') {
                const newPermission = await rootFolder.handle.requestPermission({ mode: 'read' });
                if (newPermission !== 'granted') {
                    this.showToast('⚠️ Permissão negada para acessar pasta', 'error');
                    return;
                }
            }

            // Ler diretórios e arquivos
            await this.readDirectoryFiles(rootFolder.handle, folderId);
        } catch (err) {
            console.error('Erro ao carregar projetos:', err);
            this.showToast(`Erro ao acessar pasta "${rootFolder.name}"`, 'error');
        }
    }

    // Renderiza dropdown de pastas raiz
    renderRootFolderDropdown() {
        const dropdown = document.getElementById('rootFolderDropdown');
        const manager = document.getElementById('rootFolderManager');
        const removeBtn = document.getElementById('removeRootFolderButton');
        const uploadBtn = document.getElementById('uploadButton');

        if (!dropdown || !manager) return;

        // Mostrar/ocultar gerenciador
        if (this.rootFolders.length > 0) {
            manager.style.display = 'flex';
            uploadBtn.style.display = 'none';
        } else {
            manager.style.display = 'none';
            uploadBtn.style.display = 'inline-flex';
        }

        // Preencher dropdown
        dropdown.innerHTML = '<option value="" disabled selected>Selecione pasta raiz</option>';
        this.rootFolders.forEach(rf => {
            const option = document.createElement('option');
            option.value = rf.id;
            option.textContent = `📁 ${rf.name}`;
            dropdown.appendChild(option);
        });

        // Selecionar atual
        if (this.currentRootFolderId) {
            dropdown.value = this.currentRootFolderId;
            removeBtn.style.display = 'inline-flex';
        } else {
            removeBtn.style.display = 'none';
        }
    }

    async checkSavedDirectory() {
        const savedHandle = await this.loadDirectoryHandle();
        if (!savedHandle) return;

        try {
            const permission = await savedHandle.queryPermission({ mode: 'read' });

            if (permission === 'granted') {
                this.directoryHandle = savedHandle;
                this.showToast(`✅ Pasta "${savedHandle.name}" reconectada!`, 'success');
                await this.readDirectoryFiles(savedHandle);
            } else if (permission === 'prompt') {
                const newPermission = await savedHandle.requestPermission({ mode: 'read' });
                if (newPermission === 'granted') {
                    this.directoryHandle = savedHandle;
                    await this.readDirectoryFiles(savedHandle);
                }
            }
        } catch (err) {
            console.log('Pasta salva não está mais acessível');
            await this.clearSavedDirectory();
        }
    }

    async readDirectoryFiles(dirHandle, folderId = null) {
        this.showToast('Lendo arquivos da pasta...', 'info');
        const projectMap = {};

        for await (const entry of dirHandle.values()) {
            if (entry.kind === 'directory') {
                const projectName = entry.name;
                const files = [];

                for await (const fileEntry of entry.values()) {
                    if (fileEntry.kind === 'file' && this.isSupportedFile(fileEntry.name)) {
                        const file = await fileEntry.getFile();
                        const content = await file.text();

                        files.push({
                            name: file.name,
                            content: content,
                            size: file.size,
                            relativePath: `${projectName}/${file.name}`,
                            lastModified: file.lastModified
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
        }

        // Parse sections for each project
        Object.values(projectMap).forEach(project => {
            project.sections = this.parseAllSections(project);
            this.projects[project.name] = project;
        });

        // Se folderId foi fornecido, salvar projetos na pasta raiz
        if (folderId) {
            const rootFolder = this.rootFolders.find(rf => rf.id === folderId);
            if (rootFolder) {
                rootFolder.projects = { ...projectMap };
                await this.saveRootFoldersToIndexedDB();
            }
        }

        this.saveToLocalStorage();
        this.renderProjectDropdown();
        this.updateUI();

        const projectCount = Object.keys(projectMap).length;
        const fileCount = Object.values(projectMap).reduce((sum, p) => sum + p.files.length, 0);
        this.showToast(`${projectCount} projeto(s) • ${fileCount} arquivo(s) lidos!`, 'success');
    }

    // IndexedDB methods for directory handle
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
            const request = indexedDB.open('ScriptCopierDB', 2); // Versão 2 para incluir rootFolders
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('handles')) {
                    db.createObjectStore('handles');
                }
                if (!db.objectStoreNames.contains('rootFolders')) {
                    db.createObjectStore('rootFolders');
                }
            };
        });
    }

    // Salvar pastas raiz no IndexedDB
    async saveRootFoldersToIndexedDB() {
        try {
            const db = await this.openDatabase();
            const tx = db.transaction('rootFolders', 'readwrite');
            const store = tx.objectStore('rootFolders');

            // Salvar cada pasta raiz separadamente
            for (const rf of this.rootFolders) {
                await store.put({
                    id: rf.id,
                    name: rf.name,
                    handle: rf.handle
                }, rf.id);
            }

            await tx.done;
            console.log('✅ Pastas raiz salvas no IndexedDB');
        } catch (err) {
            console.error('Erro ao salvar pastas raiz:', err);
        }
    }

    // Carregar pastas raiz do IndexedDB
    async loadRootFoldersFromIndexedDB() {
        try {
            const db = await this.openDatabase();
            const tx = db.transaction('rootFolders', 'readonly');
            const store = tx.objectStore('rootFolders');

            this.rootFolders = [];

            // Usar cursor em vez de getAllKeys para compatibilidade
            const request = store.openCursor();

            return new Promise((resolve, reject) => {
                request.onsuccess = (event) => {
                    const cursor = event.target.result;
                    if (cursor) {
                        const data = cursor.value;
                        if (data && data.handle) {
                            this.rootFolders.push({
                                id: data.id,
                                name: data.name,
                                handle: data.handle,
                                projects: {}
                            });
                        }
                        cursor.continue();
                    } else {
                        // Fim do cursor
                        console.log(`✅ ${this.rootFolders.length} pasta(s) raiz carregadas`);
                        resolve();
                    }
                };

                request.onerror = () => {
                    console.error('Erro ao carregar pastas raiz:', request.error);
                    reject(request.error);
                };
            });
        } catch (err) {
            console.error('Erro ao carregar pastas raiz:', err);
        }
    }

    // ========================================
    // FILE UPLOAD (Fallback)
    // ========================================

    async handleFileUpload(files) {
        if (files.length === 0) return;

        this.showToast('Processando arquivos...', 'info');
        const projectMap = {};

        for (const file of files) {
            if (!file.name.endsWith('.txt')) continue;

            const projectName = this.extractProjectNameFromPath(file.webkitRelativePath || file.name);
            if (!projectName) continue;

            if (!projectMap[projectName]) {
                projectMap[projectName] = {
                    name: projectName,
                    files: [],
                    path: this.extractProjectPath(file.webkitRelativePath)
                };
            }

            const content = await this.readFile(file);

            projectMap[projectName].files.push({
                name: file.name,
                content: content,
                size: file.size,
                relativePath: file.webkitRelativePath,
                lastModified: file.lastModified
            });
        }

        Object.values(projectMap).forEach(project => {
            project.sections = this.parseAllSections(project);
            this.projects[project.name] = project;
        });

        this.saveToLocalStorage();
        this.renderProjectDropdown();
        this.updateUI();

        const projectCount = Object.keys(projectMap).length;
        const fileCount = Object.values(projectMap).reduce((sum, p) => sum + p.files.length, 0);
        this.showToast(`${projectCount} projeto(s) • ${fileCount} arquivo(s) carregados!`, 'success');
    }

    extractProjectNameFromPath(path) {
        if (!path) return null;
        const parts = path.split('/');
        if (parts.length < 2) return parts[0] || 'Projeto Principal';
        return parts[parts.length - 2];
    }

    extractProjectPath(path) {
        if (!path) return '';
        const parts = path.split('/');
        parts.pop();
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
    // SECTION PARSING
    // ========================================

    parseAllSections(project) {
        const sections = [];

        // Prioridade: buscar arquivo 03_Texto_Narrado.txt
        const narratedFile = project.files.find(f => f.name.includes('03_Texto_Narrado'));

        if (narratedFile) {
            // Se encontrou arquivo 03, usar APENAS ele
            const fileSections = this.parseSections(narratedFile.content, narratedFile.name);
            sections.push(...fileSections);
        } else {
            // Senão, buscar em todos os arquivos (comportamento antigo)
            project.files.forEach(file => {
                const fileSections = this.parseSections(file.content, file.name);
                sections.push(...fileSections);
            });
        }

        return sections;
    }

    parseSections(content, fileName) {
        const sections = [];
        const patterns = [
            { regex: /^OPENING\s*[-–:]?\s*(.*)$/gmi, type: 'OPENING' },
            { regex: /^HOOK\s*\((.+?)\).*$/gmi, type: 'HOOK' },

            // ACT/ATO com números romanos ou por extenso - aceita : ou -
            { regex: /^(ATO|ACT)\s+([IVXLCDM]+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)\s*[-–:]\s*(.+?)(?:\s*▓▓▓)?$/gmi, type: 'ATO' },

            // ACT/ATO com números arábicos - aceita : ou -
            { regex: /^(ATO|ACT)\s+(\d+)\s*[-–:]\s*(.+?)(?:\s*▓▓▓)?$/gmi, type: 'ATO' },

            // CHAPTER com palavras ou números - aceita : ou -
            { regex: /^CHAPTER\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|\d+|\w+)\s*[-–:]\s*(.+?)$/gmi, type: 'CHAPTER' },

            // CAPÍTULO com números - aceita : ou -
            { regex: /^CAP[ÍI]TULO\s+(\d+)\s*[-–:]\s*(.+?)$/gmi, type: 'CAPÍTULO' },

            // PART/PARTE com números - aceita : ou -
            { regex: /^PART\s+(\d+)\s*[-–:]\s*(.+?)$/gmi, type: 'PART' },
            { regex: /^PARTE\s+(\d+)\s*[-–:]\s*(.+?)$/gmi, type: 'PARTE' },

            { regex: /^(CONCLUS[ÃA]O|CONCLUSION)\s*[-–:]?\s*(.*)(?:\s*▓▓▓)?$/gmi, type: 'CONCLUSÃO' },
            { regex: /^SCENE\s+\d+\s*[-–:]\s*(.+)$/gmi, type: 'SCENE' },
            { regex: /^CENA\s+\d+\s*[-–:]\s*(.+)$/gmi, type: 'CENA' }
        ];

        const lines = content.split('\n');
        let currentSection = null;
        let sectionContent = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();

            let matched = false;
            for (const pattern of patterns) {
                const match = line.match(new RegExp(pattern.regex.source, 'i'));
                if (match) {
                    // Save previous section
                    if (currentSection) {
                        sections.push({
                            ...currentSection,
                            text: sectionContent.join('\n').trim(),
                            wordCount: this.countWords(sectionContent.join('\n'))
                        });
                    }

                    // Start new section
                    currentSection = {
                        title: line,
                        type: pattern.type,
                        fileName: fileName,
                        lineNumber: i + 1
                    };
                    sectionContent = [];
                    matched = true;
                    break;
                }
            }

            if (!matched && currentSection) {
                sectionContent.push(line);
            }
        }

        // Save last section
        if (currentSection) {
            sections.push({
                ...currentSection,
                text: sectionContent.join('\n').trim(),
                wordCount: this.countWords(sectionContent.join('\n'))
            });
        }

        return sections;
    }

    countWords(text) {
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    }

    // Verifica se o arquivo é de um tipo suportado
    isSupportedFile(filename) {
        const lower = filename.toLowerCase();
        const supportedExtensions = [
            '.txt',   // Texto simples
            '.md',    // Markdown
            '.rtf',   // Rich Text Format
            '.doc',   // Word antigo
            '.docx',  // Word novo
            '.pdf',   // PDF
            '.srt',   // Legendas SubRip
            '.vtt',   // WebVTT
            '.sub',   // Legendas genéricas
            '.fountain', // Formato Fountain para roteiros
            '.fdx',   // Final Draft
            '.celtx', // Celtx
        ];
        return supportedExtensions.some(ext => lower.endsWith(ext));
    }

    parseYoutubeDataFromFile(content) {
        const data = {
            titles: [],
            description: '',
            thumbnail: ''
        };

        try {
            console.log('📄 Parse YouTube - Iniciando...');

            // Extrair títulos (OPÇÃO 1 a 5) - igual ao Python
            for (let i = 1; i <= 5; i++) {
                const padrao = new RegExp(`OPÇÃO\\s+${i}:([\\s\\S]*?)(?=OPÇÃO\\s+${i + 1}:|━|$)`, 'i');
                const match = content.match(padrao);
                if (match) {
                    const titulo = match[1].trim();
                    data.titles[i - 1] = titulo;
                    console.log(`✅ Título ${i}: ${titulo}`);
                }
            }

            // Extrair descrição - igual ao Python
            const descMatch = content.match(/DESCRIÇÃO PARA YOUTUBE:([\s\S]*?)(?=━|IDEIA PARA THUMBNAIL:|$)/i);
            if (descMatch) {
                data.description = descMatch[1].trim();
                console.log('✅ Descrição:', data.description.substring(0, 100) + '...');
            } else {
                console.log('❌ Descrição NÃO encontrada');
            }

            // Extrair thumbnail - igual ao Python
            const thumbnailMatch = content.match(/IDEIA PARA THUMBNAIL:([\s\S]*?)$/i);
            if (thumbnailMatch) {
                data.thumbnail = thumbnailMatch[1].trim();
                console.log('✅ Thumbnail:', data.thumbnail.substring(0, 100) + '...');
            } else {
                console.log('❌ Thumbnail NÃO encontrada');
            }

            console.log('📊 Total de títulos encontrados:', data.titles.filter(t => t).length);
        } catch (err) {
            console.error('❌ Erro ao parsear dados do YouTube:', err);
        }

        return data;
    }

    // ========================================
    // UI RENDERING
    // ========================================

    updateUI() {
        const hasProjects = Object.keys(this.projects).length > 0;

        document.getElementById('emptyState').style.display = hasProjects ? 'none' : 'block';
        document.getElementById('projectSelectorBar').style.display = hasProjects ? 'flex' : 'none';
        document.getElementById('tabsContainer').style.display = hasProjects ? 'block' : 'none';
        document.getElementById('refreshButton').style.display = this.directoryHandle ? 'inline-flex' : 'none';
        document.getElementById('saveButton').style.display = hasProjects ? 'inline-flex' : 'none';

        if (hasProjects && !this.currentProject) {
            const firstProject = Object.keys(this.projects)[0];
            this.selectProject(firstProject);
        }
    }

    renderProjectDropdown() {
        const dropdown = document.getElementById('projectDropdown');
        if (!dropdown) return;

        dropdown.innerHTML = '<option value="">Selecione um roteiro</option>';

        Object.keys(this.projects).sort().forEach(projectName => {
            const option = document.createElement('option');
            option.value = projectName;
            option.textContent = projectName;
            dropdown.appendChild(option);
        });

        if (this.currentProject) {
            dropdown.value = this.currentProject;
        }
    }

    selectProject(projectName) {
        if (!projectName || !this.projects[projectName]) return;

        this.currentProject = projectName;
        this.currentSection = null;
        this.currentFile = null;

        document.getElementById('projectDropdown').value = projectName;
        document.getElementById('folderPathDisplay').textContent = this.projects[projectName].path || projectName;

        // Mostrar botão "Analisar Projeto"
        const analyzeBtn = document.getElementById('analyzeProjectButton');
        if (analyzeBtn) analyzeBtn.style.display = 'inline-flex';

        this.renderSections();
        this.renderFiles();
        this.loadYoutubeDataForProject(projectName);
        this.clearPreview();
        this.clearFilePreview();
        this.showTranslatorPanel();
    }

    showTranslatorPanel() {
        const panel = document.getElementById('aiTranslatorPanel');
        if (!panel || !this.currentProject) return;

        const project = this.projects[this.currentProject];
        if (!project || !project.sections || project.sections.length === 0) {
            panel.style.display = 'none';
            return;
        }

        // Mostrar painel se houver seções
        panel.style.display = 'block';
    }

    renderSections() {
        const container = document.getElementById('sectionsList');
        if (!container || !this.currentProject) return;

        const project = this.projects[this.currentProject];

        if (!project.sections || project.sections.length === 0) {
            container.innerHTML = '<div class="empty-message"><p>Nenhuma seção detectada neste projeto</p></div>';
            return;
        }

        container.innerHTML = '';

        project.sections.forEach((section, index) => {
            const card = document.createElement('div');
            card.className = 'section-card';
            card.dataset.index = index;

            // Check if was copied before
            const copyInfo = this.getCopyInfo(project.name, section.title);
            if (copyInfo && copyInfo.contador > 0) {
                card.classList.add('copied');
            }

            card.innerHTML = `
                <div class="section-title">${section.title}</div>
                <div class="section-meta">
                    <span class="word-count">${section.wordCount} palavras</span>
                    ${copyInfo ? `<span class="copy-count">Copiado ${copyInfo.contador}x</span>` : ''}
                </div>
            `;

            card.addEventListener('click', () => {
                this.selectSection(index);
            });

            container.appendChild(card);
        });
    }

    selectSection(index) {
        if (!this.currentProject) return;

        const project = this.projects[this.currentProject];
        if (!project.sections || !project.sections[index]) return;

        this.currentSection = project.sections[index];

        // Update active state
        document.querySelectorAll('.section-card').forEach((card, i) => {
            card.classList.toggle('active', i === index);
        });

        this.showPreview(this.currentSection);
    }

    showPreview(section) {
        const preview = document.getElementById('textPreview');
        const actions = document.getElementById('previewActions');
        const copyInfo = document.getElementById('copyCountInfo');

        if (!preview || !actions) return;

        preview.innerHTML = section.text;
        actions.style.display = 'flex';

        const copyInfoData = this.getCopyInfo(this.currentProject, section.title);
        if (copyInfoData && copyInfoData.contador > 0) {
            copyInfo.textContent = `Copiado ${copyInfoData.contador}x • Última: ${copyInfoData.ultima_copia}`;
        } else {
            copyInfo.textContent = 'Nunca copiado';
        }
    }

    clearPreview() {
        const preview = document.getElementById('textPreview');
        const actions = document.getElementById('previewActions');

        if (!preview) return;

        preview.innerHTML = `
            <div class="empty-message">
                <svg width="60" height="60" viewBox="0 0 20 20" fill="none" style="opacity: 0.3;">
                    <path d="M1 1L19 19M1 19L19 1" stroke="currentColor" stroke-width="2"/>
                </svg>
                <p>Selecione uma seção ao lado para visualizar</p>
            </div>
        `;

        if (actions) actions.style.display = 'none';
    }

    clearSelection() {
        this.currentSection = null;
        document.querySelectorAll('.section-card').forEach(card => {
            card.classList.remove('active');
        });
        this.clearPreview();
    }

    renderFiles() {
        const container = document.getElementById('filesList');
        if (!container || !this.currentProject) return;

        const project = this.projects[this.currentProject];

        if (!project.files || project.files.length === 0) {
            container.innerHTML = '<div class="empty-message"><p>Nenhum arquivo encontrado</p></div>';
            return;
        }

        container.innerHTML = '';

        // Sort files by name
        const sortedFiles = [...project.files].sort((a, b) => a.name.localeCompare(b.name));

        sortedFiles.forEach((file, index) => {
            const hasMarkers = this.hasMarkers(file.content);

            const item = document.createElement('div');
            item.className = 'file-item';
            item.dataset.index = index;

            const sizeKB = (file.size / 1024).toFixed(2);

            item.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div style="flex: 1; min-width: 0;">
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">${sizeKB} KB</span>
                    </div>
                    ${!hasMarkers ? `
                        <button
                            class="btn-ai-detect"
                            onclick="event.stopPropagation(); app.analyzeFileWithAI(${JSON.stringify(file).replace(/"/g, '&quot;')})"
                            title="Detectar seções com IA"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                                <path d="M2 17l10 5 10-5"/>
                                <path d="M2 12l10 5 10-5"/>
                            </svg>
                        </button>
                    ` : ''}
                </div>
            `;

            item.addEventListener('click', () => {
                this.viewFile(file, index);
            });

            container.appendChild(item);
        });
    }

    viewFile(file, index) {
        const preview = document.getElementById('fileContentPreview');
        const actions = document.getElementById('fileContentActions');
        const fileInfo = document.getElementById('fileInfoDisplay');
        const columnTitle = document.querySelector('.file-content-column .column-title');

        if (!preview || !actions) return;

        // Update active state
        document.querySelectorAll('.file-item').forEach((item, i) => {
            item.classList.toggle('active', i === index);
        });

        // Update title
        if (columnTitle) {
            columnTitle.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
                    <path d="M4 4h12v12H4V4z" stroke="currentColor" stroke-width="2"/>
                    <path d="M7 7h6M7 10h6M7 13h4" stroke="currentColor" stroke-width="2"/>
                </svg>
                ${file.name}
            `;
        }

        // Show content
        preview.textContent = file.content;
        actions.style.display = 'flex';

        // Show file info
        const sizeKB = (file.size / 1024).toFixed(2);
        const wordCount = this.countWords(file.content);
        fileInfo.textContent = `${sizeKB} KB • ${wordCount} palavras`;

        // Store current file for copy
        this.currentFile = file;
    }

    clearFilePreview() {
        const preview = document.getElementById('fileContentPreview');
        const actions = document.getElementById('fileContentActions');
        const columnTitle = document.querySelector('.file-content-column .column-title');

        if (!preview) return;

        preview.innerHTML = `
            <div class="empty-message">
                <svg width="60" height="60" viewBox="0 0 20 20" fill="none" style="opacity: 0.3;">
                    <path d="M4 4h12v12H4V4z" stroke="currentColor" stroke-width="2"/>
                </svg>
                <p>Selecione um arquivo ao lado para visualizar</p>
            </div>
        `;

        if (actions) actions.style.display = 'none';

        if (columnTitle) {
            columnTitle.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
                    <path d="M4 4h12v12H4V4z" stroke="currentColor" stroke-width="2"/>
                    <path d="M7 7h6M7 10h6M7 13h4" stroke="currentColor" stroke-width="2"/>
                </svg>
                Selecione um roteiro e arquivo
            `;
        }

        this.currentFile = null;
    }

    // ========================================
    // TAB SWITCHING
    // ========================================

    switchTab(tabName) {
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}Tab`);
        });
    }

    // ========================================
    // COPY FUNCTIONALITY
    // ========================================

    async copyCurrentSection() {
        if (!this.currentSection || !this.currentProject) return;

        try {
            await navigator.clipboard.writeText(this.currentSection.text);
            this.recordCopy(this.currentProject, this.currentSection.title);
            this.showToast('✅ Texto copiado!', 'success');
            this.renderSections(); // Update green checkmark
            this.showPreview(this.currentSection); // Update copy count
        } catch (err) {
            console.error('Erro ao copiar:', err);
            this.showToast('Erro ao copiar texto', 'error');
        }
    }

    async copyCurrentFile() {
        if (!this.currentFile) return;

        try {
            await navigator.clipboard.writeText(this.currentFile.content);
            this.showToast(`✅ Arquivo "${this.currentFile.name}" copiado!`, 'success');
        } catch (err) {
            console.error('Erro ao copiar arquivo:', err);
            this.showToast('Erro ao copiar arquivo', 'error');
        }
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('✅ Copiado!', 'success');
        } catch (err) {
            console.error('Erro ao copiar:', err);
            this.showToast('Erro ao copiar', 'error');
        }
    }

    saveCurrentSection() {
        if (!this.currentSection) return;

        const blob = new Blob([this.currentSection.text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentSection.title.replace(/[^a-z0-9]/gi, '_')}.txt`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Arquivo salvo!', 'success');
    }

    // ========================================
    // COPY HISTORY
    // ========================================

    loadHistory() {
        const saved = localStorage.getItem('copyHistory');
        return saved ? JSON.parse(saved) : {};
    }

    saveHistory() {
        localStorage.setItem('copyHistory', JSON.stringify(this.copyHistory));
    }

    recordCopy(projectName, sectionTitle) {
        if (!this.copyHistory[projectName]) {
            this.copyHistory[projectName] = {};
        }

        const now = new Date().toLocaleString('pt-BR');

        if (!this.copyHistory[projectName][sectionTitle]) {
            this.copyHistory[projectName][sectionTitle] = {
                primeira_copia: now,
                ultima_copia: now,
                contador: 1
            };
        } else {
            this.copyHistory[projectName][sectionTitle].ultima_copia = now;
            this.copyHistory[projectName][sectionTitle].contador++;
        }

        this.saveHistory();
    }

    getCopyInfo(projectName, sectionTitle) {
        return this.copyHistory[projectName]?.[sectionTitle] || null;
    }

    // ========================================
    // YOUTUBE DATA
    // ========================================

    loadYoutubeData() {
        const saved = localStorage.getItem('youtubeData');
        return saved ? JSON.parse(saved) : {};
    }

    saveYoutubeDataToStorage() {
        localStorage.setItem('youtubeData', JSON.stringify(this.youtubeData));
    }

    loadYoutubeDataForProject(projectName) {
        // SEMPRE limpar e recarregar do arquivo para garantir dados atualizados
        delete this.youtubeData[projectName];
        localStorage.removeItem('youtubeData'); // Limpar cache completamente

        let data = {};

        if (this.projects[projectName]) {
            const youtubeFile = this.projects[projectName].files.find(f =>
                f.name.includes('05_Titulo_Descricao') || f.name.includes('05_Titulo_Descrição')
            );

            if (youtubeFile) {
                console.log('📄 Arquivo YouTube encontrado:', youtubeFile.name);
                const parsedData = this.parseYoutubeDataFromFile(youtubeFile.content);

                // Preencher com dados do arquivo
                data = {
                    posted: data.posted || false,
                    title1: parsedData.titles[0] || '',
                    title2: parsedData.titles[1] || '',
                    title3: parsedData.titles[2] || '',
                    title4: parsedData.titles[3] || '',
                    title5: parsedData.titles[4] || '',
                    description: parsedData.description || '',
                    thumbnail: parsedData.thumbnail || ''
                };

                // Salvar automaticamente para não precisar parsear novamente
                this.youtubeData[projectName] = data;
                this.saveYoutubeDataToStorage();

                this.showToast('✨ Dados do YouTube carregados automaticamente do arquivo!', 'success');
            }
        }

        // Preencher campos no formulário
        document.getElementById('videoPostedCheckbox').checked = data.posted || false;
        document.getElementById('title1').value = data.title1 || '';
        document.getElementById('title2').value = data.title2 || '';
        document.getElementById('title3').value = data.title3 || '';
        document.getElementById('title4').value = data.title4 || '';
        document.getElementById('title5').value = data.title5 || '';
        document.getElementById('description').value = data.description || '';
        document.getElementById('thumbnail').value = data.thumbnail || '';
    }

    saveYoutubeData() {
        if (!this.currentProject) return;

        this.youtubeData[this.currentProject] = {
            posted: document.getElementById('videoPostedCheckbox').checked,
            title1: document.getElementById('title1').value,
            title2: document.getElementById('title2').value,
            title3: document.getElementById('title3').value,
            title4: document.getElementById('title4').value,
            title5: document.getElementById('title5').value,
            description: document.getElementById('description').value,
            thumbnail: document.getElementById('thumbnail').value,
            lastUpdated: new Date().toLocaleString('pt-BR')
        };

        this.saveYoutubeDataToStorage();
        this.showToast('✅ Dados do YouTube salvos!', 'success');
    }

    // ========================================
    // LOCAL STORAGE
    // ========================================

    saveToLocalStorage() {
        try {
            const data = {
                projects: this.projects,
                currentProject: this.currentProject,
                timestamp: Date.now()
            };

            // Save with size check
            const jsonStr = JSON.stringify(data);
            if (jsonStr.length > 5000000) { // 5MB limit
                this.showToast('⚠️ Dados muito grandes. Alguns projetos não foram salvos.', 'error');
                return;
            }

            localStorage.setItem('scriptCopierData', jsonStr);
        } catch (err) {
            console.error('Erro ao salvar:', err);
            this.showToast('Erro ao salvar dados localmente', 'error');
        }
    }

    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('scriptCopierData');
            if (!saved) return;

            const data = JSON.parse(saved);
            this.projects = data.projects || {};
            this.currentProject = data.currentProject || null;

            if (Object.keys(this.projects).length > 0) {
                this.renderProjectDropdown();
                if (this.currentProject && this.projects[this.currentProject]) {
                    this.selectProject(this.currentProject);
                }
            }
        } catch (err) {
            console.error('Erro ao carregar:', err);
        }
    }

    // ========================================
    // PROJECT STATISTICS
    // ========================================

    analyzeCurrentProject() {
        if (!this.currentProject || !this.projects[this.currentProject]) {
            this.showToast('⚠️ Selecione um projeto primeiro', 'error');
            return;
        }

        const project = this.projects[this.currentProject];
        const stats = this.calculateProjectStats(project);
        const comparison = this.compareWithOtherProjects(this.currentProject, stats);

        this.showStatsModal(stats, comparison);
    }

    calculateProjectStats(project) {
        let totalWords = 0;
        let totalChars = 0;
        let oldestDate = Date.now();
        let newestDate = 0;

        project.files.forEach(file => {
            const words = this.countWords(file.content);
            totalWords += words;
            totalChars += file.content.length;

            if (file.lastModified < oldestDate) oldestDate = file.lastModified;
            if (file.lastModified > newestDate) newestDate = file.lastModified;
        });

        // Tempo estimado: 150 palavras por minuto é velocidade média de narração
        const estimatedMinutes = Math.round(totalWords / 150);

        return {
            projectName: project.name,
            fileCount: project.files.length,
            totalWords,
            totalChars,
            estimatedDuration: estimatedMinutes,
            createdDate: new Date(oldestDate),
            lastModified: new Date(newestDate),
            files: project.files.map(f => ({
                name: f.name,
                size: f.size,
                words: this.countWords(f.content)
            }))
        };
    }

    compareWithOtherProjects(currentProjectName, currentStats) {
        const allProjects = Object.values(this.projects).filter(p => p.name !== currentProjectName);

        if (allProjects.length === 0) {
            return null;
        }

        let totalWords = 0;
        let totalFiles = 0;

        allProjects.forEach(p => {
            totalFiles += p.files.length;
            p.files.forEach(f => {
                totalWords += this.countWords(f.content);
            });
        });

        const avgWords = totalWords / allProjects.length;
        const avgFiles = totalFiles / allProjects.length;

        const wordsDiff = ((currentStats.totalWords - avgWords) / avgWords * 100).toFixed(0);
        const filesDiff = ((currentStats.fileCount - avgFiles) / avgFiles * 100).toFixed(0);

        return {
            projectCount: allProjects.length,
            avgWords: Math.round(avgWords),
            avgFiles: Math.round(avgFiles),
            wordsDiff: parseFloat(wordsDiff),
            filesDiff: parseFloat(filesDiff)
        };
    }

    showStatsModal(stats, comparison) {
        const modal = document.getElementById('statsModal');
        const body = document.getElementById('statsModalBody');

        if (!modal || !body) return;

        const html = `
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h1 style="color: var(--accent-primary); font-size: 2rem; margin: 0;">${stats.projectName}</h1>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${stats.fileCount}</div>
                    <div class="stat-label">📄 Arquivos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.totalWords.toLocaleString('pt-BR')}</div>
                    <div class="stat-label">💬 Palavras</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.totalChars.toLocaleString('pt-BR')}</div>
                    <div class="stat-label">🔤 Caracteres</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.estimatedDuration} min</div>
                    <div class="stat-label">⏱️ Tempo estimado</div>
                </div>
            </div>

            <hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border-color);">

            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">📅 Datas</h3>
            <div style="margin-bottom: 1rem;">
                <strong>Criado:</strong> ${stats.createdDate.toLocaleDateString('pt-BR')}<br>
                <strong>Última edição:</strong> ${this.getRelativeTime(stats.lastModified)}
            </div>

            ${comparison ? `
                <hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border-color);">
                <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">📊 Comparação com outros projetos</h3>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    Comparando com ${comparison.projectCount} projeto(s)
                </p>

                <div class="comparison-item">
                    <span class="comparison-icon">${comparison.wordsDiff > 0 ? '▲' : '▼'}</span>
                    <span><strong>${Math.abs(comparison.wordsDiff)}%</strong> ${comparison.wordsDiff > 0 ? 'maior' : 'menor'} que a média (${comparison.avgWords.toLocaleString('pt-BR')} palavras)</span>
                </div>

                <div class="comparison-item">
                    <span class="comparison-icon">${comparison.filesDiff > 0 ? '▲' : '▼'}</span>
                    <span><strong>${Math.abs(comparison.filesDiff)}%</strong> ${comparison.filesDiff > 0 ? 'mais' : 'menos'} arquivos que a média (${comparison.avgFiles} arquivos)</span>
                </div>
            ` : `
                <hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border-color);">
                <p style="text-align: center; color: var(--text-muted);">
                    Adicione mais projetos para ver comparações
                </p>
            `}

            <hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border-color);">

            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">📁 Detalhes dos arquivos</h3>
            <div style="max-height: 200px; overflow-y: auto;">
                ${stats.files.map(f => `
                    <div style="padding: 0.5rem; margin: 0.25rem 0; background: var(--bg-hover); border-radius: var(--radius-sm); display: flex; justify-content: space-between;">
                        <span style="font-weight: 500;">${f.name}</span>
                        <span style="color: var(--text-secondary);">${f.words} palavras • ${(f.size / 1024).toFixed(1)} KB</span>
                    </div>
                `).join('')}
            </div>
        `;

        body.innerHTML = html;
        modal.style.display = 'block';
    }

    getRelativeTime(date) {
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return 'Hoje';
        if (days === 1) return 'Ontem';
        if (days < 7) return `${days} dias atrás`;
        if (days < 30) return `${Math.floor(days / 7)} semanas atrás`;
        if (days < 365) return `${Math.floor(days / 30)} meses atrás`;
        return `${Math.floor(days / 365)} anos atrás`;
    }

    // ========================================
    // AI INTEGRATION (GOOGLE GEMINI)
    // ========================================

    openSettingsModal() {
        const modal = document.getElementById('settingsModal');
        const input = document.getElementById('geminiApiKey');

        if (modal && input) {
            input.value = this.geminiApiKey;
            modal.style.display = 'block';
        }
    }

    saveGeminiApiKey() {
        const input = document.getElementById('geminiApiKey');
        if (!input) return;

        const apiKey = input.value.trim();

        if (!apiKey) {
            this.showToast('⚠️ Digite uma API Key válida', 'error');
            return;
        }

        this.geminiApiKey = apiKey;
        localStorage.setItem('geminiApiKey', apiKey);
        this.showToast('✅ API Key salva com sucesso!', 'success');
    }

    async testGeminiConnection() {
        if (!this.geminiApiKey) {
            this.showToast('⚠️ Configure a API Key primeiro', 'error');
            return;
        }

        this.showToast('🧪 Testando conexão...', 'info');

        try {
            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${this.geminiApiKey}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{
                            parts: [{ text: 'Responda apenas: OK' }]
                        }]
                    })
                }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || 'Erro desconhecido');
            }

            const data = await response.json();
            const responseText = data.candidates?.[0]?.content?.parts?.[0]?.text;

            if (responseText) {
                this.showToast('✅ Conexão bem-sucedida! API Key válida', 'success');
            } else {
                throw new Error('Resposta inesperada da API');
            }
        } catch (error) {
            console.error('Erro ao testar conexão:', error);
            this.showToast(`❌ Erro: ${error.message}`, 'error');
        }
    }

    hasMarkers(content) {
        // Detecta se o arquivo tem marcadores de seção
        const patterns = [
            /\[SEÇÃO \d+\]/i,                    // [SEÇÃO 1], [SEÇÃO 2]
            /\[SECTION \d+\]/i,                  // [SECTION 1], [SECTION 2]
            /^===+$/m,                           // ===
            /^---+$/m,                           // ---
            /^\#{2,3}\s+/m,                      // ## Título ou ### Título
            /^ACT\s+[IVX]+:/im,                  // ACT I:, ACT II:, ACT IX:
            /^ACT\s+\d+:/im,                     // ACT 1:, ACT 2:, ACT 9:
            /^PART\s+\d+:/im,                    // PART 1:, PART 2:
            /^PARTE\s+\d+:/im,                   // PARTE 1:, PARTE 2:
            /^CAP[IÍ]TULO\s+\d+:/im,            // CAPÍTULO 1:, CAPÍTULO 2:
            /^CHAPTER\s+\d+:/im                  // CHAPTER 1:, CHAPTER 2:
        ];

        return patterns.some(pattern => pattern.test(content));
    }

    showAIProgressModal(file) {
        // Criar modal de progresso se não existir
        let modal = document.getElementById('aiProgressModal');

        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'aiProgressModal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 700px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                        <h2 style="margin: 0; color: var(--accent-primary); display: flex; align-items: center; gap: 0.5rem;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                                <path d="M2 17l10 5 10-5"/>
                                <path d="M2 12l10 5 10-5"/>
                            </svg>
                            Análise de IA em Andamento
                        </h2>
                    </div>

                    <div id="aiProgressContent" style="margin-bottom: 1.5rem;">
                        <h3 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">📄 <span id="aiProgressFileName"></span></h3>
                        <div style="background: var(--bg-hover); padding: 1rem; border-radius: var(--radius-sm); max-height: 200px; overflow-y: auto; margin-bottom: 1rem;">
                            <pre id="aiProgressFilePreview" style="margin: 0; font-size: 0.85rem; color: var(--text-secondary); white-space: pre-wrap; font-family: 'Courier New', monospace;"></pre>
                        </div>
                    </div>

                    <div style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span id="aiProgressMessage" style="color: var(--text-secondary); font-weight: 500;">Iniciando...</span>
                            <span id="aiProgressPercentage" style="color: var(--accent-primary); font-weight: 600; font-size: 1.1rem;">0%</span>
                        </div>
                        <div style="background: var(--bg-hover); border-radius: 10px; height: 20px; overflow: hidden;">
                            <div id="aiProgressBar" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; width: 0%; transition: width 0.3s ease; border-radius: 10px;"></div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        // Preencher informações do arquivo
        document.getElementById('aiProgressFileName').textContent = file.name;

        // Mostrar preview do conteúdo (primeiras 1000 caracteres)
        const preview = file.content.length > 1000
            ? file.content.substring(0, 1000) + '\n\n... (arquivo continua)'
            : file.content;
        document.getElementById('aiProgressFilePreview').textContent = preview;

        // Resetar progresso
        document.getElementById('aiProgressBar').style.width = '0%';
        document.getElementById('aiProgressPercentage').textContent = '0%';
        document.getElementById('aiProgressMessage').textContent = 'Iniciando...';

        // Mostrar modal
        modal.style.display = 'block';
    }

    updateAIProgress(message, percentage) {
        const modal = document.getElementById('aiProgressModal');
        if (!modal) return;

        document.getElementById('aiProgressMessage').textContent = message;
        document.getElementById('aiProgressPercentage').textContent = `${percentage}%`;
        document.getElementById('aiProgressBar').style.width = `${percentage}%`;
    }

    closeAIProgressModal() {
        const modal = document.getElementById('aiProgressModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // ========================================
    // AI TRANSLATOR
    // ========================================

    async translateCurrentSection() {
        // Verificar se há seção selecionada
        if (!this.currentSection) {
            this.showToast('⚠️ Selecione uma seção primeiro', 'error');
            return;
        }

        // Verificar API Key
        if (!this.geminiApiKey) {
            this.showToast('⚠️ Configure a API Key do Google Gemini primeiro', 'error');
            document.getElementById('settingsModal').style.display = 'block';
            return;
        }

        // Pegar idioma selecionado
        const languageSelector = document.getElementById('translateLanguageSelector');
        if (!languageSelector || !languageSelector.value) {
            this.showToast('⚠️ Selecione um idioma primeiro', 'error');
            return;
        }

        const languageMap = {
            'english': 'Inglês',
            'portuguese': 'Português (Brasil)',
            'spanish': 'Espanhol',
            'french': 'Francês',
            'italian': 'Italiano',
            'german': 'Alemão'
        };

        const targetLanguage = languageMap[languageSelector.value];

        // Mostrar barra de progresso
        this.showAIProgressModal({
            name: this.currentSection.title,
            content: this.currentSection.text
        });
        this.updateAIProgress('Preparando tradução...', 10);

        const prompt = `
Você é um tradutor especializado em roteiros de documentários bíblicos e textos religiosos.

TAREFA: Traduza o texto abaixo de Português para ${targetLanguage}, mantendo TOTAL FIDELIDADE ao conteúdo original.

INSTRUÇÕES CRÍTICAS:
1. PRESERVAÇÃO TEOLÓGICA:
   - Mantenha EXATAMENTE o significado teológico e doutrinário
   - Preserve todos os nomes bíblicos (Jesus, Jerusalém, Abraão, etc.)
   - Mantenha termos técnicos religiosos com precisão

2. ESTILO NARRATIVO:
   - Mantenha o tom narrativo de documentário
   - Preserve o ritmo e a cadência do texto original
   - Mantenha a força dramática e emocional das passagens

3. FIDELIDADE ESTRUTURAL:
   - Mantenha TODOS os parágrafos e quebras de linha
   - Preserve marcadores de tempo (ex: "0:00-2:30")
   - Mantenha títulos e subtítulos sem alteração de formato

4. QUALIDADE LINGUÍSTICA:
   - Use linguagem culta e fluente em ${targetLanguage}
   - Evite traduções literais que soem não-naturais
   - Adapte expressões idiomáticas mantendo o sentido original

5. RESTRIÇÕES:
   - NÃO adicione explicações, notas ou comentários
   - NÃO omita ou resuma nenhuma parte do texto
   - NÃO altere números, datas ou referências bíblicas
   - Retorne APENAS a tradução, sem prefácio ou conclusão

TEXTO ORIGINAL (Português):
${this.currentSection.text}

TRADUÇÃO FIEL PARA ${targetLanguage.toUpperCase()}:
`;

        try {
            this.updateAIProgress('Enviando para IA...', 30);

            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${this.geminiApiKey}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{
                            parts: [{ text: prompt }]
                        }]
                    })
                }
            );

            this.updateAIProgress('Processando resposta...', 60);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || 'Erro na API');
            }

            const data = await response.json();
            const translatedText = data.candidates?.[0]?.content?.parts?.[0]?.text;

            if (!translatedText) {
                throw new Error('Resposta vazia da IA');
            }

            this.updateAIProgress('Concluído!', 100);

            // Fechar modal de progresso e mostrar resultado
            setTimeout(() => {
                this.closeAIProgressModal();
                this.showTranslationResult(
                    this.currentSection.title,
                    targetLanguage,
                    this.currentSection.text,
                    translatedText
                );
            }, 500);

        } catch (error) {
            console.error('Erro ao traduzir:', error);
            this.closeAIProgressModal();
            this.showToast(`❌ Erro na tradução: ${error.message}`, 'error');
        }
    }

    showTranslationResult(sectionTitle, language, originalText, translatedText) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.id = 'translationModal';

        // Escapar HTML para evitar quebras
        const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };

        modal.innerHTML = `
            <div class="modal-content" style="max-width: 1200px; width: 90%;">
                <div class="modal-header">
                    <h2>🌐 Tradução: ${escapeHtml(sectionTitle)}</h2>
                    <button class="modal-close" id="closeTranslationModal">&times;</button>
                </div>
                <div class="modal-body">
                    <div style="margin-bottom: 1rem;">
                        <p style="color: var(--text-secondary); margin: 0;">
                            <strong>Idioma de destino:</strong> ${escapeHtml(language)}
                        </p>
                    </div>

                    <!-- Comparação lado a lado com SCROLL SINCRONIZADO -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                        <!-- Coluna Original -->
                        <div>
                            <h4 style="color: var(--accent-primary); margin: 0 0 0.75rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid var(--accent-primary);">
                                📝 Original
                            </h4>
                            <div id="originalTextScroll" style="background: var(--bg-hover); padding: 1.5rem; border-radius: var(--radius-sm); max-height: 400px; overflow-y: auto;">
                                <pre id="originalTextContent" style="margin: 0; white-space: pre-wrap; font-family: 'Inter', sans-serif; line-height: 1.6; color: var(--text-primary); font-size: 0.9rem;">${escapeHtml(originalText)}</pre>
                            </div>
                        </div>

                        <!-- Coluna Tradução -->
                        <div>
                            <h4 style="color: #667eea; margin: 0 0 0.75rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #667eea;">
                                🌐 ${escapeHtml(language)}
                            </h4>
                            <div id="translatedTextScroll" style="background: linear-gradient(135deg, #667eea11 0%, #764ba211 100%); padding: 1.5rem; border-radius: var(--radius-sm); max-height: 400px; overflow-y: auto; border: 2px solid #667eea;">
                                <pre id="translatedTextContent" style="margin: 0; white-space: pre-wrap; font-family: 'Inter', sans-serif; line-height: 1.6; color: var(--text-primary); font-size: 0.9rem;">${escapeHtml(translatedText)}</pre>
                            </div>
                        </div>
                    </div>

                    <!-- Navegação entre seções -->
                    <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem; padding: 1rem; background: var(--bg-hover); border-radius: var(--radius-sm);">
                        <button id="translatePrevSection" class="btn-secondary" style="flex: 1;">
                            ⬅️ Seção Anterior
                        </button>
                        <button id="translateNextSection" class="btn-secondary" style="flex: 1;">
                            Próxima Seção ➡️
                        </button>
                    </div>

                    <!-- Botões de ação -->
                    <div style="display: flex; gap: 0.75rem;">
                        <button id="copyTranslationBtn" class="btn-primary" style="flex: 1;">
                            📋 Copiar Tradução
                        </button>
                        <button id="copyBothBtn" class="btn-secondary" style="flex: 1;">
                            📄 Copiar Ambos
                        </button>
                        <button id="closeModalBtn" class="btn-secondary" style="flex: 0 0 auto; padding: 0 1.5rem;">
                            ✕ Fechar
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // ===== SCROLL SINCRONIZADO =====
        const originalScroll = document.getElementById('originalTextScroll');
        const translatedScroll = document.getElementById('translatedTextScroll');
        let isScrolling = false;

        originalScroll.addEventListener('scroll', () => {
            if (isScrolling) return;
            isScrolling = true;

            const scrollPercent = originalScroll.scrollTop / (originalScroll.scrollHeight - originalScroll.clientHeight);
            translatedScroll.scrollTop = scrollPercent * (translatedScroll.scrollHeight - translatedScroll.clientHeight);

            setTimeout(() => { isScrolling = false; }, 50);
        });

        translatedScroll.addEventListener('scroll', () => {
            if (isScrolling) return;
            isScrolling = true;

            const scrollPercent = translatedScroll.scrollTop / (translatedScroll.scrollHeight - translatedScroll.clientHeight);
            originalScroll.scrollTop = scrollPercent * (originalScroll.scrollHeight - originalScroll.clientHeight);

            setTimeout(() => { isScrolling = false; }, 50);
        });

        // ===== EVENT LISTENERS DOS BOTÕES =====

        // Copiar apenas tradução
        document.getElementById('copyTranslationBtn').addEventListener('click', function() {
            const text = document.getElementById('translatedTextContent').textContent;
            navigator.clipboard.writeText(text).then(() => {
                this.textContent = '✅ Copiado!';
                setTimeout(() => { this.textContent = '📋 Copiar Tradução'; }, 2000);
            });
        });

        // Copiar ambos (original + tradução)
        document.getElementById('copyBothBtn').addEventListener('click', function() {
            const original = document.getElementById('originalTextContent').textContent;
            const translated = document.getElementById('translatedTextContent').textContent;
            const full = `ORIGINAL:\n${original}\n\n---\n\nTRADUÇÃO (${language}):\n${translated}`;
            navigator.clipboard.writeText(full).then(() => {
                this.textContent = '✅ Copiado!';
                setTimeout(() => { this.textContent = '📄 Copiar Ambos'; }, 2000);
            });
        });

        // Fechar modal
        const closeModal = () => modal.remove();
        document.getElementById('closeTranslationModal').addEventListener('click', closeModal);
        document.getElementById('closeModalBtn').addEventListener('click', closeModal);

        // Fechar modal ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        // ===== NAVEGAÇÃO ENTRE SEÇÕES =====
        const project = this.projects[this.currentProject];
        const sections = project ? project.sections : [];
        const currentIndex = sections.findIndex(s => s.title === this.currentSection.title);

        document.getElementById('translatePrevSection').addEventListener('click', async () => {
            if (currentIndex > 0) {
                this.currentSection = sections[currentIndex - 1];
                this.selectSection(sections[currentIndex - 1]);
                modal.remove();
                await this.translateCurrentSection();
            } else {
                this.showToast('⚠️ Esta é a primeira seção', 'warning');
            }
        });

        document.getElementById('translateNextSection').addEventListener('click', async () => {
            if (currentIndex < sections.length - 1) {
                this.currentSection = sections[currentIndex + 1];
                this.selectSection(sections[currentIndex + 1]);
                modal.remove();
                await this.translateCurrentSection();
            } else {
                this.showToast('⚠️ Esta é a última seção', 'warning');
            }
        });

        // Desabilitar botões se não houver seção anterior/próxima
        if (currentIndex === 0) {
            document.getElementById('translatePrevSection').disabled = true;
            document.getElementById('translatePrevSection').style.opacity = '0.5';
        }
        if (currentIndex === sections.length - 1) {
            document.getElementById('translateNextSection').disabled = true;
            document.getElementById('translateNextSection').style.opacity = '0.5';
        }

        this.showToast('✅ Tradução concluída!', 'success');
    }

    async translateEntireFile() {
        // Verificar se há arquivo selecionado
        if (!this.currentFileHandle) {
            this.showToast('⚠️ Selecione um arquivo primeiro', 'error');
            return;
        }

        // Verificar API Key
        if (!this.geminiApiKey) {
            this.showToast('⚠️ Configure a API Key do Google Gemini primeiro', 'error');
            document.getElementById('settingsModal').style.display = 'block';
            return;
        }

        // Pegar idioma selecionado
        const languageSelector = document.getElementById('fileTranslateLanguageSelector');
        if (!languageSelector || !languageSelector.value) {
            this.showToast('⚠️ Selecione um idioma primeiro', 'error');
            return;
        }

        const languageMap = {
            'english': 'Inglês',
            'portuguese': 'Português (Brasil)',
            'spanish': 'Espanhol',
            'french': 'Francês',
            'italian': 'Italiano',
            'german': 'Alemão'
        };

        const targetLanguage = languageMap[languageSelector.value];

        // Ler conteúdo do arquivo
        const file = await this.currentFileHandle.getFile();
        const fileContent = await file.text();

        if (!fileContent || fileContent.trim().length === 0) {
            this.showToast('⚠️ O arquivo está vazio', 'error');
            return;
        }

        // Mostrar barra de progresso
        this.showAIProgressModal({
            name: this.currentFileHandle.name,
            content: fileContent.substring(0, 500) + '...'
        });
        this.updateAIProgress('Preparando tradução do arquivo completo...', 10);

        const prompt = `
Você é um tradutor especializado em roteiros de documentários bíblicos e textos religiosos.

TAREFA: Traduza o ARQUIVO COMPLETO abaixo de Português para ${targetLanguage}, mantendo TOTAL FIDELIDADE ao conteúdo original.

INSTRUÇÕES CRÍTICAS:
1. PRESERVAÇÃO TEOLÓGICA:
   - Mantenha EXATAMENTE o significado teológico e doutrinário
   - Preserve todos os nomes bíblicos (Jesus, Jerusalém, Abraão, etc.)
   - Mantenha termos técnicos religiosos com precisão

2. ESTILO NARRATIVO:
   - Mantenha o tom narrativo de documentário
   - Preserve o ritmo e a cadência do texto original
   - Mantenha a força dramática e emocional das passagens

3. FIDELIDADE ESTRUTURAL:
   - Mantenha TODOS os parágrafos e quebras de linha
   - Preserve marcadores de seção (ex: "[SEÇÃO 1]", "[SEÇÃO 2]")
   - Preserve marcadores de tempo (ex: "0:00-2:30")
   - Mantenha títulos e subtítulos sem alteração de formato
   - Preserve TODA a estrutura do documento

4. QUALIDADE LINGUÍSTICA:
   - Use linguagem culta e fluente em ${targetLanguage}
   - Evite traduções literais que soem não-naturais
   - Adapte expressões idiomáticas mantendo o sentido original

5. RESTRIÇÕES:
   - NÃO adicione explicações, notas ou comentários
   - NÃO omita ou resuma nenhuma parte do texto
   - NÃO altere números, datas ou referências bíblicas
   - Retorne APENAS a tradução, sem prefácio ou conclusão
   - TRADUZA TODO O ARQUIVO, do início ao fim

TEXTO ORIGINAL COMPLETO (Português):
${fileContent}

TRADUÇÃO FIEL COMPLETA PARA ${targetLanguage.toUpperCase()}:
`;

        try {
            this.updateAIProgress('Enviando arquivo para IA...', 30);

            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${this.geminiApiKey}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{
                            parts: [{ text: prompt }]
                        }]
                    })
                }
            );

            this.updateAIProgress('Processando resposta...', 60);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || 'Erro na API');
            }

            const data = await response.json();
            const translatedText = data.candidates?.[0]?.content?.parts?.[0]?.text;

            if (!translatedText) {
                throw new Error('Resposta vazia da IA');
            }

            this.updateAIProgress('Concluído!', 100);

            // Fechar modal de progresso e mostrar resultado
            setTimeout(() => {
                this.closeAIProgressModal();
                this.showTranslationResult(
                    this.currentFileHandle.name,
                    targetLanguage,
                    fileContent,
                    translatedText
                );
            }, 500);

        } catch (error) {
            console.error('Erro ao traduzir arquivo:', error);
            this.closeAIProgressModal();
            this.showToast(`❌ Erro na tradução: ${error.message}`, 'error');
        }
    }

    // ========================================
    // TOAST NOTIFICATIONS
    // ========================================

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        if (!toast) return;

        toast.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// ========================================
// Initialize App
// ========================================

let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ScriptCopierApp();
});
