import streamlit as str
import re
import io
import zipfile
from datetime import datetime

# Configuração da página
str.set_page_config(page_title="HH Nick Changer", page_icon="🃏", layout="centered")

# --- FUNÇÃO DE CONVERSÃO ---
def customizar_nicks_hh(texto_hh, novo_nick):
    """Substitui a palavra 'Hero' pelo nick configurado (case-insensitive)."""
    if not novo_nick:
        return texto_hh
    texto_atualizado = re.sub(r'\bHero\b', novo_nick, texto_hh, flags=re.IGNORECASE)
    return texto_atualizado

# --- CAPTURA DE CONFIGURAÇÕES VIA URL ---
default_nome = str.query_params.get("nome", "")
default_gg = str.query_params.get("gg", "")
default_party = str.query_params.get("party", "")
default_modo = str.query_params.get("modo", "Apenas trocar o nick")

# --- INTERFACE INTERATIVA (STREAMLIT) ---
str.title("🃏 Conversor de Hand History por Plataforma")
str.markdown("---")

# 1. Configuração na Barra Lateral
str.sidebar.header("⚙️ Configurações Gerais")
nome_jogador = str.sidebar.text_input("Seu Nome e Sobrenome (Jogador)", value=default_nome, placeholder="Ex: Ramon Sfalsin")
nick_gg = str.sidebar.text_input("Seu Nick no GGPoker", value=default_gg, placeholder="Digite seu nick da GG")
nick_party = str.sidebar.text_input("Seu Nick no PartyPoker", value=default_party, placeholder="Digite seu nick da Party")

str.sidebar.markdown("---")
str.sidebar.header("🎯 Modo de Operação")
modo = str.sidebar.radio(
    "O que deseja fazer?",
    ["Apenas trocar o nick", "Organizar para o Drive"],
    index=0 if default_modo == "Apenas trocar o nick" else 1
)

# Link dinâmico para salvar nos favoritos
str.sidebar.markdown("---")
str.sidebar.markdown("### 💾 Salvar minhas Configurações")
if nome_jogador or nick_gg or nick_party:
    link_salvar = f"https://trocarsnick.streamlit.app/?nome={nome_jogador.replace(' ', '%20')}&gg={nick_gg}&party={nick_party}&modo={modo.replace(' ', '%20')}"
    str.sidebar.markdown("Adicione o link abaixo aos seus **Favoritos** para não precisar digitar de novo:")
    str.sidebar.code(link_salvar, language="text")

# Variáveis de controle de fluxo de arquivos
arquivos_totais = 0

# --- LÓGICA MODO: APENAS TROCAR O NICK ---
if modo == "Apenas trocar o nick":
    
    str.markdown("### 🔴 GGPoker")
    arquivos_gg = str.file_uploader("Arraste os arquivos .txt da GGPoker", type=["txt"], accept_multiple_files=True, key="gg_txt")
    
    str.markdown("---")
    str.markdown("### 🧡 PartyPoker")
    arquivos_party = str.file_uploader("Arraste os arquivos .txt do PartyPoker", type=["txt"], accept_multiple_files=True, key="party_txt")

    texto_final_unificado = ""
    
    if arquivos_gg:
        for arq in arquivos_gg:
            conteudo = arq.read().decode("utf-8", errors="ignore")
            texto_final_unificado += customizar_nicks_hh(conteudo, nick_gg) + "\n\n"
            arquivos_totais += 1
            
    if arquivos_party:
        for arq in arquivos_party:
            conteudo = arq.read().decode("utf-8", errors="ignore")
            texto_final_unificado += customizar_nicks_hh(conteudo, nick_party) + "\n\n"
            arquivos_totais += 1

    if arquivos_totais > 0:
        str.markdown("---")
        str.success(f"🎉 Pronto! {arquivos_totais} arquivo(s) convertido(s) com sucesso!")
        
        str.download_button(
            label="📥 Baixar Arquivo Convertido (.TXT)",
            data=texto_final_unificado,
            file_name="hands_convertidas.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        str.markdown("---")
        str.info("💡 Insira os arquivos da GG ou Party acima para gerar o seu arquivo convertido.")

# --- LÓGICA MODO: ORGANIZAR PARA O DRIVE ---
else:
    str.markdown("### 🔴 GGPoker")
    arquivos_gg = str.file_uploader("Arraste os arquivos .txt da GGPoker", type=["txt"], accept_multiple_files=True, key="drive_gg")
    
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
        # 1. Processar GG
        if arquivos_gg:
            texto_gg = ""
            for arq in arquivos_gg:
                conteudo = arq.read().decode("utf-8", errors="ignore")
                texto_gg += customizar_nicks_hh(conteudo, nick_gg) + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("GGPoker_convertido.txt", texto_gg)
            
        # 2. Processar Party
        if arquivos_party:
            texto_party = ""
            for arq in arquivos_party:
                conteudo = arq.read().decode("utf-8", errors="ignore")
                texto_party += customizar_nicks_hh(conteudo, nick_party) + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("PartyPoker_convertido.txt", texto_party)
            
        # 3. Processar PokerStars (Direto)
        if arquivos_stars:
            texto_stars = ""
            for arq in arquivos_stars:
                texto_stars += arq.read().decode("utf-8", errors="ignore") + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("PokerStars.txt", texto_stars)
            
        # 4. Processar WPN (Direto)
        if arquivos_wpn:
            texto_wpn = ""
            for arq in arquivos_wpn:
                texto_wpn += arq.read().decode("utf-8", errors="ignore") + "\n\n"
                arquivos_totais += 1
            arquivo_zip.writestr("WPN.txt", texto_wpn)
            
        # 5. Processar CoinPoker (Direto)
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
        
        str.success(f"📦 Pacote estruturado com sucesso! Total de {arquivos_totais} arquivos organizados.")
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