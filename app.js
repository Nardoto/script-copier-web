// ========================================
// SCRIPT COPIER WEB - Desktop Layout
// Portado de ScriptCopier_UNIVERSAL.py
// Version: 2.7.0 - Integração com IA (Google Gemini) - Modo Híbrido
// ========================================

class ScriptCopierApp {
    constructor() {
        console.log('🚀 Script Copier v2.7.0 - Integração com IA (Google Gemini) - Modo Híbrido');

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
            this.addNewRootFolder();
        });

        document.getElementById('removeRootFolderButton')?.addEventListener('click', () => {
            this.removeCurrentRootFolder();
        });

        document.getElementById('uploadButton').addEventListener('click', () => {
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
        if (!('showDirectoryPicker' in window)) {
            this.showToast('⚠️ Navegador não suporta acesso direto. Use upload de pasta.', 'error');
            document.getElementById('fileInput').click();
            return;
        }

        try {
            const dirHandle = await window.showDirectoryPicker({
                mode: 'read',
                startIn: 'documents'
            });

            // Adicionar como nova pasta raiz
            await this.addRootFolderFromHandle(dirHandle);
        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('Erro ao selecionar pasta:', err);
                this.showToast('Erro ao acessar pasta', 'error');
            }
        }
    }

    // Adiciona nova pasta raiz (para botão "+Nova Pasta")
    async addNewRootFolder() {
        await this.selectDirectory();
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
        dropdown.innerHTML = '<option value="">Selecione pasta raiz</option>';
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
            const allKeys = await store.getAllKeys();

            this.rootFolders = [];

            for (const key of allKeys) {
                const data = await store.get(key);
                if (data && data.handle) {
                    this.rootFolders.push({
                        id: data.id,
                        name: data.name,
                        handle: data.handle,
                        projects: {}
                    });
                }
            }

            await tx.done;
            console.log(`✅ ${this.rootFolders.length} pasta(s) raiz carregadas`);
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
            { regex: /^OPENING\s*[-–]?\s*(.*)$/gmi, type: 'OPENING' },
            { regex: /^HOOK\s*\((.+?)\).*$/gmi, type: 'HOOK' },
            { regex: /^(ATO|ACT)\s+([IVXLCDM]+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)\s*[-–]\s*(.+?)(?:\s*▓▓▓)?$/gmi, type: 'ATO' },
            { regex: /^CHAPTER\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|\w+)\s*[-–]\s*(.+?)$/gmi, type: 'CHAPTER' },
            { regex: /^(CONCLUS[ÃA]O|CONCLUSION)\s*[-–]?\s*(.*)(?:\s*▓▓▓)?$/gmi, type: 'CONCLUSÃO' },
            { regex: /^SCENE\s+\d+\s*[-–]\s*(.+)$/gmi, type: 'SCENE' },
            { regex: /^CENA\s+\d+\s*[-–]\s*(.+)$/gmi, type: 'CENA' }
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
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${this.geminiApiKey}`,
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
            /\[SEÇÃO \d+\]/i,
            /\[SECTION \d+\]/i,
            /^===+$/m,
            /^---+$/m,
            /^\#{2,3}\s+/m  // ## Título ou ### Título
        ];

        return patterns.some(pattern => pattern.test(content));
    }

    async analyzeFileWithAI(file) {
        if (!this.geminiApiKey) {
            this.showToast('⚠️ Configure a API Key do Google Gemini primeiro', 'error');
            document.getElementById('settingsModal').style.display = 'block';
            return;
        }

        this.showToast('🤖 Analisando arquivo com IA...', 'info');

        const prompt = `
Analise este roteiro de documentário bíblico e identifique as seções principais.

Retorne APENAS um JSON válido no formato:
{
  "sections": [
    {
      "title": "Título da seção",
      "startLine": 0,
      "endLine": 50,
      "summary": "Breve resumo do conteúdo"
    }
  ],
  "metadata": {
    "mainTopic": "Tema principal",
    "suggestedTitle": "Título sugerido para o vídeo"
  }
}

Regras:
- Identifique mudanças de tema, introdução/desenvolvimento/conclusão
- startLine e endLine são números de linha (começando do 0)
- Máximo de 5 seções
- Seja conciso nos resumos

