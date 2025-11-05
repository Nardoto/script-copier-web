"""
╔═══════════════════════════════════════════════════════════════════╗
║                 SCRIPT COPIER UNIVERSAL v2.0                      ║
║                                                                   ║
║  Aplicativo para gerenciar e copiar roteiros de vídeos           ║
║                                                                   ║
║  Desenvolvido por: Tharc (Nardoto)                              ║
║  Data: 2025                                                       ║
║  GitHub: github.com/nardoto                                       ║
║                                                                   ║
║  Recursos:                                                        ║
║  • Suporte universal a pastas de roteiros                        ║
║  • Histórico de cópias com timestamps                           ║
║  • Interface moderna (tema Claude Loopless)                      ║
║  • Gerenciamento de status de vídeos                            ║
║  • Sistema inteligente de salvamento                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
import pyperclip
import json
from datetime import datetime
import subprocess
import platform
import sys

class ScriptCopier:
    def listar_arquivos_incluindo_ocultos(self, caminho):
        try:
            if platform.system() == 'Windows':
                cmd = f'cmd /c "dir /b /a "{caminho}""'
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    items = result.stdout.strip().split('\n')
                    return [item.strip() for item in items if item.strip()]
                else:
                    return os.listdir(caminho)
            else:
                return os.listdir(caminho)
        except Exception as e:
            return os.listdir(caminho) if os.path.exists(caminho) else []

    def __init__(self, root):
        self.root = root
        self.root.title("Script Copier Universal - By Nardoto")
        self.root.geometry("1200x750")

        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'script_copier_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

        self.arquivo_atual = ""
        self.secoes = {}
        self.texto_completo = ""
        self.pasta_roteiros = ""
        self.pasta_raiz_selecionada = ""
        self.roteiros_disponiveis = {}
        self.roteiro_atual = None
        self.pasta_roteiro_atual = ""
        self.historico_copias = {}
        self.historico_modificado = False  # Flag para detectar mudanças

        self.configurar_estilo()
        self.criar_interface()
        self.mostrar_tela_inicial()

        # Intercepta o fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar_app)

    def configurar_estilo(self):
        """Configura o tema visual EXATO do Claude Loopless"""
        style = ttk.Style()
        style.theme_use('clam')

        # CORES EXATAS DO CLAUDE LOOPLESS
        self.bg_color = "#faf9f5"           # Fundo principal (bege/creme claro)
        self.bg_secondary = "#f0eee7"       # Fundo secundário (bege um pouco mais escuro)
        self.fg_color = "#000000"           # Texto preto
        self.fg_secondary = "#666666"       # Texto secundário (cinza)
        self.button_bg = "#e8e6df"          # Botões normais (bege mais escuro)
        self.button_hover = "#d9d7d0"       # Hover de botões normais
        self.accent_color = "#cb6246"       # Laranja/Terracota (botões principais e ícones)
        self.accent_hover = "#d97559"       # Laranja mais claro (hover)
        self.green_light = "#a8d5ba"        # Verde clarinho (copiado e salvar)
        self.green_hover = "#98c5aa"        # Verde um pouco mais escuro (hover)
        self.green_copied = "#c8e6d0"       # Verde bem clarinho (fundo de item copiado)
        self.border_color = "#e0ded7"       # Bordas sutis
        self.border_radius = 16             # Raio das bordas bem arredondadas!

        # Fontes modernas
        self.font_family = "Segoe UI"       # Fonte principal
        self.font_mono = "Consolas"         # Fonte monoespaçada

        self.root.configure(bg=self.bg_color)

    def criar_interface(self):
        # Frame topo compacto
        frame_mestre = tk.Frame(self.root, bg=self.bg_color, pady=10)
        frame_mestre.pack(fill=tk.X, padx=15)

        # Linha com título e botão
        frame_titulo_linha = tk.Frame(frame_mestre, bg=self.bg_color)
        frame_titulo_linha.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            frame_titulo_linha,
            text="📚 SCRIPT COPIER UNIVERSAL",
            bg=self.bg_color,
            fg=self.fg_color,
            font=(self.font_family, 14, "bold")
        ).pack(side=tk.LEFT)

        # Botão Criar Atalho
        btn_atalho = tk.Button(
            frame_titulo_linha,
            text="📌",
            command=self.criar_atalho_dialog,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 11, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            borderwidth=0
        )
        btn_atalho.pack(side=tk.RIGHT, padx=(0, 5))
        btn_atalho.bind("<Enter>", lambda e: btn_atalho.config(bg=self.button_hover))
        btn_atalho.bind("<Leave>", lambda e: btn_atalho.config(bg=self.button_bg))

        # Botão Sobre
        btn_sobre = tk.Button(
            frame_titulo_linha,
            text="ℹ",
            command=self.mostrar_sobre,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 11, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            borderwidth=0
        )
        btn_sobre.pack(side=tk.RIGHT, padx=(0, 5))
        btn_sobre.bind("<Enter>", lambda e: btn_sobre.config(bg=self.button_hover))
        btn_sobre.bind("<Leave>", lambda e: btn_sobre.config(bg=self.button_bg))

        # Botão Ajuda
        btn_ajuda = tk.Button(
            frame_titulo_linha,
            text="?",
            command=self.mostrar_ajuda,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 11, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            borderwidth=0
        )
        btn_ajuda.pack(side=tk.RIGHT, padx=(0, 5))
        btn_ajuda.bind("<Enter>", lambda e: btn_ajuda.config(bg=self.button_hover))
        btn_ajuda.bind("<Leave>", lambda e: btn_ajuda.config(bg=self.button_bg))

        # Botão Salvar Estado
        btn_salvar_estado = tk.Button(
            frame_titulo_linha,
            text="💾 Salvar Estado",
            command=self.salvar_estado_completo_manual,
            bg=self.green_light,
            fg=self.fg_color,
            font=(self.font_family, 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            borderwidth=0
        )
        btn_salvar_estado.pack(side=tk.RIGHT, padx=(0, 5))
        btn_salvar_estado.bind("<Enter>", lambda e: btn_salvar_estado.config(bg=self.green_hover))
        btn_salvar_estado.bind("<Leave>", lambda e: btn_salvar_estado.config(bg=self.green_light))

        # Botão selecionar pasta na mesma linha
        btn_selecionar = tk.Button(
            frame_titulo_linha,
            text="📁 Selecionar Pasta",
            command=self.selecionar_pasta_raiz,
            bg=self.accent_color,
            fg="white",
            font=(self.font_family, 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            borderwidth=0
        )
        btn_selecionar.pack(side=tk.RIGHT)
        btn_selecionar.bind("<Enter>", lambda e: btn_selecionar.config(bg=self.accent_hover))
        btn_selecionar.bind("<Leave>", lambda e: btn_selecionar.config(bg=self.accent_color))

        # Label da pasta selecionada
        self.label_pasta_selecionada = tk.Label(
            frame_mestre,
            text="Nenhuma pasta selecionada",
            bg=self.bg_color,
            fg=self.fg_secondary,
            font=(self.font_family, 8)
        )
        self.label_pasta_selecionada.pack(anchor="w", pady=(0, 5))

        # Linha separadora sutil
        tk.Frame(self.root, bg=self.border_color, height=1).pack(fill=tk.X)

        frame_selecao_mestre = tk.Frame(frame_mestre, bg=self.bg_color)
        frame_selecao_mestre.pack(fill=tk.X)

        tk.Label(
            frame_selecao_mestre,
            text="Selecione o Roteiro:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=(self.font_family, 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.combo_roteiro_mestre = ttk.Combobox(
            frame_selecao_mestre,
            state="readonly",
            font=("Arial", 10),
            width=50
        )
        self.combo_roteiro_mestre.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_roteiro_mestre.bind("<<ComboboxSelected>>", self.ao_selecionar_roteiro_mestre)

        btn_atualizar = tk.Button(
            frame_selecao_mestre,
            text="🔄",
            command=self.buscar_pasta_roteiros,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            borderwidth=0
        )
        btn_atualizar.pack(side=tk.LEFT, padx=(0, 5))
        btn_atualizar.bind("<Enter>", lambda e: btn_atualizar.config(bg=self.button_hover))
        btn_atualizar.bind("<Leave>", lambda e: btn_atualizar.config(bg=self.button_bg))

        btn_abrir = tk.Button(
            frame_selecao_mestre,
            text="📂",
            command=self.abrir_pasta_roteiro,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            borderwidth=0
        )
        btn_abrir.pack(side=tk.LEFT)
        btn_abrir.bind("<Enter>", lambda e: btn_abrir.config(bg=self.button_hover))
        btn_abrir.bind("<Leave>", lambda e: btn_abrir.config(bg=self.button_bg))

        self.label_pasta_mestre = tk.Label(
            frame_mestre,
            text="",
            bg=self.bg_color,
            fg="#888888",
            font=("Arial", 8)
        )
        self.label_pasta_mestre.pack(anchor="w", pady=(5, 0))

        tk.Frame(self.root, bg=self.border_color, height=1).pack(fill=tk.X, padx=15, pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.aba_copiar = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.aba_copiar, text="📋 Copiar Seções")

        self.aba_visualizar = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.aba_visualizar, text="📂 Visualizar Arquivos")

        self.aba_titulo = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.aba_titulo, text="🎬 Título e Descrição")

        self.criar_aba_copiar()
        self.criar_aba_visualizar()
        self.criar_aba_titulo()

        # Rodapé com fundo claro
        frame_rodape = tk.Frame(self.root, bg=self.bg_secondary, height=35)
        frame_rodape.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(
            frame_rodape,
            text="💻 Desenvolvido por Nardoto | Script Copier Universal v4.0",
            bg=self.bg_secondary,
            fg=self.fg_secondary,
            font=(self.font_family, 9)
        ).pack(pady=8)

    def criar_aba_copiar(self):
        # Frame superior removido (sem botões de limpar)
        tk.Frame(self.aba_copiar, bg=self.border_color, height=1).pack(fill=tk.X, padx=15, pady=5)

        frame_principal = tk.Frame(self.aba_copiar, bg=self.bg_color)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        frame_esquerdo = tk.Frame(frame_principal, bg=self.bg_color, width=380)
        frame_esquerdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        frame_esquerdo.pack_propagate(False)

        tk.Label(
            frame_esquerdo,
            text="📑 SEÇÕES DO ROTEIRO",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))

        self.frame_scroll = tk.Frame(frame_esquerdo, bg=self.bg_color)
        self.frame_scroll.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_scroll, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame_scroll, orient="vertical", command=self.canvas.yview)
        self.frame_botoes = tk.Frame(self.canvas, bg=self.bg_color)

        self.frame_botoes.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        canvas_window = self.canvas.create_window((0, 0), window=self.frame_botoes, anchor="nw", width=360)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure_esq(event):
            self.canvas.itemconfig(canvas_window, width=event.width - 10)
        self.canvas.bind("<Configure>", on_canvas_configure_esq)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def scroll_mouse_esq(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", scroll_mouse_esq))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.label_sem_secoes = tk.Label(
            self.frame_botoes,
            text="👈 Selecione um roteiro\npara visualizar as seções",
            bg=self.bg_color,
            fg="#888888",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        self.label_sem_secoes.pack(pady=50)

        # Frame direito - Visualização do texto
        frame_direito = tk.Frame(frame_principal, bg=self.bg_color)
        frame_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Título e informações da seção
        self.frame_info = tk.Frame(frame_direito, bg=self.bg_color)
        self.frame_info.pack(fill=tk.X, pady=(0, 10))

        self.label_secao_atual = tk.Label(
            self.frame_info,
            text="📝 Visualização do Texto",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold")
        )
        self.label_secao_atual.pack(side=tk.LEFT)

        self.label_palavras = tk.Label(
            self.frame_info,
            text="",
            bg=self.bg_color,
            fg="#aaaaaa",
            font=("Arial", 10)
        )
        self.label_palavras.pack(side=tk.LEFT, padx=(20, 0))

        frame_acoes = tk.Frame(frame_direito, bg=self.bg_color)
        frame_acoes.pack(fill=tk.X, pady=(0, 10))

        self.btn_copiar = tk.Button(
            frame_acoes,
            text="📋 Copiar",
            command=self.copiar_texto_atual,
            bg=self.accent_color,
            fg="#ffffff",  # BRANCO GARANTIDO
            font=(self.font_family, 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            state=tk.DISABLED,
            borderwidth=0,
            activeforeground="#ffffff"  # Branco quando ativo também
        )
        self.btn_copiar.pack(side=tk.LEFT, padx=(0, 5))
        self.btn_copiar.bind("<Enter>", lambda e: self.btn_copiar.config(bg=self.accent_hover) if self.btn_copiar['state'] == 'normal' else None)
        self.btn_copiar.bind("<Leave>", lambda e: self.btn_copiar.config(bg=self.accent_color) if self.btn_copiar['state'] == 'normal' else None)

        btn_salvar = tk.Button(
            frame_acoes,
            text="💾 Salvar",
            command=self.salvar_secao,
            bg=self.green_light,
            fg=self.fg_color,  # PRETO
            font=(self.font_family, 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            borderwidth=0
        )
        btn_salvar.pack(side=tk.LEFT)

        # Hover verde
        btn_salvar.bind("<Enter>", lambda e: btn_salvar.config(bg=self.green_hover))
        btn_salvar.bind("<Leave>", lambda e: btn_salvar.config(bg=self.green_light))

        self.text_area = scrolledtext.ScrolledText(
            frame_direito,
            wrap=tk.WORD,
            font=(self.font_mono, 11),
            bg=self.bg_secondary,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.button_hover,
            relief=tk.FLAT,
            padx=20,
            pady=20,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        def scroll_text_area(event):
            self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        self.text_area.bind("<Enter>", lambda e: self.text_area.bind("<MouseWheel>", scroll_text_area))
        self.text_area.bind("<Leave>", lambda e: self.text_area.unbind("<MouseWheel>"))

        self.text_area.insert(1.0, "👈 Selecione um roteiro e uma seção para visualizar o texto aqui.\n\nVocê poderá copiar o texto com um clique!")
        self.text_area.config(state=tk.DISABLED)

        frame_status = tk.Frame(self.aba_copiar, bg=self.bg_secondary, height=35)
        frame_status.pack(fill=tk.X, side=tk.BOTTOM)

        self.label_status = tk.Label(
            frame_status,
            text="🔍 Buscando roteiros...",
            bg=self.bg_secondary,
            fg=self.accent_color,
            font=(self.font_family, 9)
        )
        self.label_status.pack(side=tk.LEFT, padx=15, pady=8)

    def criar_aba_visualizar(self):
        # Remove o frame superior com dropdown - agora os arquivos aparecem na árvore
        tk.Frame(self.aba_visualizar, bg=self.border_color, height=1).pack(fill=tk.X, padx=15, pady=10)

        frame_principal = tk.Frame(self.aba_visualizar, bg=self.bg_color)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        frame_esq = tk.Frame(frame_principal, bg=self.bg_color, width=350)
        frame_esq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        frame_esq.pack_propagate(False)

        tk.Label(
            frame_esq,
            text="📂 ARQUIVOS",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))

        tree_frame = tk.Frame(frame_esq, bg=self.bg_color)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_arquivos = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll.set,
            selectmode="browse"
        )
        self.tree_arquivos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree_arquivos.yview)

        def scroll_tree(event):
            self.tree_arquivos.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        self.tree_arquivos.bind("<Enter>", lambda e: self.tree_arquivos.bind("<MouseWheel>", scroll_tree))
        self.tree_arquivos.bind("<Leave>", lambda e: self.tree_arquivos.unbind("<MouseWheel>"))
        self.tree_arquivos.bind("<<TreeviewSelect>>", self.arquivo_tree_selecionado)

        frame_dir = tk.Frame(frame_principal, bg=self.bg_color)
        frame_dir.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Info do arquivo
        frame_info = tk.Frame(frame_dir, bg=self.bg_color)
        frame_info.pack(fill=tk.X, pady=(0, 10))

        self.label_arquivo_atual = tk.Label(
            frame_info,
            text="📄 Selecione um roteiro e arquivo",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold")
        )
        self.label_arquivo_atual.pack(side=tk.LEFT)

        self.label_info_arquivo = tk.Label(
            frame_info,
            text="",
            bg=self.bg_color,
            fg="#aaaaaa",
            font=("Arial", 10)
        )
        self.label_info_arquivo.pack(side=tk.LEFT, padx=(20, 0))

        # Botões de ação
        frame_acoes_vis = tk.Frame(frame_dir, bg=self.bg_color)
        frame_acoes_vis.pack(fill=tk.X, pady=(0, 10))

        btn_copiar_vis = tk.Button(
            frame_acoes_vis,
            text="📋 Copiar",
            command=self.copiar_conteudo_visualizado,
            bg=self.accent_color,
            fg="#ffffff",
            font=(self.font_family, 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            borderwidth=0,
            activeforeground="#ffffff"
        )
        btn_copiar_vis.pack(side=tk.LEFT, padx=(0, 5))
        btn_copiar_vis.bind("<Enter>", lambda e: btn_copiar_vis.config(bg=self.accent_hover))
        btn_copiar_vis.bind("<Leave>", lambda e: btn_copiar_vis.config(bg=self.accent_color))

        btn_recarregar_vis = tk.Button(
            frame_acoes_vis,
            text="🔄",
            command=self.recarregar_arquivo_atual,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 9),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            borderwidth=0
        )
        btn_recarregar_vis.pack(side=tk.LEFT)
        btn_recarregar_vis.bind("<Enter>", lambda e: btn_recarregar_vis.config(bg=self.button_hover))
        btn_recarregar_vis.bind("<Leave>", lambda e: btn_recarregar_vis.config(bg=self.button_bg))

        # Área de visualização
        self.text_visualizar = scrolledtext.ScrolledText(
            frame_dir,
            wrap=tk.WORD,
            font=(self.font_mono, 10),
            bg=self.bg_secondary,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.button_hover,
            relief=tk.FLAT,
            padx=20,
            pady=20,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.text_visualizar.pack(fill=tk.BOTH, expand=True)

        # Habilita scroll com mouse na área de visualização
        def scroll_text_vis(event):
            self.text_visualizar.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        self.text_visualizar.bind("<Enter>", lambda e: self.text_visualizar.bind("<MouseWheel>", scroll_text_vis))
        self.text_visualizar.bind("<Leave>", lambda e: self.text_visualizar.unbind("<MouseWheel>"))

        # Placeholder
        self.text_visualizar.insert(1.0, "👆 Selecione um roteiro e arquivo para visualizar\n\nVocê poderá navegar pelas partes e capítulos na árvore ao lado.")
        self.text_visualizar.config(state=tk.DISABLED)

        # Status
        frame_status_vis = tk.Frame(self.aba_visualizar, bg=self.bg_secondary, height=35)
        frame_status_vis.pack(fill=tk.X, side=tk.BOTTOM)

        self.label_status_vis = tk.Label(
            frame_status_vis,
            text="Pronto para visualizar",
            bg=self.bg_secondary,
            fg=self.accent_color,
            font=(self.font_family, 9)
        )
        self.label_status_vis.pack(side=tk.LEFT, padx=15, pady=8)

    def mostrar_tela_inicial(self):
        """Mostra tela inicial solicitando seleção da pasta raiz"""
        self.atualizar_status("👆 Clique no botão azul acima para selecionar a pasta raiz do projeto")

    def mostrar_ajuda(self):
        """Mostra janela com instruções de como estruturar arquivos"""
        ajuda_texto = """
