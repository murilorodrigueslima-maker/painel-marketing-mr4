"""
Painel de Marketing — MR4 Distribuidora
Para uso de: Murilo (Marketing) + Fabiana (Vendas)
Comando: streamlit run integracoes/painel_marketing.py
"""

import streamlit as st
import json
import os
import urllib.request
from datetime import date, datetime, timedelta

# ── Config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Marketing MR4",
    page_icon="📣",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Login ───────────────────────────────────────────────────────────────────
SENHA_CORRETA = "mr4marketing"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
    <style>
      body, .stApp { background-color: #0f172a; color: #e2e8f0; }
      .login-box {
        max-width: 380px;
        margin: 100px auto;
        background: #1e293b;
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        border: 1px solid #334155;
      }
      .login-box h2 { color: #f97316; margin-bottom: 8px; }
      .login-box p  { color: #94a3b8; font-size: 14px; margin-bottom: 24px; }
    </style>
    <div class="login-box">
      <h2>📣 MR4 Marketing</h2>
      <p>Painel exclusivo da equipe MR4 Distribuidora</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("🔑 Senha de acesso", type="password", placeholder="Digite a senha...")
        if st.button("Entrar", use_container_width=True, type="primary"):
            if senha == SENHA_CORRETA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
    st.stop()

# ── Persistência (JSON local) ───────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marketing_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"calendario": {}, "kpis": {}, "reativacao": {}, "notas": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── GestãoClick API ─────────────────────────────────────────────────────────
GC_BASE = "https://api.gestaoclick.com"

def _gc_get(endpoint, access, secret):
    req = urllib.request.Request(
        GC_BASE + endpoint,
        headers={"access-token": access, "secret-access-token": secret, "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_clientes_reativacao(access, secret):
    hoje = datetime.today()
    data_corte = (hoje - timedelta(days=120)).strftime("%Y-%m-%d")
    orfaos = ["murilo", "swyanne", "liandro"]

    # 1) Coletar vendas dos últimos 120 dias
    ultima_compra = {}
    try:
        meta = _gc_get(f"/vendas?pagina=1&limite=1&data_inicio={data_corte}", access, secret)
        total_pag = meta["meta"]["total_paginas"]
        for pag in range(1, min(total_pag + 1, 30)):
            resp = _gc_get(f"/vendas?pagina={pag}&limite=100&data_inicio={data_corte}", access, secret)
            for v in resp["data"]:
                cid = v["cliente_id"]
                sit = v.get("nome_situacao", "")
                if sit in ["Concretizada", "Confirmado", "Faturado", "Concluído"]:
                    if cid not in ultima_compra or v["data"] > ultima_compra[cid]["data"]:
                        ultima_compra[cid] = {"data": v["data"], "valor": float(v.get("valor_total") or 0)}
    except Exception:
        pass

    # 2) Coletar todos os clientes
    clientes = {}
    try:
        meta2 = _gc_get("/clientes?pagina=1&limite=1", access, secret)
        total_pag2 = meta2["meta"]["total_paginas"]
        for pag in range(1, total_pag2 + 1):
            resp = _gc_get(f"/clientes?pagina={pag}&limite=100", access, secret)
            for c in resp["data"]:
                end = c.get("enderecos", [{}])
                end_data = end[0].get("endereco", {}) if end else {}
                clientes[c["id"]] = {
                    "nome": c["nome"],
                    "vendedor": c.get("nome_vendedor", "").lower().strip(),
                    "cidade": end_data.get("nome_cidade", ""),
                    "estado": end_data.get("estado", ""),
                }
    except Exception:
        return []

    # 3) Calcular dias sem comprar e montar lista da Fabiana
    lista = []
    for cid, cdata in clientes.items():
        vend = cdata["vendedor"]
        eh_fabiana = "fabiana" in vend
        eh_orfao   = any(o in vend for o in orfaos)
        eh_ademir  = "ademir" in vend

        uc = ultima_compra.get(cid)
        if uc:
            dias = (hoje - datetime.strptime(uc["data"], "%Y-%m-%d")).days
            valor_ult = uc["valor"]
        else:
            dias = 999
            valor_ult = 0

        if (eh_fabiana or eh_orfao) and dias >= 45:
            origem = "Fabiana" if eh_fabiana else "Órfão"
        elif eh_ademir and dias >= 120:
            origem = "Ademir→Fabiana"
        else:
            continue

        prioridade = "🟡 Em risco" if dias < 120 else "🔴 Inativo"
        cidade_fmt = f"{cdata['cidade']}/{cdata['estado']}" if cdata['cidade'] else "—"

        lista.append({
            "id": cid,
            "cliente": cdata["nome"],
            "cidade": cidade_fmt,
            "ultimo": f"{dias} dias" if dias < 900 else "120+ dias",
            "historico": valor_ult,
            "prioridade": prioridade,
            "origem": origem,
            "dias": dias,
        })

    lista.sort(key=lambda x: (0 if "risco" in x["prioridade"] else 1, -x["historico"]))
    return lista

data = load_data()

# ── Estilos ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  body, .stApp { background-color: #0f172a; color: #e2e8f0; }
  .block-container { padding: 1.5rem 2rem; }
  h1, h2, h3 { color: #f1f5f9; }
  .stTabs [data-baseweb="tab"] { color: #94a3b8; font-size: 15px; font-weight: 600; }
  .stTabs [aria-selected="true"] { color: #f97316 !important; border-bottom: 2px solid #f97316; }
  .card {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 4px solid #f97316;
  }
  .card-green  { border-left-color: #22c55e; }
  .card-blue   { border-left-color: #3b82f6; }
  .card-yellow { border-left-color: #eab308; }
  .card-red    { border-left-color: #ef4444; }
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 700;
  }
  .badge-green  { background:#166534; color:#bbf7d0; }
  .badge-yellow { background:#713f12; color:#fef08a; }
  .badge-gray   { background:#1e293b; color:#94a3b8; border:1px solid #334155; }
  .badge-blue   { background:#1e3a5f; color:#93c5fd; }
  .badge-red    { background:#7f1d1d; color:#fca5a5; }
  .metric-box {
    background: #1e293b;
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
  }
  .metric-val { font-size: 26px; font-weight: 800; color: #f97316; }
  .metric-lbl { font-size: 12px; color: #64748b; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("## 📣 Painel de Marketing · MR4 Distribuidora")
    hoje = date.today()
    st.markdown(f"<span style='color:#64748b'>{hoje.strftime('%A, %d/%m/%Y').capitalize()}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salvar tudo", use_container_width=True):
        save_data(data)
        st.success("Salvo!")

st.divider()

# ── Conteúdo do calendário ──────────────────────────────────────────────────
CALENDARIO = [
    {
        "id":"c01","data":"23/03","dia":"Seg","tipo":"POST","titulo":"Conheça a MR4 Distribuidora","resp":"Murilo","semana":1,
        "objetivo": "Apresentar a empresa para novos seguidores e reforçar credibilidade",
        "formato": "Imagem carrossel (3-5 slides) ou foto do galpão com equipe",
        "roteiro": "Slide 1: Logo MR4 + frase de impacto\nSlide 2: 'Somos distribuidores de acessórios automotivos para lojistas e instaladores do Nordeste'\nSlide 3: Produtos principais (foto do estoque: LED, alto-falantes, multimídias)\nSlide 4: Diferenciais — Entrega rápida · Sem burocracia · WhatsApp direto\nSlide 5: CTA — 'Chama a gente no WhatsApp e peça sua tabela de preços'",
        "copy": "🏭 A MR4 Distribuidora chegou no Instagram!\n\nSe você tem loja de acessórios automotivos ou faz instalação de som no Nordeste, você precisa nos conhecer.\n\nDistribuímos:\n✅ Lâmpadas LED Fênix\n✅ Alto-falantes Nano e Bomber\n✅ Multimídias automotivas\n✅ Molduras de painel\n\nSem enrolação. Sem burocracia. Você chama no WhatsApp, a gente atende e entrega. 🚀\n\n👇 Link na bio para falar com a gente agora.",
        "hashtags": "#acessoriosautomotivos #distribuidora #ledautomotivo #nordeste #fortaleza #ceara #lojadeacessorios #instaladordesom #mr4distribuidora",
        "prazo_producao": "Gravar/montar na terça 18/03",
        "obs": "Usar fotos reais do galpão e dos produtos. Evitar imagens de banco de dados."
    },
    {
        "id":"c02","data":"24/03","dia":"Ter","tipo":"REELS","titulo":"Tour no Galpão","resp":"Murilo","semana":1,
        "objetivo": "Gerar prova de existência e eliminar desconfiança de compra online",
        "formato": "Vídeo vertical 9:16 · Duração: 30-45 segundos · Câmera na mão (estilo espontâneo)",
        "roteiro": "0-3s: Câmera aponta pro estoque cheio — VOZ: 'Deixa eu te mostrar o estoque da MR4 hoje...'\n3-15s: Passeio mostrando prateleiras — LED Fênix, Alto-falantes Nano/Bomber, Multimídias, Molduras\nVOZ: 'Aqui ó, lâmpadas LED Fênix. Aqui os Bomber. Aqui as multimídias, tudo com nota fiscal, tudo pronto pra sair hoje.'\n15-25s: VOZ: 'A gente mostra o estoque porque muita gente tem medo de comprar online e cair em golpe. Aqui é empresa de verdade, com estrutura de verdade.'\n25-35s: CTA — 'Você é lojista ou instalador no Nordeste? Chama no WhatsApp. Link na bio.'",
        "copy": "📦 Quer ver com quem você tá negociando?\n\nAqui está nosso estoque hoje — sem filtro, sem edição.\n\nLED Fênix ✅ | Alto-falantes Nano e Bomber ✅ | Multimídias ✅ | Molduras ✅\n\nTudo com nota fiscal. Tudo com entrega rápida pro Nordeste.\n\n💬 Chama no WhatsApp e peça sua tabela de preços!\n\n👇 Link na bio.",
        "hashtags": "#distribuidora #estoque #acessoriosautomotivos #ledautomotivo #bomberaudio #nordeste #fornecedor #mr4distribuidora",
        "prazo_producao": "Gravar na quarta 19/03 cedo — editar na tarde",
        "obs": "Gravar de manhã com boa iluminação natural. Mostrar variedade. Falar com naturalidade, não precisa ser perfeito."
    },
    {
        "id":"c03","data":"25/03","dia":"Qua","tipo":"POST","titulo":"Top 3 produtos para sua loja","resp":"Murilo","semana":1,
        "objetivo": "Educar o lojista sobre produtos de alto giro — gerar interesse em comprar",
        "formato": "Carrossel 4 slides ou post único com layout de ranking",
        "roteiro": "Slide 1: '🏆 Top 3 produtos que mais giram em lojas de acessórios no Nordeste'\nSlide 2: '1º LUGAR — Lâmpada LED Fênix' + foto do produto + 'Alta demanda, fácil de vender, ótima margem para revenda'\nSlide 3: '2º LUGAR — Alto-falante Bomber' + foto + 'O mais pedido por instaladores. Sai todo dia.'\nSlide 4: '3º LUGAR — Multimídia Automotiva' + foto + 'Produto que fideliza cliente. Quem compra, volta.' + CTA",
        "copy": "🏆 Top 3 produtos que mais giram nas lojas de acessórios do Nordeste:\n\n1️⃣ Lâmpada LED Fênix — Alta procura, fácil de vender, boa margem\n2️⃣ Alto-falante Bomber — O favorito dos instaladores. Sai todo dia.\n3️⃣ Multimídia Automotiva — Produto que fideliza. Quem instala, recomenda.\n\nTodos disponíveis agora na MR4 com preço de distribuidor e entrega pra todo o Nordeste.\n\n💬 Chama no WhatsApp e peça os preços!\n👇 Link na bio.",
        "hashtags": "#acessoriosautomotivos #ledfenix #bomber #multimidia #revenda #nordeste #instaladorsom #mr4distribuidora",
        "prazo_producao": "Montar na quinta 20/03",
        "obs": "Usar fotos reais dos produtos. Se possível, mostrar o produto na mão ou em prateleira."
    },
    {
        "id":"c04","data":"26/03","dia":"Qui","tipo":"STORIES","titulo":"Bastidores + Enquete","resp":"Fabiana","semana":1,
        "objetivo": "Engajar a audiência e entender o que os seguidores precisam",
        "formato": "3-5 stories consecutivos",
        "roteiro": "Story 1: Foto ou vídeo rápido do movimento do dia — 'Sábado tem expediente na MR4 💪'\nStory 2: Mostrar separação de pedido ou produto em destaque — 'Olha o que saiu hoje...'\nStory 3: ENQUETE — 'Qual produto você tem mais dificuldade de encontrar perto de você?' Opções: LED | Alto-falante | Multimídia | Outro\nStory 4: Caixa de perguntas — 'Me conta: você tem loja de acessórios ou faz instalação?'\nStory 5: CTA — 'Quer trabalhar com a gente? Link na bio 👇'",
        "copy": "Use linguagem informal nos stories. Não precisa de copy longa — stories são curtos e diretos.",
        "hashtags": "Não usar hashtags em stories — usar localização: Fortaleza, CE",
        "prazo_producao": "Gravar e postar no momento — stories são espontâneos",
        "obs": "Fabiana pode gravar isso com o próprio celular durante o expediente. Quanto mais espontâneo, melhor."
    },
    {
        "id":"c05","data":"28/03","dia":"Sáb","tipo":"POST","titulo":"Pedido feito, pedido entregue","resp":"Murilo","semana":1,
        "objetivo": "Mostrar agilidade e confiabilidade na entrega — eliminar objeção de prazo",
        "formato": "Foto do motoboy/entrega + produto ou print de confirmação de envio",
        "roteiro": "Imagem principal: Motoboy com produto ou caixa pronta para envio\nTexto sobreposto: 'Pedido feito hoje → Saiu hoje'\nDetalhe: mostrar nota fiscal junto se possível",
        "copy": "⚡ Na MR4 é assim:\n\nPediu pela manhã → Separamos → Saiu no mesmo dia.\n\nSem esperar dias. Sem enrolação. Sem desculpa de 'tá em separação'.\n\nNosso motoboy já tá na rua. Seu estoque não precisa parar. 🏍️\n\nAtendemos lojistas e instaladores em todo o Nordeste.\n💬 Chama no WhatsApp — Link na bio.",
        "hashtags": "#entregarapida #distribuidora #acessoriosautomotivos #nordeste #fortaleza #mr4distribuidora #atacado",
        "prazo_producao": "Fotografar na sexta 21/03 ou segunda cedo",
        "obs": "Tirar foto real do motoboy ou da separação de pedido. Autenticidade vale mais que produção."
    },
    {
        "id":"c06","data":"29/03","dia":"Dom","tipo":"REELS","titulo":"Unboxing LED Fênix","resp":"Murilo","semana":1,
        "objetivo": "Mostrar o produto em detalhe e gerar desejo de revenda",
        "formato": "Vídeo vertical 9:16 · 30-40 segundos · Mão abrindo embalagem e mostrando produto",
        "roteiro": "0-3s: Mão pega a caixa do LED Fênix — TEXT NA TELA: 'O produto que mais vende na sua loja...'\n3-15s: Abre a embalagem, mostra o produto, acende o LED se possível\nVOZ: 'Essa é a lâmpada LED Fênix. Olha a qualidade. Olha o encaixe. É isso que tá saindo toda semana nas lojas que trabalham com a gente.'\n15-25s: Mostra preço de custo vs sugestão de revenda (se quiser revelar margem)\nVOZ: 'Você compra por X, revende por Y. Simples assim.'\n25-35s: CTA — 'Quer ter esse produto na sua loja? Chama a MR4 no WhatsApp.'",
        "copy": "💡 Você já conhece a LED Fênix?\n\nEsse produto está saindo toda semana das lojas que trabalham com a gente.\n\n✅ Qualidade comprovada\n✅ Preço competitivo para revenda\n✅ Alta rotatividade\n\nSe você tem loja de acessórios ou faz instalação, esse produto tem que estar no seu estoque.\n\n💬 Chama no WhatsApp e peça o preço de distribuidor!\n👇 Link na bio.",
        "hashtags": "#ledfenix #ledautomotivo #acessoriosautomotivos #unboxing #revenda #distribuidora #mr4distribuidora",
        "prazo_producao": "Gravar na segunda 24/03",
        "obs": "Gravar com boa iluminação para mostrar o brilho do LED. Pode usar música animada no fundo."
    },
    {
        "id":"c07","data":"30/03","dia":"Seg","tipo":"POST","titulo":"Como montar vitrine de LED","resp":"Murilo","semana":2,
        "objetivo": "Educar o lojista — conteúdo que o cliente DO SEU CLIENTE consome. Posiciona MR4 como parceiro estratégico",
        "formato": "Carrossel 5-6 slides com dicas práticas",
        "roteiro": "Slide 1: 'Como montar uma vitrine de LED que vende sozinha 💡'\nSlide 2: '1. Organize por aplicação' — Ex: LEDs para farol, LEDs para interior, LEDs para placa\nSlide 3: '2. Mostre o produto aceso' — Cliente precisa ver o resultado antes de comprar\nSlide 4: '3. Coloque o preço de forma clara' — Sem preço, o cliente passa direto\nSlide 5: '4. Tenha variedade de encaixe' — H4, H7, H11... cada carro pede um tipo\nSlide 6: 'Precisa de estoque de LED pra montar sua vitrine? A MR4 tem tudo. Chama no WhatsApp 👇'",
        "copy": "💡 Dica para lojistas: Sua vitrine de LED está vendendo ou só decorando?\n\nUma vitrine bem montada aumenta as vendas sem você precisar convencer ninguém.\n\nDesliza e veja como fazer ➡️\n\n🏪 Precisa de estoque de LED com preço de distribuidor? A MR4 entrega pra você no Nordeste.\n💬 Chama no WhatsApp — Link na bio.",
        "hashtags": "#dicasparalojistas #vitrineled #acessoriosautomotivos #ledautomotivo #dicas #lojadeacessorios #mr4distribuidora",
        "prazo_producao": "Montar na terça 25/03",
        "obs": "Conteúdo educativo tem mais compartilhamento. Lojistas vão salvar esse post. Isso aumenta o alcance orgânico."
    },
    {
        "id":"c08","data":"31/03","dia":"Ter","tipo":"REELS","titulo":"Quanto você lucra revendendo?","resp":"Murilo","semana":2,
        "objetivo": "Mostrar a margem de revenda de forma concreta — principal gatilho para lojista pedir tabela",
        "formato": "Vídeo vertical 9:16 · 30-40s · Pessoa falando pra câmera ou texto animado",
        "roteiro": "0-3s: TEXT GRANDE NA TELA: 'Quanto você lucra revendendo LED automotivo?'\n3-10s: VOZ: 'Vou te mostrar um exemplo real...'\n10-25s: Mostrar na tela ou falar: 'Você compra a lâmpada LED Fênix no atacado. Revende na sua loja pelo preço de varejo. A diferença vai pro seu bolso — sem precisar de muito espaço, sem produto pesado, sem complicação.'\n25-35s: VOZ: 'Se você tem loja de acessórios ou faz instalação e ainda não trabalha com a MR4, tá deixando dinheiro na mesa. Chama a gente no WhatsApp.'",
        "copy": "💰 Você já calculou quanto lucra revendendo acessórios automotivos?\n\nProduto leve. Alta demanda. Boa margem. Rotatividade garantida.\n\nLojistas que trabalham com a MR4 têm acesso a:\n✅ Preço de distribuidor\n✅ Produtos de alto giro\n✅ Entrega rápida no Nordeste\n✅ Sem pedido mínimo alto\n\nVem descobrir quanto você pode lucrar. 💬 Chama no WhatsApp!\n👇 Link na bio.",
        "hashtags": "#revendaacessorios #lucrocomrevenda #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora #empreendedor",
        "prazo_producao": "Gravar na quarta 26/03",
        "obs": "Não precisa revelar preços exatos — o objetivo é gerar curiosidade e fazer o lojista chamar no WhatsApp."
    },
    {
        "id":"c09","data":"01/04","dia":"Qua","tipo":"POST","titulo":"O que nossos clientes dizem","resp":"Fabiana","semana":2,
        "objetivo": "Prova social — o depoimento de um cliente convence mais do que qualquer copy",
        "formato": "Print de conversa do WhatsApp (com permissão) ou foto do cliente na loja + texto",
        "roteiro": "Opção A: Print de elogio ou feedback positivo de cliente no WhatsApp\nOpção B: Foto do cliente na loja dele com produtos MR4 + depoimento escrito\nTexto sobreposto: Nome do cliente, cidade e o que ele disse",
        "copy": "[USE O DEPOIMENTO REAL DO CLIENTE AQUI]\n\nEssa é a realidade de quem trabalha com a MR4 Distribuidora. 🙌\n\nAtendemos lojistas e instaladores em todo o Nordeste com agilidade, preço justo e sem burocracia.\n\n💬 Quer ser o próximo? Chama no WhatsApp!\n👇 Link na bio.",
        "hashtags": "#depoimento #clientesatisfeito #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora",
        "prazo_producao": "Fabiana pede autorização ao cliente até quinta 27/03",
        "obs": "IMPORTANTE: Pedir autorização ao cliente antes de postar. Pode ser um print sem mostrar número de telefone."
    },
    {
        "id":"c10","data":"04/04","dia":"Sáb","tipo":"POST","titulo":"Programa de Indicação — Lançamento","resp":"Murilo","semana":2,
        "objetivo": "Ativar a base de clientes para indicar novos lojistas — crescimento orgânico",
        "formato": "Post único com layout chamativo ou carrossel de 2-3 slides",
        "roteiro": "Slide 1: '🎁 LANÇAMENTO — Programa de Indicação MR4'\nSlide 2: 'Como funciona:\n1. Você indica um lojista ou instalador\n2. Ele faz o primeiro pedido\n3. Você ganha 5% de crédito na sua próxima compra'\nSlide 3: 'Simples assim. Você indica, a gente cuida do resto, e você ainda ganha em cima.'",
        "copy": "🎁 Apresentando o Programa de Indicação MR4!\n\nSe você já trabalha com a gente e conhece outros lojistas ou instaladores que precisam de um bom fornecedor...\n\nÉ simples:\n👉 Você indica\n👉 Ele faz o primeiro pedido\n👉 Você ganha 5% de crédito na próxima compra\n\nSem burocracia. Sem limite de indicações.\n\n💬 Manda mensagem pra gente no WhatsApp dizendo quem indicou e o nome do novo cliente.\n👇 Link na bio.",
        "hashtags": "#programadeindicacao #mr4distribuidora #acessoriosautomotivos #distribuidora #nordeste #parceria",
        "prazo_producao": "Montar na sexta 28/03 — comunicar para base via WhatsApp também no mesmo dia",
        "obs": "Além do post, enviar mensagem direta no WhatsApp para os 8 clientes ativos avisando do programa."
    },
    {
        "id":"c11","data":"05/04","dia":"Dom","tipo":"REELS","titulo":"Nano vs Bomber — Qual escolher?","resp":"Murilo","semana":2,
        "objetivo": "Educar instaladores sobre diferença entre produtos — aumentar confiança técnica da MR4",
        "formato": "Vídeo vertical 9:16 · 40-50s · Comparativo com os dois produtos na mão",
        "roteiro": "0-3s: Dois alto-falantes lado a lado — TEXT: 'Nano ou Bomber? Qual colocar no carro do seu cliente?'\n3-20s: VOZ: 'A linha Nano é mais compacta, ideal para carros menores e quem quer qualidade com custo acessível. Já o Bomber é mais robusto, potência maior, pra quem quer mais volume e graves.'\n20-35s: 'Os dois têm boa saída. A diferença tá no perfil do cliente e no que você quer oferecer.'\n35-45s: CTA — 'A MR4 distribui os dois. Chama no WhatsApp e a gente te ajuda a montar seu estoque.'",
        "copy": "🔊 Nano ou Bomber? Essa dúvida bate em todo instalador na hora de indicar pro cliente.\n\nDesliza e entende a diferença ➡️\n\n✅ Linha Nano — Compacto, qualidade, custo-benefício\n✅ Bomber — Mais potência, mais volume, mais graves\n\nOs dois estão disponíveis na MR4 com preço de distribuidor.\n\n💬 Chama no WhatsApp e monta seu estoque!\n👇 Link na bio.",
        "hashtags": "#altofante #bomber #nano #somautomotivo #instaladorsom #acessoriosautomotivos #mr4distribuidora",
        "prazo_producao": "Gravar na segunda 31/03 com os dois produtos em mãos",
        "obs": "Falar com autoridade técnica. Esse conteúdo será salvo e compartilhado por instaladores."
    },
    {
        "id":"c12","data":"06/04","dia":"Seg","tipo":"POST","titulo":"Os números de quem revende LED Fênix","resp":"Murilo","semana":3,
        "objetivo": "Mostrar resultado concreto de revenda — gatilho de prova social com números",
        "formato": "Post com layout de dados/infográfico simples",
        "roteiro": "Layout com fundo escuro e números em destaque:\n'📊 Números reais de quem revende LED Fênix com a MR4:\n• Produto mais pedido nas lojas de acessórios do Nordeste\n• Alta margem de revenda por unidade\n• Tempo médio de giro: menos de 30 dias\n• Zero devolução por defeito de fábrica'",
        "copy": "📊 Você sabia que a LED Fênix é um dos produtos com melhor giro para lojas de acessórios do Nordeste?\n\nQuem trabalha com esse produto na MR4 sabe:\n✅ Sai rápido do estoque\n✅ Boa margem por unidade\n✅ Cliente volta pra comprar mais\n\nSe você ainda não tem esse produto na sua loja, tá perdendo venda toda semana.\n\n💬 Chama no WhatsApp e peça o preço de distribuidor!\n👇 Link na bio.",
        "hashtags": "#ledfenix #ledautomotivo #revenda #distribuidora #acessoriosautomotivos #nordeste #mr4distribuidora",
        "prazo_producao": "Montar na terça 01/04",
        "obs": "Se tiver dados reais de quantas unidades vendeu no mês, use. Números reais são mais poderosos."
    },
    {
        "id":"c13","data":"07/04","dia":"Ter","tipo":"REELS","titulo":"Bastidores — Um dia na MR4","resp":"Murilo","semana":3,
        "objetivo": "Humanizar a marca. Mostrar equipe, rotina, estrutura. Gera confiança e conexão",
        "formato": "Vídeo vertical 9:16 · 45-60s · Compilado de cenas do dia",
        "roteiro": "0-5s: Abertura do galpão de manhã\n5-15s: Equipe chegando, separação de pedidos\n15-25s: Estoquista organizando produtos\n25-35s: Vendedora atendendo no WhatsApp\n35-45s: Motoboy saindo com entregas\n45-55s: Pedido chegando e cliente confirmando\n55-60s: TEXT FINAL: 'Esse é o time MR4. Trabalhando pra fazer seu estoque girar. 💪'\nCTA: Chama no WhatsApp",
        "copy": "Um dia normal aqui na MR4 Distribuidora. ☀️\n\nAbertura, separação de pedidos, atendimento no WhatsApp, saída das entregas...\n\nEnquanto você tá dormindo, a gente já tá organizando o seu pedido. 💪\n\nÉ assim que a gente trabalha — com agilidade e sem burocracia.\n\n💬 Quer fazer parte disso? Chama no WhatsApp!\n👇 Link na bio.",
        "hashtags": "#bastidores #rotina #distribuidora #acessoriosautomotivos #equipe #mr4distribuidora #nordeste",
        "prazo_producao": "Gravar durante o dia 02/04 (quarta) — editar na quinta cedo",
        "obs": "Pedir pra equipe agir naturalmente. Não precisa posar. Quanto mais real, mais engajamento gera."
    },
    {
        "id":"c14","data":"08/04","dia":"Qua","tipo":"POST","titulo":"Multimídia automotiva — produto que fideliza","resp":"Murilo","semana":3,
        "objetivo": "Destacar multimídia como produto estratégico para lojistas que querem ticket maior",
        "formato": "Foto do produto + carrossel com benefícios",
        "roteiro": "Slide 1: Foto da multimídia + 'O produto que faz o cliente voltar'\nSlide 2: 'Por que vender multimídia?' — Ticket mais alto · Instalação paga · Cliente volta pro serviço\nSlide 3: 'Disponível na MR4 — Preço de distribuidor + Entrega no Nordeste'\nSlide 4: CTA",
        "copy": "📱 Quer aumentar o ticket médio da sua loja?\n\nA multimídia automotiva é o produto que faz isso acontecer:\n\n✅ Ticket de venda mais alto\n✅ O cliente paga a instalação junto\n✅ Gera fidelização — quem instala, recomenda\n✅ Alta demanda em todo o Nordeste\n\nA MR4 distribui com preço competitivo e entrega rápida.\n\n💬 Quer colocar multimídia no seu mix? Chama no WhatsApp!\n👇 Link na bio.",
        "hashtags": "#multimidia #multimidiaautomotiva #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora #instalacao",
        "prazo_producao": "Montar na quinta 03/04",
        "obs": "Focar no benefício para o lojista (ticket maior), não apenas nas especificações técnicas do produto."
    },
    {
        "id":"c15","data":"11/04","dia":"Sáb","tipo":"POST","titulo":"Vocês falaram, a gente ouviu","resp":"Murilo","semana":3,
        "objetivo": "Mostrar que a empresa ouve os clientes — responder enquete dos stories da semana 1",
        "formato": "Post único com resultado da enquete + resposta da empresa",
        "roteiro": "Publicar o resultado da enquete dos stories (22/03) sobre qual produto o cliente tem mais dificuldade de encontrar.\nMostrar qual produto ganhou e dizer que a MR4 tem estoque desse produto.\nTransformar o feedback em argumento de venda.",
        "copy": "📊 Na semana passada perguntamos: qual produto você tem mais dificuldade de encontrar perto de você?\n\nVocês responderam! E a resposta foi: [RESULTADO DA ENQUETE]\n\nBoa notícia: temos esse produto em estoque, com preço de distribuidor e entrega rápida pro Nordeste. 😊\n\nContinue mandando suas dúvidas e necessidades — a gente tá ouvindo.\n\n💬 Chama no WhatsApp para fazer seu pedido!\n👇 Link na bio.",
        "hashtags": "#feedback #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora",
        "prazo_producao": "Verificar resultado da enquete dos stories no final de semana — montar post no domingo 06/04",
        "obs": "DEPENDE da enquete dos stories do dia 22/03. Fabiana precisa salvar o resultado antes de sumir."
    },
    {
        "id":"c16","data":"12/04","dia":"Dom","tipo":"REELS","titulo":"Kit revenda para loja pequena","resp":"Murilo","semana":3,
        "objetivo": "Apresentar ideia de kit de produtos para lojista iniciante ou loja pequena — reduz barreira de entrada",
        "formato": "Vídeo vertical 9:16 · 35-45s · Produtos montados numa bancada ou caixa",
        "roteiro": "0-3s: Câmera mostrando produtos organizados — TEXT: 'Quer começar a vender acessórios automotivos? Começa por aqui.'\n3-20s: VOZ: 'A gente montou um kit de produtos que fazem sentido pra qualquer loja pequena de acessórios. LED Fênix, um par de Nano, uma multimídia básica e algumas molduras. Produtos que giram. Produtos que o cliente chega pedindo.'\n20-35s: VOZ: 'Você não precisa de um estoque gigante pra começar. Começa com o que vende e vai aumentando.'\n35-45s: CTA — 'Quer saber o preço desse kit? Chama a MR4 no WhatsApp.'",
        "copy": "🏪 Tem loja pequena de acessórios e não sabe por onde começar o estoque?\n\nA gente montou um kit pensado pra você:\n\n✅ LED Fênix — alto giro, boa margem\n✅ Alto-falante Nano — o mais pedido\n✅ Multimídia básica — ticket maior\n✅ Molduras de painel — complemento essencial\n\nVocê não precisa de muito espaço nem de muito investimento pra começar.\n\n💬 Chama no WhatsApp e pergunta pelo Kit Revenda MR4!\n👇 Link na bio.",
        "hashtags": "#kitrevenda #lojapequeña #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora #empreendedor",
        "prazo_producao": "Separar os produtos pra foto/vídeo na segunda 07/04 — gravar na terça cedo",
        "obs": "Montar visualmente os produtos juntos numa bancada para o vídeo ter mais impacto."
    },
    {
        "id":"c17","data":"13/04","dia":"Seg","tipo":"POST","titulo":"⚡ Kit Relâmpago MR4","resp":"Murilo","semana":4,
        "objetivo": "Gerar urgência e vendas rápidas com oferta especial de tempo limitado",
        "formato": "Post único com layout de oferta — cores chamativas, prazo visível",
        "roteiro": "Layout com fundo laranja ou vermelho:\n'⚡ KIT RELÂMPAGO — Só até sexta-feira!'\n3 produtos em combo com preço especial\nCTA: 'Chama no WhatsApp AGORA — estoque limitado'\nContagem: 'Válido até 11/04'",
        "copy": "⚡ KIT RELÂMPAGO MR4 — Só até sexta!\n\nCombo especial de produtos mais pedidos com preço de atacado:\n\n🔦 LED Fênix\n🔊 Alto-falante Nano\n📱 Moldura de painel\n\n⏰ Oferta válida até sexta-feira 11/04 ou enquanto durar o estoque.\n\nNão precisa de pedido mínimo alto. Entregamos em todo o Nordeste.\n\n💬 Chama AGORA no WhatsApp — Link na bio.\n\n⚠️ Estoque limitado.",
        "hashtags": "#promocao #kitrelampago #mr4distribuidora #acessoriosautomotivos #distribuidora #nordeste #oferta",
        "prazo_producao": "Montar na terça 08/04 — postar na quarta às 8h",
        "obs": "Criar urgência real. Se possível, definir quantidades limitadas de verdade. Não fazer promoção falsa."
    },
    {
        "id":"c18","data":"14/04","dia":"Ter","tipo":"REELS","titulo":"Março em números — resultados reais","resp":"Murilo","semana":4,
        "objetivo": "Mostrar crescimento e resultados do mês — gera credibilidade e prova social",
        "formato": "Vídeo vertical 9:16 · 30-40s · Números aparecendo na tela com animação simples",
        "roteiro": "0-5s: TEXT GRANDE: 'Março foi assim na MR4 👇'\n5-20s: Números um a um: X pedidos entregues | X lojistas atendidos | X cidades do Nordeste\n20-30s: VOZ ou TEXT: 'Crescendo junto com quem confia na gente. Obrigado a cada cliente que escolheu a MR4 em março.'\n30-40s: CTA — 'Quer fazer parte em abril? Chama no WhatsApp.'",
        "copy": "📈 Março foi histórico pra MR4!\n\n[X] pedidos entregues\n[X] lojistas atendidos\n[X] cidades no Nordeste\n\nCada número é um lojista que confiou na gente. E a gente vai continuar merecendo essa confiança em abril. 💪\n\nVocê ainda não trabalha com a MR4? Abril é uma boa hora pra começar.\n\n💬 Link na bio — Chama no WhatsApp!",
        "hashtags": "#resultados #crescimento #mr4distribuidora #distribuidora #nordeste #acessoriosautomotivos",
        "prazo_producao": "Levantar números reais até quarta 09/04 — gravar e editar na quinta cedo",
        "obs": "Usar números reais. Mesmo que modestos, autenticidade gera mais confiança que números inflados."
    },
    {
        "id":"c19","data":"15/04","dia":"Qua","tipo":"POST","titulo":"Você ainda não trabalha com a MR4?","resp":"Murilo","semana":4,
        "objetivo": "Capturar quem acompanha mas ainda não comprou — post de conversão direta",
        "formato": "Post direto com texto forte e CTA claro",
        "roteiro": "Imagem com texto:\n'Se você tem loja de acessórios ou faz instalação no Nordeste e ainda não trabalha com a MR4...\nA gente precisa conversar.'\nLogo abaixo: lista de diferenciais e CTA",
        "copy": "Se você tem loja de acessórios automotivos ou faz instalação de som no Nordeste e ainda não trabalha com a MR4...\n\nA gente precisa conversar. 😄\n\nO que você vai encontrar aqui:\n✅ Preço de distribuidor (sem pagar preço de varejo)\n✅ Produtos que giram — LED, Alto-falante, Multimídia, Moldura\n✅ Entrega rápida pro Nordeste\n✅ Atendimento direto no WhatsApp — sem robô, sem burocracia\n✅ Equipe real, galpão real, nota fiscal em tudo\n\nNão precisa de pedido gigante pra começar. Vem conversar.\n\n💬 Link na bio → WhatsApp direto.",
        "hashtags": "#lojadeacessorios #instaladorsom #distribuidora #acessoriosautomotivos #nordeste #mr4distribuidora #fornecedor",
        "prazo_producao": "Montar na quinta 10/04",
        "obs": "Post de conversão direta. Usar foto do galpão ou equipe como imagem de fundo para reforçar credibilidade."
    },
    {
        "id":"c20","data":"18/04","dia":"Sáb","tipo":"POST","titulo":"Março foi assim — balanço do mês","resp":"Murilo","semana":4,
        "objetivo": "Consolidar a imagem de empresa em crescimento — gera confiança para novos clientes",
        "formato": "Carrossel 3-4 slides com balanço visual do mês",
        "roteiro": "Slide 1: 'Março 2026 na MR4 — Balanço do mês 📊'\nSlide 2: Números do mês (pedidos, cidades, clientes novos)\nSlide 3: 'O que aprendemos em março:' — produto mais pedido, região que mais comprou, feedback dos clientes\nSlide 4: 'Abril vai ser ainda melhor. Vem com a gente.' + CTA",
        "copy": "📊 Março 2026 — Balanço MR4\n\nFoi um mês de crescimento, novos clientes e novos estados atendidos.\n\n🏆 Produto mais pedido: LED Fênix\n📍 Região mais ativa: Ceará\n🤝 Novos clientes: [X]\n\nObrigado a cada lojista e instalador que confiou no nosso trabalho. Vocês são o motivo de cada caixa que sai daqui. 🙏\n\nAbril chegou — e a gente tá pronto pra mais.\n\n💬 Link na bio.",
        "hashtags": "#balancomensal #crescimento #mr4distribuidora #acessoriosautomotivos #nordeste #distribuidora",
        "prazo_producao": "Levantar dados do mês no final de semana — montar no domingo 13/04",
        "obs": "Usar dados reais. Incluir agradecimento genuíno à base de clientes."
    },
    {
        "id":"c21","data":"19/04","dia":"Dom","tipo":"REELS","titulo":"Por que lojistas escolhem a MR4","resp":"Murilo","semana":4,
        "objetivo": "Post de fechamento de ciclo — consolidar posicionamento e gerar novos leads",
        "formato": "Vídeo vertical 9:16 · 40-50s · Murilo ou vendedor falando direto pra câmera",
        "roteiro": "0-3s: Olhar direto pra câmera — 'Você já se perguntou por que lojistas do Nordeste estão trocando de fornecedor pra MR4?'\n3-25s: VOZ: 'A resposta é simples. A gente atende rápido, sem burocracia. Você chama no WhatsApp, a gente responde. Você pede, a gente entrega. Sem esperar dias, sem enrolação, sem pedido mínimo absurdo.'\n25-40s: 'Lojistas e instaladores do Ceará, Piauí, Rio Grande do Norte e Paraíba já estão trabalhando com a gente. E os resultados aparecem na semana seguinte.'\n40-50s: CTA — 'Quer ser o próximo? Chama agora. Link na bio.'",
        "copy": "Por que lojistas do Nordeste estão escolhendo a MR4 como fornecedor?\n\nNão é mágica. É simples:\n\n✅ Atendimento rápido no WhatsApp\n✅ Sem burocracia pra fechar pedido\n✅ Produtos que giram na sua loja\n✅ Entrega que sai no mesmo dia\n✅ Empresa real, nota fiscal em tudo\n\nCE · PI · RN · PB — a gente entrega onde você está.\n\n💬 Chama no WhatsApp e veja como é fácil trabalhar com a MR4.\n👇 Link na bio.",
        "hashtags": "#fornecedorconfiavel #distribuidora #acessoriosautomotivos #nordeste #mr4distribuidora #lojista #instaladorsom",
        "prazo_producao": "Gravar na segunda 14/04 — editar na terça cedo",
        "obs": "Esse é o post de fechamento dos 30 dias. Falar com confiança e autoridade. Resultado do ciclo todo."
    },
]

REATIVACAO_BASE = [
    {"id":"r01","cliente":"KAYO LED","cidade":"Sobral/CE","ultimo":"101 dias","historico":53313,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r02","cliente":"VITOR SOM EQUIPADORA","cidade":"Itaitinga/CE","ultimo":"80 dias","historico":9622,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r03","cliente":"JUNIOR SOM","cidade":"Redenção/CE","ultimo":"99 dias","historico":6767,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r04","cliente":"ALLAN TRANSPORTES","cidade":"Fortaleza/CE","ultimo":"93 dias","historico":6607,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r05","cliente":"AUTOPECAS & SERVICOS RJ","cidade":"Umirim/CE","ultimo":"107 dias","historico":5695,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r06","cliente":"STOPFILM","cidade":"Fortaleza/CE","ultimo":"97 dias","historico":5311,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r07","cliente":"NATANAEL LIMA","cidade":"/","ultimo":"113 dias","historico":4290,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r08","cliente":"JAJA SOM E ACESSORIOS LTDA","cidade":"Fortaleza/CE","ultimo":"80 dias","historico":4090,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r09","cliente":"MT SERVIÇO","cidade":"Caucaia/CE","ultimo":"79 dias","historico":2355,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r10","cliente":"FRANCISCO ISRAEL BRUNO MARTINS PARENTE","cidade":"Hidrolândia/CE","ultimo":"94 dias","historico":1492,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r11","cliente":"JAMACARU AUTOPECAS","cidade":"Missão Velha/CE","ultimo":"49 dias","historico":1472,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r12","cliente":"DELIO FEITOSA FILHO","cidade":"Teresina/PI","ultimo":"61 dias","historico":1417,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r13","cliente":"LOPES VEICULOS CONCEITO","cidade":"Fortaleza/CE","ultimo":"106 dias","historico":1398,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r14","cliente":"KAQUERA TALENTO AUTOMOTIVO","cidade":"Taquaritinga do Norte/PE","ultimo":"48 dias","historico":1143,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r15","cliente":"AL CAR","cidade":"Fortaleza/CE","ultimo":"86 dias","historico":1040,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r16","cliente":"Supreme Peças e Acessórios","cidade":"Fortaleza/CE","ultimo":"112 dias","historico":1012,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r17","cliente":"PEDRO FUMÊ","cidade":"Iguatu/CE","ultimo":"93 dias","historico":906,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r18","cliente":"LABORATORIO AUTOMOTIVO","cidade":"Fortaleza/CE","ultimo":"90 dias","historico":864,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r19","cliente":"VIVI SOM","cidade":"Fortaleza/CE","ultimo":"66 dias","historico":769,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r20","cliente":"FORCA LIVRE RACING PECAS E SERVICOS","cidade":"Fortaleza/CE","ultimo":"52 dias","historico":719,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r21","cliente":"GAMBARINI SERVICOS AUTOMOTIVOS","cidade":"Eusébio/CE","ultimo":"91 dias","historico":664,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r22","cliente":"REVIZZI AUTO CENTER","cidade":"Picos/PI","ultimo":"57 dias","historico":643,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r23","cliente":"EMPÓRIO LEDS","cidade":"Pedra Branca/CE","ultimo":"57 dias","historico":634,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r24","cliente":"BROTHES CAR SERVICE","cidade":"Fortaleza/CE","ultimo":"90 dias","historico":506,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r25","cliente":"SPEED","cidade":"Aracati/CE","ultimo":"48 dias","historico":491,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r26","cliente":"C2 ACESSORIOS","cidade":"Fortaleza/CE","ultimo":"59 dias","historico":487,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r27","cliente":"ALISSON FUME E ACESSORIOS","cidade":"Caucaia/CE","ultimo":"52 dias","historico":481,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r28","cliente":"GARAGE020","cidade":"Maracanaú/CE","ultimo":"87 dias","historico":433,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r29","cliente":"BROTHER´S SOM E ACESSORIOS","cidade":"Fortaleza/CE","ultimo":"48 dias","historico":426,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r30","cliente":"RS LEDS","cidade":"Fortaleza/CE","ultimo":"72 dias","historico":395,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r31","cliente":"HYEDY SOM E ACESSORIOS","cidade":"Caridade/CE","ultimo":"56 dias","historico":285,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r32","cliente":"Rodrigo severo Diniz","cidade":"Maracanaú/CE","ultimo":"73 dias","historico":261,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r33","cliente":"Dalyson De Queiroz Barros","cidade":"Fortaleza/CE","ultimo":"49 dias","historico":256,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r34","cliente":"CENTER FAROIS","cidade":"Fortaleza/CE","ultimo":"56 dias","historico":211,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r35","cliente":"TOP LEDS","cidade":"Natal/RN","ultimo":"45 dias","historico":200,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r36","cliente":"PLAY MOTO PREMIUM","cidade":"Fortaleza/CE","ultimo":"92 dias","historico":178,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r37","cliente":"Leonardo gomes da silva","cidade":"Fortaleza/CE","ultimo":"64 dias","historico":173,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r38","cliente":"ADEMIR MARTINS FELIX JUNIOR","cidade":"Fortaleza/CE","ultimo":"49 dias","historico":168,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r39","cliente":"ALESSANDRO MONTEIRO DOS SANTOS LTDA","cidade":"Fortim/CE","ultimo":"50 dias","historico":164,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r40","cliente":"EMANOEL SOM","cidade":"Fortaleza/CE","ultimo":"57 dias","historico":154,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r41","cliente":"José Veloso Filho","cidade":"/","ultimo":"45 dias","historico":138,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r42","cliente":"Antônio Rodrigues Pereira Filho","cidade":"Fortaleza/CE","ultimo":"55 dias","historico":96,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r43","cliente":"BRAYN GLASS POLIMENTO DE VIDRO E FAROL","cidade":"Horizonte/CE","ultimo":"48 dias","historico":80,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r44","cliente":"JUNINHO LAVSCAR","cidade":"Fortaleza/CE","ultimo":"72 dias","historico":72,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r45","cliente":"W.S FILM","cidade":"Fortaleza/CE","ultimo":"55 dias","historico":61,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r46","cliente":"MAX STYLE","cidade":"Fortaleza/CE","ultimo":"58 dias","historico":60,"prioridade":"🟡 Em risco","origem":"Fabiana"},
    {"id":"r47","cliente":"THIAAGO ACESSÓRIOS","cidade":"Fortaleza/CE","ultimo":"51 dias","historico":29,"prioridade":"🟡 Em risco","origem":"Órfão"},
    {"id":"r48","cliente":"MAX BASS EQUIPADORA","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":19493,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r49","cliente":"Alan kayvison Queiroz de oliveira","cidade":"Pacatuba/CE","ultimo":"120+ dias","historico":17106,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r50","cliente":"Magno Ernesto Teixeira","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":16201,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r51","cliente":"GENAINA XIMENES MOREIRA","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":13697,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r52","cliente":"ALLAN CRISTYAN OLIVEIRA DE PAULA","cidade":"/","ultimo":"120+ dias","historico":12970,"prioridade":"🔴 Inativo","origem":"Fabiana"},
    {"id":"r53","cliente":"BC PRODUTOS AUTOMOTIVOS","cidade":"Madalena/CE","ultimo":"120+ dias","historico":8877,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r54","cliente":"KING ACESSORIOS AUTOMOTIVO","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":8465,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r55","cliente":"BRASIL CAR PINTURAS AUTOMOTIVAS","cidade":"Juazeiro do Norte/CE","ultimo":"120+ dias","historico":8418,"prioridade":"🔴 Inativo","origem":"Fabiana"},
    {"id":"r56","cliente":"PINTURAS AUTOMOTIVAS","cidade":"Solonópole/CE","ultimo":"120+ dias","historico":8418,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r57","cliente":"ITALO SOM","cidade":"Maracanaú/CE","ultimo":"120+ dias","historico":7306,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r58","cliente":"LUB CENTER CARIRE","cidade":"Cariré/CE","ultimo":"120+ dias","historico":6926,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r59","cliente":"PADRÃO 55 / GARAGEM55","cidade":"Aracati/CE","ultimo":"120+ dias","historico":6320,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r60","cliente":"SUED CAR SHOP","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":5993,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r61","cliente":"ATS TRANSPORTES","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":5453,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r62","cliente":"REMAQ","cidade":"Joaquim Pires/PI","ultimo":"120+ dias","historico":5368,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r63","cliente":"ALEX CAR","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":5330,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r64","cliente":"MFLEDS","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":4205,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r65","cliente":"ALEX AN CAR","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":4104,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r66","cliente":"ROBERTO SOM","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":3907,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r67","cliente":"Francisco Jhonantan ferreira Freitas","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":3880,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r68","cliente":"V W MANUTENCAO E SERVICOS","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":3795,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r69","cliente":"Oficina o Chico Juan Laureano Mesquita","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":3385,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r70","cliente":"TOP GEAR FILM","cidade":"Caucaia/CE","ultimo":"120+ dias","historico":3361,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r71","cliente":"HELIO ACESSORIOS","cidade":"Redenção/CE","ultimo":"120+ dias","historico":3350,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r72","cliente":"AJ ACESSORIOS","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":3343,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r73","cliente":"Guilherme de mesquita Rodrigues","cidade":"Fortaleza/CE","ultimo":"120+ dias","historico":3300,"prioridade":"🔴 Inativo","origem":"Órfão"},
    {"id":"r74","cliente":"CARLINHOS FUMÊ 2024","cidade":"Maracanaú/CE","ultimo":"120+ dias","historico":3246,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
    {"id":"r75","cliente":"MARLON MICASSIO SILVESTRE","cidade":"Ubajara/CE","ultimo":"120+ dias","historico":3164,"prioridade":"🔴 Inativo","origem":"Ademir→Fabiana"},
]

STATUS_CONTENT = ["⬜ Pendente","🎬 Gravando","✏️ Editando","✅ Publicado","❌ Cancelado"]
STATUS_REATIV  = ["⬜ Pendente","🟡 Contatado","🟢 Respondeu","✅ Comprou","❌ Sem retorno"]
TIPO_CORES = {"POST":"badge-blue","REELS":"badge-red","STORIES":"badge-yellow"}

# ── Abas ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Hoje & Esta Semana",
    "🗓️ Calendário 30 Dias",
    "📊 KPIs Semanais",
    "📞 Reativação de Clientes",
    "🔄 Relatório Semanal",
])

# ═══════════════════════════════════════════════════
# ABA 1 — HOJE & ESTA SEMANA
# ═══════════════════════════════════════════════════
with tab1:
    hoje_str = hoje.strftime("%d/%m")
    dia_semana_hoje = hoje.strftime("%a").capitalize()[:3]

    # Detecta semana atual
    semanas = {
        1: ("19/03","25/03","ATIVAR o que está parado"),
        2: ("26/03","01/04","POSICIONAR como referência"),
        3: ("02/04","08/04","ENGAJAR a comunidade"),
        4: ("09/04","17/04","CONVERTER e medir"),
    }
    semana_atual = 1
    try:
        d = hoje
        if date(2026,3,26) <= d <= date(2026,4,1):  semana_atual = 2
        elif date(2026,4,2) <= d <= date(2026,4,8):  semana_atual = 3
        elif date(2026,4,9) <= d <= date(2026,4,17): semana_atual = 4
    except Exception:
        pass

    sem_info = semanas[semana_atual]

    st.markdown(f"""
    <div class='card'>
      <b style='font-size:18px'>📍 Semana {semana_atual} de 4</b>
      &nbsp;&nbsp;<span style='color:#94a3b8'>{sem_info[0]} → {sem_info[1]}</span><br>
      <span style='color:#f97316;font-size:15px'>Foco: <b>{sem_info[2]}</b></span>
    </div>
    """, unsafe_allow_html=True)

    # Conteúdo de hoje
    hoje_items = [c for c in CALENDARIO if c["data"] == hoje_str]
    semana_items = [c for c in CALENDARIO if c["semana"] == semana_atual]

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("### 🎯 Conteúdo de hoje")
        if hoje_items:
            for item in hoje_items:
                status_key = f"cal_{item['id']}"
                current = data["calendario"].get(status_key, "⬜ Pendente")
                tipo_badge = TIPO_CORES.get(item["tipo"], "badge-gray")

                st.markdown(f"<span class='badge {tipo_badge}'>{item['tipo']}</span>&nbsp;&nbsp;<b style='font-size:15px'>{item['titulo']}</b>", unsafe_allow_html=True)
                novo_status = st.selectbox("Status", STATUS_CONTENT,
                    index=STATUS_CONTENT.index(current),
                    key=f"sel_hoje_{item['id']}")
                if novo_status != current:
                    data["calendario"][status_key] = novo_status
                    save_data(data)

                with st.expander("📋 Ver briefing completo"):
                    st.markdown("**🎯 Objetivo**")
                    st.info(item.get("objetivo","—"))
                    st.markdown("**📐 Formato**")
                    st.markdown(f"> {item.get('formato','—')}")
                    st.markdown("**🎬 Roteiro**")
                    st.markdown(f"""<div class='card card-blue' style='white-space:pre-line;font-size:13px'>{item.get('roteiro','—')}</div>""", unsafe_allow_html=True)
                    st.markdown("**✍️ Copy pronta**")
                    st.code(item.get("copy","—"), language=None)
                    st.markdown("**#️⃣ Hashtags**")
                    st.markdown(f"<span style='color:#64748b;font-size:12px'>{item.get('hashtags','—')}</span>", unsafe_allow_html=True)
                    st.warning(f"⚠️ {item.get('obs','—')}")
        else:
            st.markdown("<div class='card card-green'><span style='color:#22c55e'>✓ Sem postagem programada para hoje</span></div>", unsafe_allow_html=True)

        # Tarefas fixas do dia (vendas)
        st.markdown("### 📋 Tarefas diárias — Fabiana")
        tarefas_dia = [
            "Responder todos os leads no WhatsApp",
            "Fazer 5 contatos de reativação",
            "Registrar pedidos fechados no controle",
            "Verificar leads sem resposta há +2 dias",
        ]
        for t in tarefas_dia:
            tk = f"tarefa_{t[:20]}"
            checked = data["notas"].get(tk + hoje_str, False)
            novo = st.checkbox(t, value=checked, key=f"cb_{tk}")
            if novo != checked:
                data["notas"][tk + hoje_str] = novo
                save_data(data)

    with col_b:
        st.markdown("### 📅 Esta semana completa")
        publicados = sum(1 for c in semana_items if "✅" in data["calendario"].get(f"cal_{c['id']}", ""))
        total = len(semana_items)

        st.markdown(f"""
        <div class='metric-box' style='margin-bottom:16px'>
          <div class='metric-val'>{publicados}/{total}</div>
          <div class='metric-lbl'>Conteúdos publicados esta semana</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(publicados / max(total, 1))

        for item in semana_items:
            status_key = f"cal_{item['id']}"
            current = data["calendario"].get(status_key, "⬜ Pendente")
            cor = "card-green" if "✅" in current else ("card-yellow" if "🎬" in current or "✏️" in current else "")
            tipo_badge = TIPO_CORES.get(item["tipo"], "badge-gray")
            is_hoje = item["data"] == hoje_str
            st.markdown(f"""
            <div class='card {cor}' style='{"border:2px solid #f97316;" if is_hoje else ""}'>
              <b style='color:#94a3b8;font-size:11px'>{item["data"]} {item["dia"]}</b>
              &nbsp;<span class='badge {tipo_badge}'>{item["tipo"]}</span>
              {"&nbsp;<span class='badge badge-yellow'>HOJE</span>" if is_hoje else ""}<br>
              <span style='font-size:13px'>{item["titulo"]}</span><br>
              <span style='font-size:11px;color:#64748b'>{current} · {item["resp"]}</span>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# ABA 2 — CALENDÁRIO 30 DIAS
# ═══════════════════════════════════════════════════
with tab2:
    st.markdown("### 🗓️ Calendário completo — 19 Mar → 17 Abr 2026")

    col_f1, col_f2 = st.columns([1,1])
    with col_f1:
        filtro_semana = st.selectbox("Filtrar por semana", ["Todas","Semana 1","Semana 2","Semana 3","Semana 4"])
    with col_f2:
        filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos","POST","REELS","STORIES"])

    itens_filtrados = CALENDARIO
    if filtro_semana != "Todas":
        n = int(filtro_semana[-1])
        itens_filtrados = [c for c in itens_filtrados if c["semana"] == n]
    if filtro_tipo != "Todos":
        itens_filtrados = [c for c in itens_filtrados if c["tipo"] == filtro_tipo]

    # Métricas resumo
    mc1, mc2, mc3, mc4 = st.columns(4)
    total_cal = len(CALENDARIO)
    pub_cal = sum(1 for c in CALENDARIO if "✅" in data["calendario"].get(f"cal_{c['id']}", ""))
    posts_cal = len([c for c in CALENDARIO if c["tipo"]=="POST"])
    reels_cal = len([c for c in CALENDARIO if c["tipo"]=="REELS"])
    for col, val, lbl in [(mc1, pub_cal, "Publicados"), (mc2, total_cal-pub_cal, "Pendentes"),
                           (mc3, posts_cal, "Posts Feed"), (mc4, reels_cal, "Reels")]:
        col.markdown(f"<div class='metric-box'><div class='metric-val'>{val}</div><div class='metric-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cards de conteúdo com briefing completo
    for item in itens_filtrados:
        status_key = f"cal_{item['id']}"
        current = data["calendario"].get(status_key, "⬜ Pendente")
        tipo_badge = TIPO_CORES.get(item["tipo"], "badge-gray")
        cor_card = "card-green" if "✅" in current else ("card-yellow" if "🎬" in current or "✏️" in current else "")
        is_hoje = item["data"] == hoje.strftime("%d/%m")

        label = f"{'🔴 HOJE · ' if is_hoje else ''}{item['data']} {item['dia']}  ·  {item['tipo']}  ·  {item['titulo']}  ·  {current}"
        with st.expander(label, expanded=is_hoje):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"<span class='badge {tipo_badge}'>{item['tipo']}</span>&nbsp;&nbsp;<b style='font-size:16px'>{item['titulo']}</b>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#64748b;font-size:12px'>📅 {item['data']} {item['dia']} &nbsp;|&nbsp; 👤 Responsável: <b>{item['resp']}</b> &nbsp;|&nbsp; ⏰ Produção: {item.get('prazo_producao','—')}</span>", unsafe_allow_html=True)
                st.markdown("---")

                st.markdown("**🎯 Objetivo**")
                st.info(item.get("objetivo", "—"))

                st.markdown("**📐 Formato**")
                st.markdown(f"> {item.get('formato','—')}")

                st.markdown("**🎬 Roteiro / Instruções de Produção**")
                st.markdown(f"""<div class='card card-blue' style='white-space:pre-line;font-size:13px'>{item.get('roteiro','—')}</div>""", unsafe_allow_html=True)

                st.markdown("**✍️ Copy pronta (legenda para postar)**")
                st.code(item.get("copy", "—"), language=None)

                col_h, col_o = st.columns(2)
                with col_h:
                    st.markdown("**#️⃣ Hashtags**")
                    st.markdown(f"<span style='color:#64748b;font-size:12px'>{item.get('hashtags','—')}</span>", unsafe_allow_html=True)
                with col_o:
                    st.markdown("**⚠️ Observações**")
                    st.warning(item.get("obs", "—"))

            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                novo = st.selectbox("Status", STATUS_CONTENT,
                    index=STATUS_CONTENT.index(current),
                    key=f"cal_sel_{item['id']}")
                if novo != current:
                    data["calendario"][status_key] = novo
                    save_data(data)
                st.markdown(f"""
                <div class='metric-box' style='margin-top:12px'>
                  <div style='font-size:13px;color:#94a3b8'>Semana</div>
                  <div class='metric-val'>{item['semana']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")

# ═══════════════════════════════════════════════════
# ABA 3 — KPIs SEMANAIS
# ═══════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 KPIs Semanais — Preencher toda segunda-feira")

    semana_sel = st.radio("Semana", ["Semana 1 (19-25 Mar)","Semana 2 (26 Mar-1 Abr)","Semana 3 (2-8 Abr)","Semana 4 (9-17 Abr)"],
        horizontal=True)
    sk = semana_sel[:8].replace(" ","_")

    if sk not in data["kpis"]:
        data["kpis"][sk] = {}
    kpi = data["kpis"][sk]

    col_k1, col_k2, col_k3 = st.columns(3)

    with col_k1:
        st.markdown("#### 📦 Vendas")
        kpi["pedidos"]    = st.number_input("Pedidos fechados", min_value=0, value=kpi.get("pedidos",0), key=f"k1_{sk}")
        kpi["faturamento"]= st.number_input("Faturamento (R$)", min_value=0.0, value=float(kpi.get("faturamento",0)), key=f"k2_{sk}", format="%.2f")
        kpi["clientes_novos"] = st.number_input("Clientes novos", min_value=0, value=kpi.get("clientes_novos",0), key=f"k3_{sk}")
        kpi["reativados"] = st.number_input("Clientes reativados", min_value=0, value=kpi.get("reativados",0), key=f"k4_{sk}")
        kpi["indicacoes"] = st.number_input("Indicações recebidas", min_value=0, value=kpi.get("indicacoes",0), key=f"k5_{sk}")

    with col_k2:
        st.markdown("#### 📱 Meta Ads")
        kpi["conversas"]   = st.number_input("Conversas iniciadas", min_value=0, value=kpi.get("conversas",0), key=f"k6_{sk}")
        kpi["custo_conv"]  = st.number_input("Custo/conversa (R$)", min_value=0.0, value=float(kpi.get("custo_conv",0)), key=f"k7_{sk}", format="%.2f")
        kpi["gasto_ads"]   = st.number_input("Gasto total ads (R$)", min_value=0.0, value=float(kpi.get("gasto_ads",0)), key=f"k8_{sk}", format="%.2f")
        kpi["ctr"]         = st.number_input("CTR (%)", min_value=0.0, value=float(kpi.get("ctr",0)), key=f"k9_{sk}", format="%.2f")

    with col_k3:
        st.markdown("#### 📸 Instagram")
        kpi["posts_ig"]   = st.number_input("Posts publicados", min_value=0, value=kpi.get("posts_ig",0), key=f"k10_{sk}")
        kpi["reels_ig"]   = st.number_input("Reels publicados", min_value=0, value=kpi.get("reels_ig",0), key=f"k11_{sk}")
        kpi["stories_ig"] = st.number_input("Stories (dias ativos)", min_value=0, value=kpi.get("stories_ig",0), key=f"k12_{sk}")
        kpi["alcance_ig"] = st.number_input("Alcance total", min_value=0, value=kpi.get("alcance_ig",0), key=f"k13_{sk}")
        kpi["seguidores_novos"] = st.number_input("Seguidores novos", min_value=0, value=kpi.get("seguidores_novos",0), key=f"k14_{sk}")

    kpi["dificuldade"] = st.text_area("⚠️ Principal dificuldade da semana", value=kpi.get("dificuldade",""), key=f"k15_{sk}")
    kpi["funcionou"]   = st.text_area("💡 O que funcionou bem", value=kpi.get("funcionou",""), key=f"k16_{sk}")

    if st.button("💾 Salvar KPIs", key=f"save_kpi_{sk}", use_container_width=True):
        data["kpis"][sk] = kpi
        save_data(data)
        st.success("KPIs salvos!")

    # Resumo acumulado
    if any(data["kpis"].get(f"Semana_{i}", {}).get("pedidos", 0) for i in range(1,5)):
        st.divider()
        st.markdown("#### 📈 Acumulado do mês")
        tot_ped = sum(data["kpis"].get(f"Semana_{i}", {}).get("pedidos", 0) for i in range(1,5))
        tot_fat = sum(data["kpis"].get(f"Semana_{i}", {}).get("faturamento", 0) for i in range(1,5))
        tot_ads = sum(data["kpis"].get(f"Semana_{i}", {}).get("gasto_ads", 0) for i in range(1,5))
        roi = (tot_fat / tot_ads) if tot_ads > 0 else 0
        r1,r2,r3,r4 = st.columns(4)
        for col, val, lbl in [(r1,tot_ped,"Pedidos totais"),(r2,f"R${tot_fat:,.0f}","Faturamento total"),(r3,f"R${tot_ads:,.0f}","Gasto total ads"),(r4,f"{roi:.1f}x","ROI ads")]:
            col.markdown(f"<div class='metric-box'><div class='metric-val'>{val}</div><div class='metric-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# ABA 4 — REATIVAÇÃO DE CLIENTES
# ═══════════════════════════════════════════════════
with tab4:
    st.markdown("### 📞 Reativação de Base de Clientes")
    st.markdown("""
    <div class='card card-yellow'>
    💬 <b>Template de mensagem:</b><br>
    <i>"Oi [NOME]! Tudo bem? Aqui é [SEU NOME] da MR4 😊 Faz um tempinho que a gente não se fala.
    Chegaram produtos novos que costumam girar bem em lojas como a sua. Posso te mandar os detalhes e o preço?"</i>
    </div>
    """, unsafe_allow_html=True)

    # ── Buscar dados ao vivo do GestãoClick ─────────────────────────────────
    gc_access = st.secrets.get("GESTAOCLICK_ACCESS_TOKEN","")
    gc_secret = st.secrets.get("GESTAOCLICK_SECRET_TOKEN","")

    col_info, col_btn = st.columns([4,1])
    with col_btn:
        if st.button("🔄 Atualizar lista", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    lista_viva = []
    if gc_access and gc_secret:
        with st.spinner("⏳ Carregando clientes do GestãoClick... (só demora na 1ª vez, depois fica em cache por 1h)"):
            lista_viva = buscar_clientes_reativacao(gc_access, gc_secret)
        with col_info:
            from datetime import datetime as _dt
            st.caption(f"✅ Dados ao vivo do GestãoClick · {len(lista_viva)} clientes · atualiza a cada 1h")
        if not lista_viva:
            st.warning("⚠️ Não foi possível buscar dados do GestãoClick. Usando lista salva.")
            lista_viva = REATIVACAO_BASE
    else:
        lista_viva = REATIVACAO_BASE
        with col_info:
            st.caption("⚠️ Usando lista local (configure secrets para dados ao vivo)")

    # Filtros
    f1, f2, f3 = st.columns(3)
    filtro_prior = f1.selectbox("Filtrar prioridade", ["Todas","🟡 Em risco","🔴 Inativo"])
    filtro_orig  = f2.selectbox("Filtrar origem", ["Todas","Fabiana","Órfão","Ademir→Fabiana"])
    filtro_status= f3.selectbox("Filtrar status", ["Todos","⬜ Pendente","🟡 Contatado","🟢 Respondeu","✅ Comprou","❌ Sem retorno"])

    lista_filtrada = lista_viva
    if filtro_prior != "Todas":
        lista_filtrada = [c for c in lista_filtrada if c.get("prioridade","") == filtro_prior]
    if filtro_orig != "Todas":
        lista_filtrada = [c for c in lista_filtrada if c.get("origem","") == filtro_orig]
    if filtro_status != "Todos":
        lista_filtrada = [c for c in lista_filtrada if data["reativacao"].get(str(c["id"]),{}).get("status","⬜ Pendente") == filtro_status]

    # Métricas reativação
    total_r  = len(lista_viva)
    risco_r  = sum(1 for c in lista_viva if "risco" in c.get("prioridade",""))
    contat_r = sum(1 for c in lista_viva if data["reativacao"].get(str(c["id"]),{}).get("status","⬜ Pendente") not in ["⬜ Pendente"])
    comprou_r= sum(1 for c in lista_viva if "✅ Comprou" in data["reativacao"].get(str(c["id"]),{}).get("status",""))
    rc1,rc2,rc3,rc4 = st.columns(4)
    for col,val,lbl in [(rc1,total_r,"Total na base"),(rc2,risco_r,"⚠️ Em risco"),(rc3,contat_r,"Contatados"),(rc4,comprou_r,"Compraram")]:
        col.markdown(f"<div class='metric-box'><div class='metric-val'>{val}</div><div class='metric-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown(f"<br><b>{len(lista_filtrada)} clientes exibidos</b>", unsafe_allow_html=True)

    for item in lista_filtrada:
        cid = str(item["id"])
        if cid not in data["reativacao"]:
            data["reativacao"][cid] = {"status":"⬜ Pendente","nota":""}

        r_data = data["reativacao"][cid]
        current_status = r_data.get("status","⬜ Pendente")
        cor = "card-green" if "✅" in current_status else ("card-yellow" if "🟡" in current_status or "🟢" in current_status else "card-red" if "❌" in current_status else "")
        hist = item.get("historico", 0)
        hist_fmt = f"R$ {hist:,.0f}".replace(",",".")

        with st.expander(f"{item.get('prioridade','🔴')} {item['cliente']} — {item['cidade']} | {hist_fmt} · {current_status}"):
            rc1, rc2 = st.columns([2,1])
            with rc1:
                st.markdown(f"**Sem comprar:** {item['ultimo']}")
                st.markdown(f"**Histórico de compras:** {hist_fmt}")
                st.markdown(f"**Carteira:** {item.get('origem','—')}")
                novo_status = st.selectbox("Status do contato", STATUS_REATIV,
                    index=STATUS_REATIV.index(current_status) if current_status in STATUS_REATIV else 0,
                    key=f"reat_sel_{cid}")
                nota = st.text_input("Observação / próximo passo", value=r_data.get("nota",""), key=f"reat_nota_{cid}")
            with rc2:
                st.markdown(f"""
                <div class='card {cor}' style='margin-top:20px'>
                  <b>{item['cliente']}</b><br>
                  <span style='font-size:13px;color:#f97316'>{hist_fmt}</span><br>
                  <span style='font-size:11px;color:#94a3b8'>{item.get('origem','—')} · {current_status}</span>
                </div>
                """, unsafe_allow_html=True)
            if st.button("💾 Salvar", key=f"reat_save_{cid}"):
                data["reativacao"][cid] = {"status": novo_status, "nota": nota}
                save_data(data)
                st.success("Salvo!")
                st.rerun()

# ═══════════════════════════════════════════════════
# ABA 5 — RELATÓRIO SEMANAL
# ═══════════════════════════════════════════════════
with tab5:
    st.markdown("### 🔄 Relatório Semanal — Para enviar ao Consultor IA")
    st.markdown("""
    <div class='card card-blue'>
    📌 <b>Como funciona:</b> Todo <b>segunda-feira antes das 10h</b>, preencha os campos abaixo,
    copie o relatório gerado e cole na conversa com o consultor IA para receber o plano da semana.
    </div>
    """, unsafe_allow_html=True)

    rs1, rs2 = st.columns(2)
    with rs1:
        semana_rel = st.selectbox("Qual semana está reportando?",
            ["Semana 1 (19-25 Mar)","Semana 2 (26 Mar-1 Abr)","Semana 3 (2-8 Abr)","Semana 4 (9-17 Abr)"])
        ped = st.number_input("Pedidos fechados na semana", min_value=0, key="rel_ped")
        fat = st.number_input("Faturamento (R$)", min_value=0.0, key="rel_fat", format="%.2f")
        cn  = st.number_input("Clientes novos", min_value=0, key="rel_cn")
    with rs2:
        custo_c  = st.number_input("Custo/conversa Meta Ads (R$)", min_value=0.0, key="rel_cc", format="%.2f")
        gasto_a  = st.number_input("Gasto total em ads (R$)", min_value=0.0, key="rel_ga", format="%.2f")
        posts_p  = st.number_input("Posts publicados", min_value=0, key="rel_pp")
        reels_p  = st.number_input("Reels publicados", min_value=0, key="rel_rp")
        stories_p= st.number_input("Stories (dias ativos)", min_value=0, key="rel_sp")

    reativ_c = st.number_input("Clientes da base contatados", min_value=0, key="rel_rc")
    reativ_v = st.number_input("Desses, quantos compraram", min_value=0, key="rel_rv")
    dificuldade_r = st.text_area("⚠️ Principal dificuldade da semana", key="rel_dif")
    duvida_r      = st.text_area("❓ Dúvida ou decisão pendente", key="rel_duv")
    funcionou_r   = st.text_area("💡 O que funcionou bem", key="rel_func")

    if st.button("📋 Gerar relatório para copiar", use_container_width=True):
        ticket = (fat / ped) if ped > 0 else 0
        roi_r  = (fat / gasto_a) if gasto_a > 0 else 0
        relatorio = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📣 RELATÓRIO SEMANAL — MR4 DISTRIBUIDORA
{semana_rel}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 VENDAS:
• Pedidos fechados: {ped}
• Faturamento: R$ {fat:,.2f}
• Clientes novos: {cn}
• Ticket médio da semana: R$ {ticket:,.2f}

📱 META ADS:
• Custo/conversa: R$ {custo_c:.2f}
• Gasto total: R$ {gasto_a:,.2f}
• ROI ads: {roi_r:.1f}x

📸 INSTAGRAM:
• Posts publicados: {posts_p}
• Reels publicados: {reels_p}
• Stories ativos: {stories_p} dias

🔄 REATIVAÇÃO:
• Contatos feitos: {reativ_c}
• Compraram: {reativ_v}

⚠️ Dificuldade da semana:
{dificuldade_r if dificuldade_r else "—"}

❓ Dúvida ou decisão:
{duvida_r if duvida_r else "—"}

💡 O que funcionou:
{funcionou_r if funcionou_r else "—"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
        st.code(relatorio, language=None)
        st.success("✅ Copie o texto acima e cole na conversa com o consultor IA!")


