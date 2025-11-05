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
        self.root.title("Script Copier - Universal")
        self.root.geometry("1200x700")

        try:
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(__file__)

            icon_path = os.path.join(app_dir, 'script_copier_icon.ico')
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

    def mostrar_tela_inicial(self):
        """Mostra mensagem inicial pedindo para selecionar pasta"""
        self.label_pasta_mestre.config(
            text="👆 Clique em 'Selecionar Pasta Raiz' para começar",
            fg="#FFA726"
        )
        self.atualizar_status("📁 Aguardando seleção de pasta...")

    def selecionar_pasta_raiz(self):
        """Permite selecionar qualquer pasta como raiz do projeto"""
        pasta = filedialog.askdirectory(
            title="Selecione a pasta raiz do projeto",
            mustexist=True
        )

        if pasta:
            self.pasta_raiz_selecionada = pasta
            self.label_pasta_mestre.config(
                text=f"📁 Pasta selecionada: {pasta}",
                fg=self.accent_color
            )
            self.atualizar_status("🔍 Buscando roteiros...")
            self.buscar_pasta_roteiros()
        else:
            self.atualizar_status("❌ Seleção cancelada")

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
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            frame_acoes,
            text="🧹 Limpar Tudo",
            command=self.limpar_historico_completo,
            bg="#FF8C00",
            fg="white",
            font=("Arial", 9),
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
            font=("Arial", 11),
            justify=tk.CENTER
        )
        self.label_sem_secoes.pack(pady=50)

        frame_direito = tk.Frame(frame_principal, bg=self.bg_color)
        frame_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.frame_info = tk.Frame(frame_direito, bg=self.bg_color)
        self.frame_info.pack(fill=tk.X, pady=(0, 10))

        self.label_titulo_secao = tk.Label(
            self.frame_info,
            text="",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Arial", 14, "bold"),
            wraplength=700,
            justify=tk.LEFT
        )
        self.label_titulo_secao.pack(side=tk.LEFT)

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
            command=self.copiar_texto,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.btn_copiar.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            frame_acoes,
            text="📄 COPIAR TUDO",
            command=self.copiar_tudo,
            bg=self.button_bg,
            fg="white",
            font=("Arial", 10),
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
            text="🔍 Aguardando seleção de pasta...",
            bg="#1a1a1a",
            fg="#ffffff",
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

        frame_info = tk.Frame(frame_dir, bg=self.bg_color)
        frame_info.pack(fill=tk.X, pady=(0, 10))

        self.label_arquivo_info = tk.Label(
            frame_info,
            text="",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Arial", 12, "bold")
        )
        self.label_arquivo_info.pack(side=tk.LEFT)

        self.text_visualizador = scrolledtext.ScrolledText(
            frame_dir,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#ffffff",
            padx=20,
            pady=20
        )
        self.text_visualizador.pack(fill=tk.BOTH, expand=True)

    def criar_aba_titulo(self):
        frame_principal = tk.Frame(self.aba_titulo, bg=self.bg_color)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            frame_principal,
            text="🎬 TÍTULO E DESCRIÇÃO DO VÍDEO",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))

        self.text_titulo = scrolledtext.ScrolledText(
            frame_principal,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#ffffff",
            height=25,
            padx=20,
            pady=20
        )
        self.text_titulo.pack(fill=tk.BOTH, expand=True)

        frame_botoes = tk.Frame(frame_principal, bg=self.bg_color)
        frame_botoes.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            frame_botoes,
            text="📋 COPIAR TÍTULO E DESCRIÇÃO",
            command=self.copiar_titulo_descricao,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack()

        self.text_titulo.insert(1.0, "👈 Selecione um roteiro para visualizar título e descrição")
        self.text_titulo.config(state=tk.DISABLED)

    def carregar_historico(self):
        """Carrega o histórico de cópias do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_historico):
                with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                    self.historico_copias = json.load(f)
            else:
                self.historico_copias = {}
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
            self.historico_copias = {}

    def salvar_historico(self):
        """Salva o histórico de cópias no arquivo JSON"""
        try:
            with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(self.historico_copias, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    def registrar_copia(self, secao_titulo):
        """Registra uma cópia no histórico"""
        if not self.roteiro_atual:
            return

        if self.roteiro_atual not in self.historico_copias:
            self.historico_copias[self.roteiro_atual] = {}

        agora = datetime.now()
        data_hora = agora.strftime("%Y-%m-%d %H:%M:%S")

        if secao_titulo not in self.historico_copias[self.roteiro_atual]:
            self.historico_copias[self.roteiro_atual][secao_titulo] = {
                "contador": 0,
                "ultima_copia": data_hora
            }

        self.historico_copias[self.roteiro_atual][secao_titulo]["contador"] += 1
        self.historico_copias[self.roteiro_atual][secao_titulo]["ultima_copia"] = data_hora

        self.salvar_historico()

    def limpar_historico_roteiro_atual(self):
        """Limpa o histórico do roteiro atual"""
        if not self.roteiro_atual:
            messagebox.showwarning("Aviso", "Nenhum roteiro selecionado!")
            return

        resposta = messagebox.askyesno(
            "Confirmar Limpeza",
            f"Tem certeza que deseja limpar o histórico de cópias do roteiro:\n\n{self.roteiro_atual}?"
        )

        if resposta:
            if self.roteiro_atual in self.historico_copias:
                del self.historico_copias[self.roteiro_atual]
                self.salvar_historico()
                self.criar_botoes_secoes()
                messagebox.showinfo("Sucesso", "Histórico do roteiro limpo com sucesso!")

    def limpar_historico_completo(self):
        """Limpa todo o histórico"""
        resposta = messagebox.askyesno(
            "Confirmar Limpeza Total",
            "Tem certeza que deseja limpar TODO o histórico de cópias de TODOS os roteiros?\n\nEsta ação não pode ser desfeita!"
        )

        if resposta:
            self.historico_copias = {}
            self.salvar_historico()
            self.criar_botoes_secoes()
            messagebox.showinfo("Sucesso", "Histórico completo limpo com sucesso!")

    def buscar_pasta_roteiros(self):
        """Busca roteiros na pasta raiz selecionada"""
        if not self.pasta_raiz_selecionada:
            self.atualizar_status("❌ Nenhuma pasta raiz selecionada")
            return

        pasta_roteiros = self.pasta_raiz_selecionada
        self.pasta_roteiros = pasta_roteiros

        if os.path.exists(pasta_roteiros):
            self.label_pasta_mestre.config(text=f"📂 Pasta: {pasta_roteiros}")

            try:
                self.roteiros_disponiveis = {}
                items = self.listar_arquivos_incluindo_ocultos(pasta_roteiros)

                roteiros_com_status = []

                for item in items:
                    caminho_item = os.path.join(pasta_roteiros, item)

                    if os.path.isdir(caminho_item):
                        arquivos_txt = [f for f in os.listdir(caminho_item) if f.endswith('.txt')]

                        if arquivos_txt:
                            nome_roteiro = item.replace("_", " ").title()

                            arquivo_status = os.path.join(caminho_item, "video_status.json")
                            indicador = "⚪ "

                            if os.path.exists(arquivo_status):
                                try:
                                    with open(arquivo_status, 'r', encoding='utf-8') as f:
                                        status = json.load(f)
                                        video_gravado = status.get("video_gravado", False)
                                        video_postado = status.get("video_postado", False)

                                        if video_postado:
                                            indicador = "✅ "
                                        elif video_gravado:
                                            indicador = "🎬 "
                                except:
                                    pass

                            nome_com_status = f"{indicador}{nome_roteiro}"
                            roteiros_com_status.append(nome_com_status)
                            self.roteiros_disponiveis[nome_roteiro] = caminho_item

                if self.roteiros_disponiveis:
                    nomes_ordenados = sorted(roteiros_com_status)
                    self.combo_roteiro_mestre['values'] = nomes_ordenados

                    self.atualizar_status(f"✅ {len(nomes_ordenados)} roteiro(s) encontrado(s)")
                else:
                    self.atualizar_status("⚠️ Nenhum roteiro encontrado na pasta")
                    self.label_pasta_mestre.config(text=f"⚠️ Pasta sem roteiros: {pasta_roteiros}")

            except Exception as e:
                self.atualizar_status(f"❌ Erro ao listar roteiros: {str(e)}")
        else:
            self.pasta_roteiros = ""
            self.label_pasta_mestre.config(text="❌ Pasta não encontrada!")
            self.atualizar_status("❌ Pasta não encontrada")

    def ao_selecionar_roteiro_mestre(self, event):
        """Callback quando um roteiro é selecionado no combobox mestre"""
        selecao = self.combo_roteiro_mestre.get()

        if not selecao:
            return

        nome_roteiro_limpo = re.sub(r'^[⚪✅🎬]\s*', '', selecao)

        if nome_roteiro_limpo in self.roteiros_disponiveis:
            pasta_roteiro = self.roteiros_disponiveis[nome_roteiro_limpo]
            self.roteiro_atual = nome_roteiro_limpo
            self.pasta_roteiro_atual = pasta_roteiro

            arquivos_txt = [f for f in os.listdir(pasta_roteiro) if f.endswith('.txt')]

            if arquivos_txt:
                arquivos_txt_ordenados = sorted(arquivos_txt)
                primeiro_arquivo = os.path.join(pasta_roteiro, arquivos_txt_ordenados[0])

                self.carregar_arquivo(primeiro_arquivo)
                self.atualizar_arvore_estrutura(pasta_roteiro)
                self.carregar_lista_arquivos(pasta_roteiro)
                self.carregar_titulo_descricao()

    def carregar_arquivo(self, caminho):
        """Carrega e processa o arquivo selecionado - TODOS OS TXT"""
        try:
            with open(caminho, 'r', encoding='utf-8') as file:
                self.texto_completo = file.read()

            self.arquivo_atual = caminho

            self.identificar_secoes()
            self.criar_botoes_secoes()

            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, "👈 Selecione uma seção à esquerda para visualizar")
            self.text_area.config(state=tk.DISABLED)

            nome_arquivo = os.path.basename(caminho)
            self.atualizar_status(f"✅ Arquivo carregado: {nome_arquivo}")

        except Exception as e:
            self.atualizar_status(f"❌ Erro ao carregar arquivo: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")

    def identificar_secoes(self):
        """Identifica todas as seções do texto"""
        self.secoes = {}

        padrao_secoes = [
            (r'^HOOK\s*\(.*?\).*?$', 'HOOK'),
            (r'^ATO\s+[IVXLCDM]+\s*-\s*(.+?)(?:\s*▓▓▓)?$', 'ATO'),
            (r'^CONCLUS[ÃA]O\s*(?:-\s*(.+?))?(?:\s*▓▓▓)?$', 'CONCLUSÃO'),
            (r'^CHAPTER\s+\w+\s*-\s*(.+)$', 'CHAPTER'),
            (r'^#+\s*(.+)$', 'HEADING'),
        ]

        linhas = self.texto_completo.split('\n')
        posicao_atual = 0
        secoes_encontradas = []

        for i, linha in enumerate(linhas):
            linha_limpa = linha.strip()

            for padrao, tipo in padrao_secoes:
                match = re.match(padrao, linha_limpa, re.IGNORECASE)
                if match:
                    if tipo == 'ATO':
                        titulo = f"ATO - {match.group(1)}"
                    elif tipo == 'CONCLUSÃO':
                        titulo = "CONCLUSÃO"
                    elif tipo == 'CHAPTER':
                        titulo = f"CHAPTER - {match.group(1)}"
                    elif tipo == 'HEADING':
                        titulo = match.group(1)
                    else:
                        titulo = linha_limpa

                    posicao_linha = self.texto_completo.find(linha, posicao_atual)
                    if posicao_linha != -1:
                        secoes_encontradas.append((titulo, posicao_linha))
                        posicao_atual = posicao_linha + len(linha)
                    break

        for i, (titulo, posicao_inicio) in enumerate(secoes_encontradas):
            if i < len(secoes_encontradas) - 1:
                posicao_fim = secoes_encontradas[i + 1][1]
            else:
                posicao_fim = len(self.texto_completo)

            texto_secao = self.texto_completo[posicao_inicio:posicao_fim].strip()
            self.secoes[titulo] = texto_secao

        if not self.secoes:
            self.secoes["TEXTO COMPLETO"] = self.texto_completo

    def criar_botoes_secoes(self):
        """Cria botões para cada seção identificada"""
        for widget in self.frame_botoes.winfo_children():
            widget.destroy()

        if not self.secoes:
            self.label_sem_secoes = tk.Label(
                self.frame_botoes,
                text="⚠️ Nenhuma seção encontrada\nno arquivo selecionado",
                bg=self.bg_color,
                fg="#888888",
                font=("Arial", 11),
                justify=tk.CENTER
            )
            self.label_sem_secoes.pack(pady=50)
            return

        historico_roteiro = self.historico_copias.get(self.roteiro_atual, {})

        for i, (titulo, texto) in enumerate(self.secoes.items()):
            frame_botao_container = tk.Frame(self.frame_botoes, bg=self.bg_color)
            frame_botao_container.pack(fill=tk.X, pady=3)

            foi_copiado = titulo in historico_roteiro
            contador_copias = historico_roteiro.get(titulo, {}).get("contador", 0)

            if foi_copiado:
                bg_color = "#2E7D32"
                status_text = f" ✓ ({contador_copias}x)"
            else:
                bg_color = self.button_bg
                status_text = ""

            texto_botao = f"{titulo}{status_text}"

            btn = tk.Button(
                frame_botao_container,
                text=texto_botao,
                command=lambda t=titulo: self.mostrar_secao(t),
                bg=bg_color,
                fg="white",
                font=("Arial", 10),
                relief=tk.FLAT,
                anchor="w",
                padx=15,
                pady=12,
                cursor="hand2",
                wraplength=320,
                justify=tk.LEFT
            )
            btn.pack(fill=tk.X, expand=True)

            def on_enter(e, b=btn):
                if b['bg'] == "#2E7D32":
                    b.config(bg="#388E3C")
                else:
                    b.config(bg=self.button_hover)

            def on_leave(e, b=btn, original=bg_color):
                b.config(bg=original)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def mostrar_secao(self, titulo):
        """Mostra o texto da seção selecionada"""
        if titulo in self.secoes:
            texto = self.secoes[titulo]

            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, texto)
            self.text_area.config(state=tk.DISABLED)

            self.label_titulo_secao.config(text=titulo)

            palavras = len(texto.split())
            self.label_palavras.config(text=f"📊 {palavras} palavras")

    def copiar_texto(self):
        """Copia o texto atual para a área de transferência"""
        try:
            texto = self.text_area.get(1.0, tk.END).strip()

            if not texto or texto == "👈 Selecione um roteiro e uma seção para visualizar o texto aqui.\n\nVocê poderá copiar o texto com um clique!":
                messagebox.showwarning("Aviso", "Nenhum texto selecionado para copiar!")
                return

            pyperclip.copy(texto)

            titulo_atual = self.label_titulo_secao.cget("text")
            if titulo_atual:
                self.registrar_copia(titulo_atual)
                self.criar_botoes_secoes()

            self.atualizar_status("✅ Texto copiado!")

            self.btn_copiar.config(text="✅ COPIADO!", bg="#2E7D32")
            self.root.after(2000, lambda: self.btn_copiar.config(text="📋 COPIAR TEXTO", bg=self.accent_color))

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar texto:\n{str(e)}")

    def copiar_tudo(self):
        """Copia todo o conteúdo do arquivo"""
        try:
            if not self.texto_completo:
                messagebox.showwarning("Aviso", "Nenhum arquivo carregado!")
                return

            pyperclip.copy(self.texto_completo)
            self.atualizar_status("✅ Texto completo copiado!")
            messagebox.showinfo("Sucesso", "Todo o conteúdo do arquivo foi copiado!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar texto:\n{str(e)}")

    def atualizar_status(self, mensagem):
        """Atualiza a barra de status"""
        self.label_status.config(text=mensagem)

    def abrir_pasta_roteiro(self):
        """Abre a pasta do roteiro atual no explorador"""
        if self.pasta_roteiro_atual and os.path.exists(self.pasta_roteiro_atual):
            if platform.system() == 'Windows':
                os.startfile(self.pasta_roteiro_atual)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', self.pasta_roteiro_atual])
            else:
                subprocess.run(['xdg-open', self.pasta_roteiro_atual])
        else:
            messagebox.showwarning("Aviso", "Nenhum roteiro selecionado ou pasta não encontrada!")

    def carregar_lista_arquivos(self, pasta_roteiro):
        """Carrega lista de TODOS os arquivos da pasta"""
        try:
            arquivos = os.listdir(pasta_roteiro)
            arquivos_txt = [f for f in arquivos if f.endswith('.txt')]
            arquivos_txt_ordenados = sorted(arquivos_txt)

            self.combo_arquivos['values'] = arquivos_txt_ordenados

            if arquivos_txt_ordenados:
                self.combo_arquivos.set(arquivos_txt_ordenados[0])

        except Exception as e:
            self.atualizar_status(f"❌ Erro ao listar arquivos: {str(e)}")

    def visualizar_arquivo_selecionado(self, event):
        """Visualiza o arquivo selecionado no combo"""
        arquivo_selecionado = self.combo_arquivos.get()

        if arquivo_selecionado and self.pasta_roteiro_atual:
            caminho_completo = os.path.join(self.pasta_roteiro_atual, arquivo_selecionado)
            self.carregar_arquivo_na_visualizacao(caminho_completo)

    def carregar_arquivo_na_visualizacao(self, caminho):
        """Carrega arquivo na aba de visualização"""
        try:
            with open(caminho, 'r', encoding='utf-8') as file:
                conteudo = file.read()

            self.text_visualizador.config(state=tk.NORMAL)
            self.text_visualizador.delete(1.0, tk.END)
            self.text_visualizador.insert(1.0, conteudo)
            self.text_visualizador.config(state=tk.DISABLED)

            nome_arquivo = os.path.basename(caminho)
            self.label_arquivo_info.config(text=f"📄 {nome_arquivo}")

        except Exception as e:
            self.text_visualizador.config(state=tk.NORMAL)
            self.text_visualizador.delete(1.0, tk.END)
            self.text_visualizador.insert(1.0, f"❌ Erro ao carregar arquivo:\n\n{str(e)}")
            self.text_visualizador.config(state=tk.DISABLED)

    def atualizar_arvore_estrutura(self, pasta_roteiro):
        """Atualiza a árvore de estrutura com TODOS os arquivos"""
        for item in self.tree_estrutura.get_children():
            self.tree_estrutura.delete(item)

        try:
            arquivos = os.listdir(pasta_roteiro)
            arquivos_ordenados = sorted(arquivos)

            for arquivo in arquivos_ordenados:
                caminho_completo = os.path.join(pasta_roteiro, arquivo)

                if arquivo.endswith('.txt'):
                    self.tree_estrutura.insert('', 'end', text=f"📄 {arquivo}", values=[caminho_completo])
                elif arquivo.endswith('.json'):
                    self.tree_estrutura.insert('', 'end', text=f"⚙️ {arquivo}", values=[caminho_completo])
                elif os.path.isdir(caminho_completo):
                    self.tree_estrutura.insert('', 'end', text=f"📁 {arquivo}", values=[caminho_completo])
                else:
                    self.tree_estrutura.insert('', 'end', text=f"📋 {arquivo}", values=[caminho_completo])

        except Exception as e:
            self.atualizar_status(f"❌ Erro ao atualizar árvore: {str(e)}")

    def item_selecionado(self, event):
        """Quando um item é selecionado na árvore"""
        selecionados = self.tree_estrutura.selection()

        if selecionados:
            item = selecionados[0]
            valores = self.tree_estrutura.item(item, 'values')

            if valores:
                caminho = valores[0]

                if os.path.isfile(caminho) and caminho.endswith('.txt'):
                    self.carregar_arquivo_na_visualizacao(caminho)
                elif os.path.isfile(caminho):
                    nome = os.path.basename(caminho)
                    self.text_visualizador.config(state=tk.NORMAL)
                    self.text_visualizador.delete(1.0, tk.END)
                    self.text_visualizador.insert(1.0, f"❌ Arquivo {nome} não pode ser visualizado (não é .txt)")
                    self.text_visualizador.config(state=tk.DISABLED)

    def carregar_titulo_descricao(self):
        """Carrega o arquivo de título e descrição"""
        if not self.pasta_roteiro_atual:
            return

        arquivo_titulo = os.path.join(self.pasta_roteiro_atual, "05_Titulo_Descricao.txt")

        try:
            if os.path.exists(arquivo_titulo):
                with open(arquivo_titulo, 'r', encoding='utf-8') as file:
                    conteudo = file.read()

                self.text_titulo.config(state=tk.NORMAL)
                self.text_titulo.delete(1.0, tk.END)
                self.text_titulo.insert(1.0, conteudo)
                self.text_titulo.config(state=tk.DISABLED)
            else:
                self.text_titulo.config(state=tk.NORMAL)
                self.text_titulo.delete(1.0, tk.END)
                self.text_titulo.insert(1.0, "⚠️ Arquivo 05_Titulo_Descricao.txt não encontrado neste roteiro")
                self.text_titulo.config(state=tk.DISABLED)

        except Exception as e:
            self.text_titulo.config(state=tk.NORMAL)
            self.text_titulo.delete(1.0, tk.END)
            self.text_titulo.insert(1.0, f"❌ Erro ao carregar título e descrição:\n\n{str(e)}")
            self.text_titulo.config(state=tk.DISABLED)

    def copiar_titulo_descricao(self):
        """Copia o título e descrição"""
        try:
            texto = self.text_titulo.get(1.0, tk.END).strip()

            if not texto or "Selecione um roteiro" in texto or "não encontrado" in texto or "Erro ao carregar" in texto:
                messagebox.showwarning("Aviso", "Nenhum título/descrição disponível para copiar!")
                return

            pyperclip.copy(texto)
            self.atualizar_status("✅ Título e descrição copiados!")
            messagebox.showinfo("Sucesso", "Título e descrição copiados para área de transferência!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ScriptCopier(root)
    root.mainloop()


if __name__ == "__main__":
    main()
