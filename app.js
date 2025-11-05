// ========================================
// SCRIPT COPIER WEB - Desktop Layout
// Portado de ScriptCopier_UNIVERSAL.py
// ========================================

class ScriptCopierApp {
    constructor() {
        this.projects = {};
        this.currentProject = null;
        this.currentSection = null;
        this.currentFile = null;
        this.copyHistory = this.loadHistory();
        this.youtubeData = this.loadYoutubeData();
        this.directoryHandle = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFromLocalStorage();
        this.updateUI();
        this.checkSavedDirectory();
    }

    // ========================================
    // EVENT LISTENERS
    // ========================================

    setupEventListeners() {
        // Header buttons
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

            this.directoryHandle = dirHandle;
            await this.saveDirectoryHandle(dirHandle);
            this.showToast(`📁 Pasta "${dirHandle.name}" selecionada!`, 'success');
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

    async readDirectoryFiles(dirHandle) {
        this.showToast('Lendo arquivos da pasta...', 'info');
        const projectMap = {};

        for await (const entry of dirHandle.values()) {
            if (entry.kind === 'directory') {
                const projectName = entry.name;
                const files = [];

                for await (const fileEntry of entry.values()) {
                    if (fileEntry.kind === 'file' && fileEntry.name.endsWith('.txt')) {
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

    parseYoutubeDataFromFile(content) {
        const data = {
            titles: [],
            description: '',
            thumbnail: ''
        };

        try {
            // Debug: Log para verificar o conteúdo
            console.log('Parseando conteúdo do YouTube:', content.substring(0, 500));

            // Extrair títulos (OPÇÃO 1 a 5) - agora corrigido para o formato real
            // Buscar por OPÇÃO X: seguido de quebra de linha e o texto até a próxima linha vazia
            const titleRegex = /OPÇÃO\s+(\d+):\s*\n(.*?)(?:\n\n|\n━|$)/g;
            let match;
            let titleCount = 0;

            while ((match = titleRegex.exec(content)) !== null) {
                const optionNum = parseInt(match[1]);
                const title = match[2].trim();
                console.log(`Título encontrado - OPÇÃO ${optionNum}: ${title}`);
                data.titles[optionNum - 1] = title;
                titleCount++;
            }

            console.log(`Total de títulos encontrados: ${titleCount}`);
            console.log('Array de títulos:', data.titles);

            // Extrair descrição
            const descMatch = content.match(/DESCRIÇÃO PARA YOUTUBE:\s*\n\n([\s\S]+?)(?=\n━|$)/);
            if (descMatch) {
                data.description = descMatch[1].trim();
                console.log('Descrição encontrada:', data.description.substring(0, 100) + '...');
            }

            // Extrair ideias para thumbnail
            const thumbnailMatch = content.match(/IDEIA PARA THUMBNAIL:\s*\n\n([\s\S]+?)$/);
            if (thumbnailMatch) {
                data.thumbnail = thumbnailMatch[1].trim();
                console.log('Thumbnail encontrada:', data.thumbnail.substring(0, 100) + '...');
            }
        } catch (err) {
            console.error('Erro ao parsear dados do YouTube:', err);
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
            const item = document.createElement('div');
            item.className = 'file-item';
            item.dataset.index = index;

            const sizeKB = (file.size / 1024).toFixed(2);

            item.innerHTML = `
                <span class="file-name">${file.name}</span>
                <span class="file-size">${sizeKB} KB</span>
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
        let data = this.youtubeData[projectName] || {};

        // SEMPRE tentar carregar do arquivo 05_Titulo_Descricao.txt para garantir dados atualizados
        if (this.projects[projectName]) {
            const youtubeFile = this.projects[projectName].files.find(f =>
                f.name.includes('05_Titulo_Descricao') || f.name.includes('05_Titulo_Descrição')
            );

            if (youtubeFile) {
                // Limpar dados antigos para forçar reparse
                delete this.youtubeData[projectName];

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
