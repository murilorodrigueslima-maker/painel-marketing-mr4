     1→"""
     2→Painel de Marketing — MR4 Distribuidora
     3→Para uso de: Murilo (Marketing) + Fabiana (Vendas)
     4→Comando: streamlit run integracoes/painel_marketing.py
     5→"""
     6→
     7→import streamlit as st
     8→import json
     9→import os
    10→from datetime import date, datetime
    11→
    12→# ── Config ─────────────────────────────────────────────────────────────────
    13→st.set_page_config(
    14→    page_title="Marketing MR4",
    15→    page_icon="📣",
    16→    layout="wide",
    17→    initial_sidebar_state="collapsed",
    18→)
    19→
    20→# ── Persistência (JSON local) ───────────────────────────────────────────────
    21→DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marketing_data.json")
    22→
    23→def load_data():
    24→    if os.path.exists(DATA_FILE):
    25→        with open(DATA_FILE, "r", encoding="utf-8") as f:
    26→            return json.load(f)
    27→    return {"calendario": {}, "kpis": {}, "reativacao": {}, "notas": {}}
    28→
    29→def save_data(data):
    30→    with open(DATA_FILE, "w", encoding="utf-8") as f:
    31→        json.dump(data, f, ensure_ascii=False, indent=2)
    32→
    33→data = load_data()
    34→
    35→# ── Estilos ─────────────────────────────────────────────────────────────────
    36→st.markdown("""
    37→<style>
    38→  body, .stApp { background-color: #0f172a; color: #e2e8f0; }
    39→  .block-container { padding: 1.5rem 2rem; }
    40→  h1, h2, h3 { color: #f1f5f9; }
    41→  .stTabs [data-baseweb="tab"] { color: #94a3b8; font-size: 15px; font-weight: 600; }
    42→  .stTabs [aria-selected="true"] { color: #f97316 !important; border-bottom: 2px solid #f97316; }
    43→  .card {
    44→    background: #1e293b;
    45→    border-radius: 12px;
    46→    padding: 16px 20px;
    47→    margin-bottom: 12px;
    48→    border-left: 4px solid #f97316;
    49→  }
    50→  .card-green  { border-left-color: #22c55e; }
    51→  .card-blue   { border-left-color: #3b82f6; }
    52→  .card-yellow { border-left-color: #eab308; }
    53→  .card-red    { border-left-color: #ef4444; }
    54→  .badge {
    55→    display: inline-block;
    56→    padding: 2px 10px;
    57→    border-radius: 99px;
    58→    font-size: 12px;
    59→    font-weight: 700;
    60→  }
    61→  .badge-green  { background:#166534; color:#bbf7d0; }
    62→  .badge-yellow { background:#713f12; color:#fef08a; }
    63→  .badge-gray   { background:#1e293b; color:#94a3b8; border:1px solid #334155; }
    64→  .badge-blue   { background:#1e3a5f; color:#93c5fd; }
    65→  .badge-red    { background:#7f1d1d; color:#fca5a5; }
    66→  .metric-box {
    67→    background: #1e293b;
    68→    border-radius: 10px;
    69→    padding: 14px 18px;
    70→    text-align: center;
    71→  }
    72→  .metric-val { font-size: 26px; font-weight: 800; color: #f97316; }
    73→  .metric-lbl { font-size: 12px; color: #64748b; margin-top: 4px; }
    74→</style>
    75→""", unsafe_allow_html=True)
    76→
    77→# ── Header ──────────────────────────────────────────────────────────────────
    78→col_h1, col_h2 = st.columns([3, 1])
    79→with col_h1:
    80→    st.markdown("## 📣 Painel de Marketing · MR4 Distribuidora")
    81→    hoje = date.today()
    82→    st.markdown(f"<span style='color:#64748b'>{hoje.strftime('%A, %d/%m/%Y').capitalize()}</span>", unsafe_allow_html=True)
    83→with col_h2:
    84→    st.markdown("<br>", unsafe_allow_html=True)
    85→    if st.button("💾 Salvar tudo", use_container_width=True):
    86→        save_data(data)
    87→        st.success("Salvo!")
    88→
    89→st.divider()
    90→
    91→# ── Conteúdo do calendário ──────────────────────────────────────────────────
    92→CALENDARIO = [
    93→    {
    94→        "id":"c01","data":"19/03","dia":"Qua","tipo":"POST","titulo":"Conheça a MR4 Distribuidora","resp":"Murilo","semana":1,
    95→        "objetivo": "Apresentar a empresa para novos seguidores e reforçar credibilidade",
    96→        "formato": "Imagem carrossel (3-5 slides) ou foto do galpão com equipe",
    97→        "roteiro": "Slide 1: Logo MR4 + frase de impacto\nSlide 2: 'Somos distribuidores de acessórios automotivos para lojistas e instaladores do Nordeste'\nSlide 3: Produtos principais (foto do estoque: LED, alto-falantes, multimídias)\nSlide 4: Diferenciais — Entrega rápida · Sem burocracia · WhatsApp direto\nSlide 5: CTA — 'Chama a gente no WhatsApp e peça sua tabela de preços'",
    98→        "copy": "🏭 A MR4 Distribuidora chegou no Instagram!\n\nSe você tem loja de acessórios automotivos ou faz instalação de som no Nordeste, você precisa nos conhecer.\n\nDistribuímos:\n✅ Lâmpadas LED Fênix\n✅ Alto-falantes Nano e Bomber\n✅ Multimídias automotivas\n✅ Molduras de painel\n\nSem enrolação. Sem burocracia. Você chama no WhatsApp, a gente atende e entrega. 🚀\n\n👇 Link na bio para falar com a gente agora.",
    99→        "hashtags": "#acessoriosautomotivos #distribuidora #ledautomotivo #nordeste #fortaleza #ceara #lojadeacessorios #instaladordesom #mr4distribuidora",
   100→        "prazo_producao": "Gravar/montar na terça 18/03",
   101→        "obs": "Usar fotos reais do galpão e dos produtos. Evitar imagens de banco de dados."
   102→    },
   103→    {
   104→        "id":"c02","data":"20/03","dia":"Qui","tipo":"REELS","titulo":"Tour no Galpão","resp":"Murilo","semana":1,
   105→        "objetivo": "Gerar prova de existência e eliminar desconfiança de compra online",
   106→        "formato": "Vídeo vertical 9:16 · Duração: 30-45 segundos · Câmera na mão (estilo espontâneo)",
   107→        "roteiro": "0-3s: Câmera aponta pro estoque cheio — VOZ: 'Deixa eu te mostrar o estoque da MR4 hoje...'\n3-15s: Passeio mostrando prateleiras — LED Fênix, Alto-falantes Nano/Bomber, Multimídias, Molduras\nVOZ: 'Aqui ó, lâmpadas LED Fênix. Aqui os Bomber. Aqui as multimídias, tudo com nota fiscal, tudo pronto pra sair hoje.'\n15-25s: VOZ: 'A gente mostra o estoque porque muita gente tem medo de comprar online e cair em golpe. Aqui é empresa de verdade, com estrutura de verdade.'\n25-35s: CTA — 'Você é lojista ou instalador no Nordeste? Chama no WhatsApp. Link na bio.'",
   108→        "copy": "📦 Quer ver com quem você tá negociando?\n\nAqui está nosso estoque hoje — sem filtro, sem edição.\n\nLED Fênix ✅ | Alto-falantes Nano e Bomber ✅ | Multimídias ✅ | Molduras ✅\n\nTudo com nota fiscal. Tudo com entrega rápida pro Nordeste.\n\n💬 Chama no WhatsApp e peça sua tabela de preços!\n\n👇 Link na bio.",
   109→        "hashtags": "#distribuidora #estoque #acessoriosautomotivos #ledautomotivo #bomberaudio #nordeste #fornecedor #mr4distribuidora",
   110→        "prazo_producao": "Gravar na quarta 19/03 cedo — editar na tarde",
   111→        "obs": "Gravar de manhã com boa iluminação natural. Mostrar variedade. Falar com naturalidade, não precisa ser perfeito."
   112→    },
   113→    {
   114→        "id":"c03","data":"21/03","dia":"Sex","tipo":"POST","titulo":"Top 3 produtos para sua loja","resp":"Murilo","semana":1,
   115→        "objetivo": "Educar o lojista sobre produtos de alto giro — gerar interesse em comprar",
   116→        "formato": "Carrossel 4 slides ou post único com layout de ranking",
   117→        "roteiro": "Slide 1: '🏆 Top 3 produtos que mais giram em lojas de acessórios no Nordeste'\nSlide 2: '1º LUGAR — Lâmpada LED Fênix' + foto do produto + 'Alta demanda, fácil de vender, ótima margem para revenda'\nSlide 3: '2º LUGAR — Alto-falante Bomber' + foto + 'O mais pedido por instaladores. Sai todo dia.'\nSlide 4: '3º LUGAR — Multimídia Automotiva' + foto + 'Produto que fideliza cliente. Quem compra, volta.' + CTA",
   118→        "copy": "🏆 Top 3 produtos que mais giram nas lojas de acessórios do Nordeste:\n\n1️⃣ Lâmpada LED Fênix — Alta procura, fácil de vender, boa margem\n2️⃣ Alto-falante Bomber — O favorito dos instaladores. Sai todo dia.\n3️⃣ Multimídia Automotiva — Produto que fideliza. Quem instala, recomenda.\n\nTodos disponíveis agora na MR4 com preço de distribuidor e entrega pra todo o Nordeste.\n\n💬 Chama no WhatsApp e peça os preços!\n👇 Link na bio.",
   119→        "hashtags": "#acessoriosautomotivos #ledfenix #bomber #multimidia #revenda #nordeste #instaladorsom #mr4distribuidora",
   120→        "prazo_producao": "Montar na quinta 20/03",
   121→        "obs": "Usar fotos reais dos produtos. Se possível, mostrar o produto na mão ou em prateleira."
   122→    },
   123→    {
   124→        "id":"c04","data":"22/03","dia":"Sáb","tipo":"STORIES","titulo":"Bastidores + Enquete","resp":"Fabiana","semana":1,
   125→        "objetivo": "Engajar a audiência e entender o que os seguidores precisam",
   126→        "formato": "3-5 stories consecutivos",
   127→        "roteiro": "Story 1: Foto ou vídeo rápido do movimento do dia — 'Sábado tem expediente na MR4 💪'\nStory 2: Mostrar separação de pedido ou produto em destaque — 'Olha o que saiu hoje...'\nStory 3: ENQUETE — 'Qual produto você tem mais dificuldade de encontrar perto de você?' Opções: LED | Alto-falante | Multimídia | Outro\nStory 4: Caixa de perguntas — 'Me conta: você tem loja de acessórios ou faz instalação?'\nStory 5: CTA — 'Quer trabalhar com a gente? Link na bio 👇'",
   128→        "copy": "Use linguagem informal nos stories. Não precisa de copy longa — stories são curtos e diretos.",
   129→        "hashtags": "Não usar hashtags em stories — usar localização: Fortaleza, CE",
   130→        "prazo_producao": "Gravar e postar no momento — stories são espontâneos",
   131→        "obs": "Fabiana pode gravar isso com o próprio celular durante o expediente. Quanto mais espontâneo, melhor."
   132→    },
   133→    {
   134→        "id":"c05","data":"24/03","dia":"Seg","tipo":"POST","titulo":"Pedido feito, pedido entregue","resp":"Murilo","semana":1,
   135→        "objetivo": "Mostrar agilidade e confiabilidade na entrega — eliminar objeção de prazo",
   136→        "formato": "Foto do motoboy/entrega + produto ou print de confirmação de envio",
   137→        "roteiro": "Imagem principal: Motoboy com produto ou caixa pronta para envio\nTexto sobreposto: 'Pedido feito hoje → Saiu hoje'\nDetalhe: mostrar nota fiscal junto se possível",
   138→        "copy": "⚡ Na MR4 é assim:\n\nPediu pela manhã → Separamos → Saiu no mesmo dia.\n\nSem esperar dias. Sem enrolação. Sem desculpa de 'tá em separação'.\n\nNosso motoboy já tá na rua. Seu estoque não precisa parar. 🏍️\n\nAtendemos lojistas e instaladores em todo o Nordeste.\n💬 Chama no WhatsApp — Link na bio.",
   139→        "hashtags": "#entregarapida #distribuidora #acessoriosautomotivos #nordeste #fortaleza #mr4distribuidora #atacado",
   140→        "prazo_producao": "Fotografar na sexta 21/03 ou segunda cedo",
   141→        "obs": "Tirar foto real do motoboy ou da separação de pedido. Autenticidade vale mais que produção."
   142→    },
   143→    {
   144→        "id":"c06","data":"25/03","dia":"Ter","tipo":"REELS","titulo":"Unboxing LED Fênix","resp":"Murilo","semana":1,
   145→        "objetivo": "Mostrar o produto em detalhe e gerar desejo de revenda",
   146→        "formato": "Vídeo vertical 9:16 · 30-40 segundos · Mão abrindo embalagem e mostrando produto",
   147→        "roteiro": "0-3s: Mão pega a caixa do LED Fênix — TEXT NA TELA: 'O produto que mais vende na sua loja...'\n3-15s: Abre a embalagem, mostra o produto, acende o LED se possível\nVOZ: 'Essa é a lâmpada LED Fênix. Olha a qualidade. Olha o encaixe. É isso que tá saindo toda semana nas lojas que trabalham com a gente.'\n15-25s: Mostra preço de custo vs sugestão de revenda (se quiser revelar margem)\nVOZ: 'Você compra por X, revende por Y. Simples assim.'\n25-35s: CTA — 'Quer ter esse produto na sua loja? Chama a MR4 no WhatsApp.'",
   148→        "copy": "💡 Você já conhece a LED Fênix?\n\nEsse produto está saindo toda semana das lojas que trabalham com a gente.\n\n✅ Qualidade comprovada\n✅ Preço competitivo para revenda\n✅ Alta rotatividade\n\nSe você tem loja de acessórios ou faz instalação, esse produto tem que estar no seu estoque.\n\n💬 Chama no WhatsApp e peça o preço de distribuidor!\n👇 Link na bio.",
   149→        "hashtags": "#ledfenix #ledautomotivo #acessoriosautomotivos #unboxing #revenda #distribuidora #mr4distribuidora",
   150→        "prazo_producao": "Gravar na segunda 24/03",
   151→        "obs": "Gravar com boa iluminação para mostrar o brilho do LED. Pode usar música animada no fundo."
   152→    },
   153→    {
   154→        "id":"c07","data":"26/03","dia":"Qua","tipo":"POST","titulo":"Como montar vitrine de LED","resp":"Murilo","semana":2,
   155→        "objetivo": "Educar o lojista — conteúdo que o cliente DO SEU CLIENTE consome. Posiciona MR4 como parceiro estratégico",
   156→        "formato": "Carrossel 5-6 slides com dicas práticas",
   157→        "roteiro": "Slide 1: 'Como montar uma vitrine de LED que vende sozinha 💡'\nSlide 2: '1. Organize por aplicação' — Ex: LEDs para farol, LEDs para interior, LEDs para placa\nSlide 3: '2. Mostre o produto aceso' — Cliente precisa ver o resultado antes de comprar\nSlide 4: '3. Coloque o preço de forma clara' — Sem preço, o cliente passa direto\nSlide 5: '4. Tenha variedade de encaixe' — H4, H7, H11... cada carro pede um tipo\nSlide 6: 'Precisa de estoque de LED pra montar sua vitrine? A MR4 tem tudo. Chama no WhatsApp 👇'",
   158→        "copy": "💡 Dica para lojistas: Sua vitrine de LED está vendendo ou só decorando?\n\nUma vitrine bem montada aumenta as vendas sem você precisar convencer ninguém.\n\nDesliza e veja como fazer ➡️\n\n🏪 Precisa de estoque de LED com preço de distribuidor? A MR4 entrega pra você no Nordeste.\n💬 Chama no WhatsApp — Link na bio.",
   159→        "hashtags": "#dicasparalojistas #vitrineled #acessoriosautomotivos #ledautomotivo #dicas #lojadeacessorios #mr4distribuidora",
   160→        "prazo_producao": "Montar na terça 25/03",
   161→        "obs": "Conteúdo educativo tem mais compartilhamento. Lojistas vão salvar esse post. Isso aumenta o alcance orgânico."
   162→    },
   163→    {
   164→        "id":"c08","data":"27/03","dia":"Qui","tipo":"REELS","titulo":"Quanto você lucra revendendo?","resp":"Murilo","semana":2,
   165→        "objetivo": "Mostrar a margem de revenda de forma concreta — principal gatilho para lojista pedir tabela",
   166→        "formato": "Vídeo vertical 9:16 · 30-40s · Pessoa falando pra câmera ou texto animado",
   167→        "roteiro": "0-3s: TEXT GRANDE NA TELA: 'Quanto você lucra revendendo LED automotivo?'\n3-10s: VOZ: 'Vou te mostrar um exemplo real...'\n10-25s: Mostrar na tela ou falar: 'Você compra a lâmpada LED Fênix no atacado. Revende na sua loja pelo preço de varejo. A diferença vai pro seu bolso — sem precisar de muito espaço, sem produto pesado, sem complicação.'\n25-35s: VOZ: 'Se você tem loja de acessórios ou faz instalação e ainda não trabalha com a MR4, tá deixando dinheiro na mesa. Chama a gente no WhatsApp.'",
   168→        "copy": "💰 Você já calculou quanto lucra revendendo acessórios automotivos?\n\nProduto leve. Alta demanda. Boa margem. Rotatividade garantida.\n\nLojistas que trabalham com a MR4 têm acesso a:\n✅ Preço de distribuidor\n✅ Produtos de alto giro\n✅ Entrega rápida no Nordeste\n✅ Sem pedido mínimo alto\n\nVem descobrir quanto você pode lucrar. 💬 Chama no WhatsApp!\n👇 Link na bio.",
   169→        "hashtags": "#revendaacessorios #lucrocomrevenda #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora #empreendedor",
   170→        "prazo_producao": "Gravar na quarta 26/03",
   171→        "obs": "Não precisa revelar preços exatos — o objetivo é gerar curiosidade e fazer o lojista chamar no WhatsApp."
   172→    },
   173→    {
   174→        "id":"c09","data":"28/03","dia":"Sex","tipo":"POST","titulo":"O que nossos clientes dizem","resp":"Fabiana","semana":2,
   175→        "objetivo": "Prova social — o depoimento de um cliente convence mais do que qualquer copy",
   176→        "formato": "Print de conversa do WhatsApp (com permissão) ou foto do cliente na loja + texto",
   177→        "roteiro": "Opção A: Print de elogio ou feedback positivo de cliente no WhatsApp\nOpção B: Foto do cliente na loja dele com produtos MR4 + depoimento escrito\nTexto sobreposto: Nome do cliente, cidade e o que ele disse",
   178→        "copy": "[USE O DEPOIMENTO REAL DO CLIENTE AQUI]\n\nEssa é a realidade de quem trabalha com a MR4 Distribuidora. 🙌\n\nAtendemos lojistas e instaladores em todo o Nordeste com agilidade, preço justo e sem burocracia.\n\n💬 Quer ser o próximo? Chama no WhatsApp!\n👇 Link na bio.",
   179→        "hashtags": "#depoimento #clientesatisfeito #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora",
   180→        "prazo_producao": "Fabiana pede autorização ao cliente até quinta 27/03",
   181→        "obs": "IMPORTANTE: Pedir autorização ao cliente antes de postar. Pode ser um print sem mostrar número de telefone."
   182→    },
   183→    {
   184→        "id":"c10","data":"31/03","dia":"Seg","tipo":"POST","titulo":"Programa de Indicação — Lançamento","resp":"Murilo","semana":2,
   185→        "objetivo": "Ativar a base de clientes para indicar novos lojistas — crescimento orgânico",
   186→        "formato": "Post único com layout chamativo ou carrossel de 2-3 slides",
   187→        "roteiro": "Slide 1: '🎁 LANÇAMENTO — Programa de Indicação MR4'\nSlide 2: 'Como funciona:\n1. Você indica um lojista ou instalador\n2. Ele faz o primeiro pedido\n3. Você ganha 5% de crédito na sua próxima compra'\nSlide 3: 'Simples assim. Você indica, a gente cuida do resto, e você ainda ganha em cima.'",
   188→        "copy": "🎁 Apresentando o Programa de Indicação MR4!\n\nSe você já trabalha com a gente e conhece outros lojistas ou instaladores que precisam de um bom fornecedor...\n\nÉ simples:\n👉 Você indica\n👉 Ele faz o primeiro pedido\n👉 Você ganha 5% de crédito na próxima compra\n\nSem burocracia. Sem limite de indicações.\n\n💬 Manda mensagem pra gente no WhatsApp dizendo quem indicou e o nome do novo cliente.\n👇 Link na bio.",
   189→        "hashtags": "#programadeindicacao #mr4distribuidora #acessoriosautomotivos #distribuidora #nordeste #parceria",
   190→        "prazo_producao": "Montar na sexta 28/03 — comunicar para base via WhatsApp também no mesmo dia",
   191→        "obs": "Além do post, enviar mensagem direta no WhatsApp para os 8 clientes ativos avisando do programa."
   192→    },
   193→    {
   194→        "id":"c11","data":"01/04","dia":"Ter","tipo":"REELS","titulo":"Nano vs Bomber — Qual escolher?","resp":"Murilo","semana":2,
   195→        "objetivo": "Educar instaladores sobre diferença entre produtos — aumentar confiança técnica da MR4",
   196→        "formato": "Vídeo vertical 9:16 · 40-50s · Comparativo com os dois produtos na mão",
   197→        "roteiro": "0-3s: Dois alto-falantes lado a lado — TEXT: 'Nano ou Bomber? Qual colocar no carro do seu cliente?'\n3-20s: VOZ: 'A linha Nano é mais compacta, ideal para carros menores e quem quer qualidade com custo acessível. Já o Bomber é mais robusto, potência maior, pra quem quer mais volume e graves.'\n20-35s: 'Os dois têm boa saída. A diferença tá no perfil do cliente e no que você quer oferecer.'\n35-45s: CTA — 'A MR4 distribui os dois. Chama no WhatsApp e a gente te ajuda a montar seu estoque.'",
   198→        "copy": "🔊 Nano ou Bomber? Essa dúvida bate em todo instalador na hora de indicar pro cliente.\n\nDesliza e entende a diferença ➡️\n\n✅ Linha Nano — Compacto, qualidade, custo-benefício\n✅ Bomber — Mais potência, mais volume, mais graves\n\nOs dois estão disponíveis na MR4 com preço de distribuidor.\n\n💬 Chama no WhatsApp e monta seu estoque!\n👇 Link na bio.",
   199→        "hashtags": "#altofante #bomber #nano #somautomotivo #instaladorsom #acessoriosautomotivos #mr4distribuidora",
   200→        "prazo_producao": "Gravar na segunda 31/03 com os dois produtos em mãos",
   201→        "obs": "Falar com autoridade técnica. Esse conteúdo será salvo e compartilhado por instaladores."
   202→    },
   203→    {
   204→        "id":"c12","data":"02/04","dia":"Qua","tipo":"POST","titulo":"Os números de quem revende LED Fênix","resp":"Murilo","semana":3,
   205→        "objetivo": "Mostrar resultado concreto de revenda — gatilho de prova social com números",
   206→        "formato": "Post com layout de dados/infográfico simples",
   207→        "roteiro": "Layout com fundo escuro e números em destaque:\n'📊 Números reais de quem revende LED Fênix com a MR4:\n• Produto mais pedido nas lojas de acessórios do Nordeste\n• Alta margem de revenda por unidade\n• Tempo médio de giro: menos de 30 dias\n• Zero devolução por defeito de fábrica'",
   208→        "copy": "📊 Você sabia que a LED Fênix é um dos produtos com melhor giro para lojas de acessórios do Nordeste?\n\nQuem trabalha com esse produto na MR4 sabe:\n✅ Sai rápido do estoque\n✅ Boa margem por unidade\n✅ Cliente volta pra comprar mais\n\nSe você ainda não tem esse produto na sua loja, tá perdendo venda toda semana.\n\n💬 Chama no WhatsApp e peça o preço de distribuidor!\n👇 Link na bio.",
   209→        "hashtags": "#ledfenix #ledautomotivo #revenda #distribuidora #acessoriosautomotivos #nordeste #mr4distribuidora",
   210→        "prazo_producao": "Montar na terça 01/04",
   211→        "obs": "Se tiver dados reais de quantas unidades vendeu no mês, use. Números reais são mais poderosos."
   212→    },
   213→    {
   214→        "id":"c13","data":"03/04","dia":"Qui","tipo":"REELS","titulo":"Bastidores — Um dia na MR4","resp":"Murilo","semana":3,
   215→        "objetivo": "Humanizar a marca. Mostrar equipe, rotina, estrutura. Gera confiança e conexão",
   216→        "formato": "Vídeo vertical 9:16 · 45-60s · Compilado de cenas do dia",
   217→        "roteiro": "0-5s: Abertura do galpão de manhã\n5-15s: Equipe chegando, separação de pedidos\n15-25s: Estoquista organizando produtos\n25-35s: Vendedora atendendo no WhatsApp\n35-45s: Motoboy saindo com entregas\n45-55s: Pedido chegando e cliente confirmando\n55-60s: TEXT FINAL: 'Esse é o time MR4. Trabalhando pra fazer seu estoque girar. 💪'\nCTA: Chama no WhatsApp",
   218→        "copy": "Um dia normal aqui na MR4 Distribuidora. ☀️\n\nAbertura, separação de pedidos, atendimento no WhatsApp, saída das entregas...\n\nEnquanto você tá dormindo, a gente já tá organizando o seu pedido. 💪\n\nÉ assim que a gente trabalha — com agilidade e sem burocracia.\n\n💬 Quer fazer parte disso? Chama no WhatsApp!\n👇 Link na bio.",
   219→        "hashtags": "#bastidores #rotina #distribuidora #acessoriosautomotivos #equipe #mr4distribuidora #nordeste",
   220→        "prazo_producao": "Gravar durante o dia 02/04 (quarta) — editar na quinta cedo",
   221→        "obs": "Pedir pra equipe agir naturalmente. Não precisa posar. Quanto mais real, mais engajamento gera."
   222→    },
   223→    {
   224→        "id":"c14","data":"04/04","dia":"Sex","tipo":"POST","titulo":"Multimídia automotiva — produto que fideliza","resp":"Murilo","semana":3,
   225→        "objetivo": "Destacar multimídia como produto estratégico para lojistas que querem ticket maior",
   226→        "formato": "Foto do produto + carrossel com benefícios",
   227→        "roteiro": "Slide 1: Foto da multimídia + 'O produto que faz o cliente voltar'\nSlide 2: 'Por que vender multimídia?' — Ticket mais alto · Instalação paga · Cliente volta pro serviço\nSlide 3: 'Disponível na MR4 — Preço de distribuidor + Entrega no Nordeste'\nSlide 4: CTA",
   228→        "copy": "📱 Quer aumentar o ticket médio da sua loja?\n\nA multimídia automotiva é o produto que faz isso acontecer:\n\n✅ Ticket de venda mais alto\n✅ O cliente paga a instalação junto\n✅ Gera fidelização — quem instala, recomenda\n✅ Alta demanda em todo o Nordeste\n\nA MR4 distribui com preço competitivo e entrega rápida.\n\n💬 Quer colocar multimídia no seu mix? Chama no WhatsApp!\n👇 Link na bio.",
   229→        "hashtags": "#multimidia #multimidiaautomotiva #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora #instalacao",
   230→        "prazo_producao": "Montar na quinta 03/04",
   231→        "obs": "Focar no benefício para o lojista (ticket maior), não apenas nas especificações técnicas do produto."
   232→    },
   233→    {
   234→        "id":"c15","data":"07/04","dia":"Seg","tipo":"POST","titulo":"Vocês falaram, a gente ouviu","resp":"Murilo","semana":3,
   235→        "objetivo": "Mostrar que a empresa ouve os clientes — responder enquete dos stories da semana 1",
   236→        "formato": "Post único com resultado da enquete + resposta da empresa",
   237→        "roteiro": "Publicar o resultado da enquete dos stories (22/03) sobre qual produto o cliente tem mais dificuldade de encontrar.\nMostrar qual produto ganhou e dizer que a MR4 tem estoque desse produto.\nTransformar o feedback em argumento de venda.",
   238→        "copy": "📊 Na semana passada perguntamos: qual produto você tem mais dificuldade de encontrar perto de você?\n\nVocês responderam! E a resposta foi: [RESULTADO DA ENQUETE]\n\nBoa notícia: temos esse produto em estoque, com preço de distribuidor e entrega rápida pro Nordeste. 😊\n\nContinue mandando suas dúvidas e necessidades — a gente tá ouvindo.\n\n💬 Chama no WhatsApp para fazer seu pedido!\n👇 Link na bio.",
   239→        "hashtags": "#feedback #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora",
   240→        "prazo_producao": "Verificar resultado da enquete dos stories no final de semana — montar post no domingo 06/04",
   241→        "obs": "DEPENDE da enquete dos stories do dia 22/03. Fabiana precisa salvar o resultado antes de sumir."
   242→    },
   243→    {
   244→        "id":"c16","data":"08/04","dia":"Ter","tipo":"REELS","titulo":"Kit revenda para loja pequena","resp":"Murilo","semana":3,
   245→        "objetivo": "Apresentar ideia de kit de produtos para lojista iniciante ou loja pequena — reduz barreira de entrada",
   246→        "formato": "Vídeo vertical 9:16 · 35-45s · Produtos montados numa bancada ou caixa",
   247→        "roteiro": "0-3s: Câmera mostrando produtos organizados — TEXT: 'Quer começar a vender acessórios automotivos? Começa por aqui.'\n3-20s: VOZ: 'A gente montou um kit de produtos que fazem sentido pra qualquer loja pequena de acessórios. LED Fênix, um par de Nano, uma multimídia básica e algumas molduras. Produtos que giram. Produtos que o cliente chega pedindo.'\n20-35s: VOZ: 'Você não precisa de um estoque gigante pra começar. Começa com o que vende e vai aumentando.'\n35-45s: CTA — 'Quer saber o preço desse kit? Chama a MR4 no WhatsApp.'",
   248→        "copy": "🏪 Tem loja pequena de acessórios e não sabe por onde começar o estoque?\n\nA gente montou um kit pensado pra você:\n\n✅ LED Fênix — alto giro, boa margem\n✅ Alto-falante Nano — o mais pedido\n✅ Multimídia básica — ticket maior\n✅ Molduras de painel — complemento essencial\n\nVocê não precisa de muito espaço nem de muito investimento pra começar.\n\n💬 Chama no WhatsApp e pergunta pelo Kit Revenda MR4!\n👇 Link na bio.",
   249→        "hashtags": "#kitrevenda #lojapequeña #acessoriosautomotivos #distribuidora #nordeste #mr4distribuidora #empreendedor",
   250→        "prazo_producao": "Separar os produtos pra foto/vídeo na segunda 07/04 — gravar na terça cedo",
   251→        "obs": "Montar visualmente os produtos juntos numa bancada para o vídeo ter mais impacto."
   252→    },
   253→    {
   254→        "id":"c17","data":"09/04","dia":"Qua","tipo":"POST","titulo":"⚡ Kit Relâmpago MR4","resp":"Murilo","semana":4,
   255→        "objetivo": "Gerar urgência e vendas rápidas com oferta especial de tempo limitado",
   256→        "formato": "Post único com layout de oferta — cores chamativas, prazo visível",
   257→        "roteiro": "Layout com fundo laranja ou vermelho:\n'⚡ KIT RELÂMPAGO — Só até sexta-feira!'\n3 produtos em combo com preço especial\nCTA: 'Chama no WhatsApp AGORA — estoque limitado'\nContagem: 'Válido até 11/04'",
   258→        "copy": "⚡ KIT RELÂMPAGO MR4 — Só até sexta!\n\nCombo especial de produtos mais pedidos com preço de atacado:\n\n🔦 LED Fênix\n🔊 Alto-falante Nano\n📱 Moldura de painel\n\n⏰ Oferta válida até sexta-feira 11/04 ou enquanto durar o estoque.\n\nNão precisa de pedido mínimo alto. Entregamos em todo o Nordeste.\n\n💬 Chama AGORA no WhatsApp — Link na bio.\n\n⚠️ Estoque limitado.",
   259→        "hashtags": "#promocao #kitrelampago #mr4distribuidora #acessoriosautomotivos #distribuidora #nordeste #oferta",
   260→        "prazo_producao": "Montar na terça 08/04 — postar na quarta às 8h",
   261→        "obs": "Criar urgência real. Se possível, definir quantidades limitadas de verdade. Não fazer promoção falsa."
   262→    },
   263→    {
   264→        "id":"c18","data":"10/04","dia":"Qui","tipo":"REELS","titulo":"Março em números — resultados reais","resp":"Murilo","semana":4,
   265→        "objetivo": "Mostrar crescimento e resultados do mês — gera credibilidade e prova social",
   266→        "formato": "Vídeo vertical 9:16 · 30-40s · Números aparecendo na tela com animação simples",
   267→        "roteiro": "0-5s: TEXT GRANDE: 'Março foi assim na MR4 👇'\n5-20s: Números um a um: X pedidos entregues | X lojistas atendidos | X cidades do Nordeste\n20-30s: VOZ ou TEXT: 'Crescendo junto com quem confia na gente. Obrigado a cada cliente que escolheu a MR4 em março.'\n30-40s: CTA — 'Quer fazer parte em abril? Chama no WhatsApp.'",
   268→        "copy": "📈 Março foi histórico pra MR4!\n\n[X] pedidos entregues\n[X] lojistas atendidos\n[X] cidades no Nordeste\n\nCada número é um lojista que confiou na gente. E a gente vai continuar merecendo essa confiança em abril. 💪\n\nVocê ainda não trabalha com a MR4? Abril é uma boa hora pra começar.\n\n💬 Link na bio — Chama no WhatsApp!",
   269→        "hashtags": "#resultados #crescimento #mr4distribuidora #distribuidora #nordeste #acessoriosautomotivos",
   270→        "prazo_producao": "Levantar números reais até quarta 09/04 — gravar e editar na quinta cedo",
   271→        "obs": "Usar números reais. Mesmo que modestos, autenticidade gera mais confiança que números inflados."
   272→    },
   273→    {
   274→        "id":"c19","data":"11/04","dia":"Sex","tipo":"POST","titulo":"Você ainda não trabalha com a MR4?","resp":"Murilo","semana":4,
   275→        "objetivo": "Capturar quem acompanha mas ainda não comprou — post de conversão direta",
   276→        "formato": "Post direto com texto forte e CTA claro",
   277→        "roteiro": "Imagem com texto:\n'Se você tem loja de acessórios ou faz instalação no Nordeste e ainda não trabalha com a MR4...\nA gente precisa conversar.'\nLogo abaixo: lista de diferenciais e CTA",
   278→        "copy": "Se você tem loja de acessórios automotivos ou faz instalação de som no Nordeste e ainda não trabalha com a MR4...\n\nA gente precisa conversar. 😄\n\nO que você vai encontrar aqui:\n✅ Preço de distribuidor (sem pagar preço de varejo)\n✅ Produtos que giram — LED, Alto-falante, Multimídia, Moldura\n✅ Entrega rápida pro Nordeste\n✅ Atendimento direto no WhatsApp — sem robô, sem burocracia\n✅ Equipe real, galpão real, nota fiscal em tudo\n\nNão precisa de pedido gigante pra começar. Vem conversar.\n\n💬 Link na bio → WhatsApp direto.",
   279→        "hashtags": "#lojadeacessorios #instaladorsom #distribuidora #acessoriosautomotivos #nordeste #mr4distribuidora #fornecedor",
   280→        "prazo_producao": "Montar na quinta 10/04",
   281→        "obs": "Post de conversão direta. Usar foto do galpão ou equipe como imagem de fundo para reforçar credibilidade."
   282→    },
   283→    {
   284→        "id":"c20","data":"14/04","dia":"Seg","tipo":"POST","titulo":"Março foi assim — balanço do mês","resp":"Murilo","semana":4,
   285→        "objetivo": "Consolidar a imagem de empresa em crescimento — gera confiança para novos clientes",
   286→        "formato": "Carrossel 3-4 slides com balanço visual do mês",
   287→        "roteiro": "Slide 1: 'Março 2026 na MR4 — Balanço do mês 📊'\nSlide 2: Números do mês (pedidos, cidades, clientes novos)\nSlide 3: 'O que aprendemos em março:' — produto mais pedido, região que mais comprou, feedback dos clientes\nSlide 4: 'Abril vai ser ainda melhor. Vem com a gente.' + CTA",
   288→        "copy": "📊 Março 2026 — Balanço MR4\n\nFoi um mês de crescimento, novos clientes e novos estados atendidos.\n\n🏆 Produto mais pedido: LED Fênix\n📍 Região mais ativa: Ceará\n🤝 Novos clientes: [X]\n\nObrigado a cada lojista e instalador que confiou no nosso trabalho. Vocês são o motivo de cada caixa que sai daqui. 🙏\n\nAbril chegou — e a gente tá pronto pra mais.\n\n💬 Link na bio.",
   289→        "hashtags": "#balancomensal #crescimento #mr4distribuidora #acessoriosautomotivos #nordeste #distribuidora",
   290→        "prazo_producao": "Levantar dados do mês no final de semana — montar no domingo 13/04",
   291→        "obs": "Usar dados reais. Incluir agradecimento genuíno à base de clientes."
   292→    },
   293→    {
   294→        "id":"c21","data":"15/04","dia":"Ter","tipo":"REELS","titulo":"Por que lojistas escolhem a MR4","resp":"Murilo","semana":4,
   295→        "objetivo": "Post de fechamento de ciclo — consolidar posicionamento e gerar novos leads",
   296→        "formato": "Vídeo vertical 9:16 · 40-50s · Murilo ou vendedor falando direto pra câmera",
   297→        "roteiro": "0-3s: Olhar direto pra câmera — 'Você já se perguntou por que lojistas do Nordeste estão trocando de fornecedor pra MR4?'\n3-25s: VOZ: 'A resposta é simples. A gente atende rápido, sem burocracia. Você chama no WhatsApp, a gente responde. Você pede, a gente entrega. Sem esperar dias, sem enrolação, sem pedido mínimo absurdo.'\n25-40s: 'Lojistas e instaladores do Ceará, Piauí, Rio Grande do Norte e Paraíba já estão trabalhando com a gente. E os resultados aparecem na semana seguinte.'\n40-50s: CTA — 'Quer ser o próximo? Chama agora. Link na bio.'",
   298→        "copy": "Por que lojistas do Nordeste estão escolhendo a MR4 como fornecedor?\n\nNão é mágica. É simples:\n\n✅ Atendimento rápido no WhatsApp\n✅ Sem burocracia pra fechar pedido\n✅ Produtos que giram na sua loja\n✅ Entrega que sai no mesmo dia\n✅ Empresa real, nota fiscal em tudo\n\nCE · PI · RN · PB — a gente entrega onde você está.\n\n💬 Chama no WhatsApp e veja como é fácil trabalhar com a MR4.\n👇 Link na bio.",
   299→        "hashtags": "#fornecedorconfiavel #distribuidora #acessoriosautomotivos #nordeste #mr4distribuidora #lojista #instaladorsom",
   300→        "prazo_producao": "Gravar na segunda 14/04 — editar na terça cedo",
   301→        "obs": "Esse é o post de fechamento dos 30 dias. Falar com confiança e autoridade. Resultado do ciclo todo."
   302→    },
   303→]
   304→
   305→REATIVACAO_BASE = [
   306→    {"id":"r01","cliente":"Real Auto Peças","cidade":"Fortaleza/CE","ultimo":"Mar/26","produto":"LED Fênix"},
   307→    {"id":"r02","cliente":"Drums Som Acessórios","cidade":"Fortaleza/CE","ultimo":"Mar/26","produto":"Alto-falante Nano"},
   308→    {"id":"r03","cliente":"Bola Som","cidade":"Fortaleza/CE","ultimo":"Mar/26","produto":"Multimídia"},
   309→    {"id":"r04","cliente":"Hélio Mendonça","cidade":"Caririaçu/CE","ultimo":"Mar/26","produto":"LED Fênix"},
   310→    {"id":"r05","cliente":"Estabilcar","cidade":"Fortaleza/CE","ultimo":"Mar/26","produto":"Verificar histórico"},
   311→    {"id":"r06","cliente":"Lucivando da Silva","cidade":"Fortaleza/CE","ultimo":"Mar/26","produto":"Verificar histórico"},
   312→    {"id":"r07","cliente":"GX Lava Jato","cidade":"Aquiraz/CE","ultimo":"Mar/26","produto":"Verificar histórico"},
   313→    {"id":"r08","cliente":"Siney Freire","cidade":"Cascavel/CE","ultimo":"Mar/26","produto":"Verificar histórico"},
   314→]
   315→
   316→STATUS_CONTENT = ["⬜ Pendente","🎬 Gravando","✏️ Editando","✅ Publicado","❌ Cancelado"]
   317→STATUS_REATIV  = ["⬜ Pendente","🟡 Contatado","🟢 Respondeu","✅ Comprou","❌ Sem retorno"]
   318→TIPO_CORES = {"POST":"badge-blue","REELS":"badge-red","STORIES":"badge-yellow"}
   319→
   320→# ── Abas ────────────────────────────────────────────────────────────────────
   321→tab1, tab2, tab3, tab4, tab5 = st.tabs([
   322→    "📅 Hoje & Esta Semana",
   323→    "🗓️ Calendário 30 Dias",
   324→    "📊 KPIs Semanais",
   325→    "📞 Reativação de Clientes",
   326→    "🔄 Relatório Semanal",
   327→])
   328→
   329→# ═══════════════════════════════════════════════════
   330→# ABA 1 — HOJE & ESTA SEMANA
   331→# ═══════════════════════════════════════════════════
   332→with tab1:
   333→    hoje_str = hoje.strftime("%d/%m")
   334→    dia_semana_hoje = hoje.strftime("%a").capitalize()[:3]
   335→
   336→    # Detecta semana atual
   337→    semanas = {
   338→        1: ("19/03","25/03","ATIVAR o que está parado"),
   339→        2: ("26/03","01/04","POSICIONAR como referência"),
   340→        3: ("02/04","08/04","ENGAJAR a comunidade"),
   341→        4: ("09/04","17/04","CONVERTER e medir"),
   342→    }
   343→    semana_atual = 1
   344→    try:
   345→        d = hoje
   346→        if date(2026,3,26) <= d <= date(2026,4,1):  semana_atual = 2
   347→        elif date(2026,4,2) <= d <= date(2026,4,8):  semana_atual = 3
   348→        elif date(2026,4,9) <= d <= date(2026,4,17): semana_atual = 4
   349→    except Exception:
   350→        pass
   351→
   352→    sem_info = semanas[semana_atual]
   353→
   354→    st.markdown(f"""
   355→    <div class='card'>
   356→      <b style='font-size:18px'>📍 Semana {semana_atual} de 4</b>
   357→      &nbsp;&nbsp;<span style='color:#94a3b8'>{sem_info[0]} → {sem_info[1]}</span><br>
   358→      <span style='color:#f97316;font-size:15px'>Foco: <b>{sem_info[2]}</b></span>
   359→    </div>
   360→    """, unsafe_allow_html=True)
   361→
   362→    # Conteúdo de hoje
   363→    hoje_items = [c for c in CALENDARIO if c["data"] == hoje_str]
   364→    semana_items = [c for c in CALENDARIO if c["semana"] == semana_atual]
   365→
   366→    col_a, col_b = st.columns([1, 1])
   367→
   368→    with col_a:
   369→        st.markdown("### 🎯 Conteúdo de hoje")
   370→        if hoje_items:
   371→            for item in hoje_items:
   372→                status_key = f"cal_{item['id']}"
   373→                current = data["calendario"].get(status_key, "⬜ Pendente")
   374→                tipo_badge = TIPO_CORES.get(item["tipo"], "badge-gray")
   375→
   376→                st.markdown(f"<span class='badge {tipo_badge}'>{item['tipo']}</span>&nbsp;&nbsp;<b style='font-size:15px'>{item['titulo']}</b>", unsafe_allow_html=True)
   377→                novo_status = st.selectbox("Status", STATUS_CONTENT,
   378→                    index=STATUS_CONTENT.index(current),
   379→                    key=f"sel_hoje_{item['id']}")
   380→                if novo_status != current:
   381→                    data["calendario"][status_key] = novo_status
   382→                    save_data(data)
   383→
   384→                with st.expander("📋 Ver briefing completo"):
   385→                    st.markdown("**🎯 Objetivo**")
   386→                    st.info(item.get("objetivo","—"))
   387→                    st.markdown("**📐 Formato**")
   388→                    st.markdown(f"> {item.get('formato','—')}")
   389→                    st.markdown("**🎬 Roteiro**")
   390→                    st.markdown(f"""<div class='card card-blue' style='white-space:pre-line;font-size:13px'>{item.get('roteiro','—')}</div>""", unsafe_allow_html=True)
   391→                    st.markdown("**✍️ Copy pronta**")
   392→                    st.code(item.get("copy","—"), language=None)
   393→                    st.markdown("**#️⃣ Hashtags**")
   394→                    st.markdown(f"<span style='color:#64748b;font-size:12px'>{item.get('hashtags','—')}</span>", unsafe_allow_html=True)
   395→                    st.warning(f"⚠️ {item.get('obs','—')}")
   396→        else:
   397→            st.markdown("<div class='card card-green'><span style='color:#22c55e'>✓ Sem postagem programada para hoje</span></div>", unsafe_allow_html=True)
   398→
   399→        # Tarefas fixas do dia (vendas)
   400→        st.markdown("### 📋 Tarefas diárias — Fabiana")
   401→        tarefas_dia = [
   402→            "Responder todos os leads no WhatsApp",
   403→            "Fazer 5 contatos de reativação",
   404→            "Registrar pedidos fechados no controle",
   405→            "Verificar leads sem resposta há +2 dias",
   406→        ]
   407→        for t in tarefas_dia:
   408→            tk = f"tarefa_{t[:20]}"
   409→            checked = data["notas"].get(tk + hoje_str, False)
   410→            novo = st.checkbox(t, value=checked, key=f"cb_{tk}")
   411→            if novo != checked:
   412→                data["notas"][tk + hoje_str] = novo
   413→                save_data(data)
   414→
   415→    with col_b:
   416→        st.markdown("### 📅 Esta semana completa")
   417→        publicados = sum(1 for c in semana_items if "✅" in data["calendario"].get(f"cal_{c['id']}", ""))
   418→        total = len(semana_items)
   419→
   420→        st.markdown(f"""
   421→        <div class='metric-box' style='margin-bottom:16px'>
   422→          <div class='metric-val'>{publicados}/{total}</div>
   423→          <div class='metric-lbl'>Conteúdos publicados esta semana</div>
   424→        </div>
   425→        """, unsafe_allow_html=True)
   426→        st.progress(publicados / max(total, 1))
   427→
   428→        for item in semana_items:
   429→            status_key = f"cal_{item['id']}"
   430→            current = data["calendario"].get(status_key, "⬜ Pendente")
   431→            cor = "card-green" if "✅" in current else ("card-yellow" if "🎬" in current or "✏️" in current else "")
   432→            tipo_badge = TIPO_CORES.get(item["tipo"], "badge-gray")
   433→            is_hoje = item["data"] == hoje_str
   434→            st.markdown(f"""
   435→            <div class='card {cor}' style='{"border:2px solid #f97316;" if is_hoje else ""}'>
   436→              <b style='color:#94a3b8;font-size:11px'>{item["data"]} {item["dia"]}</b>
   437→              &nbsp;<span class='badge {tipo_badge}'>{item["tipo"]}</span>
   438→              {"&nbsp;<span class='badge badge-yellow'>HOJE</span>" if is_hoje else ""}<br>
   439→              <span style='font-size:13px'>{item["titulo"]}</span><br>
   440→              <span style='font-size:11px;color:#64748b'>{current} · {item["resp"]}</span>
   441→            </div>
   442→            """, unsafe_allow_html=True)
   443→
   444→# ═══════════════════════════════════════════════════
   445→# ABA 2 — CALENDÁRIO 30 DIAS
   446→# ═══════════════════════════════════════════════════
   447→with tab2:
   448→    st.markdown("### 🗓️ Calendário completo — 19 Mar → 17 Abr 2026")
   449→
   450→    col_f1, col_f2 = st.columns([1,1])
   451→    with col_f1:
   452→        filtro_semana = st.selectbox("Filtrar por semana", ["Todas","Semana 1","Semana 2","Semana 3","Semana 4"])
   453→    with col_f2:
   454→        filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos","POST","REELS","STORIES"])
   455→
   456→    itens_filtrados = CALENDARIO
   457→    if filtro_semana != "Todas":
   458→        n = int(filtro_semana[-1])
   459→        itens_filtrados = [c for c in itens_filtrados if c["semana"] == n]
   460→    if filtro_tipo != "Todos":
   461→        itens_filtrados = [c for c in itens_filtrados if c["tipo"] == filtro_tipo]
   462→
   463→    # Métricas resumo
   464→    mc1, mc2, mc3, mc4 = st.columns(4)
   465→    total_cal = len(CALENDARIO)
   466→    pub_cal = sum(1 for c in CALENDARIO if "✅" in data["calendario"].get(f"cal_{c['id']}", ""))
   467→    posts_cal = len([c for c in CALENDARIO if c["tipo"]=="POST"])
   468→    reels_cal = len([c for c in CALENDARIO if c["tipo"]=="REELS"])
   469→    for col, val, lbl in [(mc1, pub_cal, "Publicados"), (mc2, total_cal-pub_cal, "Pendentes"),
   470→                           (mc3, posts_cal, "Posts Feed"), (mc4, reels_cal, "Reels")]:
   471→        col.markdown(f"<div class='metric-box'><div class='metric-val'>{val}</div><div class='metric-lbl'>{lbl}</div></div>", unsafe_allow_html=True)
   472→
   473→    st.markdown("<br>", unsafe_allow_html=True)
   474→
   475→    # Cards de conteúdo com briefing completo
   476→    for item in itens_filtrados:
   477→        status_key = f"cal_{item['id']}"
   478→        current = data["calendario"].get(status_key, "⬜ Pendente")
   479→        tipo_badge = TIPO_CORES.get(item["tipo"], "badge-gray")
   480→        cor_card = "card-green" if "✅" in current else ("card-yellow" if "🎬" in current or "✏️" in current else "")
   481→        is_hoje = item["data"] == hoje.strftime("%d/%m")
   482→
   483→        label = f"{'🔴 HOJE · ' if is_hoje else ''}{item['data']} {item['dia']}  ·  {item['tipo']}  ·  {item['titulo']}  ·  {current}"
   484→        with st.expander(label, expanded=is_hoje):
   485→            c1, c2 = st.columns([3, 1])
   486→            with c1:
   487→                st.markdown(f"<span class='badge {tipo_badge}'>{item['tipo']}</span>&nbsp;&nbsp;<b style='font-size:16px'>{item['titulo']}</b>", unsafe_allow_html=True)
   488→                st.markdown(f"<span style='color:#64748b;font-size:12px'>📅 {item['data']} {item['dia']} &nbsp;|&nbsp; 👤 Responsável: <b>{item['resp']}</b> &nbsp;|&nbsp; ⏰ Produção: {item.get('prazo_producao','—')}</span>", unsafe_allow_html=True)
   489→                st.markdown("---")
   490→
   491→                st.markdown("**🎯 Objetivo**")
   492→                st.info(item.get("objetivo", "—"))
   493→
   494→                st.markdown("**📐 Formato**")
   495→                st.markdown(f"> {item.get('formato','—')}")
   496→
   497→                st.markdown("**🎬 Roteiro / Instruções de Produção**")
   498→                st.markdown(f"""<div class='card card-blue' style='white-space:pre-line;font-size:13px'>{item.get('roteiro','—')}</div>""", unsafe_allow_html=True)
   499→
   500→                st.markdown("**✍️ Copy pronta (legenda para postar)**")
   501→                st.code(item.get("copy", "—"), language=None)
   502→
   503→                col_h, col_o = st.columns(2)
   504→                with col_h:
   505→                    st.markdown("**#️⃣ Hashtags**")
   506→                    st.markdown(f"<span style='color:#64748b;font-size:12px'>{item.get('hashtags','—')}</span>", unsafe_allow_html=True)
   507→                with col_o:
   508→                    st.markdown("**⚠️ Observações**")
   509→                    st.warning(item.get("obs", "—"))
   510→
   511→            with c2:
   512→                st.markdown("<br>", unsafe_allow_html=True)
   513→                novo = st.selectbox("Status", STATUS_CONTENT,
   514→                    index=STATUS_CONTENT.index(current),
   515→                    key=f"cal_sel_{item['id']}")
   516→                if novo != current:
   517→                    data["calendario"][status_key] = novo
   518→                    save_data(data)
   519→                st.markdown(f"""
   520→                <div class='metric-box' style='margin-top:12px'>
   521→                  <div style='font-size:13px;color:#94a3b8'>Semana</div>
   522→                  <div class='metric-val'>{item['semana']}</div>
   523→                </div>
   524→                """, unsafe_allow_html=True)
   525→
   526→        st.markdown("")
   527→
   528→# ═══════════════════════════════════════════════════
   529→# ABA 3 — KPIs SEMANAIS
   530→# ═══════════════════════════════════════════════════
   531→with tab3:
   532→    st.markdown("### 📊 KPIs Semanais — Preencher toda segunda-feira")
   533→
   534→    semana_sel = st.radio("Semana", ["Semana 1 (19-25 Mar)","Semana 2 (26 Mar-1 Abr)","Semana 3 (2-8 Abr)","Semana 4 (9-17 Abr)"],
   535→        horizontal=True)
   536→    sk = semana_sel[:8].replace(" ","_")
   537→
   538→    if sk not in data["kpis"]:
   539→        data["kpis"][sk] = {}
   540→    kpi = data["kpis"][sk]
   541→
   542→    col_k1, col_k2, col_k3 = st.columns(3)
   543→
   544→    with col_k1:
   545→        st.markdown("#### 📦 Vendas")
   546→        kpi["pedidos"]    = st.number_input("Pedidos fechados", min_value=0, value=kpi.get("pedidos",0), key=f"k1_{sk}")
   547→        kpi["faturamento"]= st.number_input("Faturamento (R$)", min_value=0.0, value=float(kpi.get("faturamento",0)), key=f"k2_{sk}", format="%.2f")
   548→        kpi["clientes_novos"] = st.number_input("Clientes novos", min_value=0, value=kpi.get("clientes_novos",0), key=f"k3_{sk}")
   549→        kpi["reativados"] = st.number_input("Clientes reativados", min_value=0, value=kpi.get("reativados",0), key=f"k4_{sk}")
   550→        kpi["indicacoes"] = st.number_input("Indicações recebidas", min_value=0, value=kpi.get("indicacoes",0), key=f"k5_{sk}")
   551→
   552→    with col_k2:
   553→        st.markdown("#### 📱 Meta Ads")
   554→        kpi["conversas"]   = st.number_input("Conversas iniciadas", min_value=0, value=kpi.get("conversas",0), key=f"k6_{sk}")
   555→        kpi["custo_conv"]  = st.number_input("Custo/conversa (R$)", min_value=0.0, value=float(kpi.get("custo_conv",0)), key=f"k7_{sk}", format="%.2f")
   556→        kpi["gasto_ads"]   = st.number_input("Gasto total ads (R$)", min_value=0.0, value=float(kpi.get("gasto_ads",0)), key=f"k8_{sk}", format="%.2f")
   557→        kpi["ctr"]         = st.number_input("CTR (%)", min_value=0.0, value=float(kpi.get("ctr",0)), key=f"k9_{sk}", format="%.2f")
   558→
   559→    with col_k3:
   560→        st.markdown("#### 📸 Instagram")
   561→        kpi["posts_ig"]   = st.number_input("Posts publicados", min_value=0, value=kpi.get("posts_ig",0), key=f"k10_{sk}")
   562→        kpi["reels_ig"]   = st.number_input("Reels publicados", min_value=0, value=kpi.get("reels_ig",0), key=f"k11_{sk}")
   563→        kpi["stories_ig"] = st.number_input("Stories (dias ativos)", min_value=0, value=kpi.get("stories_ig",0), key=f"k12_{sk}")
   564→        kpi["alcance_ig"] = st.number_input("Alcance total", min_value=0, value=kpi.get("alcance_ig",0), key=f"k13_{sk}")
   565→        kpi["seguidores_novos"] = st.number_input("Seguidores novos", min_value=0, value=kpi.get("seguidores_novos",0), key=f"k14_{sk}")
   566→
   567→    kpi["dificuldade"] = st.text_area("⚠️ Principal dificuldade da semana", value=kpi.get("dificuldade",""), key=f"k15_{sk}")
   568→    kpi["funcionou"]   = st.text_area("💡 O que funcionou bem", value=kpi.get("funcionou",""), key=f"k16_{sk}")
   569→
   570→    if st.button("💾 Salvar KPIs", key=f"save_kpi_{sk}", use_container_width=True):
   571→        data["kpis"][sk] = kpi
   572→        save_data(data)
   573→        st.success("KPIs salvos!")
   574→
   575→    # Resumo acumulado
   576→    if any(data["kpis"].get(f"Semana_{i}", {}).get("pedidos", 0) for i in range(1,5)):
   577→        st.divider()
   578→        st.markdown("#### 📈 Acumulado do mês")
   579→        tot_ped = sum(data["kpis"].get(f"Semana_{i}", {}).get("pedidos", 0) for i in range(1,5))
   580→        tot_fat = sum(data["kpis"].get(f"Semana_{i}", {}).get("faturamento", 0) for i in range(1,5))
   581→        tot_ads = sum(data["kpis"].get(f"Semana_{i}", {}).get("gasto_ads", 0) for i in range(1,5))
   582→        roi = (tot_fat / tot_ads) if tot_ads > 0 else 0
   583→        r1,r2,r3,r4 = st.columns(4)
   584→        for col, val, lbl in [(r1,tot_ped,"Pedidos totais"),(r2,f"R${tot_fat:,.0f}","Faturamento total"),(r3,f"R${tot_ads:,.0f}","Gasto total ads"),(r4,f"{roi:.1f}x","ROI ads")]:
   585→            col.markdown(f"<div class='metric-box'><div class='metric-val'>{val}</div><div class='metric-lbl'>{lbl}</div></div>", unsafe_allow_html=True)
   586→
   587→# ═══════════════════════════════════════════════════
   588→# ABA 4 — REATIVAÇÃO DE CLIENTES
   589→# ═══════════════════════════════════════════════════
   590→with tab4:
   591→    st.markdown("### 📞 Reativação de Base de Clientes")
   592→    st.markdown("""
   593→    <div class='card card-yellow'>
   594→    💬 <b>Template de mensagem:</b><br>
   595→    <i>"Oi [NOME]! Tudo bem? Aqui é [SEU NOME] da MR4 😊 Faz um tempinho que a gente não se fala.
   596→    Chegaram produtos novos que costumam girar bem em lojas como a sua — [PRODUTO]. Posso te mandar os detalhes e o preço?"</i>
   597→    </div>
   598→    """, unsafe_allow_html=True)
   599→
   600→    # Métricas reativação
   601→    total_r = len(REATIVACAO_BASE)
   602→    contat_r = sum(1 for c in REATIVACAO_BASE if data["reativacao"].get(c["id"],{}).get("status","⬜ Pendente") not in ["⬜ Pendente"])
   603→    comprou_r = sum(1 for c in REATIVACAO_BASE if "✅ Comprou" in data["reativacao"].get(c["id"],{}).get("status",""))
   604→    rc1,rc2,rc3 = st.columns(3)
   605→    for col,val,lbl in [(rc1,total_r,"Total na base"),(rc2,contat_r,"Contatados"),(rc3,comprou_r,"Compraram")]:
   606→        col.markdown(f"<div class='metric-box'><div class='metric-val'>{val}</div><div class='metric-lbl'>{lbl}</div></div>", unsafe_allow_html=True)
   607→
   608→    st.markdown("<br>", unsafe_allow_html=True)
   609→
   610→    for item in REATIVACAO_BASE:
   611→        if item["id"] not in data["reativacao"]:
   612→            data["reativacao"][item["id"]] = {"status":"⬜ Pendente","nota":""}
   613→
   614→        r_data = data["reativacao"][item["id"]]
   615→        current_status = r_data.get("status","⬜ Pendente")
   616→        cor = "card-green" if "✅" in current_status else ("card-yellow" if "🟡" in current_status or "🟢" in current_status else "card-red" if "❌" in current_status else "")
   617→
   618→        with st.expander(f"{item['cliente']} — {item['cidade']} · {current_status}"):
   619→            rc1, rc2 = st.columns([2,1])
   620→            with rc1:
   621→                st.markdown(f"**Produto histórico:** {item['produto']}")
   622→                st.markdown(f"**Último pedido:** {item['ultimo']}")
   623→                novo_status = st.selectbox("Status do contato", STATUS_REATIV,
   624→                    index=STATUS_REATIV.index(current_status),
   625→                    key=f"reat_sel_{item['id']}")
   626→                nota = st.text_input("Observação", value=r_data.get("nota",""), key=f"reat_nota_{item['id']}")
   627→            with rc2:
   628→                st.markdown(f"""
   629→                <div class='card {cor}' style='margin-top:20px'>
   630→                  <b>{item['cliente']}</b><br>
   631→                  <span style='font-size:12px;color:#94a3b8'>{current_status}</span>
   632→                </div>
   633→                """, unsafe_allow_html=True)
   634→            if st.button("Salvar", key=f"reat_save_{item['id']}"):
   635→                data["reativacao"][item["id"]] = {"status": novo_status, "nota": nota}
   636→                save_data(data)
   637→                st.success("Salvo!")
   638→                st.rerun()
   639→
   640→    # Adicionar novo cliente
   641→    st.divider()
   642→    st.markdown("#### ➕ Adicionar cliente para reativar")
   643→    with st.form("add_cliente"):
   644→        nc1, nc2, nc3 = st.columns(3)
   645→        novo_nome    = nc1.text_input("Nome do cliente")
   646→        nova_cidade  = nc2.text_input("Cidade/Estado")
   647→        novo_produto = nc3.text_input("Produto histórico")
   648→        if st.form_submit_button("Adicionar"):
   649→            if novo_nome:
   650→                new_id = f"r{len(REATIVACAO_BASE)+100:03d}"
   651→                REATIVACAO_BASE.append({"id":new_id,"cliente":novo_nome,"cidade":nova_cidade,"ultimo":"Novo","produto":novo_produto})
   652→                data["reativacao"][new_id] = {"status":"⬜ Pendente","nota":""}
   653→                save_data(data)
   654→                st.success(f"{novo_nome} adicionado!")
   655→                st.rerun()
   656→
   657→# ═══════════════════════════════════════════════════
   658→# ABA 5 — RELATÓRIO SEMANAL
   659→# ═══════════════════════════════════════════════════
   660→with tab5:
   661→    st.markdown("### 🔄 Relatório Semanal — Para enviar ao Consultor IA")
   662→    st.markdown("""
   663→    <div class='card card-blue'>
   664→    📌 <b>Como funciona:</b> Todo <b>segunda-feira antes das 10h</b>, preencha os campos abaixo,
   665→    copie o relatório gerado e cole na conversa com o consultor IA para receber o plano da semana.
   666→    </div>
   667→    """, unsafe_allow_html=True)
   668→
   669→    rs1, rs2 = st.columns(2)
   670→    with rs1:
   671→        semana_rel = st.selectbox("Qual semana está reportando?",
   672→            ["Semana 1 (19-25 Mar)","Semana 2 (26 Mar-1 Abr)","Semana 3 (2-8 Abr)","Semana 4 (9-17 Abr)"])
   673→        ped = st.number_input("Pedidos fechados na semana", min_value=0, key="rel_ped")
   674→        fat = st.number_input("Faturamento (R$)", min_value=0.0, key="rel_fat", format="%.2f")
   675→        cn  = st.number_input("Clientes novos", min_value=0, key="rel_cn")
   676→    with rs2:
   677→        custo_c  = st.number_input("Custo/conversa Meta Ads (R$)", min_value=0.0, key="rel_cc", format="%.2f")
   678→        gasto_a  = st.number_input("Gasto total em ads (R$)", min_value=0.0, key="rel_ga", format="%.2f")
   679→        posts_p  = st.number_input("Posts publicados", min_value=0, key="rel_pp")
   680→        reels_p  = st.number_input("Reels publicados", min_value=0, key="rel_rp")
   681→        stories_p= st.number_input("Stories (dias ativos)", min_value=0, key="rel_sp")
   682→
   683→    reativ_c = st.number_input("Clientes da base contatados", min_value=0, key="rel_rc")
   684→    reativ_v = st.number_input("Desses, quantos compraram", min_value=0, key="rel_rv")
   685→    dificuldade_r = st.text_area("⚠️ Principal dificuldade da semana", key="rel_dif")
   686→    duvida_r      = st.text_area("❓ Dúvida ou decisão pendente", key="rel_duv")
   687→    funcionou_r   = st.text_area("💡 O que funcionou bem", key="rel_func")
   688→
   689→    if st.button("📋 Gerar relatório para copiar", use_container_width=True):
   690→        ticket = (fat / ped) if ped > 0 else 0
   691→        roi_r  = (fat / gasto_a) if gasto_a > 0 else 0
   692→        relatorio = f"""
   693→━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   694→📣 RELATÓRIO SEMANAL — MR4 DISTRIBUIDORA
   695→{semana_rel}
   696→━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   697→
   698→📦 VENDAS:
   699→• Pedidos fechados: {ped}
   700→• Faturamento: R$ {fat:,.2f}
   701→• Clientes novos: {cn}
   702→• Ticket médio da semana: R$ {ticket:,.2f}
   703→
   704→📱 META ADS:
   705→• Custo/conversa: R$ {custo_c:.2f}
   706→• Gasto total: R$ {gasto_a:,.2f}
   707→• ROI ads: {roi_r:.1f}x
   708→
   709→📸 INSTAGRAM:
   710→• Posts publicados: {posts_p}
   711→• Reels publicados: {reels_p}
   712→• Stories ativos: {stories_p} dias
   713→
   714→🔄 REATIVAÇÃO:
   715→• Contatos feitos: {reativ_c}
   716→• Compraram: {reativ_v}
   717→
   718→⚠️ Dificuldade da semana:
   719→{dificuldade_r if dificuldade_r else "—"}
   720→
   721→❓ Dúvida ou decisão:
   722→{duvida_r if duvida_r else "—"}
   723→
   724→💡 O que funcionou:
   725→{funcionou_r if funcionou_r else "—"}
   726→━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   727→        """.strip()
   728→        st.code(relatorio, language=None)
   729→        st.success("✅ Copie o texto acima e cole na conversa com o consultor IA!")
   730→

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>
