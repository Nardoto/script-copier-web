# 🚀 INSTRUÇÕES DE DEPLOY - GitHub Pages

**Script Copier Web está pronto para ir ao ar!**

Git já está inicializado e primeiro commit feito ✅

---

## 📋 PASSO A PASSO COMPLETO

### **Passo 1: Criar Repositório no GitHub (2 minutos)**

1. Acesse: https://github.com/new

2. Preencha:
   - **Repository name:** `script-copier-web`
   - **Description:** "Gerenciador web de roteiros para documentários - Script Copier Universal"
   - **Visibilidade:** 🔓 **PUBLIC** (obrigatório para GitHub Pages gratuito)
   - ❌ **NÃO** marque "Initialize with README" (já temos commit local)

3. Clique em **"Create repository"**

4. **Copie** a URL do repositório que aparece (ex: `https://github.com/Nardoto/script-copier-web.git`)

---

### **Passo 2: Fazer Push do Código (1 minuto)**

Abra o terminal e execute **OS 3 COMANDOS** abaixo:

```bash
# 1. Navegar até a pasta do projeto
cd "C:\Users\tharc\Videos\documentario biblicos\GERADOR DE ROTEIROS\APP_DESENVOLVIMENTO\web-app"

# 2. Conectar com seu repositório GitHub (SUBSTITUIR pela SUA URL)
git remote add origin https://github.com/Nardoto/script-copier-web.git

# 3. Fazer push
git branch -M main
git push -u origin main
```

⚠️ **IMPORTANTE:** Substituir `Nardoto` pelo seu username do GitHub na URL!

**Se pedir autenticação:**
- Username: seu username do GitHub
- Password: **Personal Access Token** (não a senha normal)

**Não tem token?**
1. Vá em https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Marque: `repo` (full control)
4. Copie o token (só aparece 1 vez!)

---

### **Passo 3: Ativar GitHub Pages (1 minuto)**

1. No seu repositório, clique em **"Settings"** (engrenagem)

2. No menu lateral esquerdo, clique em **"Pages"**

3. Em **"Source"**:
   - Branch: Selecione **`main`**
   - Folder: Deixe **`/ (root)`**

4. Clique em **"Save"**

5. **Aguarde 1-2 minutos** - GitHub vai fazer o deploy

6. **Refresh a página** - vai aparecer:
   ```
   ✅ Your site is live at https://[seu-usuario].github.io/script-copier-web/
   ```

---

### **Passo 4: Testar a Aplicação (2 minutos)**

1. Abra a URL do seu site

2. Teste:
   - ✅ Clique em "Carregar Roteiros"
   - ✅ Faça upload do arquivo `exemplo-roteiro.txt` (está na pasta)
   - ✅ Veja as seções detectadas
   - ✅ Clique em uma seção e copie o texto
   - ✅ Verifique o histórico de cópias

**Deu erro?**
- Abra o Console do navegador (F12)
- Veja se há erros em vermelho
- Verifique se a URL está correta

---

### **Passo 5: Configurar Domínio Personalizado (Opcional - 10 minutos)**

Se quiser usar `roteiros.nardoto.com.br`:

#### 5.1. No GitHub:

1. Settings > Pages > Custom domain
2. Digite: `roteiros.nardoto.com.br`
3. Clique em **"Save"**

#### 5.2. No seu provedor de domínio (ex: Registro.br, GoDaddy):

Adicione um registro DNS:

```
Tipo: CNAME
Nome: roteiros
Valor: [seu-usuario].github.io
TTL: 3600
```

#### 5.3. Criar arquivo CNAME no repositório:

```bash
cd "C:\Users\tharc\Videos\documentario biblicos\GERADOR DE ROTEIROS\APP_DESENVOLVIMENTO\web-app"

echo "roteiros.nardoto.com.br" > CNAME

git add CNAME
git commit -m "Add custom domain: roteiros.nardoto.com.br"
git push
```

#### 5.4. Aguardar propagação DNS (até 24h)

- Geralmente leva 10-30 minutos
- Testar em: https://dnschecker.org/

#### 5.5. Ativar HTTPS (automático)

- GitHub Pages ativa automaticamente
- Marque "Enforce HTTPS" em Settings > Pages

---

## 🔧 COMANDOS ÚTEIS PARA FUTURO

### Atualizar o site depois de fazer mudanças:

```bash
cd "C:\Users\tharc\Videos\documentario biblicos\GERADOR DE ROTEIROS\APP_DESENVOLVIMENTO\web-app"

git add .
git commit -m "Descrição da mudança"
git push
```

### Ver status dos arquivos:

```bash
git status
```

### Ver histórico de commits:

```bash
git log --oneline
```

---

## ❓ SOLUÇÃO DE PROBLEMAS

### Erro: "Permission denied"

**Causa:** Sem autenticação
**Solução:** Criar Personal Access Token (instruções no Passo 2)

### Erro: "Remote origin already exists"

**Causa:** Já configurou remote antes
**Solução:**
```bash
git remote remove origin
git remote add origin https://github.com/[seu-usuario]/script-copier-web.git
```

### Site não atualiza após push

**Causa:** Deploy demora alguns minutos
**Solução:**
1. Aguardar 2-5 minutos
2. Limpar cache: `Ctrl + Shift + R`
3. Verificar Actions: https://github.com/[seu-usuario]/script-copier-web/actions

### Clipboard não funciona

**Causa:** Precisa de HTTPS
**Solução:** GitHub Pages usa HTTPS automaticamente - aguardar deploy completo

---

## 📊 CHECKLIST FINAL

Antes de considerar concluído, verificar:

- [ ] Repositório criado no GitHub
- [ ] Push feito com sucesso
- [ ] GitHub Pages ativado
- [ ] Site abrindo no navegador
- [ ] Upload de arquivos funciona
- [ ] Seções sendo detectadas
- [ ] Botão copiar funcionando
- [ ] Histórico salvando no localStorage
- [ ] 3 abas navegáveis
- [ ] Responsivo no mobile (opcional: testar)

---

## 🎉 PRONTO!

Seu Script Copier Web está no ar! 🚀

**Próximos passos opcionais:**

1. Compartilhar com amigos/equipe
2. Configurar domínio personalizado
3. Adicionar mais features (ver README.md > Roadmap)
4. Integrar com Firebase (sync entre dispositivos)
5. Transformar em PWA (funciona offline)

---

**URL final:** `https://[seu-usuario].github.io/script-copier-web/`

**Substituir [seu-usuario]** pelo seu username do GitHub!

---

📝 Dúvidas? Veja o README.md completo na pasta
🐛 Bugs? Abra uma Issue no GitHub
🎨 Criado com Claude Code - https://claude.com/claude-code
