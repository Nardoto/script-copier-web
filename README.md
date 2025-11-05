# Script Copier Web 📝

**Aplicação web para gerenciamento de roteiros de documentários**
Portado de ScriptCopier_UNIVERSAL.py para HTML/CSS/JavaScript

[![Deploy](https://img.shields.io/badge/deploy-GitHub%20Pages-success)](https://pages.github.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Sobre o Projeto

Script Copier Web é uma aplicação moderna para gerenciar roteiros de documentários bíblicos. Permite fazer upload de arquivos `.txt`, detectar automaticamente seções (OPENING, ACT, CHAPTER, CONCLUSION), copiar seções para o clipboard e rastrear histórico de cópias.

### ✨ Funcionalidades

- ✅ **Upload de múltiplos arquivos** - Drag & drop de arquivos .txt
- ✅ **Detecção automática de seções** - Parser inteligente com regex
- ✅ **Copiar para clipboard** - Um clique para copiar seções
- ✅ **Histórico de cópias** - Rastreamento com timestamps e contadores
- ✅ **3 Abas organizadas** - Copiar Seções, Visualizar Arquivos, YouTube
- ✅ **Tema Claude Loopless** - Design moderno e responsivo
- ✅ **Armazenamento local** - localStorage para persistência
- ✅ **100% client-side** - Sem necessidade de backend

---

## 📁 Estrutura do Projeto

```
web-app/
├── index.html              # Aplicação principal
├── styles.css              # Tema Claude Loopless
├── app.js                  # Lógica da aplicação
├── exemplo-roteiro.txt     # Arquivo de exemplo para teste
├── .gitignore
├── README.md               # Este arquivo
│
├── source-python/          # Código Python original (referência)
│   ├── ScriptCopier_UNIVERSAL.py
│   ├── ScriptCopier_NEW.py
│   ├── ScriptCopier.py
│   ├── historico_copias.json
│   └── requirements.txt
│
└── docs/                   # Documentação
    ├── CHANGELOG_UNIVERSAL.txt
    └── README_DESENVOLVIMENTO.txt
```

---

## 🚀 Como Usar Localmente

### 1. Clonar ou baixar os arquivos

```bash
# Baixe os arquivos: index.html, styles.css, app.js
```

### 2. Abrir no navegador

```bash
# Abra index.html direto no navegador
# OU use um servidor local:

# Python 3
python -m http.server 8000

# Node.js (npx)
npx http-server

# Acesse: http://localhost:8000
```

### 3. Usar a aplicação

1. Clique em "Carregar Roteiros"
2. Selecione arquivos `.txt` com roteiros
3. As seções serão detectadas automaticamente
4. Clique em uma seção para visualizar/copiar

---

## 🌐 Deploy no GitHub Pages

### Método 1: Interface Web (Mais Fácil)

1. **Criar repositório no GitHub:**
   - Acesse https://github.com/new
   - Nome: `script-copier-web`
   - Visibilidade: **Público** ✅
   - Clique em "Create repository"

2. **Fazer upload dos arquivos:**
   - Clique em "uploading an existing file"
   - Arraste: `index.html`, `styles.css`, `app.js`, `README.md`
   - Commit: "Initial commit"

3. **Ativar GitHub Pages:**
   - Vá em **Settings** > **Pages**
   - Source: **Deploy from a branch**
   - Branch: **main** / root
   - Clique em **Save**

4. **Acessar seu site:**
   - URL: `https://[seu-usuario].github.io/script-copier-web/`
   - Aguarde 1-2 minutos para o deploy

### Método 2: Git CLI (Via Terminal)

```bash
# 1. Navegar até a pasta web-app
cd "C:\Users\tharc\Videos\documentario biblicos\GERADOR DE ROTEIROS\APP_DESENVOLVIMENTO\web-app"

# 2. Inicializar repositório Git
git init
git add .
git commit -m "Initial commit - Script Copier Web v1.0"

# 3. Conectar com GitHub
git remote add origin https://github.com/[seu-usuario]/script-copier-web.git

# 4. Fazer push
git branch -M main
git push -u origin main

# 5. Ativar GitHub Pages no site (mesmo passo 3 do Método 1)
```

---

## 🔧 Configurar Domínio Personalizado

### Adicionar subdomínio `roteiros.nardoto.com.br`

1. **No GitHub:**
   - Settings > Pages > Custom domain
   - Digite: `roteiros.nardoto.com.br`
   - Clique em **Save**

2. **No seu provedor de domínio:**
   - Adicione um registro **CNAME**:
     ```
     Nome: roteiros
     Tipo: CNAME
     Valor: [seu-usuario].github.io
     TTL: 3600
     ```

3. **Criar arquivo CNAME no repositório:**
   ```bash
   echo "roteiros.nardoto.com.br" > CNAME
   git add CNAME
   git commit -m "Add custom domain"
   git push
   ```

4. **Aguardar propagação DNS** (pode levar até 24h)

5. **Ativar HTTPS no GitHub Pages** (automático após DNS propagar)

---

## 🎨 Tecnologias Utilizadas

| Tecnologia | Uso |
|------------|-----|
| **HTML5** | Estrutura da aplicação |
| **CSS3** | Estilização (tema Claude Loopless) |
| **JavaScript ES6+** | Lógica e interatividade |
| **Clipboard API** | Copiar texto para área de transferência |
| **localStorage** | Persistência de dados local |
| **GitHub Pages** | Hospedagem gratuita |

### Cores do Tema Claude Loopless

```css
--bg-primary: #faf9f5;      /* Fundo principal */
--accent-primary: #cb6246;   /* Laranja/terracota */
--accent-secondary: #a8d5ba; /* Verde suave */
```

---

## 📚 Parser de Seções

O parser detecta automaticamente os seguintes formatos:

```javascript
// Tipos de seção suportados:
✓ HOOK (description)
✓ ATO I - Título
✓ ACT III - Título
✓ CONCLUSÃO - Título
✓ CHAPTER ONE - Título
✓ SCENE 1 - Título
✓ OPENING - Título
✓ CENA 2 - Título
✓ # Markdown headers
```

**Exemplo de arquivo de roteiro:**

```txt
OPENING - O Início

Texto da abertura aqui...

ATO I - A Jornada Começa

Conteúdo do ato 1...

CHAPTER ONE - Primeiro Capítulo

Texto do capítulo...

CONCLUSÃO

Conclusão do roteiro...
```

---

## 💾 Armazenamento de Dados

### localStorage (Atual)

- Projetos salvos automaticamente
- Histórico de cópias persistente
- Sem necessidade de login

### Firebase (Futuro - Opcional)

Para implementar sync entre dispositivos:

1. Criar projeto no Firebase
2. Adicionar Firebase SDK ao HTML
3. Configurar Firestore
4. Substituir localStorage por Firebase

---

## 🐛 Solução de Problemas

### Clipboard não funciona

**Problema:** `navigator.clipboard` requer HTTPS
**Solução:**
- GitHub Pages usa HTTPS automaticamente ✅
- Localhost funciona sem HTTPS
- Se necessário, use `http-server` com flag SSL

### Arquivos não carregam

**Problema:** Seções não detectadas
**Solução:**
- Verificar encoding UTF-8 nos arquivos .txt
- Conferir se títulos seguem padrões suportados
- Ver console do navegador (F12) para erros

### Site não atualiza após push

**Problema:** Deploy demora no GitHub Pages
**Solução:**
- Aguardar 1-5 minutos
- Forçar refresh: `Ctrl + Shift + R`
- Verificar status em Settings > Pages

---

## 📝 Roadmap

- [x] Aplicação web funcional
- [x] Parser de seções
- [x] Sistema de cópias
- [x] Tema Claude Loopless
- [x] Histórico persistente
- [ ] PWA (Progressive Web App)
- [ ] Exportar histórico JSON
- [ ] Integração Firebase
- [ ] Modo escuro
- [ ] Atalhos de teclado

---

## 📄 Licença

MIT License - Livre para uso pessoal e comercial

---

## 👨‍💻 Autor

**Tharcisio Nardoto**
Engenheiro Civil → Creator de Automações
🌐 [nardoto.com.br](https://nardoto.com.br)

---

## 🎯 Status do Projeto

- [x] Faxina da pasta original (27 MB → 519 KB)
- [x] Organização dos arquivos essenciais
- [x] Criação da aplicação web
- [ ] Deploy no GitHub Pages (aguardando push)
- [ ] Configuração do domínio personalizado

---

**🚀 Pronto para deploy! Siga as instruções acima para colocar no ar.**
