import json
import random
import unicodedata
from pathlib import Path
from nicegui import ui, app

# ── Caminhos JSON ──────────────────────────────────────────────────────────────
BASE = Path(__file__).parent / "JSON"
JSON_USUARIO_INDEX  = BASE / "IndexUsuario.json"
JSON_IDIOMA_INDEX   = BASE / "IndexIdioma.json"
JSON_PALAVRA_INDEX  = BASE / "IndexPalavra.json"
JSON_EXERCICIO_INDEX = BASE / "IndexExercicio.json"

# ── Helpers JSON ───────────────────────────────────────────────────────────────
def load_usuarios():
    with open(JSON_USUARIO_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)["usuarios"]

def save_usuarios(lista):
    with open(JSON_USUARIO_INDEX, "r", encoding="utf-8") as f:
        dados = json.load(f)
    dados["usuarios"] = lista
    with open(JSON_USUARIO_INDEX, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def load_idiomas():
    with open(JSON_IDIOMA_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)["idiomas"]

def load_palavras():
    with open(JSON_PALAVRA_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)["palavras"]

def save_palavras(lista):
    with open(JSON_PALAVRA_INDEX, "r", encoding="utf-8") as f:
        dados = json.load(f)
    dados["palavras"] = lista
    with open(JSON_PALAVRA_INDEX, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def load_exercicios():
    with open(JSON_EXERCICIO_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)["exercicios"]

def busca_usuario(codigo):
    lista = load_usuarios()
    for i, u in enumerate(lista):
        if u["codigo"] == codigo:
            return i
    return None

def limpar(texto):
    decompor = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decompor if unicodedata.category(c) != "Mn").casefold()

# ── Estado da sessão ───────────────────────────────────────────────────────────
state = {
    "usuario": None,   # nome do usuário logado
    "is_admin": False,
    # exercício em andamento
    "ex_lista": None,       # lista de (palavra_idioma, traducao) sortadas
    "ex_gabarito_idx": None,
    "ex_pergunta_texto": "",
    "ex_count": 0,
    "ex_pontos": 0,
    "ex_total": 3,
}

# ── Cores / estilos ────────────────────────────────────────────────────────────
CARD_CLS   = "w-full max-w-lg mx-auto shadow-lg rounded-xl p-6 bg-white"
TITLE_CLS  = "text-3xl font-bold text-indigo-700 mb-2"
LABEL_CLS  = "text-sm font-semibold text-gray-600"
BTN_PRIMARY = "bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 w-full"
BTN_DANGER  = "bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 w-full"
BTN_SUCCESS = "bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 w-full"
BTN_WARN    = "bg-amber-500 text-white px-4 py-2 rounded-lg hover:bg-amber-600 w-full"
BTN_GRAY    = "bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 w-full"
MSG_OK      = "text-green-700 font-semibold"
MSG_ERR     = "text-red-600 font-semibold"
MSG_INFO    = "text-indigo-700 font-semibold"

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA DE LOGIN
# ══════════════════════════════════════════════════════════════════════════════
@ui.page("/")
def page_login():
    state["usuario"]  = None
    state["is_admin"] = False

    with ui.column().classes("min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-indigo-100 to-purple-100"):
        with ui.card().classes(CARD_CLS):
            ui.label("🌐 Idioma App").classes(TITLE_CLS)
            ui.label("Bem-vindo! Faça seu login.").classes("text-gray-500 mb-4")

            inp_user  = ui.input("Usuário").classes("w-full")
            inp_senha = ui.input("Senha", password=True, password_toggle_button=True).classes("w-full")
            msg       = ui.label("").classes(MSG_ERR)

            def fazer_login():
                usuario = inp_user.value.strip()
                senha   = inp_senha.value.strip()

                if not usuario or not senha:
                    msg.set_text("Preencha usuário e senha.")
                    return

                pos = busca_usuario(usuario)
                if pos is None:
                    msg.set_text("Usuário não encontrado.")
                    return

                lista = load_usuarios()
                if lista[pos]["senha"] != senha:
                    msg.set_text("Senha incorreta.")
                    return

                # Login OK
                state["usuario"]  = usuario
                state["is_admin"] = (usuario == "Admin")
                if state["is_admin"]:
                    ui.navigate.to("/admin")
                else:
                    ui.navigate.to("/menu")

            ui.button("Entrar", on_click=fazer_login).classes(BTN_PRIMARY)


# ══════════════════════════════════════════════════════════════════════════════
#  MENU DO USUÁRIO
# ══════════════════════════════════════════════════════════════════════════════
@ui.page("/menu")
def page_menu():
    if not state["usuario"] or state["is_admin"]:
        ui.navigate.to("/")
        return

    nome = state["usuario"]
    pos  = busca_usuario(nome)
    lista = load_usuarios()
    info  = lista[pos]

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-indigo-50 to-purple-50 p-6"):
        # Header
        with ui.row().classes("w-full max-w-lg mx-auto justify-between items-center mb-6"):
            ui.label(f"Olá, {nome}! 👋").classes("text-2xl font-bold text-indigo-700")
            ui.button("Sair", on_click=lambda: ui.navigate.to("/")).classes(BTN_DANGER + " w-auto px-4")

        # Card de status
        with ui.card().classes(CARD_CLS + " mb-4"):
            ui.label("Seu progresso").classes("text-lg font-semibold text-gray-700 mb-2")
            with ui.row().classes("gap-6"):
                with ui.column().classes("items-center"):
                    ui.label(str(info["nivel"])).classes("text-3xl font-bold text-indigo-600")
                    ui.label("Nível").classes("text-xs text-gray-500")
                with ui.column().classes("items-center"):
                    ui.label(str(info["pontos_atual"])).classes("text-3xl font-bold text-purple-600")
                    ui.label("Pontos").classes("text-xs text-gray-500")
                with ui.column().classes("items-center"):
                    ui.label(info["cod_idioma"]).classes("text-3xl font-bold text-green-600")
                    ui.label("Idioma").classes("text-xs text-gray-500")

        # Opções de menu
        with ui.card().classes(CARD_CLS):
            ui.label("O que deseja fazer?").classes("text-lg font-semibold text-gray-700 mb-4")
            ui.button("📚 Fazer Lição", on_click=lambda: ui.navigate.to("/licao")).classes(BTN_PRIMARY + " mb-2")
            ui.button("🌍 Alterar Idioma", on_click=lambda: ui.navigate.to("/alterar_idioma")).classes(BTN_WARN + " mb-2")
            ui.button("🏆 Ver Ranking", on_click=lambda: ui.navigate.to("/ranking")).classes(BTN_SUCCESS + " mb-2")
            ui.button("🎓 Certificado", on_click=lambda: ui.navigate.to("/certificado")).classes(BTN_GRAY)


# ══════════════════════════════════════════════════════════════════════════════
#  LIÇÃO / EXERCÍCIO
# ══════════════════════════════════════════════════════════════════════════════
def gerar_exercicio(idioma, nivel):
    """Retorna (pergunta_str, lista_opcoes, gabarito_idx) ou None se sem dados."""
    palavras = load_palavras()
    nivelada = [(p["descricao"], p["traducao"]) for p in palavras
                if p["nivel"] <= nivel and p["cod_idioma"] == idioma]
    if len(nivelada) < 4:
        return None
    opcoes = random.sample(nivelada, 4)
    gabarito = random.randint(0, 3)
    exercicios = load_exercicios()
    pergunta_base = exercicios[0]["pergunta"] if exercicios else "Qual a tradução de:"
    pergunta = f'{pergunta_base} **{opcoes[gabarito][1]}**?'
    return pergunta, opcoes, gabarito


@ui.page("/licao")
def page_licao():
    if not state["usuario"] or state["is_admin"]:
        ui.navigate.to("/")
        return

    nome = state["usuario"]
    pos  = busca_usuario(nome)
    lista = load_usuarios()
    info  = lista[pos]
    idioma = info["cod_idioma"]
    nivel  = info["nivel"]

    # Reset exercício
    state["ex_count"]  = 0
    state["ex_pontos"] = 0

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-indigo-50 to-purple-50 p-6"):
        with ui.row().classes("w-full max-w-lg mx-auto justify-between items-center mb-4"):
            ui.label("📚 Lição").classes("text-2xl font-bold text-indigo-700")
            ui.button("← Voltar", on_click=lambda: ui.navigate.to("/menu")).classes(BTN_GRAY + " w-auto")

        contador_lbl  = ui.label(f"Exercício 1 de {state['ex_total']}").classes("text-center text-gray-500 max-w-lg mx-auto w-full")
        pontos_lbl    = ui.label("Pontos desta sessão: 0").classes("text-center text-indigo-600 font-semibold max-w-lg mx-auto w-full mb-2")

        area = ui.column().classes("w-full max-w-lg mx-auto")

        def mostrar_exercicio():
            area.clear()
            state["ex_count"] += 1
            if state["ex_count"] > state["ex_total"]:
                # Salvar pontos
                _salvar_pontos(nome, state["ex_pontos"])
                with area:
                    lista_att = load_usuarios()
                    info_att  = lista_att[busca_usuario(nome)]
                    total_pts  = info_att["pontos_atual"]
                    novo_nivel = info_att["nivel"]
                    with ui.card().classes(CARD_CLS):
                        ui.label("✅ Lição concluída!").classes("text-2xl font-bold text-green-700 mb-2")
                        ui.label(f"Pontos ganhos nesta sessão: {state['ex_pontos']:.0f}").classes(MSG_OK)
                        ui.label(f"Total de pontos: {total_pts}").classes(MSG_INFO)
                        ui.label(f"Nível atual: {novo_nivel}").classes(MSG_INFO)
                        if novo_nivel == 5:
                            ui.label("🎉 Parabéns! Você concluiu o curso!").classes("text-yellow-600 font-bold text-lg")
                        ui.button("Fazer outra lição", on_click=lambda: ui.navigate.to("/licao")).classes(BTN_PRIMARY + " mt-4")
                        ui.button("Voltar ao Menu", on_click=lambda: ui.navigate.to("/menu")).classes(BTN_GRAY + " mt-2")
                return

            contador_lbl.set_text(f"Exercício {state['ex_count']} de {state['ex_total']}")
            resultado = gerar_exercicio(idioma, nivel)

            with area:
                if resultado is None:
                    with ui.card().classes(CARD_CLS):
                        ui.label("⚠️ Sem palavras suficientes para este idioma/nível.").classes(MSG_ERR)
                        ui.button("Voltar ao Menu", on_click=lambda: ui.navigate.to("/menu")).classes(BTN_GRAY + " mt-4")
                    return

                pergunta, opcoes, gabarito = resultado
                with ui.card().classes(CARD_CLS):
                    ui.markdown(pergunta).classes("text-lg font-semibold text-gray-800 mb-4")
                    msg_res = ui.label("").classes("text-center font-bold mb-2")

                    botoes = []
                    def on_resposta(idx, bts, msg_label):
                        exercicios = load_exercicios()
                        pontos_ex  = exercicios[0]["pontos"] if exercicios else 20
                        for b in bts:
                            b.disable()
                        if idx == gabarito:
                            msg_label.set_text(f"✅ Correto! +{pontos_ex} pontos")
                            msg_label.classes(replace=MSG_OK)
                            state["ex_pontos"] += pontos_ex
                        else:
                            desconto = pontos_ex * 0.1
                            msg_label.set_text(f"❌ Incorreto! A resposta era: {opcoes[gabarito][0]}  (-{desconto:.0f} pontos)")
                            msg_label.classes(replace=MSG_ERR)
                            state["ex_pontos"] -= desconto
                        pontos_lbl.set_text(f"Pontos desta sessão: {state['ex_pontos']:.0f}")
                        ui.timer(1.5, mostrar_exercicio, once=True)

                    for i, (palavra, _trad) in enumerate(opcoes):
                        idx_cap = i
                        b = ui.button(palavra,
                                      on_click=lambda e, ii=idx_cap: on_resposta(ii, botoes, msg_res)
                                      ).classes("w-full mb-2 bg-white border border-indigo-300 text-indigo-700 hover:bg-indigo-50 rounded-lg py-2")
                        botoes.append(b)
                    msg_res  # já declarado acima

        mostrar_exercicio()


def _salvar_pontos(nome, pontos_sessao):
    lista = load_usuarios()
    pos = busca_usuario(nome)
    if pos is None:
        return
    lista[pos]["pontos_atual"] += int(pontos_sessao)
    level_str = str(lista[pos]["pontos_atual"])
    if len(level_str) > 2:
        lista[pos]["nivel"] = int(level_str[:-2]) + 1
    lista[pos]["nivel"] = min(lista[pos]["nivel"], 5)
    save_usuarios(lista)


# ══════════════════════════════════════════════════════════════════════════════
#  ALTERAR IDIOMA
# ══════════════════════════════════════════════════════════════════════════════
@ui.page("/alterar_idioma")
def page_alterar_idioma():
    if not state["usuario"] or state["is_admin"]:
        ui.navigate.to("/")
        return

    nome = state["usuario"]
    pos  = busca_usuario(nome)
    lista_u = load_usuarios()
    info = lista_u[pos]

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-indigo-50 to-purple-50 p-6"):
        with ui.row().classes("w-full max-w-lg mx-auto justify-between items-center mb-4"):
            ui.label("🌍 Alterar Idioma").classes("text-2xl font-bold text-indigo-700")
            ui.button("← Voltar", on_click=lambda: ui.navigate.to("/menu")).classes(BTN_GRAY + " w-auto")

        with ui.card().classes(CARD_CLS):
            ui.label(f"Idioma atual: {info['cod_idioma']}").classes("text-gray-600 mb-4")
            idiomas = [i["codigo"] for i in load_idiomas()]
            sel = ui.select(idiomas, label="Novo idioma", value=info["cod_idioma"]).classes("w-full mb-4")
            msg = ui.label("").classes(MSG_INFO)

            def confirmar():
                novo = sel.value
                if novo == info["cod_idioma"]:
                    msg.set_text("Esse já é o seu idioma atual.")
                    msg.classes(replace=MSG_ERR)
                    return
                lista = load_usuarios()
                lista[pos]["cod_idioma"] = novo
                lista[pos]["nivel"] = 1
                lista[pos]["pontos_atual"] = 0
                save_usuarios(lista)
                msg.set_text(f"✅ Idioma alterado para {novo}! Nível e pontos reiniciados.")
                msg.classes(replace=MSG_OK)

            ui.button("Confirmar alteração", on_click=confirmar).classes(BTN_PRIMARY)


# ══════════════════════════════════════════════════════════════════════════════
#  RANKING
# ══════════════════════════════════════════════════════════════════════════════
@ui.page("/ranking")
def page_ranking():
    if not state["usuario"] or state["is_admin"]:
        ui.navigate.to("/")
        return

    nome = state["usuario"]
    pos  = busca_usuario(nome)
    lista = load_usuarios()
    proprio = lista[pos]["cod_idioma"]

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-indigo-50 to-purple-50 p-6"):
        with ui.row().classes("w-full max-w-lg mx-auto justify-between items-center mb-4"):
            ui.label("🏆 Ranking").classes("text-2xl font-bold text-indigo-700")
            ui.button("← Voltar", on_click=lambda: ui.navigate.to("/menu")).classes(BTN_GRAY + " w-auto")

        ranking_area = ui.column().classes("w-full max-w-lg mx-auto")

        def mostrar_ranking(modo):
            ranking_area.clear()
            lista_att = load_usuarios()
            if modo == "idioma":
                filtrado = [p for p in lista_att if p["cod_idioma"] == proprio and p["codigo"] != 0]
                titulo = f"Ranking — {proprio}"
            else:
                filtrado = [p for p in lista_att if p["codigo"] != 0]
                titulo = "Ranking — Geral"

            filtrado.sort(key=lambda u: u["pontos_atual"], reverse=True)

            with ranking_area:
                with ui.card().classes(CARD_CLS):
                    ui.label(titulo).classes("text-lg font-semibold text-gray-700 mb-3")
                    medals = ["🥇", "🥈", "🥉"]
                    for i, u in enumerate(filtrado):
                        medal = medals[i] if i < 3 else f"{i+1}°"
                        destaque = "font-bold text-indigo-700" if u["codigo"] == nome else "text-gray-700"
                        with ui.row().classes("w-full justify-between items-center py-1 border-b border-gray-100"):
                            ui.label(f"{medal} {u['nome']}").classes(destaque)
                            ui.label(f"{u['pontos_atual']} pts").classes("text-gray-500 text-sm")

        with ui.card().classes(CARD_CLS + " mb-4"):
            with ui.row().classes("gap-2"):
                ui.button(f"Meu idioma ({proprio})", on_click=lambda: mostrar_ranking("idioma")).classes(BTN_PRIMARY + " flex-1")
                ui.button("Geral", on_click=lambda: mostrar_ranking("geral")).classes(BTN_SUCCESS + " flex-1")

        mostrar_ranking("idioma")


# ══════════════════════════════════════════════════════════════════════════════
#  CERTIFICADO
# ══════════════════════════════════════════════════════════════════════════════
@ui.page("/certificado")
def page_certificado():
    if not state["usuario"] or state["is_admin"]:
        ui.navigate.to("/")
        return

    nome = state["usuario"]
    pos  = busca_usuario(nome)
    lista = load_usuarios()
    info  = lista[pos]

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-indigo-50 to-purple-50 p-6"):
        with ui.row().classes("w-full max-w-lg mx-auto justify-between items-center mb-4"):
            ui.label("🎓 Certificado").classes("text-2xl font-bold text-indigo-700")
            ui.button("← Voltar", on_click=lambda: ui.navigate.to("/menu")).classes(BTN_GRAY + " w-auto")

        with ui.card().classes(CARD_CLS + " text-center"):
            if info["nivel"] >= 5:
                ui.label("🏆").classes("text-6xl mb-2")
                ui.label("Certificado de Conclusão").classes("text-2xl font-bold text-indigo-700")
                ui.label(f"Parabéns, {nome}!").classes("text-xl text-gray-700 mt-2")
                ui.label(f"Você concluiu o curso de {info['cod_idioma']}!").classes("text-gray-600")
                ui.label(f"Pontuação final: {info['pontos_atual']} pontos").classes("text-indigo-600 font-semibold mt-2")
            else:
                ui.label("🔒").classes("text-5xl mb-2")
                ui.label("Certificado não disponível").classes("text-xl font-bold text-gray-600")
                ui.label(f"Você está no nível {info['nivel']}. Alcance o nível 5 para obter o certificado.").classes("text-gray-500 mt-2")
                nivel_restante = 5 - info["nivel"]
                ui.label(f"Faltam {nivel_restante} nível(is)!").classes("text-amber-600 font-semibold")


# ══════════════════════════════════════════════════════════════════════════════
#  PAINEL ADMIN
# ══════════════════════════════════════════════════════════════════════════════
@ui.page("/admin")
def page_admin():
    if not state["is_admin"]:
        ui.navigate.to("/")
        return

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-gray-100 to-slate-200 p-6"):
        with ui.row().classes("w-full max-w-2xl mx-auto justify-between items-center mb-6"):
            ui.label("⚙️ Painel Admin").classes("text-2xl font-bold text-slate-700")
            ui.button("Sair", on_click=lambda: ui.navigate.to("/")).classes(BTN_DANGER + " w-auto px-4")

        with ui.card().classes("w-full max-w-2xl mx-auto shadow-lg rounded-xl p-6 bg-white"):
            ui.label("Gerenciar").classes("text-lg font-semibold text-gray-700 mb-4")
            with ui.grid(columns=3).classes("w-full gap-3"):
                ui.button("👥 Usuários",   on_click=lambda: ui.navigate.to("/admin/usuarios")).classes(BTN_PRIMARY)
                ui.button("🌐 Idiomas",    on_click=lambda: ui.navigate.to("/admin/idiomas")).classes(BTN_PRIMARY)
                ui.button("📝 Palavras",   on_click=lambda: ui.navigate.to("/admin/palavras")).classes(BTN_PRIMARY)


# ── Admin: Usuários ────────────────────────────────────────────────────────────
@ui.page("/admin/usuarios")
def page_admin_usuarios():
    if not state["is_admin"]:
        ui.navigate.to("/")
        return

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-gray-100 to-slate-200 p-6"):
        with ui.row().classes("w-full max-w-3xl mx-auto justify-between items-center mb-4"):
            ui.label("👥 Gerenciar Usuários").classes("text-2xl font-bold text-slate-700")
            ui.button("← Admin", on_click=lambda: ui.navigate.to("/admin")).classes(BTN_GRAY + " w-auto")

        # ── Inserir ──
        with ui.card().classes("w-full max-w-3xl mx-auto shadow rounded-xl p-5 bg-white mb-4"):
            ui.label("➕ Inserir Usuário").classes("text-lg font-semibold mb-3")
            inp_nome  = ui.input("Nome / Código").classes("w-full")
            inp_senha = ui.input("Senha").classes("w-full")
            idiomas = [i["codigo"] for i in load_idiomas()]
            sel_idioma = ui.select(idiomas, label="Idioma").classes("w-full")
            msg_ins = ui.label("").classes(MSG_INFO)

            def inserir_usuario():
                nome  = inp_nome.value.strip()
                senha = inp_senha.value.strip()
                idioma = sel_idioma.value
                if not nome or not senha or not idioma:
                    msg_ins.set_text("Preencha todos os campos.")
                    msg_ins.classes(replace=MSG_ERR)
                    return
                if busca_usuario(nome) is not None:
                    msg_ins.set_text("Usuário já existe.")
                    msg_ins.classes(replace=MSG_ERR)
                    return
                lista = load_usuarios()
                novo = {"codigo": nome, "nome": nome, "senha": senha,
                        "cod_idioma": idioma, "nivel": 1, "pontos_atual": 0}
                lista.append(novo)
                save_usuarios(lista)
                msg_ins.set_text(f"✅ Usuário '{nome}' inserido!")
                msg_ins.classes(replace=MSG_OK)
                atualizar_tabela()

            ui.button("Inserir", on_click=inserir_usuario).classes(BTN_SUCCESS + " mt-2")

        # ── Remover ──
        with ui.card().classes("w-full max-w-3xl mx-auto shadow rounded-xl p-5 bg-white mb-4"):
            ui.label("🗑️ Remover Usuário").classes("text-lg font-semibold mb-3")
            inp_rem = ui.input("Código do usuário").classes("w-full")
            msg_rem = ui.label("").classes(MSG_INFO)

            def remover_usuario():
                codigo = inp_rem.value.strip()
                pos = busca_usuario(codigo)
                if pos is None:
                    msg_rem.set_text("Usuário não encontrado.")
                    msg_rem.classes(replace=MSG_ERR)
                    return
                lista = load_usuarios()
                lista[pos]["codigo"] = 0
                save_usuarios(lista)
                msg_rem.set_text(f"✅ Usuário '{codigo}' removido.")
                msg_rem.classes(replace=MSG_OK)
                atualizar_tabela()

            ui.button("Remover", on_click=remover_usuario).classes(BTN_DANGER + " mt-2")

        # ── Tabela ──
        with ui.card().classes("w-full max-w-3xl mx-auto shadow rounded-xl p-5 bg-white"):
            ui.label("📋 Lista de Usuários").classes("text-lg font-semibold mb-3")
            tabela_area = ui.column().classes("w-full")

            def atualizar_tabela():
                tabela_area.clear()
                lista = load_usuarios()
                ativos = [u for u in lista if u["codigo"] != 0]
                with tabela_area:
                    cols = [
                        {"name": "codigo",      "label": "Código",   "field": "codigo"},
                        {"name": "cod_idioma",  "label": "Idioma",   "field": "cod_idioma"},
                        {"name": "nivel",       "label": "Nível",    "field": "nivel"},
                        {"name": "pontos_atual","label": "Pontos",   "field": "pontos_atual"},
                    ]
                    ui.table(columns=cols, rows=ativos, row_key="codigo").classes("w-full")

            atualizar_tabela()


# ── Admin: Idiomas ─────────────────────────────────────────────────────────────
@ui.page("/admin/idiomas")
def page_admin_idiomas():
    if not state["is_admin"]:
        ui.navigate.to("/")
        return

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-gray-100 to-slate-200 p-6"):
        with ui.row().classes("w-full max-w-3xl mx-auto justify-between items-center mb-4"):
            ui.label("🌐 Gerenciar Idiomas").classes("text-2xl font-bold text-slate-700")
            ui.button("← Admin", on_click=lambda: ui.navigate.to("/admin")).classes(BTN_GRAY + " w-auto")

        with ui.card().classes("w-full max-w-3xl mx-auto shadow rounded-xl p-5 bg-white mb-4"):
            ui.label("➕ Inserir Idioma").classes("text-lg font-semibold mb-3")
            inp_idioma = ui.input("Nome do idioma").classes("w-full")
            msg_id = ui.label("").classes(MSG_INFO)

            def inserir_idioma():
                nome = inp_idioma.value.strip()
                if not nome:
                    msg_id.set_text("Digite um nome.")
                    msg_id.classes(replace=MSG_ERR)
                    return
                with open(JSON_IDIOMA_INDEX, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                for i in dados["idiomas"]:
                    if i["codigo"].lower() == nome.lower():
                        msg_id.set_text("Idioma já existe.")
                        msg_id.classes(replace=MSG_ERR)
                        return
                dados["idiomas"].append({"codigo": nome, "descricao": nome})
                with open(JSON_IDIOMA_INDEX, "w", encoding="utf-8") as f:
                    json.dump(dados, f, indent=4, ensure_ascii=False)
                msg_id.set_text(f"✅ Idioma '{nome}' inserido!")
                msg_id.classes(replace=MSG_OK)
                atualizar_idiomas()

            ui.button("Inserir", on_click=inserir_idioma).classes(BTN_SUCCESS + " mt-2")

        with ui.card().classes("w-full max-w-3xl mx-auto shadow rounded-xl p-5 bg-white"):
            ui.label("📋 Idiomas cadastrados").classes("text-lg font-semibold mb-3")
            idiomas_area = ui.column().classes("w-full")

            def atualizar_idiomas():
                idiomas_area.clear()
                lista = load_idiomas()
                with idiomas_area:
                    for i in lista:
                        with ui.row().classes("w-full border-b border-gray-100 py-1"):
                            ui.label(i["codigo"]).classes("text-gray-700")

            atualizar_idiomas()


# ── Admin: Palavras ────────────────────────────────────────────────────────────
@ui.page("/admin/palavras")
def page_admin_palavras():
    if not state["is_admin"]:
        ui.navigate.to("/")
        return

    with ui.column().classes("min-h-screen w-full bg-gradient-to-br from-gray-100 to-slate-200 p-6"):
        with ui.row().classes("w-full max-w-3xl mx-auto justify-between items-center mb-4"):
            ui.label("📝 Gerenciar Palavras").classes("text-2xl font-bold text-slate-700")
            ui.button("← Admin", on_click=lambda: ui.navigate.to("/admin")).classes(BTN_GRAY + " w-auto")

        with ui.card().classes("w-full max-w-3xl mx-auto shadow rounded-xl p-5 bg-white mb-4"):
            ui.label("➕ Inserir Palavra").classes("text-lg font-semibold mb-3")
            inp_desc  = ui.input("Palavra no idioma estrangeiro").classes("w-full")
            inp_trad  = ui.input("Tradução (Português)").classes("w-full")
            idiomas   = [i["codigo"] for i in load_idiomas()]
            sel_id    = ui.select(idiomas, label="Idioma").classes("w-full")
            inp_nivel = ui.number("Nível (1–5)", value=1, min=1, max=5).classes("w-full")
            msg_p     = ui.label("").classes(MSG_INFO)

            def inserir_palavra():
                desc  = inp_desc.value.strip()
                trad  = inp_trad.value.strip()
                idiom = sel_id.value
                nvl   = int(inp_nivel.value)
                if not desc or not trad or not idiom:
                    msg_p.set_text("Preencha todos os campos.")
                    msg_p.classes(replace=MSG_ERR)
                    return
                lista = load_palavras()
                novo = {"codigo": desc, "cod_idioma": idiom,
                        "nivel": nvl, "descricao": desc, "traducao": trad}
                lista.append(novo)
                save_palavras(lista)
                msg_p.set_text(f"✅ Palavra '{desc}' inserida!")
                msg_p.classes(replace=MSG_OK)
                atualizar_palavras()

            ui.button("Inserir", on_click=inserir_palavra).classes(BTN_SUCCESS + " mt-2")

        with ui.card().classes("w-full max-w-3xl mx-auto shadow rounded-xl p-5 bg-white"):
            ui.label("📋 Palavras cadastradas").classes("text-lg font-semibold mb-3")
            palavras_area = ui.column().classes("w-full")

            def atualizar_palavras():
                palavras_area.clear()
                lista = load_palavras()
                x =1
                if x==0:
                    x+=1
                with palavras_area:
                    cols = [
                        {"name": "descricao",  "label": "Palavra",   "field": "descricao"},
                        {"name": "traducao",   "label": "Tradução",  "field": "traducao"},
                        {"name": "cod_idioma", "label": "Idioma",    "field": "cod_idioma"},
                        {"name": "nivel",      "label": "Nível",     "field": "nivel"},
                    ]
                    ui.table(columns=cols, rows=lista, row_key="codigo").classes("w-full")

            atualizar_palavras()


# ══════════════════════════════════════════════════════════════════════════════
#  INICIAR
# ══════════════════════════════════════════════════════════════════════════════
ui.run(title="Idioma App", port=8080, reload=False)