╔═══════════════════════════════════════════════════════════════════╗
║           COMO ESTRUTURAR SEUS ARQUIVOS PARA O APP               ║
╚═══════════════════════════════════════════════════════════════════╝

📁 ESTRUTURA DE PASTAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROTEIROS_GERADOS/
├── NOME_DO_ROTEIRO_1/
│   ├── 01_Roteiro_Estruturado.txt
│   ├── 02_Texto_Narrado.txt
│   ├── 05_Titulo_Descricao.txt (opcional)
│   └── video_status.json (criado automaticamente)
│
├── NOME_DO_ROTEIRO_2/
│   └── arquivo.txt (qualquer arquivo .txt)
│
└── historico.json (criado automaticamente)


📄 PADRÕES DE SEÇÕES RECONHECIDOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

O app identifica automaticamente seções usando estes padrões:

✓ OPENING - Título da Abertura
✓ ACT 1 - Título do Ato  |  ACT ONE - Título do Ato
✓ CHAPTER 1 - Título do Capítulo  |  CHAPTER ONE - Título do Capítulo
✓ PART 1 - Título da Parte  |  PART ONE - Título da Parte
✓ CONCLUSION - Título da Conclusão


📋 EXEMPLO 1: 01_Roteiro_Estruturado.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPENING - O DILÚVIO: JULGAMENTO E REDENÇÃO

Há mais de 4.000 anos, a Terra testemunhou um evento catastrófico
que moldaria para sempre a história da humanidade. Um dilúvio global
que cobriu montanhas, destruiu civilizações e preservou apenas
aqueles escolhidos para recomeçar.

Esta é a história do Grande Dilúvio.


CHAPTER 1 - A CORRUPÇÃO DA HUMANIDADE

Nos dias antes do dilúvio, a maldade do homem havia se multiplicado
sobre a Terra. Gênesis 6:5 nos diz que "toda a imaginação dos
pensamentos do coração do homem era só má continuamente."

A violência tomou conta do mundo. A justiça havia desaparecido.
E Deus se entristeceu por ter criado o homem.


CHAPTER 2 - NOÉ ENCONTRA GRAÇA

Mas um homem se destacava em meio à corrupção: Noé.

Ele era justo, íntegro entre os seus contemporâneos. Noé andava
com Deus em uma época em que poucos se lembravam do Criador.

E Deus falou com Noé...


CONCLUSION - O ARCO-ÍRIS DA PROMESSA

Quando as águas baixaram e a família de Noé pisou em terra seca,
Deus estabeleceu uma aliança eterna.

