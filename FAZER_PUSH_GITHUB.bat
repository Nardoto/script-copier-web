@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   SCRIPT COPIER WEB - PUSH PARA GITHUB
echo ========================================
echo.
echo [1/3] Configurando remote do GitHub...
git remote add origin https://github.com/Nardoto/script-copier-web.git 2>nul

echo.
echo [2/3] Renomeando branch para 'main'...
git branch -M main

echo.
echo [3/3] Fazendo push para GitHub...
echo.
echo Você vai precisar se autenticar:
echo - Username: Nardoto
echo - Password: Use um Personal Access Token (não a senha normal)
echo.
echo Se não tiver token, gere em: https://github.com/settings/tokens
echo.
pause

git push -u origin main

echo.
echo ========================================
echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ SUCESSO! Código enviado para GitHub!
    echo.
    echo Próximos passos:
    echo 1. Acesse: https://github.com/Nardoto/script-copier-web
    echo 2. Vá em Settings ^> Pages
    echo 3. Branch: main / root ^> Save
    echo 4. Aguarde 2 minutos
    echo 5. Acesse: https://nardoto.github.io/script-copier-web/
    echo.
) else (
    echo ❌ ERRO! Algo deu errado.
    echo.
    echo Possíveis causas:
    echo - Repositório não foi criado no GitHub
    echo - Autenticação incorreta
    echo - Token sem permissão 'repo'
    echo.
    echo Solução: Veja o arquivo DEPLOY.md
    echo.
)

pause