ARQUIVO "${file.name}":
${file.content}
`;

        try {
            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${this.geminiApiKey}`,
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

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || 'Erro na API');
            }

            const data = await response.json();
            const responseText = data.candidates?.[0]?.content?.parts?.[0]?.text;

            if (!responseText) {
                throw new Error('Resposta vazia da IA');
            }

            // Extrair JSON da resposta (pode vir com markdown)
            const jsonMatch = responseText.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('IA não retornou JSON válido');
            }

            const analysis = JSON.parse(jsonMatch[0]);
            this.showAISuggestions(file, analysis);

        } catch (error) {
            console.error('Erro ao analisar com IA:', error);
            this.showToast(`❌ Erro na análise: ${error.message}`, 'error');
        }
    }

    showAISuggestions(file, analysis) {
        const modal = document.getElementById('aiSuggestionsModal');
        const body = document.getElementById('aiSuggestionsBody');

        if (!modal || !body) return;

        const html = `
            <div style="margin-bottom: 1.5rem;">
                <h3 style="color: var(--accent-primary); margin: 0;">📄 ${file.name}</h3>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">
                    <strong>Tema:</strong> ${analysis.metadata?.mainTopic || 'Não identificado'}
                </p>
                ${analysis.metadata?.suggestedTitle ? `
                    <p style="color: var(--text-secondary); margin-top: 0.5rem;">
                        <strong>Título sugerido:</strong> ${analysis.metadata.suggestedTitle}
                    </p>
                ` : ''}
            </div>

            <h3 style="color: var(--accent-primary);">🎯 Seções detectadas (${analysis.sections.length})</h3>

            <div style="max-height: 400px; overflow-y: auto;">
                ${analysis.sections.map((section, index) => `
                    <div style="background: var(--bg-hover); padding: 1rem; margin: 0.75rem 0; border-radius: var(--radius-sm); border-left: 4px solid var(--accent-primary);">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <h4 style="margin: 0; color: var(--text-primary);">
                                ${index + 1}. ${section.title}
                            </h4>
                            <span style="font-size: 0.85rem; color: var(--text-muted);">
                                Linhas ${section.startLine}-${section.endLine}
                            </span>
                        </div>
                        <p style="margin: 0; font-size: 0.9rem; color: var(--text-secondary);">
                            ${section.summary}
                        </p>
                    </div>
                `).join('')}
            </div>

            <div style="margin-top: 2rem; padding-top: 1rem; border-top: 2px solid var(--border-color);">
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">
                    A IA identificou ${analysis.sections.length} seção(ões) neste arquivo. Deseja aplicar estas divisões?
                </p>
                <div style="display: flex; gap: 0.75rem;">
                    <button id="applyAISuggestionsButton" class="btn-primary" style="flex: 1;">
                        ✅ Aplicar Sugestões
                    </button>
                    <button onclick="document.getElementById('aiSuggestionsModal').style.display='none'" class="btn-secondary" style="flex: 1;">
                        ❌ Cancelar
                    </button>
                </div>
            </div>
        `;

        body.innerHTML = html;
        modal.style.display = 'block';

        // Event listener para aplicar sugestões
        document.getElementById('applyAISuggestionsButton')?.addEventListener('click', () => {
            this.applyAISuggestions(file, analysis);
            modal.style.display = 'none';
        });
    }

    applyAISuggestions(file, analysis) {
        // Criar marcadores no conteúdo do arquivo baseado nas sugestões
        const lines = file.content.split('\n');
        const newLines = [];

        analysis.sections.forEach((section, index) => {
            // Adicionar marcador de seção
            if (index === 0 && section.startLine > 0) {
                // Adicionar conteúdo antes da primeira seção
                newLines.push(...lines.slice(0, section.startLine));
            }

            newLines.push(`[SEÇÃO ${index + 1}] ${section.title}`);
            newLines.push(''); // Linha em branco

            // Adicionar conteúdo da seção
            const sectionContent = lines.slice(section.startLine, section.endLine + 1);
            newLines.push(...sectionContent);
            newLines.push(''); // Linha em branco entre seções
        });

        // Atualizar conteúdo do arquivo
        file.content = newLines.join('\n');

        // Re-parsear as seções
        const project = this.projects[this.currentProject];
        if (project) {
            project.sections = this.parseAllSections(project);
            this.saveToLocalStorage();
            this.renderSections();
            this.showToast(`✅ ${analysis.sections.length} seção(ões) aplicadas com sucesso!`, 'success');
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