O arco-íris surgiu no céu como sinal de que nunca mais destruiria
a Terra com um dilúvio.

Esta promessa permanece até hoje, lembrando-nos da misericórdia
divina e da fidelidade de Deus.


📝 EXEMPLO 2: 02_Texto_Narrado.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Há mais de quatro mil anos, a Terra testemunhou um evento catastrófico
que moldaria para sempre a história da humanidade.

Um dilúvio global. Que cobriu as montanhas. Destruiu civilizações.
E preservou apenas aqueles escolhidos para recomeçar.

Esta é a história do Grande Dilúvio.

(Pausa)

Nos dias antes do dilúvio, a maldade do homem havia se multiplicado
sobre a Terra.

Gênesis capítulo 6, versículo 5, nos diz:
"Toda a imaginação dos pensamentos do coração do homem era só má,
continuamente."

A violência tomou conta do mundo.
A justiça havia desaparecido.
E Deus se entristeceu por ter criado o homem.


📺 EXEMPLO 3: 05_Titulo_Descricao.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TÍTULO:
O Grande Dilúvio: A História Completa de Noé e a Arca | Documentário Bíblico

DESCRIÇÃO:
Descubra a história completa do Grande Dilúvio que transformou o mundo
há mais de 4.000 anos. Neste documentário bíblico, exploramos:

✓ A corrupção que levou ao julgamento divino
✓ A construção da arca e o chamado de Noé
✓ O dilúvio que cobriu toda a Terra
✓ A aliança do arco-íris e o recomeço da humanidade

Baseado em Gênesis capítulos 6 a 9, esta narrativa mergulha nos
eventos que moldaram a história da humanidade e revelam o caráter
de Deus: justo no julgamento, misericordioso na salvação.

📖 Versículos principais:
• Gênesis 6:5-8
• Gênesis 7:11-24
• Gênesis 8:1-22
• Gênesis 9:8-17

Se você gosta de estudos bíblicos profundos e documentários sobre
história sagrada, inscreva-se no canal!

#Dilúvio #Noé #DocumentárioBíblico #Gênesis #HistóriaBíblica


⚙️ COMPATIBILIDADE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Funciona com arquivos .txt e .srt
✓ Aceita pastas com estrutura organizada OU arquivos diretos
✓ Detecta automaticamente o formato
✓ Salva histórico de cópias automaticamente
✓ Arquivos podem ter qualquer nome (não precisa ser exatamente esses nomes)
"""

        # Cria janela de ajuda
        janela_ajuda = tk.Toplevel(self.root)
        janela_ajuda.title("Como Usar o Script Copier")
        janela_ajuda.geometry("800x600")
        janela_ajuda.configure(bg=self.bg_color)

        # Área de texto com scroll
        frame_texto = tk.Frame(janela_ajuda, bg=self.bg_color)
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        text_ajuda = scrolledtext.ScrolledText(
            frame_texto,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.bg_secondary,
            fg=self.fg_color,
            padx=20,
            pady=20,
            relief=tk.FLAT
        )
        text_ajuda.pack(fill=tk.BOTH, expand=True)
        text_ajuda.insert(1.0, ajuda_texto)
        text_ajuda.config(state=tk.DISABLED)

        # Botão fechar
        btn_fechar = tk.Button(
            janela_ajuda,
            text="Fechar",
            command=janela_ajuda.destroy,
            bg=self.accent_color,
            fg="white",
            font=(self.font_family, 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0
        )
        btn_fechar.pack(pady=(0, 20))

    def criar_atalho_dialog(self):
        """Mostra diálogo para criar atalhos do aplicativo"""
        dialog_texto = """
╔═══════════════════════════════════════════════════════════════════╗
║              CRIAR ATALHOS DO SCRIPT COPIER                       ║
╚═══════════════════════════════════════════════════════════════════╝

📌 CRIAR ATALHO NA ÁREA DE TRABALHO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Clique no botão "Criar Atalho na Área de Trabalho" abaixo para criar
automaticamente um atalho na sua área de trabalho.


📍 FIXAR NA BARRA DE TAREFAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para fixar o aplicativo na barra de tarefas do Windows:

MÉTODO 1 (Mais fácil):
1. Abra o aplicativo normalmente
2. Clique com o botão DIREITO no ícone na barra de tarefas
3. Selecione "Fixar na barra de tarefas"

MÉTODO 2 (Alternativo):
1. Localize o arquivo "ScriptCopier_Universal_v2.0.exe"
2. Clique com o botão DIREITO no arquivo
3. Selecione "Fixar na barra de tarefas"

MÉTODO 3 (Arrastar):
1. Localize o arquivo "ScriptCopier_Universal_v2.0.exe"
2. ARRASTE o arquivo para a barra de tarefas
3. Solte o botão do mouse


📂 LOCALIZAÇÃO DO EXECUTÁVEL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

O executável está localizado em:
"""
        # Cria janela de diálogo
        dialog_atalho = tk.Toplevel(self.root)
        dialog_atalho.title("Criar Atalhos")
        dialog_atalho.geometry("750x550")
        dialog_atalho.configure(bg=self.bg_color)

        # Área de texto com scroll
        frame_texto = tk.Frame(dialog_atalho, bg=self.bg_color)
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        text_dialog = scrolledtext.ScrolledText(
            frame_texto,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.bg_secondary,
            fg=self.fg_color,
            padx=20,
            pady=20,
            relief=tk.FLAT,
            height=15
        )
        text_dialog.pack(fill=tk.BOTH, expand=True)

        # Adiciona o caminho do executável ao texto
        exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        texto_completo = dialog_texto + f"{exe_path}\n"

        text_dialog.insert(1.0, texto_completo)
        text_dialog.config(state=tk.DISABLED)

        # Frame para botões
        frame_botoes = tk.Frame(dialog_atalho, bg=self.bg_color)
        frame_botoes.pack(pady=(10, 20))

        # Botão criar atalho na área de trabalho
        btn_criar_desktop = tk.Button(
            frame_botoes,
            text="📌 Criar Atalho na Área de Trabalho",
            command=lambda: self.criar_atalho_desktop(dialog_atalho),
            bg=self.accent_color,
            fg="white",
            font=(self.font_family, 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0
        )
        btn_criar_desktop.pack(side=tk.LEFT, padx=5)

        # Botão abrir pasta do executável
        btn_abrir_pasta = tk.Button(
            frame_botoes,
            text="📂 Abrir Pasta do Executável",
            command=self.abrir_pasta_executavel,
            bg=self.green_light,
            fg=self.fg_color,
            font=(self.font_family, 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0
        )
        btn_abrir_pasta.pack(side=tk.LEFT, padx=5)

        # Botão fechar
        btn_fechar = tk.Button(
            frame_botoes,
            text="Fechar",
            command=dialog_atalho.destroy,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0
        )
        btn_fechar.pack(side=tk.LEFT, padx=5)

    def criar_atalho_desktop(self, janela_pai):
        """Cria um atalho na área de trabalho"""
        try:
            # Obtém o caminho do executável
            if getattr(sys, 'frozen', False):
                # Rodando como executável
                exe_path = sys.executable
            else:
                # Rodando como script Python
                exe_path = os.path.abspath(__file__)

            # Obtém o caminho da área de trabalho
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            atalho_path = os.path.join(desktop, 'Script Copier Universal.lnk')

            # Cria o atalho usando PowerShell (funciona sem dependências extras)
            ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{atalho_path}")
$Shortcut.TargetPath = "{exe_path}"
$Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
$Shortcut.Description = "Script Copier Universal - Gerenciador de Roteiros"
$Shortcut.Save()
'''

            # Executa o script PowerShell
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                messagebox.showinfo(
                    "Sucesso!",
                    "Atalho criado com sucesso na Área de Trabalho!\n\n"
                    "Você pode encontrá-lo como:\n"
                    "'Script Copier Universal'"
                )
                janela_pai.destroy()
            else:
                raise Exception(result.stderr)

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível criar o atalho:\n{str(e)}\n\n"
                "Você pode criar manualmente:\n"
                "1. Clique com botão direito no executável\n"
                "2. Selecione 'Enviar para > Área de trabalho (criar atalho)'"
            )

    def abrir_pasta_executavel(self):
        """Abre a pasta onde está o executável"""
        try:
            # Obtém o caminho do executável
            if getattr(sys, 'frozen', False):
                # Rodando como executável
                exe_path = sys.executable
            else:
                # Rodando como script Python
                exe_path = os.path.abspath(__file__)

            # Abre o Explorer na pasta e seleciona o arquivo
            subprocess.run(['explorer', '/select,', exe_path])

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{str(e)}")

    def mostrar_sobre(self):
        """Mostra janela com informações sobre o aplicativo e créditos"""
        sobre_texto = """
╔═══════════════════════════════════════════════════════════════════╗
║                 SCRIPT COPIER UNIVERSAL v2.0                      ║
╚═══════════════════════════════════════════════════════════════════╝

📌 SOBRE O APLICATIVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

O Script Copier Universal é uma ferramenta profissional desenvolvida
para facilitar o gerenciamento e a cópia de roteiros de vídeos,
especialmente útil para criadores de conteúdo que trabalham com
documentários, vídeos educacionais e produções narrativas.


👨‍💻 DESENVOLVEDOR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Desenvolvido por: Tharc (Nardoto)
Ano: 2025
GitHub: github.com/nardoto


✨ RECURSOS PRINCIPAIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Suporte universal a qualquer estrutura de pastas
✓ Detecção automática de seções em roteiros
✓ Histórico inteligente de cópias com timestamps
✓ Interface moderna e intuitiva (tema Claude Loopless)
✓ Gerenciamento de status de vídeos (gravado/postado)
✓ Sistema inteligente de salvamento automático
✓ Indicadores visuais para seções já copiadas
✓ Suporte para múltiplos formatos (.txt, .srt)
✓ Compatível com Windows, Linux e macOS


🔧 TECNOLOGIAS UTILIZADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Python 3.x
• Tkinter (Interface Gráfica)
• JSON (Armazenamento de dados)
• PyInstaller (Geração de executável)


📄 LICENÇA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

© 2025 Tharc (Nardoto). Todos os direitos reservados.

Este software foi desenvolvido com dedicação para facilitar o
trabalho de criadores de conteúdo. Sinta-se livre para usar,
mas mantenha os créditos ao desenvolvedor.


💡 SUPORTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para dúvidas, sugestões ou reportar bugs:
• GitHub: github.com/nardoto
• Email: contato disponível no GitHub


