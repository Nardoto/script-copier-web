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
        self.root.title("Script Copier - Copiador de Roteiros")
        self.root.geometry("1200x700")

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
        self.roteiros_disponiveis = {}
        self.roteiro_atual = None
        self.pasta_roteiro_atual = ""
        self.historico_copias = {}

        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(__file__)

        self.arquivo_historico = os.path.join(app_dir, "historico_copias.json")

        self.carregar_historico()
        self.configurar_estilo()
        self.criar_interface()

        self.mostrar_tela_inicial()

    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')

        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.button_bg = "#4a4a4a"
        self.button_hover = "#5a5a5a"
        self.select_bg = "#3a3a3a"
        self.accent_color = "#4CAF50"

        self.root.configure(bg=self.bg_color)

    def criar_interface(self):
        frame_mestre = tk.Frame(self.root, bg=self.bg_color, pady=15)
        frame_mestre.pack(fill=tk.X, padx=15)

        tk.Label(
            frame_mestre,
            text="📚 SCRIPT COPIER",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(0, 10))

        frame_selecao_mestre = tk.Frame(frame_mestre, bg=self.bg_color)
        frame_selecao_mestre.pack(fill=tk.X)

        tk.Label(
            frame_selecao_mestre,
            text="Selecione o Roteiro:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.combo_roteiro_mestre = ttk.Combobox(
            frame_selecao_mestre,
            state="readonly",
            font=("Arial", 10),
            width=50
        )
        self.combo_roteiro_mestre.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_roteiro_mestre.bind("<<ComboboxSelected>>", self.ao_selecionar_roteiro_mestre)

        tk.Button(
            frame_selecao_mestre,
            text="📁 Selecionar Pasta Raiz",
            command=self.selecionar_pasta_raiz,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            frame_selecao_mestre,
            text="🔄 Atualizar",
            command=self.buscar_pasta_roteiros,
            bg=self.button_bg,
            fg=self.fg_color,
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            frame_selecao_mestre,
            text="📂 Abrir Pasta",
            command=self.abrir_pasta_roteiro,
            bg=self.button_bg,
            fg=self.fg_color,
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT)

        self.label_pasta_mestre = tk.Label(
            frame_mestre,
            text="",
            bg=self.bg_color,
            fg="#888888",
            font=("Arial", 8)
        )
        self.label_pasta_mestre.pack(anchor="w", pady=(5, 0))

        tk.Frame(self.root, bg="#444444", height=2).pack(fill=tk.X, padx=15, pady=10)

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

    def criar_aba_copiar(self):
        frame_superior = tk.Frame(self.aba_copiar, bg=self.bg_color, pady=15)
        frame_superior.pack(fill=tk.X, padx=15)

        frame_acoes = tk.Frame(frame_superior, bg=self.bg_color)
        frame_acoes.pack(fill=tk.X)

        tk.Button(
            frame_acoes,
            text="🗑️ Limpar Este Roteiro",
            command=self.limpar_historico_roteiro_atual,
            bg="#FF6B6B",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            frame_acoes,
            text="🗑️ Limpar Tudo",
            command=self.limpar_historico_completo,
            bg="#C70039",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT)

        tk.Frame(self.aba_copiar, bg="#444444", height=1).pack(fill=tk.X, padx=15, pady=10)

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
            text="📋 COPIAR TEXTO",
            command=self.copiar_texto_atual,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_copiar.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            frame_acoes,
            text="💾 Salvar Seção",
            command=self.salvar_secao,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(side=tk.LEFT)

        self.text_area = scrolledtext.ScrolledText(
            frame_direito,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="white",
            selectbackground="#4a4a4a",
            padx=20,
            pady=20
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        def scroll_text_area(event):
            self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        self.text_area.bind("<Enter>", lambda e: self.text_area.bind("<MouseWheel>", scroll_text_area))
        self.text_area.bind("<Leave>", lambda e: self.text_area.unbind("<MouseWheel>"))

        self.text_area.insert(1.0, "👈 Selecione um roteiro e uma seção para visualizar o texto aqui.\n\nVocê poderá copiar o texto com um clique!")
        self.text_area.config(state=tk.DISABLED)

        frame_status = tk.Frame(self.aba_copiar, bg="#1a1a1a", height=35)
        frame_status.pack(fill=tk.X, side=tk.BOTTOM)

        self.label_status = tk.Label(
            frame_status,
            text="🔍 Buscando roteiros...",
            bg="#1a1a1a",
            fg="#00ff00",
            font=("Arial", 9)
        )
        self.label_status.pack(side=tk.LEFT, padx=15, pady=8)

    def criar_aba_visualizar(self):
        frame_superior = tk.Frame(self.aba_visualizar, bg=self.bg_color, pady=15)
        frame_superior.pack(fill=tk.X, padx=15)

        frame_sel = tk.Frame(frame_superior, bg=self.bg_color)
        frame_sel.pack(fill=tk.X)

        tk.Label(
            frame_sel,
            text="Selecione o Arquivo:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.combo_arquivos = ttk.Combobox(
            frame_sel,
            state="readonly",
            font=("Arial", 10),
            width=50
        )
        self.combo_arquivos.pack(side=tk.LEFT)
        self.combo_arquivos.bind("<<ComboboxSelected>>", self.visualizar_arquivo_selecionado)

        tk.Frame(self.aba_visualizar, bg="#444444", height=1).pack(fill=tk.X, padx=15, pady=10)

        frame_principal = tk.Frame(self.aba_visualizar, bg=self.bg_color)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        frame_esq = tk.Frame(frame_principal, bg=self.bg_color, width=300)
        frame_esq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        frame_esq.pack_propagate(False)

        tk.Label(
            frame_esq,
            text="📑 ESTRUTURA",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))

        tree_frame = tk.Frame(frame_esq, bg=self.bg_color)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_estrutura = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll.set,
            selectmode="browse"
        )
        self.tree_estrutura.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree_estrutura.yview)

        def scroll_tree(event):
            self.tree_estrutura.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        self.tree_estrutura.bind("<Enter>", lambda e: self.tree_estrutura.bind("<MouseWheel>", scroll_tree))
        self.tree_estrutura.bind("<Leave>", lambda e: self.tree_estrutura.unbind("<MouseWheel>"))
        self.tree_estrutura.bind("<<TreeviewSelect>>", self.item_selecionado)

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

        tk.Button(
            frame_acoes_vis,
            text="📋 Copiar Conteúdo",
            command=self.copiar_conteudo_visualizado,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            frame_acoes_vis,
            text="🔄 Recarregar",
            command=self.recarregar_arquivo_atual,
            bg=self.button_bg,
            fg=self.fg_color,
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT)

        # Área de visualização
        self.text_visualizar = scrolledtext.ScrolledText(
            frame_dir,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="white",
            selectbackground="#4a4a4a",
            padx=20,
            pady=20
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
        frame_status_vis = tk.Frame(self.aba_visualizar, bg="#1a1a1a", height=35)
        frame_status_vis.pack(fill=tk.X, side=tk.BOTTOM)

        self.label_status_vis = tk.Label(
            frame_status_vis,
            text="Pronto para visualizar",
            bg="#1a1a1a",
            fg="#00ff00",
            font=("Arial", 9)
        )
        self.label_status_vis.pack(side=tk.LEFT, padx=15, pady=8)

    def carregar_arquivos_roteiro(self, event=None):
        """Carrega os arquivos disponíveis do roteiro selecionado"""
        if not self.pasta_roteiro_atual or not os.path.exists(self.pasta_roteiro_atual):
            return

        # Lista os arquivos .txt disponíveis
        arquivos = {}
        for arquivo in self.listar_arquivos_incluindo_ocultos(self.pasta_roteiro_atual):
            if arquivo.endswith('.txt'):
                caminho = os.path.join(self.pasta_roteiro_atual, arquivo)
                # Nome amigável
                nome_amigavel = arquivo.replace('_', ' ').replace('.txt', '')
                arquivos[nome_amigavel] = caminho

        if arquivos:
            self.arquivos_disponiveis = arquivos
            self.combo_arquivos['values'] = sorted(arquivos.keys())
            self.combo_arquivos.set('')
            self.label_status_vis.config(text=f"✅ {len(arquivos)} arquivo(s) encontrado(s)")
        else:
            self.combo_arquivos['values'] = []
            self.label_status_vis.config(text="⚠️ Nenhum arquivo .txt encontrado")

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
        """Analisa a estrutura do conteúdo e cria árvore de navegação"""
        # Limpa árvore
        for item in self.tree_estrutura.get_children():
            self.tree_estrutura.delete(item)

        # Remove colunas e configura
        self.tree_estrutura['columns'] = ()
        self.tree_estrutura.heading('#0', text='Estrutura do Documento')

        linhas = conteudo.split('\n')
        self.mapa_estrutura = {}  # {item_id: (inicio_linha, fim_linha, texto)}

        # Padrões para identificar seções - SIMPLIFICADO (sem linhas de ====)
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

        # Adiciona último item
        if item_atual:
            texto_secao = '\n'.join(linhas[linha_inicio:])
            self.mapa_estrutura[item_atual['id']] = (linha_inicio, len(linhas) - 1, texto_secao)

        # Se não encontrou estrutura, adiciona "Documento Completo"
        if not itens_raiz:
            item_id = self.tree_estrutura.insert('', 'end', text="📄 Documento Completo")
            self.mapa_estrutura[item_id] = (0, len(linhas) - 1, conteudo)

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
                pyperclip.copy(texto)
                self.label_status_vis.config(text="✅ Conteúdo copiado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao copiar:\n{str(e)}")

    def recarregar_arquivo_atual(self):
        """Recarrega o arquivo atual"""
        if hasattr(self, 'arquivo_visualizacao_atual'):
            self.visualizar_arquivo_selecionado()

    def buscar_pasta_roteiros(self):
        """Busca a pasta ROTEIROS_GERADOS e lista os roteiros disponíveis"""
        # Limpa a lista anterior
        self.roteiros_disponiveis = {}
        self.combo_roteiro_mestre.set("")
        self.combo_roteiro_mestre['values'] = []

        # Tenta encontrar a pasta ROTEIROS_GERADOS
        pasta_atual = os.getcwd()
        pasta_roteiros = os.path.join(pasta_atual, "ROTEIROS_GERADOS")

        if not os.path.exists(pasta_roteiros):
            # Tenta um nível acima
            pasta_pai = os.path.dirname(pasta_atual)
            pasta_roteiros = os.path.join(pasta_pai, "ROTEIROS_GERADOS")

        if os.path.exists(pasta_roteiros):
            self.pasta_roteiros = pasta_roteiros
            self.label_pasta_mestre.config(text=f"📂 Pasta: {pasta_roteiros}")

            # Lista todas as subpastas (cada uma é um roteiro)
            try:
                roteiros_com_status = []

                for item in self.listar_arquivos_incluindo_ocultos(pasta_roteiros):
                    caminho_item = os.path.join(pasta_roteiros, item)
                    if os.path.isdir(caminho_item):
                        # Procura pelo arquivo de texto narrado (aceita formatos antigos e novos)
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
                                # Se não encontrou nenhum dos dois, procura qualquer .txt
                                arquivos_txt = [f for f in self.listar_arquivos_incluindo_ocultos(caminho_item)
                                              if f.endswith('.txt')]
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
                                        video_gravado = status.get("video_gravado", False)
                                        video_postado = status.get("video_postado", False)

                                        if video_postado:
                                            indicador = "✅ "  # Postado
                                        elif video_gravado:
                                            indicador = "🎬 "  # Gravado
                                except:
                                    pass  # Mantém indicador padrão em caso de erro

                            nome_com_status = f"{indicador}{nome_roteiro}"
                            roteiros_com_status.append(nome_com_status)
                            self.roteiros_disponiveis[nome_roteiro] = arquivo_texto

                if self.roteiros_disponiveis:
                    # Atualiza o combobox mestre
                    nomes_ordenados = sorted(roteiros_com_status)
                    self.combo_roteiro_mestre['values'] = nomes_ordenados

                    self.atualizar_status(f"✅ {len(nomes_ordenados)} roteiro(s) encontrado(s)")
                else:
                    self.atualizar_status("⚠️ Nenhum roteiro encontrado na pasta")
                    self.label_pasta_mestre.config(text=f"⚠️ Pasta encontrada mas sem roteiros: {pasta_roteiros}")

            except Exception as e:
                self.atualizar_status(f"❌ Erro ao listar roteiros: {str(e)}")
        else:
            self.pasta_roteiros = ""
            self.label_pasta_mestre.config(text="❌ Pasta ROTEIROS_GERADOS não encontrada!")
            self.atualizar_status("❌ Pasta ROTEIROS_GERADOS não encontrada")


    def carregar_arquivo(self, caminho):
        """Carrega e processa o arquivo selecionado"""
        try:
            with open(caminho, 'r', encoding='utf-8') as file:
                self.texto_completo = file.read()

            self.arquivo_atual = caminho

            # Processa o texto e identifica seções
            self.identificar_secoes()

            # Cria botões para cada seção
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
                cor_btn = "#2d5f2d"  # Verde escuro para copiado
                cor_fg = "#90EE90"  # Verde claro para texto
            else:
                icone = "📄"
                cor_btn = self.button_bg
                cor_fg = self.fg_color

            # Botão principal com quebra de linha para títulos longos
            btn = tk.Button(
                frame_btn,
                text=f"{icone} {titulo_btn}",
                command=lambda idx=indice: self.exibir_secao(idx),
                bg=cor_btn,
                fg=cor_fg,
                font=("Arial", 9, "bold" if foi_copiado else "normal"),
                relief=tk.FLAT,
                anchor="w",
                padx=10,
                pady=10,
                cursor="hand2",
                wraplength=340,  # Quebra texto em múltiplas linhas
                justify=tk.LEFT
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
            hover_color = "#3d6f3d" if foi_copiado else self.button_hover
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
                pyperclip.copy(texto)

                # Registra no histórico
                roteiro_nome = self.roteiro_atual if self.roteiro_atual else ""
                secao = self.secoes[self.secao_atual_indice]
                self.registrar_copia(roteiro_nome, secao['titulo'])

                # Atualiza os botões para mostrar o indicador
                self.criar_botoes_secoes()

                # Mostra quantas vezes foi copiado
                info = self.get_info_copia(roteiro_nome, secao['titulo'])
                contador = info['contador'] if info else 1

                self.atualizar_status(f"✅ Texto copiado! (Copiado {contador}x)")

                # Efeito visual no botão
                self.btn_copiar.config(bg="#45a049", text="✓ COPIADO!")
                self.root.after(2000, lambda: self.btn_copiar.config(bg=self.accent_color, text="📋 COPIAR TEXTO"))

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

    def carregar_historico(self):
        """Carrega o histórico de cópias do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_historico):
                with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                    self.historico_copias = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
            self.historico_copias = {}

    def salvar_historico(self):
        """Salva o histórico de cópias no arquivo JSON"""
        try:
            with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(self.historico_copias, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    def registrar_copia(self, roteiro_nome, secao_titulo):
        """Registra uma cópia no histórico"""
        if roteiro_nome not in self.historico_copias:
            self.historico_copias[roteiro_nome] = {}

        agora = datetime.now()

        if secao_titulo in self.historico_copias[roteiro_nome]:
            # Incrementa contador
            self.historico_copias[roteiro_nome][secao_titulo]['contador'] += 1
            self.historico_copias[roteiro_nome][secao_titulo]['ultima_copia'] = agora.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Primeira cópia
            self.historico_copias[roteiro_nome][secao_titulo] = {
                'primeira_copia': agora.strftime("%Y-%m-%d %H:%M:%S"),
                'ultima_copia': agora.strftime("%Y-%m-%d %H:%M:%S"),
                'contador': 1
            }

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
            self.label_status.config(fg="#00ff00")
        elif "❌" in mensagem:
            self.label_status.config(fg="#ff0000")
        elif "⚠️" in mensagem:
            self.label_status.config(fg="#FFA500")
        else:
            self.label_status.config(fg="#ffff00")

    def criar_aba_titulo(self):
        """Cria a interface da aba de título e descrição"""
        # Frame superior fixo com status
        frame_topo = tk.Frame(self.aba_titulo, bg=self.bg_color)
        frame_topo.pack(fill=tk.X, padx=15, pady=15)

        # Título da seção
        tk.Label(
            frame_topo,
            text="🎬 INFORMAÇÕES DO VÍDEO",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, pady=(0, 0))

        # Status da produção no topo
        frame_status_topo = tk.Frame(frame_topo, bg=self.bg_color)
        frame_status_topo.pack(side=tk.RIGHT)

        tk.Label(
            frame_status_topo,
            text="STATUS DA PRODUÇÃO:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 15))

        self.var_gravado = tk.BooleanVar()
        self.check_gravado = tk.Checkbutton(
            frame_status_topo,
            text="Vídeo Gravado",
            variable=self.var_gravado,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 10),
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.check_gravado.pack(side=tk.LEFT, padx=(0, 15))

        self.var_postado = tk.BooleanVar()
        self.check_postado = tk.Checkbutton(
            frame_status_topo,
            text="Vídeo Postado",
            variable=self.var_postado,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 10),
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.check_postado.pack(side=tk.LEFT)

        # Linha separadora
        tk.Frame(self.aba_titulo, bg="#444444", height=1).pack(fill=tk.X, padx=15)

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
                font=("Arial", 10),
                bg="#1e1e1e",
                fg=self.fg_color,
                insertbackground="white"
            )
            entry_titulo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

            btn_copiar = tk.Button(
                frame_titulo,
                text="📋 Copiar",
                command=lambda idx=i-1: self.copiar_titulo(idx),
                bg=self.button_bg,
                fg=self.fg_color,
                font=("Arial", 9),
                relief=tk.FLAT,
                padx=10,
                cursor="hand2"
            )
            btn_copiar.pack(side=tk.LEFT)

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
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg=self.fg_color,
            insertbackground="white",
            height=15
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

        tk.Button(
            frame_btn_desc,
            text="📋 Copiar Descrição",
            command=self.copiar_descricao,
            bg=self.button_bg,
            fg=self.fg_color,
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.RIGHT)

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
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg=self.fg_color,
            insertbackground="white",
            height=5
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

        # Botões de ação
        frame_botoes = tk.Frame(frame_conteudo, bg=self.bg_color)
        frame_botoes.pack(fill=tk.X, pady=20)

        tk.Button(
            frame_botoes,
            text="💾 Salvar Tudo",
            command=self.salvar_info_video,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            frame_botoes,
            text="🔄 Recarregar",
            command=self.carregar_info_video,
            bg=self.button_bg,
            fg=self.fg_color,
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor="hand2"
        ).pack(side=tk.LEFT)

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
        for item in self.listar_arquivos_incluindo_ocultos(self.pasta_roteiros):
            if item.replace("_", " ").title() == roteiro_limpo:
                self.pasta_roteiro_atual = os.path.join(self.pasta_roteiros, item)
                break

        if not self.pasta_roteiro_atual or not os.path.exists(self.pasta_roteiro_atual):
            return

        # Atualiza label de pasta
        self.label_pasta_mestre.config(text=f"📂 {self.pasta_roteiro_atual}")

        # Atualizar Aba 1: Copiar Seções
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

        # Atualizar Aba 2: Visualizar Arquivos
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
        self.var_gravado.set(False)
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
                    self.var_gravado.set(status.get("video_gravado", False))
                    self.var_postado.set(status.get("video_postado", False))
            except Exception as e:
                print(f"Erro ao carregar status: {e}")

    def salvar_info_video(self):
        """Salva informações do vídeo no arquivo"""
        if not self.pasta_roteiro_atual:
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

            # Salvar status JSON
            arquivo_status = os.path.join(self.pasta_roteiro_atual, "video_status.json")
            status = {
                "video_gravado": self.var_gravado.get(),
                "video_postado": self.var_postado.get()
            }
            with open(arquivo_status, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Sucesso", "Informações salvas com sucesso!")

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
