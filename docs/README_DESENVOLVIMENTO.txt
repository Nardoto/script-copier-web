╔═══════════════════════════════════════════════════════════════════════════╗
║              SCRIPT COPIER UNIVERSAL - ARQUIVOS DE DESENVOLVIMENTO        ║
║                                                                           ║
║                   Desenvolvido por: Tharc (Nardoto)                      ║
║                            Ano: 2025                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝


📁 CONTEÚDO DESTA PASTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Esta pasta contém TODOS os arquivos necessários para desenvolver, modificar
e compilar o Script Copier Universal.


📂 ESTRUTURA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dist/
   📦 EXECUTÁVEL PRONTO PARA DISTRIBUIR
   • ScriptCopier_Universal_v2.0.exe  ← Use este!
   • README.txt                        ← Instruções para usuários finais

build/
   🔧 Arquivos temporários de compilação do PyInstaller
   (pode ser deletado com segurança, será recriado ao compilar)

.claude/
   ⚙️  Configurações do Claude Code (se usado)


🐍 CÓDIGO FONTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ScriptCopier_UNIVERSAL.py
   ⭐ ARQUIVO PRINCIPAL DO APLICATIVO
   • Código completo e comentado
   • Versão 2.0 com todas as funcionalidades
   • Edite este arquivo para fazer modificações

ScriptCopier_NEW.py
   📝 Versão alternativa/backup

ScriptCopier.py
   📝 Versão original antiga


🔨 COMPILAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ScriptCopier.spec
   ⚙️  Arquivo de configuração do PyInstaller
   • Define como o executável será compilado
   • Inclui ícone e configurações

REBUILD_UNIVERSAL.bat
   🔄 Script para recompilar o executável rapidamente

EXECUTAR_APP.bat
   ▶️  Executa o app sem compilar (modo desenvolvimento)


📦 ARQUIVOS DE DEPENDÊNCIAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

requirements.txt
   📋 Lista de bibliotecas Python necessárias

1_instalar_dependencias.bat
   📥 Instala as dependências automaticamente


🎨 RECURSOS VISUAIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

script_copier_icon.ico
   🎯 Ícone principal do aplicativo

script_copier_icon.png
   🖼️  Versão PNG do ícone

launcher_icon.ico
   🚀 Ícone alternativo


📚 DOCUMENTAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

README_EXECUTAVEL.txt
   📖 Instruções sobre o executável

CHANGELOG_UNIVERSAL.txt
   📝 Histórico de mudanças e versões

LEIA-ME.txt, LEIA_ISSO_PRIMEIRO.txt
   📋 Documentação adicional


🛠️ COMO MODIFICAR E RECOMPILAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EDITAR O CÓDIGO:
   • Abra: ScriptCopier_UNIVERSAL.py
   • Faça suas modificações
   • Salve o arquivo

2. TESTAR AS MUDANÇAS (sem compilar):
   • Execute: EXECUTAR_APP.bat
   • Ou: python ScriptCopier_UNIVERSAL.py

3. RECOMPILAR O EXECUTÁVEL:
   Método 1 - Usar o script:
   • Execute: REBUILD_UNIVERSAL.bat

   Método 2 - Linha de comando:
   • pyinstaller --clean ScriptCopier.spec

   O novo executável será criado em: dist/

4. TESTAR O EXECUTÁVEL:
   • Vá para: dist/
   • Execute: ScriptCopier_Universal_v2.0.exe


💡 DICAS IMPORTANTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ SEMPRE teste o código antes de recompilar
✓ Mantenha backup do ScriptCopier_UNIVERSAL.py
✓ A pasta build/ pode ser deletada com segurança
✓ O arquivo .spec define todas as configurações de compilação
✓ Se mudar o ícone, atualize no arquivo .spec


🔧 DEPENDÊNCIAS DO PROJETO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Python 3.14+
• tkinter (interface gráfica)
• pyperclip (copiar para clipboard)
• PyInstaller (gerar executável)


📞 SUPORTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GitHub: github.com/nardoto


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

© 2025 Tharc (Nardoto). Todos os direitos reservados.

Esta pasta é seu BACKUP completo do desenvolvimento!
Mantenha-a segura para futuras modificações.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