Obrigado por usar o Script Copier Universal! 🚀
"""

        # Cria janela sobre
        janela_sobre = tk.Toplevel(self.root)
        janela_sobre.title("Sobre o Script Copier Universal")
        janela_sobre.geometry("750x650")
        janela_sobre.configure(bg=self.bg_color)

        # Área de texto com scroll
        frame_texto = tk.Frame(janela_sobre, bg=self.bg_color)
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        text_sobre = scrolledtext.ScrolledText(
            frame_texto,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.bg_secondary,
            fg=self.fg_color,
            padx=20,
            pady=20,
            relief=tk.FLAT
        )
        text_sobre.pack(fill=tk.BOTH, expand=True)
        text_sobre.insert(1.0, sobre_texto)
        text_sobre.config(state=tk.DISABLED)

        # Botão fechar
        btn_fechar = tk.Button(
            janela_sobre,
            text="Fechar",
            command=janela_sobre.destroy,
            bg=self.accent_color,
            fg="white",
            font=(self.font_family, 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0
        )
        btn_fechar.pack(pady=(0, 20))

    def ao_fechar_app(self):
        """Chamado ao fechar o aplicativo - pergunta se quer salvar"""
        # Só pergunta se houver mudanças não salvas
        if self.historico_modificado:
            resposta = messagebox.askyesnocancel(
                "Salvar Estado",
                "Você fez alterações não salvas.\n\n"
                "Deseja salvar antes de sair?\n\n"
                "• SIM: Salva o histórico de cópias\n"
                "• NÃO: Sai sem salvar\n"
                "• CANCELAR: Volta ao aplicativo"
            )

            if resposta is None:  # Cancelar
                return
            elif resposta:  # Sim - Salvar
                self.salvar_estado_completo()
                messagebox.showinfo("Sucesso", "Estado salvo com sucesso!")

        # Fecha o aplicativo
        self.root.destroy()

    def salvar_estado_completo(self):
        """Salva todo o estado do aplicativo (sem mensagem)"""
        try:
            # Salva o histórico de cópias
            self.salvar_historico()

            # Marca como salvo
            self.historico_modificado = False

            # Se houver roteiro selecionado, salva info do vídeo também
            if self.pasta_roteiro_atual:
                self.salvar_info_video(mostrar_mensagem=False)

            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar estado:\n{str(e)}")
            return False

    def salvar_estado_completo_manual(self):
        """Salva o estado manualmente via botão"""
        if not self.pasta_raiz_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma pasta raiz primeiro!")
            return

        try:
            # Salva o histórico de cópias
            self.salvar_historico()

            # Conta quantas cópias foram salvas
            total_copias = sum(
                len(secoes)
                for secoes in self.historico_copias.values()
            )

            # Se houver roteiro selecionado, salva info do vídeo também
            if self.pasta_roteiro_atual:
                self.salvar_info_video(mostrar_mensagem=False)

            agora = datetime.now()
            messagebox.showinfo(
                "✅ Estado Salvo",
                f"Estado salvo com sucesso!\n\n"
                f"📋 Total de cópias: {total_copias}\n"
                f"📂 Roteiros: {len(self.historico_copias)}\n"
                f"🕒 Data: {agora.strftime('%d/%m/%Y às %H:%M')}"
            )

            self.atualizar_status(f"✅ Estado salvo! {total_copias} cópias registradas")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar estado:\n{str(e)}")

    def selecionar_pasta_raiz(self):
        """Permite ao usuário selecionar a pasta raiz do projeto"""
        pasta_selecionada = filedialog.askdirectory(
            title="Selecione a Pasta Raiz do Projeto (contém as subpastas dos roteiros)"
        )

        if pasta_selecionada:
            self.pasta_raiz_selecionada = pasta_selecionada
            self.label_pasta_selecionada.config(
                text=f"📁 Pasta selecionada: {pasta_selecionada}",
                fg="#4CAF50"
            )
            # Busca roteiros na pasta selecionada
            self.buscar_pasta_roteiros()

    def carregar_arquivos_roteiro(self, event=None):
        """Carrega os arquivos disponíveis e popula a árvore"""
        if not self.pasta_roteiro_atual or not os.path.exists(self.pasta_roteiro_atual):
            return

        # Limpa a árvore
        for item in self.tree_arquivos.get_children():
            self.tree_arquivos.delete(item)

        # Remove colunas e configura
        self.tree_arquivos['columns'] = ()
        self.tree_arquivos.heading('#0', text='Arquivos da Pasta')

        # Dicionário para guardar info dos arquivos e suas estruturas
        self.mapa_arquivos = {}  # {item_id: {'tipo': 'arquivo'|'secao', 'caminho': '...', 'conteudo': '...'}}

        # Lista TODOS os arquivos .txt e .srt
        arquivos_encontrados = []
        try:
            for arquivo in self.listar_arquivos_incluindo_ocultos(self.pasta_roteiro_atual):
                caminho_completo = os.path.join(self.pasta_roteiro_atual, arquivo)
                if arquivo.endswith(('.txt', '.srt')) and os.path.isfile(caminho_completo):
                    arquivos_encontrados.append((arquivo, caminho_completo))
        except Exception as e:
            pass  # Silencioso em produção

        if arquivos_encontrados:
            # Ordena arquivos alfabeticamente
            arquivos_encontrados.sort()

            for arquivo, caminho in arquivos_encontrados:
                # Determina o ícone baseado na extensão
                if arquivo.endswith('.txt'):
                    icone = "📄"
                elif arquivo.endswith('.srt'):
                    icone = "📝"
                else:
                    icone = "📋"

                # Adiciona o arquivo como nó principal
                item_id = self.tree_arquivos.insert('', 'end', text=f"{icone} {arquivo}")

                # Guarda informações do arquivo
                self.mapa_arquivos[item_id] = {
                    'tipo': 'arquivo',
                    'caminho': caminho,
                    'nome': arquivo
                }

                # Tenta carregar e analisar estrutura do arquivo (BONUS)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo = f.read()

                    # Analisa se tem estrutura (ACT, CHAPTER, etc.)
                    secoes = self.detectar_secoes_arquivo(conteudo)

                    if secoes:
                        # Se tem estrutura, adiciona como sub-items
                        for secao in secoes:
                            icone_secao = "📖"
                            if 'ACT' in secao['titulo'].upper() or 'ATO' in secao['titulo'].upper():
                                icone_secao = "🎭"
                            elif 'OPENING' in secao['titulo'].upper() or 'HOOK' in secao['titulo'].upper():
                                icone_secao = "🎬"
                            elif 'CLOSING' in secao['titulo'].upper() or 'CONCLUS' in secao['titulo'].upper():
                                icone_secao = "🏁"

                            titulo_curto = secao['titulo'][:70]
                            if len(secao['titulo']) > 70:
                                titulo_curto += "..."

                            secao_id = self.tree_arquivos.insert(item_id, 'end', text=f"  {icone_secao} {titulo_curto}")

                            # Guarda info da seção
                            self.mapa_arquivos[secao_id] = {
                                'tipo': 'secao',
                                'caminho': caminho,
                                'conteudo': secao['texto'],
                                'titulo': secao['titulo']
                            }

                except Exception as e:
                    print(f"Erro ao analisar {arquivo}: {e}")

            self.label_status_vis.config(text=f"✅ {len(arquivos_encontrados)} arquivo(s) encontrado(s)")
        else:
            self.label_status_vis.config(text="⚠️ Nenhum arquivo .txt ou .srt encontrado")

    def detectar_secoes_arquivo(self, conteudo):
        """Detecta seções em um arquivo (BONUS se tiver estrutura)"""
        secoes = []
        linhas = conteudo.split('\n')

        # Padrões para identificar seções
        padroes = [
            r'^(?:ATO|ACT)\s+([IVX\d]+)',
            r'^(?:PARTE|PART)\s+([IVX\d]+)',
            r'^(?:CAPÍTULO|CAPITULO|CHAPTER|CAP\.?)\s+([IVX\d]+)',
            r'^(?:CENA|SCENE)\s+([IVX\d]+)',
            r'^(?:HOOK|ABERTURA|OPENING)',
            r'^(?:CONCLUS[ÃA]O|CLOSING|ENCERRAMENTO)',
            r'^(?:EPÍLOGO|EPILOGO|EPILOGUE)'
        ]

        secao_atual = None
        texto_secao = []
        linha_inicio = 0

        for i, linha in enumerate(linhas):
            linha_limpa = linha.strip()

            # Pula linhas vazias e decorativas
            if not linha_limpa or re.match(r'^[=\-▓━╔╗║╚═]{3,}$', linha_limpa):
                continue

            # Remove símbolos decorativos
            linha_para_analise = re.sub(r'\s*[▓▓▓━\-=]+\s*$', '', linha_limpa)

            # Verifica se é uma seção
            for padrao in padroes:
                if re.match(padrao, linha_para_analise, re.IGNORECASE):
                    # Salva seção anterior
                    if secao_atual:
                        secoes.append({
                            'titulo': secao_atual,
                            'texto': '\n'.join(texto_secao).strip()
                        })

                    # Inicia nova seção
                    secao_atual = linha_para_analise
                    texto_secao = [linha]
                    linha_inicio = i
                    break
            else:
                # Não é título de seção, adiciona ao texto
                if secao_atual:
                    texto_secao.append(linha)

        # Salva última seção
        if secao_atual:
            secoes.append({
                'titulo': secao_atual,
                'texto': '\n'.join(texto_secao).strip()
            })

        return secoes

    def arquivo_tree_selecionado(self, event=None):
        """Chamado quando clica em um arquivo ou seção na árvore"""
        selecao = self.tree_arquivos.selection()
        if not selecao:
            return

        item_id = selecao[0]
        if item_id not in self.mapa_arquivos:
            return

        info = self.mapa_arquivos[item_id]

        if info['tipo'] == 'arquivo':
            # Carrega e exibe o arquivo completo
            try:
                with open(info['caminho'], 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                self.text_visualizar.config(state=tk.NORMAL)
                self.text_visualizar.delete(1.0, tk.END)
                self.text_visualizar.insert(1.0, conteudo)
                self.text_visualizar.config(state=tk.DISABLED)

                # Atualiza labels
                self.label_arquivo_atual.config(text=f"📄 {info['nome']}")

                num_palavras = len(conteudo.split())
                num_linhas = len(conteudo.split('\n'))
                num_chars = len(conteudo)
                self.label_info_arquivo.config(
                    text=f"({num_palavras} palavras | {num_linhas} linhas | {num_chars} caracteres)"
                )

                self.label_status_vis.config(text=f"✅ Arquivo carregado: {info['nome']}")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
                self.label_status_vis.config(text=f"❌ Erro ao carregar arquivo")

        elif info['tipo'] == 'secao':
            # Exibe apenas a seção selecionada
            texto = info['conteudo']

            self.text_visualizar.config(state=tk.NORMAL)
            self.text_visualizar.delete(1.0, tk.END)
            self.text_visualizar.insert(1.0, texto)
            self.text_visualizar.config(state=tk.DISABLED)

            # Atualiza labels
            titulo_display = info['titulo'][:60]
            if len(info['titulo']) > 60:
                titulo_display += "..."

            self.label_arquivo_atual.config(text=f"📖 {titulo_display}")

            num_palavras = len(texto.split())
            num_linhas = len(texto.split('\n'))
            self.label_info_arquivo.config(
                text=f"({num_palavras} palavras | {num_linhas} linhas)"
            )

            self.label_status_vis.config(text=f"✅ Seção visualizada")

    def visualizar_arquivo_selecionado(self, event=None):
        """Visualiza o arquivo selecionado"""
        arquivo_nome = self.combo_arquivos.get()
        if not arquivo_nome or arquivo_nome not in self.arquivos_disponiveis:
            return

        caminho_arquivo = self.arquivos_disponiveis[arquivo_nome]
        self.arquivo_visualizacao_atual = caminho_arquivo

        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()

            self.conteudo_atual = conteudo

            # Analisa estrutura (partes, capítulos)
            self.analisar_estrutura(conteudo)

            # Exibe conteúdo completo
            self.text_visualizar.config(state=tk.NORMAL)
            self.text_visualizar.delete(1.0, tk.END)
            self.text_visualizar.insert(1.0, conteudo)
            self.text_visualizar.config(state=tk.DISABLED)

            # Atualiza labels
            self.label_arquivo_atual.config(text=f"📄 {arquivo_nome}")

            num_palavras = len(conteudo.split())
            num_linhas = len(conteudo.split('\n'))
            num_chars = len(conteudo)
            self.label_info_arquivo.config(
                text=f"({num_palavras} palavras | {num_linhas} linhas | {num_chars} caracteres)"
            )

            self.label_status_vis.config(text=f"✅ Arquivo carregado: {arquivo_nome}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
            self.label_status_vis.config(text=f"❌ Erro ao carregar arquivo")

    def analisar_estrutura(self, conteudo):
        """Analisa a estrutura do conteúdo e cria árvore de navegação (OPCIONAL - BONUS)"""
        # Limpa árvore
        for item in self.tree_estrutura.get_children():
            self.tree_estrutura.delete(item)

        # Remove colunas e configura
        self.tree_estrutura['columns'] = ()
        self.tree_estrutura.heading('#0', text='Estrutura do Documento')

        linhas = conteudo.split('\n')
        self.mapa_estrutura = {}  # {item_id: (inicio_linha, fim_linha, texto)}

        # SEMPRE adiciona "Documento Completo" primeiro - GARANTIDO
        item_completo = self.tree_estrutura.insert('', 'end', text="📄 Documento Completo")
        self.mapa_estrutura[item_completo] = (0, len(linhas) - 1, conteudo)

        # Padrões para identificar seções - BONUS se o arquivo tiver estrutura
        padroes = {
            'ato': r'^(?:ATO|ACT)\s+([IVX\d]+)',
            'parte': r'^(?:PARTE|PART)\s+([IVX\d]+)',
            'capitulo': r'^(?:CAPÍTULO|CAPITULO|CHAPTER|CAP\.?)\s+([IVX\d]+)',
            'cena': r'^(?:CENA|SCENE)\s+([IVX\d]+)',
            'hook': r'^(?:HOOK|ABERTURA|OPENING)',
            'conclusao': r'^(?:CONCLUS[ÃA]O|CLOSING|ENCERRAMENTO)',
            'epilogo': r'^(?:EPÍLOGO|EPILOGO|EPILOGUE)'
        }

        itens_raiz = []
        item_atual = None
        linha_inicio = 0

        # Tenta encontrar estrutura (BONUS)
        for i, linha in enumerate(linhas):
            linha_limpa = linha.strip()

            # Pula linhas vazias e linhas decorativas
            if not linha_limpa or re.match(r'^[=\-▓━╔╗║╚═]{3,}$', linha_limpa):
                continue

            # Remove símbolos decorativos do final da linha para análise
            linha_para_analise = re.sub(r'\s*[▓▓▓━\-=]+\s*$', '', linha_limpa)

            # Verifica cada padrão
            for tipo, padrao in padroes.items():
                match = re.match(padrao, linha_para_analise, re.IGNORECASE)
                if match:
                    # Adiciona item anterior se existir
                    if item_atual:
                        fim = i - 1
                        texto_secao = '\n'.join(linhas[linha_inicio:fim + 1])
                        self.mapa_estrutura[item_atual['id']] = (linha_inicio, fim, texto_secao)

                    # Cria novo item
                    titulo = linha_para_analise[:80]
                    if len(linha_para_analise) > 80:
                        titulo += "..."

                    # Determina o ícone baseado no tipo
                    icone = "📖"
                    if tipo == 'ato':
                        icone = "🎭"
                    elif tipo == 'hook':
                        icone = "🎬"
                    elif tipo == 'conclusao':
                        icone = "🏁"
                    elif tipo == 'parte':
                        icone = "📚"
                    elif tipo == 'capitulo':
                        icone = "📖"

                    item_id = self.tree_estrutura.insert('', 'end', text=f"{icone} {titulo}")
                    item_atual = {'id': item_id, 'tipo': tipo, 'titulo': linha_para_analise}
                    linha_inicio = i
                    itens_raiz.append(item_atual)
                    break

        # Adiciona último item se encontrou estrutura
        if item_atual:
            texto_secao = '\n'.join(linhas[linha_inicio:])
            self.mapa_estrutura[item_atual['id']] = (linha_inicio, len(linhas) - 1, texto_secao)

    def item_selecionado(self, event=None):
        """Quando um item da árvore é selecionado"""
        selecao = self.tree_estrutura.selection()
        if not selecao:
            return

        item_id = selecao[0]
        if item_id not in self.mapa_estrutura:
            return

        inicio, fim, texto = self.mapa_estrutura[item_id]

        # Exibe o texto da seção
        self.text_visualizar.config(state=tk.NORMAL)
        self.text_visualizar.delete(1.0, tk.END)
        self.text_visualizar.insert(1.0, texto)
        self.text_visualizar.config(state=tk.DISABLED)

        # Atualiza info
        num_palavras = len(texto.split())
        num_linhas = len(texto.split('\n'))
        self.label_info_arquivo.config(
            text=f"({num_palavras} palavras | {num_linhas} linhas | Linhas {inicio+1}-{fim+1})"
        )

        titulo_item = self.tree_estrutura.item(item_id)['text']
        self.label_arquivo_atual.config(text=f"📄 {titulo_item}")
        self.label_status_vis.config(text=f"✅ Seção visualizada")

    def copiar_conteudo_visualizado(self):
        """Copia o conteúdo atualmente visualizado"""
        texto = self.text_visualizar.get(1.0, tk.END).strip()
        if texto:
            try:
                # Usa APENAS o clipboard do tkinter (mais confiável no Windows)
                self.root.clipboard_clear()
                self.root.clipboard_append(texto)
                self.root.update()

                self.label_status_vis.config(text="✅ Conteúdo copiado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao copiar:\n{str(e)}")

    def recarregar_arquivo_atual(self):
        """Recarrega o arquivo atual"""
        if hasattr(self, 'arquivo_visualizacao_atual'):
            self.visualizar_arquivo_selecionado()

    def buscar_pasta_roteiros(self):
        """Lista os roteiros disponíveis na pasta raiz selecionada"""
        # Limpa a lista anterior
        self.roteiros_disponiveis = {}
        self.combo_roteiro_mestre.set("")
        self.combo_roteiro_mestre['values'] = []

        # Verifica se uma pasta foi selecionada
        if not self.pasta_raiz_selecionada:
            self.atualizar_status("⚠️ Nenhuma pasta selecionada. Clique no botão azul acima.")
            self.label_pasta_mestre.config(text="❌ Nenhuma pasta selecionada")
            return

        pasta_roteiros = self.pasta_raiz_selecionada

        if os.path.exists(pasta_roteiros):
            self.pasta_roteiros = pasta_roteiros
            self.label_pasta_mestre.config(text=f"📂 Pasta: {pasta_roteiros}")

            try:
                roteiros_com_status = []

                # PRIMEIRO: Verifica se há arquivos .txt DIRETAMENTE na pasta raiz
                arquivos_txt_raiz = [f for f in self.listar_arquivos_incluindo_ocultos(pasta_roteiros)
                                     if f.endswith(('.txt', '.srt')) and os.path.isfile(os.path.join(pasta_roteiros, f))]

                if arquivos_txt_raiz:
                    # Se há arquivos diretos, cria um "roteiro virtual" para esta pasta
                    nome_pasta = os.path.basename(pasta_roteiros)
                    nome_roteiro = f"📁 {nome_pasta} ({len(arquivos_txt_raiz)} arquivos)"
                    roteiros_com_status.append(nome_roteiro)
                    # Guarda a própria pasta como "roteiro"
                    self.roteiros_disponiveis[nome_roteiro] = pasta_roteiros

                # SEGUNDO: Procura por SUBPASTAS com arquivos .txt
                for item in self.listar_arquivos_incluindo_ocultos(pasta_roteiros):
                    caminho_item = os.path.join(pasta_roteiros, item)
                    if os.path.isdir(caminho_item):
                        # Procura por arquivos .txt ou .srt na subpasta
                        arquivo_texto = None
                        # Tenta formato novo primeiro (02_Texto_Narrado.txt)
                        arquivo_novo = os.path.join(caminho_item, "02_Texto_Narrado.txt")
                        if os.path.exists(arquivo_novo):
                            arquivo_texto = arquivo_novo
                        else:
                            # Tenta formato antigo (03_Texto_Narrado.txt)
                            arquivo_antigo = os.path.join(caminho_item, "03_Texto_Narrado.txt")
                            if os.path.exists(arquivo_antigo):
                                arquivo_texto = arquivo_antigo
                            else:
                                # Se não encontrou nenhum dos dois, procura qualquer .txt ou .srt
                                arquivos_txt = [f for f in self.listar_arquivos_incluindo_ocultos(caminho_item)
                                              if f.endswith(('.txt', '.srt'))]
                                if arquivos_txt:
                                    arquivo_texto = os.path.join(caminho_item, arquivos_txt[0])

                        if arquivo_texto:
                            # Formata o nome do roteiro
                            nome_roteiro = item.replace("_", " ").title()

                            # Verifica o status do vídeo
                            arquivo_status = os.path.join(caminho_item, "video_status.json")
                            indicador = "⚪ "  # Padrão: novo/pendente

                            if os.path.exists(arquivo_status):
                                try:
                                    with open(arquivo_status, 'r', encoding='utf-8') as f:
                                        status = json.load(f)
                                        video_postado = status.get("video_postado", False)

                                        if video_postado:
                                            indicador = "✅ "  # Postado
                                except:
                                    pass  # Mantém indicador padrão em caso de erro

                            nome_com_status = f"{indicador}{nome_roteiro}"
                            roteiros_com_status.append(nome_com_status)
                            self.roteiros_disponiveis[nome_roteiro] = arquivo_texto

                if roteiros_com_status:
                    # Atualiza o combobox mestre
                    nomes_ordenados = sorted(roteiros_com_status)
                    self.combo_roteiro_mestre['values'] = nomes_ordenados

                    self.atualizar_status(f"✅ {len(nomes_ordenados)} roteiro(s) encontrado(s)")
                else:
                    self.atualizar_status("⚠️ Nenhum arquivo .txt ou .srt encontrado")
                    self.label_pasta_mestre.config(text=f"⚠️ Pasta sem arquivos: {pasta_roteiros}")

            except Exception as e:
                self.atualizar_status(f"❌ Erro ao listar roteiros: {str(e)}")
        else:
            self.pasta_roteiros = ""
            self.label_pasta_mestre.config(text="❌ Pasta não encontrada!")
            self.atualizar_status("❌ Pasta não encontrada")


    def carregar_arquivo(self, caminho):
        """Carrega e processa o arquivo selecionado"""
        try:
            with open(caminho, 'r', encoding='utf-8') as file:
                self.texto_completo = file.read()

            self.arquivo_atual = caminho

            # Processa o texto e identifica seções
            self.identificar_secoes()

            # Carrega o histórico ANTES de criar os botões
            self.carregar_historico()

            # Cria botões para cada seção (agora com histórico carregado)
            self.criar_botoes_secoes()

            # Limpa a área de texto
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, "👈 Selecione uma seção ao lado para visualizar")
            self.text_area.config(state=tk.DISABLED)

            self.atualizar_status(f"✅ Roteiro carregado: {len(self.secoes)} seção(ões) identificada(s)")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
            self.atualizar_status(f"❌ Erro: {str(e)}")

    def identificar_secoes(self):
        """Identifica as seções no texto usando marcadores padrão"""
        self.secoes = {}

        # Padrões para identificar seções
        padroes = [
            r'^OPENING\s*[-–—]\s*(.+)$',
            r'^CHAPTER\s+(\w+)\s*[-–—]\s*(.+)$',
            r'^ACT\s+(\w+)\s*[-–—]\s*(.+)$',
            r'^ATO\s+(\w+)\s*[-–—]\s*(.+)$',
            r'^CLOSING\s*[-–—]\s*(.+)$',
            r'^EPILOGUE\s*[-–—]\s*(.+)$',
            r'^CONCLUSION\s*[-–—]\s*(.+)$'
        ]

        linhas = self.texto_completo.split('\n')
        secao_atual = None
        texto_secao = []
        indice_secao = 0
        inicio_atual = 0

        # Primeira passada - identificar títulos de seções
        for i, linha in enumerate(linhas):
            linha_limpa = linha.strip()

            # Verifica se é um título de seção
            secao_encontrada = False
            for padrao in padroes:
                match = re.match(padrao, linha_limpa, re.IGNORECASE)
                if match:
                    # Se já havia uma seção sendo processada, salva ela
                    if secao_atual and texto_secao:
                        self.secoes[indice_secao] = {
                            'titulo': secao_atual,
                            'texto': '\n'.join(texto_secao).strip(),
                            'linha_inicio': inicio_atual
                        }
                        indice_secao += 1

                    # Inicia nova seção
                    secao_atual = linha_limpa
                    texto_secao = [linha]
                    inicio_atual = i
                    secao_encontrada = True
                    break

            # Se não é um título de seção, adiciona ao texto da seção atual
            if not secao_encontrada and secao_atual:
                texto_secao.append(linha)

        # Salva a última seção
        if secao_atual and texto_secao:
            self.secoes[indice_secao] = {
                'titulo': secao_atual,
                'texto': '\n'.join(texto_secao).strip(),
                'linha_inicio': inicio_atual
            }

        # Se não encontrou seções com os padrões, divide por blocos vazios
        if not self.secoes:
            self.dividir_por_blocos()

    def dividir_por_blocos(self):
        """Divide o texto em blocos quando não há marcadores claros"""
        blocos = self.texto_completo.split('\n\n\n')

        for i, bloco in enumerate(blocos):
            if bloco.strip():
                # Pega as primeiras palavras como título
                primeiras_palavras = ' '.join(bloco.strip().split()[:5])
                if len(primeiras_palavras) > 50:
                    primeiras_palavras = primeiras_palavras[:50] + "..."

                self.secoes[i] = {
                    'titulo': f"Bloco {i+1}: {primeiras_palavras}",
                    'texto': bloco.strip(),
                    'linha_inicio': 0
                }

    def criar_botoes_secoes(self):
        """Cria botões para cada seção identificada"""
        # Limpa botões anteriores
        for widget in self.frame_botoes.winfo_children():
            widget.destroy()

        if not self.secoes:
            # Mostra mensagem se não há seções
            tk.Label(
                self.frame_botoes,
                text="⚠️ Nenhuma seção\nidentificada no texto",
                bg=self.bg_color,
                fg="#888888",
                font=("Arial", 10),
                justify=tk.CENTER
            ).pack(pady=50)
            return

        # Cria novo botão para cada seção
        for indice in sorted(self.secoes.keys()):
            secao = self.secoes[indice]

            # Conta palavras
            num_palavras = len(secao['texto'].split())

            # Cria frame para o botão
            frame_btn = tk.Frame(self.frame_botoes, bg=self.bg_color)
            frame_btn.pack(fill=tk.X, pady=3, padx=5)

            # Prepara o título do botão - agora sem cortar
            titulo_btn = secao['titulo'][:60]
            if len(secao['titulo']) > 60:
                titulo_btn += "..."

            # Verifica se foi copiado
            roteiro_nome = self.roteiro_atual if self.roteiro_atual else ""
            foi_copiado = self.secao_foi_copiada(roteiro_nome, secao['titulo'])
            info_copia = self.get_info_copia(roteiro_nome, secao['titulo'])

            # Define ícone e cor baseado no status
            if foi_copiado:
                icone = "✓"
                cor_btn = self.green_copied  # Verde bem clarinho para copiado
                cor_fg = self.fg_color  # Texto preto
            else:
                icone = "📄"
                cor_btn = self.button_bg
                cor_fg = self.fg_color

            # Botão principal compacto
            btn = tk.Button(
                frame_btn,
                text=f"{icone} {titulo_btn}",
                command=lambda idx=indice: self.exibir_secao(idx),
                bg=cor_btn,
                fg=cor_fg,
                font=(self.font_family, 9, "bold" if foi_copiado else "normal"),
                relief=tk.FLAT,
                anchor="w",
                padx=10,
                pady=6,
                cursor="hand2",
                wraplength=340,  # Quebra texto em múltiplas linhas
                justify=tk.LEFT,
                borderwidth=0
            )
            btn.pack(fill=tk.X, side=tk.TOP)

            # Tooltip com título completo e informações de cópia
            tooltip_text = secao['titulo']
            if info_copia:
                tooltip_text += f"\n\n✓ Copiado {info_copia['contador']}x"
                tooltip_text += f"\nÚltima cópia: {info_copia['ultima_copia']}"

            self.criar_tooltip(btn, tooltip_text)

            # Label com contagem de palavras e status
            status_text = f"   {num_palavras} palavras"
            if info_copia:
                status_text += f" • Copiado {info_copia['contador']}x"

            tk.Label(
                frame_btn,
                text=status_text,
                bg=self.bg_color,
                fg="#4CAF50" if foi_copiado else "#888888",
                font=("Arial", 8, "bold" if foi_copiado else "normal")
            ).pack(anchor="w", padx=5)

            # Efeitos hover (mantém cor original se copiado)
            hover_color = self.green_hover if foi_copiado else self.button_hover
            normal_color = cor_btn

            btn.bind("<Enter>", lambda e, b=btn, hc=hover_color: b.config(bg=hc))
            btn.bind("<Leave>", lambda e, b=btn, nc=normal_color: b.config(bg=nc))

    def criar_tooltip(self, widget, text):
        """Cria tooltip ao passar o mouse"""
        def on_enter(event):
            # Cria tooltip
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                background="#333333",
                foreground="white",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Arial", 9),
                padx=10,
                pady=5,
                wraplength=400
            )
            label.pack()

            widget._tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")

    def exibir_secao(self, indice):
        """Exibe o texto da seção selecionada"""
        secao = self.secoes[indice]

        # Atualiza área de texto
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, secao['texto'])

        # Atualiza labels
        titulo_display = secao['titulo'][:60]
        if len(secao['titulo']) > 60:
            titulo_display += "..."
        self.label_secao_atual.config(text=f"📝 {titulo_display}")

        num_palavras = len(secao['texto'].split())
        num_caracteres = len(secao['texto'])
        self.label_palavras.config(text=f"({num_palavras} palavras | {num_caracteres} caracteres)")

        # Habilita botão de copiar
        self.btn_copiar.config(state=tk.NORMAL)

        # Guarda índice da seção atual
        self.secao_atual_indice = indice

        self.atualizar_status(f"✅ Seção carregada: {secao['titulo'][:40]}...")

    def copiar_texto_atual(self):
        """Copia o texto exibido para a área de transferência"""
        texto = self.text_area.get(1.0, tk.END).strip()
        if texto and hasattr(self, 'secao_atual_indice'):
            try:
                # Usa APENAS o clipboard do tkinter (mais confiável no Windows)
                self.root.clipboard_clear()
                self.root.clipboard_append(texto)
                self.root.update()

                # Registra no histórico
                roteiro_nome = self.roteiro_atual if self.roteiro_atual else ""
                secao = self.secoes[self.secao_atual_indice]
                self.registrar_copia(roteiro_nome, secao['titulo'])

                # Atualiza os botões para mostrar o indicador
                self.criar_botoes_secoes()

                # Mostra quantas vezes foi copiado
                info = self.get_info_copia(roteiro_nome, secao['titulo'])
                contador = info['contador'] if info else 1

                self.atualizar_status(f"Texto copiado! (Copiado {contador}x)")

                # Efeito visual no botão
                self.btn_copiar.config(bg="#45a049", text="✓ COPIADO!")
                self.root.after(2000, lambda: self.btn_copiar.config(bg=self.accent_color, text="📋 Copiar"))

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao copiar:\n{str(e)}")

    def salvar_secao(self):
        """Salva a seção atual em um arquivo separado"""
        if not hasattr(self, 'secao_atual_indice'):
            messagebox.showwarning("Aviso", "Selecione uma seção primeiro!")
            return

        secao = self.secoes[self.secao_atual_indice]

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialfile=f"{secao['titulo'][:30].replace(':', '').replace('/', '')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(secao['texto'])
                self.atualizar_status(f"✅ Seção salva em: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")

    def obter_arquivo_historico(self):
        """Retorna o caminho do arquivo de histórico na pasta raiz do projeto"""
        # Salva na pasta RAIZ do projeto (não na pasta do roteiro individual)
        # Isso evita problemas de permissão
        if self.pasta_raiz_selecionada and os.path.exists(self.pasta_raiz_selecionada):
            # IMPORTANTE: Normaliza o caminho para evitar barras mistas
            pasta_normalizada = os.path.normpath(self.pasta_raiz_selecionada)
            arquivo = os.path.join(pasta_normalizada, "historico.json")
            return os.path.normpath(arquivo)  # Normaliza o caminho completo
        return None

    def carregar_historico(self):
        """Carrega o histórico de cópias do arquivo JSON local"""
        arquivo = self.obter_arquivo_historico()
        print(f"\n=== DEBUG CARREGAR ===")
        print(f"Arquivo histórico: {arquivo}")
        print(f"Pasta raiz: {self.pasta_raiz_selecionada}")

        if not arquivo:
            print("AVISO: Arquivo é None!")
            self.historico_copias = {}
            return

        try:
            if os.path.exists(arquivo):
                print(f"Arquivo EXISTE! Carregando...")
                with open(arquivo, 'r', encoding='utf-8') as f:
                    self.historico_copias = json.load(f)
                print(f"Histórico CARREGADO: {len(self.historico_copias)} roteiros")
                print(f"Conteúdo: {self.historico_copias}")
            else:
                print(f"Arquivo NÃO EXISTE ainda")
                self.historico_copias = {}
        except Exception as e:
            print(f"ERRO ao carregar histórico: {e}")
            self.historico_copias = {}

    def salvar_historico(self):
        """Salva o histórico de cópias no arquivo JSON local"""
        arquivo = self.obter_arquivo_historico()
        print(f"\n=== DEBUG SALVAR ===")
        print(f"Arquivo: {arquivo}")
        print(f"Histórico tem {len(self.historico_copias)} roteiros")

        if not arquivo:
            print("ERRO: Arquivo é None - não pode salvar!")
            return

        try:
            # Garante que o diretório existe
            pasta_historico = os.path.dirname(arquivo)
            print(f"Pasta destino: {pasta_historico}")

            if not os.path.exists(pasta_historico):
                print(f"Pasta não existe, criando...")
                os.makedirs(pasta_historico, exist_ok=True)

            # Salva o histórico
            print(f"Salvando histórico com {len(self.historico_copias)} roteiros...")
            print(f"Conteúdo a salvar: {self.historico_copias}")

            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.historico_copias, f, indent=2, ensure_ascii=False)

            print(f"✅ Arquivo SALVO com sucesso!")

            # Verifica se foi salvo mesmo
            if os.path.exists(arquivo):
                tamanho = os.path.getsize(arquivo)
                print(f"✅ Arquivo confirmado: {tamanho} bytes")
            else:
                print(f"❌ ERRO: Arquivo não existe após salvar!")

        except PermissionError as e:
            print(f"❌ ERRO DE PERMISSÃO: {e}")
        except Exception as e:
            print(f"❌ ERRO AO SALVAR: {e}")
            import traceback
            traceback.print_exc()

    def registrar_copia(self, roteiro_nome, secao_titulo):
        """Registra uma cópia no histórico"""
        print(f"\n=== DEBUG REGISTRAR CÓPIA ===")
        print(f"Roteiro: {roteiro_nome}")
        print(f"Seção: {secao_titulo}")

        if roteiro_nome not in self.historico_copias:
            print(f"Primeira vez que copia deste roteiro")
            self.historico_copias[roteiro_nome] = {}

        agora = datetime.now()

        if secao_titulo in self.historico_copias[roteiro_nome]:
            # Incrementa contador
            contador_anterior = self.historico_copias[roteiro_nome][secao_titulo]['contador']
            self.historico_copias[roteiro_nome][secao_titulo]['contador'] += 1
            self.historico_copias[roteiro_nome][secao_titulo]['ultima_copia'] = agora.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Incrementado de {contador_anterior} para {self.historico_copias[roteiro_nome][secao_titulo]['contador']}")
        else:
            # Primeira cópia
            self.historico_copias[roteiro_nome][secao_titulo] = {
                'primeira_copia': agora.strftime("%Y-%m-%d %H:%M:%S"),
                'ultima_copia': agora.strftime("%Y-%m-%d %H:%M:%S"),
                'contador': 1
            }
            print(f"Primeira cópia desta seção!")

        print(f"Total de seções neste roteiro: {len(self.historico_copias[roteiro_nome])}")

        # Marca que há mudanças não salvas
        self.historico_modificado = True

        self.salvar_historico()

    def secao_foi_copiada(self, roteiro_nome, secao_titulo):
        """Verifica se uma seção já foi copiada"""
        if roteiro_nome in self.historico_copias:
            return secao_titulo in self.historico_copias[roteiro_nome]
        return False

    def get_info_copia(self, roteiro_nome, secao_titulo):
        """Retorna informações sobre as cópias de uma seção"""
        if self.secao_foi_copiada(roteiro_nome, secao_titulo):
            return self.historico_copias[roteiro_nome][secao_titulo]
        return None

    def limpar_historico_roteiro_atual(self):
        """Limpa o histórico do roteiro atual"""
        roteiro_nome = self.roteiro_atual
        if roteiro_nome and roteiro_nome in self.historico_copias:
            resultado = messagebox.askyesno(
                "Limpar Memória",
                f"Deseja limpar o histórico de cópias do roteiro '{roteiro_nome}'?\n\n"
                f"Todas as marcações de seções copiadas serão removidas."
            )
            if resultado:
                del self.historico_copias[roteiro_nome]
                self.salvar_historico()
                # Recarrega os botões para atualizar indicadores
                self.criar_botoes_secoes()
                self.atualizar_status("✅ Histórico limpo com sucesso!")

    def limpar_historico_completo(self):
        """Limpa todo o histórico de cópias"""
        resultado = messagebox.askyesno(
            "Limpar Toda Memória",
            "Deseja limpar o histórico de TODOS os roteiros?\n\n"
            "Esta ação não pode ser desfeita!"
        )
        if resultado:
            self.historico_copias = {}
            self.salvar_historico()
            # Recarrega os botões para atualizar indicadores
            self.criar_botoes_secoes()
            self.atualizar_status("✅ Todo histórico foi limpo!")

    def atualizar_status(self, mensagem):
        """Atualiza a barra de status"""
        self.label_status.config(text=mensagem)

        # Define cor baseada no tipo de mensagem
        if "✅" in mensagem:
            self.label_status.config(fg="#4CAF50")  # Verde
        elif "❌" in mensagem:
            self.label_status.config(fg="#FF6B6B")  # Vermelho
        elif "⚠️" in mensagem:
            self.label_status.config(fg="#FFA500")  # Laranja
        else:
            self.label_status.config(fg=self.accent_color)  # Laranja terracota

    def criar_aba_titulo(self):
        """Cria a interface da aba de título e descrição"""
        # Frame superior fixo com status
        frame_topo = tk.Frame(self.aba_titulo, bg=self.bg_color)
        frame_topo.pack(fill=tk.X, padx=15, pady=10)

        # Título da seção
        tk.Label(
            frame_topo,
            text="🎬 INFORMAÇÕES DO VÍDEO",
            bg=self.bg_color,
            fg=self.accent_color,
            font=(self.font_family, 12, "bold")
        ).pack(side=tk.LEFT)

        # Frame direita com checkbox e botão
        frame_direita = tk.Frame(frame_topo, bg=self.bg_color)
        frame_direita.pack(side=tk.RIGHT)

        # Checkbox de vídeo postado
        self.var_postado = tk.BooleanVar()
        self.check_postado = tk.Checkbutton(
            frame_direita,
            text="✅ Vídeo Postado",
            variable=self.var_postado,
            bg=self.bg_color,
            fg=self.fg_color,
            font=(self.font_family, 9, "bold"),
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.check_postado.pack(side=tk.LEFT, padx=(0, 10))

        # Botão Salvar Tudo ao lado
        btn_salvar_tudo = tk.Button(
            frame_direita,
            text="💾 Salvar",
            command=self.salvar_info_video,
            bg=self.accent_color,
            fg="#ffffff",
            font=(self.font_family, 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            borderwidth=0,
            activeforeground="#ffffff"
        )
        btn_salvar_tudo.pack(side=tk.LEFT)
        btn_salvar_tudo.bind("<Enter>", lambda e: btn_salvar_tudo.config(bg=self.accent_hover))
        btn_salvar_tudo.bind("<Leave>", lambda e: btn_salvar_tudo.config(bg=self.accent_color))

        # Linha separadora
        tk.Frame(self.aba_titulo, bg=self.border_color, height=1).pack(fill=tk.X, padx=15)

        # Container com scroll
        canvas = tk.Canvas(self.aba_titulo, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.aba_titulo, orient="vertical", command=canvas.yview)
        frame_conteudo = tk.Frame(canvas, bg=self.bg_color)

        frame_conteudo.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=frame_conteudo, anchor="nw", width=1150)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Atualiza a largura do frame quando o canvas muda de tamanho
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width - 10)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y")

        # Habilita scroll com a roda do mouse no canvas principal
        def scroll_canvas_titulo(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        # Bind do scroll no canvas e no frame de conteúdo
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", scroll_canvas_titulo))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        frame_conteudo.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", scroll_canvas_titulo))
        frame_conteudo.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Seção: TÍTULOS SUGERIDOS
        tk.Label(
            frame_conteudo,
            text="📝 TÍTULOS SUGERIDOS (Curiosidade + Sensacional + Pergunta):",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        # Criar 5 campos de título
        self.campos_titulo = []
        for i in range(1, 6):
            frame_titulo = tk.Frame(frame_conteudo, bg=self.bg_color)
            frame_titulo.pack(fill=tk.X, pady=5)

            tk.Label(
                frame_titulo,
                text=f"Opção {i}:",
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10, "bold"),
                width=10,
                anchor="w"
            ).pack(side=tk.LEFT)

            entry_titulo = tk.Entry(
                frame_titulo,
                font=(self.font_family, 10),
                bg=self.bg_secondary,
                fg=self.fg_color,
                insertbackground=self.fg_color,
                relief=tk.FLAT,
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=self.border_color,
                highlightcolor=self.accent_color
            )
            entry_titulo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

            btn_copiar_tit = tk.Button(
                frame_titulo,
                text="📋",
                command=lambda idx=i-1: self.copiar_titulo(idx),
                bg=self.button_bg,
                fg=self.fg_color,
                font=(self.font_family, 9),
                relief=tk.FLAT,
                padx=8,
                pady=4,
                cursor="hand2",
                borderwidth=0
            )
            btn_copiar_tit.pack(side=tk.LEFT)
            btn_copiar_tit.bind("<Enter>", lambda e, b=btn_copiar_tit: b.config(bg=self.button_hover))
            btn_copiar_tit.bind("<Leave>", lambda e, b=btn_copiar_tit: b.config(bg=self.button_bg))

            self.campos_titulo.append(entry_titulo)

        # Seção: DESCRIÇÃO
        tk.Label(
            frame_conteudo,
            text="📄 DESCRIÇÃO PARA YOUTUBE (com gancho):",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(20, 10))

        frame_descricao = tk.Frame(frame_conteudo, bg=self.bg_color)
        frame_descricao.pack(fill=tk.BOTH, expand=True)

        self.text_descricao = scrolledtext.ScrolledText(
            frame_descricao,
            wrap=tk.WORD,
            font=(self.font_mono, 10),
            bg=self.bg_secondary,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.button_hover,
            relief=tk.FLAT,
            height=15,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.text_descricao.pack(fill=tk.BOTH, expand=True)

        # Habilita scroll com mouse na descrição - tem prioridade sobre o canvas
        def scroll_desc(event):
            self.text_descricao.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        def on_desc_enter(e):
            canvas.unbind_all("<MouseWheel>")
            self.text_descricao.bind("<MouseWheel>", scroll_desc)

        def on_desc_leave(e):
            self.text_descricao.unbind("<MouseWheel>")
            canvas.bind_all("<MouseWheel>", scroll_canvas_titulo)

        self.text_descricao.bind("<Enter>", on_desc_enter)
        self.text_descricao.bind("<Leave>", on_desc_leave)

        frame_btn_desc = tk.Frame(frame_conteudo, bg=self.bg_color)
        frame_btn_desc.pack(fill=tk.X, pady=5)

        btn_copiar_desc = tk.Button(
            frame_btn_desc,
            text="📋 Copiar",
            command=self.copiar_descricao,
            bg=self.button_bg,
            fg=self.fg_color,
            font=(self.font_family, 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            borderwidth=0
        )
        btn_copiar_desc.pack(side=tk.RIGHT)
        btn_copiar_desc.bind("<Enter>", lambda e: btn_copiar_desc.config(bg=self.button_hover))
        btn_copiar_desc.bind("<Leave>", lambda e: btn_copiar_desc.config(bg=self.button_bg))

        # Seção: IDEIA PARA THUMBNAIL
        tk.Label(
            frame_conteudo,
            text="🎨 IDEIA PARA THUMBNAIL:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(20, 10))

        self.text_thumbnail = scrolledtext.ScrolledText(
            frame_conteudo,
            wrap=tk.WORD,
            font=(self.font_mono, 10),
            bg=self.bg_secondary,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.button_hover,
            relief=tk.FLAT,
            height=5,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.text_thumbnail.pack(fill=tk.X)

        # Habilita scroll com mouse na thumbnail - tem prioridade sobre o canvas
        def scroll_thumb(event):
            self.text_thumbnail.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        def on_thumb_enter(e):
            canvas.unbind_all("<MouseWheel>")
            self.text_thumbnail.bind("<MouseWheel>", scroll_thumb)

        def on_thumb_leave(e):
            self.text_thumbnail.unbind("<MouseWheel>")
            canvas.bind_all("<MouseWheel>", scroll_canvas_titulo)

        self.text_thumbnail.bind("<Enter>", on_thumb_enter)
        self.text_thumbnail.bind("<Leave>", on_thumb_leave)

    def ao_selecionar_roteiro_mestre(self, event=None):
        """Chamado quando seleciona um roteiro no dropdown mestre"""
        roteiro_nome = self.combo_roteiro_mestre.get()
        if not roteiro_nome:
            return

        # Remove indicadores de status do nome para comparação
        roteiro_limpo = roteiro_nome.replace("⚪ ", "").replace("🎬 ", "").replace("✅ ", "")
        self.roteiro_atual = roteiro_limpo

        # Encontra a pasta do roteiro
        if not self.pasta_roteiros:
            return

        self.pasta_roteiro_atual = ""

        # Verifica se é o "roteiro virtual" da própria pasta raiz (quando há arquivos diretos)
        if roteiro_limpo in self.roteiros_disponiveis:
            caminho_associado = self.roteiros_disponiveis[roteiro_limpo]
            # Se o caminho é uma PASTA (não um arquivo específico)
            if os.path.isdir(caminho_associado):
                self.pasta_roteiro_atual = caminho_associado
            else:
                # É um arquivo específico, pega a pasta dele
                self.pasta_roteiro_atual = os.path.dirname(caminho_associado)
        else:
            # Procura por subpasta com nome correspondente
            for item in self.listar_arquivos_incluindo_ocultos(self.pasta_roteiros):
                item_formatado = item.replace("_", " ").title()
                if item_formatado == roteiro_limpo:
                    self.pasta_roteiro_atual = os.path.join(self.pasta_roteiros, item)
                    break

        if not self.pasta_roteiro_atual or not os.path.exists(self.pasta_roteiro_atual):
            return

        # Atualiza label de pasta
        self.label_pasta_mestre.config(text=f"📂 {self.pasta_roteiro_atual}")

        # Atualizar Aba 1: Copiar Seções (apenas se houver arquivo de texto narrado)
        arquivo_texto_narrado = None
        arquivo_novo = os.path.join(self.pasta_roteiro_atual, "02_Texto_Narrado.txt")
        if os.path.exists(arquivo_novo):
            arquivo_texto_narrado = arquivo_novo
        else:
            arquivo_antigo = os.path.join(self.pasta_roteiro_atual, "03_Texto_Narrado.txt")
            if os.path.exists(arquivo_antigo):
                arquivo_texto_narrado = arquivo_antigo

        if arquivo_texto_narrado:
            self.carregar_arquivo(arquivo_texto_narrado)
        else:
            # Se não tem arquivo específico de texto narrado, limpa a aba
            try:
                for widget in self.frame_botoes.winfo_children():
                    widget.destroy()
                # Recria o label se necessário
                if hasattr(self, 'label_sem_secoes') and self.label_sem_secoes.winfo_exists():
                    self.label_sem_secoes.pack(pady=50)
                else:
                    # Recria o label
                    self.label_sem_secoes = tk.Label(
                        self.frame_botoes,
                        text="👈 Selecione um roteiro\npara visualizar as seções",
                        bg=self.bg_color,
                        fg="#888888",
                        font=("Arial", 10),
                        justify=tk.CENTER
                    )
                    self.label_sem_secoes.pack(pady=50)
            except Exception as e:
                pass  # Silencioso em produção

        # Atualizar Aba 2: Visualizar Arquivos (SEMPRE)
        self.carregar_arquivos_roteiro()

        # Atualizar Aba 3: Título e Descrição
        self.carregar_info_video()

    def abrir_pasta_roteiro(self):
        """Abre a pasta do roteiro atual no explorador"""
        if self.pasta_roteiro_atual and os.path.exists(self.pasta_roteiro_atual):
            if platform.system() == "Windows":
                os.startfile(self.pasta_roteiro_atual)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.pasta_roteiro_atual])
            else:  # Linux
                subprocess.run(["xdg-open", self.pasta_roteiro_atual])
        else:
            messagebox.showwarning("Aviso", "Nenhum roteiro selecionado ou pasta não existe!")

    def copiar_titulo(self, indice):
        """Copia um título específico"""
        if indice < len(self.campos_titulo):
            titulo = self.campos_titulo[indice].get()
            if titulo:
                try:
                    pyperclip.copy(titulo)
                    messagebox.showinfo("Sucesso", f"Título {indice + 1} copiado!")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao copiar: {str(e)}")

    def copiar_descricao(self):
        """Copia a descrição"""
        descricao = self.text_descricao.get(1.0, tk.END).strip()
        if descricao:
            try:
                pyperclip.copy(descricao)
                messagebox.showinfo("Sucesso", "Descrição copiada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao copiar: {str(e)}")

    def carregar_info_video(self):
        """Carrega informações do vídeo do arquivo"""
        if not self.pasta_roteiro_atual:
            return

        # Limpar campos primeiro
        for campo in self.campos_titulo:
            campo.delete(0, tk.END)
        self.text_descricao.delete(1.0, tk.END)
        self.text_thumbnail.delete(1.0, tk.END)
        self.var_postado.set(False)

        # Carregar do arquivo 05_Titulo_Descricao.txt
        arquivo_info = os.path.join(self.pasta_roteiro_atual, "05_Titulo_Descricao.txt")
        if os.path.exists(arquivo_info):
            try:
                with open(arquivo_info, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                # Parse do conteúdo
                titulos = []
                descricao = ""
                thumbnail = ""

                # Extrair títulos
                for i in range(1, 6):
                    padrao = rf"OPÇÃO {i}:(.*?)(?=OPÇÃO {i+1}:|━|$)"
                    match = re.search(padrao, conteudo, re.DOTALL)
                    if match:
                        titulo = match.group(1).strip()
                        titulos.append(titulo)

                # Extrair descrição
                match_desc = re.search(r"DESCRIÇÃO PARA YOUTUBE:(.*?)(?=━|IDEIA PARA THUMBNAIL:|$)", conteudo, re.DOTALL)
                if match_desc:
                    descricao = match_desc.group(1).strip()

                # Extrair thumbnail
                match_thumb = re.search(r"IDEIA PARA THUMBNAIL:(.*?)(?=$)", conteudo, re.DOTALL)
                if match_thumb:
                    thumbnail = match_thumb.group(1).strip()

                # Preencher campos
                for i, titulo in enumerate(titulos):
                    if i < len(self.campos_titulo):
                        self.campos_titulo[i].insert(0, titulo)

                if descricao:
                    self.text_descricao.insert(1.0, descricao)

                if thumbnail:
                    self.text_thumbnail.insert(1.0, thumbnail)

            except Exception as e:
                print(f"Erro ao carregar informações: {e}")

        # Carregar status do JSON
        arquivo_status = os.path.join(self.pasta_roteiro_atual, "video_status.json")
        if os.path.exists(arquivo_status):
            try:
                with open(arquivo_status, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    self.var_postado.set(status.get("video_postado", False))
            except Exception as e:
                print(f"Erro ao carregar status: {e}")

    def salvar_info_video(self, mostrar_mensagem=True):
        """Salva informações do vídeo no arquivo"""
        if not self.pasta_roteiro_atual:
            if mostrar_mensagem:
                messagebox.showwarning("Aviso", "Nenhum roteiro selecionado!")
            return

        try:
            # Coletar dados
            titulos = [campo.get() for campo in self.campos_titulo]
            descricao = self.text_descricao.get(1.0, tk.END).strip()
            thumbnail = self.text_thumbnail.get(1.0, tk.END).strip()

            # Criar conteúdo do arquivo
            conteudo = []
            for i, titulo in enumerate(titulos, 1):
                conteudo.append(f"OPÇÃO {i}:")
                conteudo.append(titulo if titulo else "[Título não preenchido]")
                conteudo.append("")

            conteudo.append("━" * 60)
            conteudo.append("")
            conteudo.append("DESCRIÇÃO PARA YOUTUBE:")
            conteudo.append("")
            conteudo.append(descricao if descricao else "[Descrição não preenchida]")
            conteudo.append("")
            conteudo.append("━" * 60)
            conteudo.append("")
            conteudo.append("IDEIA PARA THUMBNAIL:")
            conteudo.append("")
            conteudo.append(thumbnail if thumbnail else "[Ideia não preenchida]")

            # Salvar arquivo de texto
            arquivo_info = os.path.join(self.pasta_roteiro_atual, "05_Titulo_Descricao.txt")
            with open(arquivo_info, 'w', encoding='utf-8') as f:
                f.write('\n'.join(conteudo))

            # Salvar status JSON com timestamp
            arquivo_status = os.path.join(self.pasta_roteiro_atual, "video_status.json")
            agora = datetime.now()
            status = {
                "video_postado": self.var_postado.get(),
                "data_salvamento": agora.strftime("%Y-%m-%d %H:%M:%S")
            }

            # Se marcou como postado, registra a data
            if self.var_postado.get():
                status["data_postagem"] = agora.strftime("%Y-%m-%d %H:%M:%S")

            with open(arquivo_status, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)

            if mostrar_mensagem:
                messagebox.showinfo("Sucesso", f"Informações salvas!\nData: {agora.strftime('%d/%m/%Y às %H:%M')}")

            # Atualizar lista de roteiros para mostrar indicadores
            self.buscar_pasta_roteiros()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

def main():
    root = tk.Tk()
    app = ScriptCopier(root)
    root.mainloop()

if __name__ == "__main__":
    main()
