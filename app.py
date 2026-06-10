import streamlit as str
import re
import io
import zipfile
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA (Interface limpa e centralizada)
str.set_page_config(
    page_title="HH Nick Changer", 
    page_icon="🃏", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Injetar CSS para garantir que a barra lateral nativa fique 100% invisível
str.markdown(
    """
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- FUNÇÃO DE CONVERSÃO ---
def customizar_nicks_hh(texto_hh, novo_nick):
    """Substitui a palavra 'Hero' pelo nick configurado (case-insensitive)."""
    if not novo_nick:
        return texto_hh
    texto_atualizado = re.sub(r'\bHero\b', novo_nick, texto_hh, flags=re.IGNORECASE)
    return texto_atualizado

# --- FUNÇÃO PARA PROCESSAR INPUTS DA GG (TXT OU ZIP) ---
def processar_arquivos_gg(arquivos_upados, nick):
    """Lê arquivos da GG, aceitando tanto .txt quanto extraindo de dentro de .zip"""
    texto_acumulado = ""
    contagem = 0
    
    for arq in arquivos_upados:
        name_arq = arq.name.lower()
        
        if name_arq.endswith(".zip"):
            try:
                with zipfile.ZipFile(arq) as z:
                    for filename in z.namelist():
                        if filename.lower().endswith(".txt"):
                            with z.open(filename) as f:
                                conteudo = f.read().decode("utf-8", errors="ignore")
                                texto_acumulado += customizar_nicks_hh(conteudo, nick) + "\n\n"
                                contagem += 1
            except Exception:
                pass
                
        elif name_arq.endswith(".txt"):
            conteudo = arq.read().decode("utf-8", errors="ignore")
            texto_acumulado += customizar_nicks_hh(conteudo, nick) + "\n\n"
            contagem += 1
            
    return texto_acumulado, contagem

# --- CAPTURA DE CONFIGURAÇÕES VIA URL ---
default_nome = str.query_params.get("nome", "")
default_gg = str.query_params.get("gg", "")
default_party = str.query_params.get("party", "")
default_modo = str.query_params.get("modo", "Apenas trocar o nick")

# --- INTERFACE INTERATIVA (CORPO PRINCIPAL) ---
str.title("🃏 Conversor de Hand History por Plataforma")
str.markdown("---")

# 1. Painel de Configurações Gerais no Topo
str.subheader("⚙️ Configurações Gerais")
col1, col2, col3 = str.columns(3)

with col1:
    nome_jogador = str.text_input("Seu Nome e Sobrenome (Jogador)", value=default_nome, placeholder="Ex: Ramon Sfalsin")
with col2:
    nick_gg = str.text_input("Seu Nick no GGPoker", value=default_gg, placeholder="Digite seu nick da GG")
with col3:
    nick_party = str.text_input("Seu Nick no PartyPoker", value=default_party, placeholder="Digite seu nick da Party")

# 2. Seleção do Modo de Operação
str.markdown("### 🎯 Modo de Operação")
modo = str.radio(
    "O que deseja fazer?",
    ["Apenas trocar o nick", "Organizar para o Drive"],
    index=0 if default_modo == "Apenas trocar o nick" else 1,
    horizontal=True
)

# 3. Bloco para Salvar Configurações (Apenas se tiver dados)
if nome_jogador or nick_gg or nick_party:
    with str.expander("💾 Salvar minhas Configurações (Clique para ver o Link)"):
        link_salvar = f"https://trocarnick.streamlit.app/?nome={nome_jogador.replace(' ', '%20')}&gg={nick_gg}&party={nick_party}&modo={modo.replace(' ', '%20')}"
        str.markdown("Adicione o link abaixo aos seus **Favoritos** do seu navegador para carregar tudo preenchido automaticamente:")
        str.code(link_salvar, language="text")

str.markdown("---")

# Variáveis de controle de fluxo de arquivos
arquivos_totais = 0

# --- LÓGICA MODO: APENAS TROCAR O NICK ---
if modo == "Apenas trocar o nick":
    
    str.markdown("### 🔴 GGPoker")
    arquivos_gg = str.file_uploader("Arraste o seu arquivo .zip (ou .txt) da GGPoker", type=["txt", "zip"], accept_multiple_files=True, key="gg_txt")
    
    str.markdown("---")
    str.markdown("### 🧡 PartyPoker")
    arquivos_party = str.file_uploader("Arraste os arquivos .txt do PartyPoker", type=["txt"], accept_multiple_files=True, key="party_txt")

    texto_final_unificado = ""
    
    if arquivos_gg:
        texto_gg, qtd = processar_arquivos_gg(arquivos_gg, nick_gg)
        texto_final_unificado += texto_gg
        arquivos_totais += qtd
            
    if arquivos_party:
        for arq in arquivos_party:
            conteudo = arq.read().decode("utf-8", errors="ignore")
            texto_final_unificado += customizar_nicks_hh(conteudo, nick_party) + "\n\n"
            arquivos_totais += 1

    if arquivos_totais > 0:
        str.markdown("---")
        str.success(f"🎉 Pronto! {arquivos_totais} arquivo(s) de mãos convertido(s) com sucesso!")
        
        str.download_button(
            label="📥 Baixar Arquivo Convertido (.TXT)",
            data=texto_final_unificado,
            file_name="hands_convertidas.txt",
            mime="text/plain",
            use_container_width=True
        )
else:
    # --- LÓGICA MODO: ORGANIZAR PARA O DRIVE ---
    str.markdown("### 🔴 GGPoker")
    arquivos_gg = str.file_uploader("Arraste o seu arquivo .zip (ou .txt) da GGPoker", type=["txt", "zip"], accept_multiple_files=True, key="drive_gg")
    
    str.markdown("---")
    str.markdown("### 🧡 PartyPoker")
    arquivos_party = str.file_uploader("Arraste os arquivos .txt do PartyPoker", type=["txt"], accept_multiple_files=True, key="drive_party")
    
    str.markdown("---")
    str.markdown("### ♠️ PokerStars")
    arquivos_stars = str.file_uploader("Arraste os arquivos .txt do PokerStars", type=["txt"], accept_multiple_files=True, key="drive_stars")
    
    str.markdown("---")
    str.markdown("### 🟦 WPN (Winning Poker Network)")
    arquivos_wpn = str.file_uploader("Arraste os arquivos .txt da WPN", type=["txt"], accept_multiple_files=True, key="drive_wpn")
    
    str.markdown("---")
    str.markdown("### 🪙 CoinPoker")
    arquivos_coin = str.file_uploader("Arraste os arquivos .txt do CoinPoker", type=["txt"], accept_multiple_files=True, key="drive_coin")

    # Preparar o ZIP na memória
    buffer_zip = io.BytesIO()
    
    with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as arquivo_zip:
        if arquivos_gg:
            texto_gg, qtd = processar_arquivos_gg(arquivos_gg, nick_gg)
            if texto_gg:
                arquivo_zip.writestr("GGPoker_convertido.txt", texto_gg)
                arquivos_totais += qtd
            
        if arquivos_party:
            texto_party = ""
            for arq in arquivos_party:
                conteudo = arq.read().decode("utf-8", errors="ignore")
                texto_party += customizar_nicks_hh(conteudo, nick_party) + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("PartyPoker_convertido.txt", texto_party)
            
        if arquivos_stars:
            texto_stars = ""
            for arq in arquivos_stars:
                texto_stars += arq.read().decode("utf-8", errors="ignore") + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("PokerStars.txt", texto_stars)
            
        if arquivos_wpn:
            texto_wpn = ""
            for arq in arquivos_wpn:
                texto_wpn += arq.read().decode("utf-8", errors="ignore") + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("WPN.txt", texto_wpn)
            
        if arquivos_coin:
            texto_coin = ""
            for arq in arquivos_coin:
                texto_coin += arq.read().decode("utf-8", errors="ignore") + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("CoinPoker.txt", texto_coin)

    if arquivos_totais > 0:
        str.markdown("---")
        ano_mes = datetime.now().strftime("[%Y.%m]")
        nome_limpo = nome_jogador.strip() if nome_jogador.strip() else "Jogador Sem Nome"
        nome_zip_final = f"{ano_mes} {nome_limpo}.zip"
        
        str.success(f"📦 Pacote estruturado com sucesso! Total de {arquivos_totais} arquivos de mãos organizados.")
        str.info(f"ℹ️ **Próximo passo:** Baixe o arquivo abaixo e coloque-o diretamente na sua pasta de **Database** no Google Drive!")
        
        buffer_zip.seek(0)
        
        str.download_button(
            label=f"📥 Baixar Pacote: {nome_zip_final}",
            data=buffer_zip,
            file_name=nome_zip_final,
            mime="application/zip",
            use_container_width=True
        )
    else:
        str.markdown("---")
        str.info("💡 Insira os arquivos das salas desejadas acima para gerar o pacote do Drive.")
