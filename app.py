import streamlit as st
import re
import io
import zipfile
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="HH Nick Changer - PokerLab", 
    page_icon="🃏", 
    layout="wide"
)

# --- 🔐 BANCO DE DADOS DE JOGADORES PERMITIDOS ---
# Você gerencia quem entra por aqui. Adicione os tokens para os seus jogadores.
# Dica: Passe um token exclusivo para cada jogador do seu time.
TOKENS_PERMITIDOS = {
    "youssef-pokerlab": "Youssef Fernandez",
    "ramon-pokerlab": "Ramon Sfalsin",
    "teste-pokerlab": "Jogador Teste"
}

# --- FUNÇÃO DE CONVERSÃO ---
def customizar_nicks_hh(texto_hh, novo_nick):
    if not novo_nick:
        return texto_hh
    return re.sub(r'\bHero\b', novo_nick, texto_hh, flags=re.IGNORECASE)

# --- FUNÇÃO PARA PROCESSAR INPUTS DA GG ---
def processar_arquivos_gg(arquivos_upados, nick):
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
                                texto_acumulado += customizar_nicks_hh(f.read().decode("utf-8", errors="ignore"), nick) + "\n\n"
                                contagem += 1
            except Exception:
                pass
        elif name_arq.endswith(".txt"):
            texto_acumulado += customizar_nicks_hh(arq.read().decode("utf-8", errors="ignore"), nick) + "\n\n"
            contagem += 1
    return texto_acumulado, contagem

# --- CAPTURA DE CONFIGURAÇÕES VIA URL ---
default_token = st.query_params.get("token", "")
default_gg = st.query_params.get("gg", "")
default_party = st.query_params.get("party", "")
default_modo = st.query_params.get("modo", "Apenas trocar o nick")

# --- INTERFACE INTERATIVA ---
st.title("🃏 Conversor de Hand History por Plataforma")
st.markdown("---")

col_esquerda, col_direita = st.columns([1, 3], gap="large")

# --- COLUNA DA ESQUERDA (AUTENTICAÇÃO POR TOKEN) ---
with col_esquerda:
    st.subheader("🔐 Identificação do Time")
    token_inserido = st.text_input("Digite seu Token de Acesso Individual", value=default_token, type="password", placeholder="Ex: seu-token-exclusivo")
    
    if token_inserido.strip() not in TOKENS_PERMITIDOS:
        if token_inserido:
            st.error("❌ Token inválido ou revogado pela gerência.")
        acesso_liberado = False
        nome_jogador = ""
    else:
        nome_jogador = TOKENS_PERMITIDOS[token_inserido.strip()]
        st.success(f"✅ Olá, {nome_jogador}! Acesso PokerLab Liberado.")
        acesso_liberado = True
        
    if acesso_liberado:
        st.markdown("---")
        st.subheader("⚙️ Nicks do Jogador")
        nick_gg = st.text_input("Nick no GGPoker", value=default_gg, placeholder="Seu nick na GG")
        nick_party = st.text_input("Nick no PartyPoker", value=default_party, placeholder="Seu nick na Party")
        
        st.markdown("---")
        st.subheader("🎯 Operação")
        modo = st.radio("Escolha o modo:", ["Apenas trocar o nick", "Organizar para o Drive"], index=0 if default_modo == "Apenas trocar o nick" else 1)

# --- COLUNA DA DIREITA (ÁREA DE TRABALHO PROTEGIDA) ---
with col_direita:
    if not acesso_liberado:
        st.info("🔒 Painel restrito aos membros da PokerLab. Insira seu Token Individual na barra lateral para liberar as ferramentas.")
    else:
        arquivos_totais = 0

        if modo == "Apenas trocar o nick":
            st.markdown("### 🔴 GGPoker `[GG]`")
            arquivos_gg = st.file_uploader("Arraste o seu arquivo .zip (ou .txt) da GGPoker", type=["txt", "zip"], accept_multiple_files=True, key="gg_txt")
            st.markdown("---")
            st.markdown("### 🧡 PartyPoker `[partypoker]`")
            arquivos_party = st.file_uploader("Arraste os arquivos .txt do PartyPoker", type=["txt"], accept_multiple_files=True, key="party_txt")

            texto_final_unificado = ""
            if arquivos_gg:
                texto_gg, qtd = processar_arquivos_gg(arquivos_gg, nick_gg)
                texto_final_unificado += texto_gg
                arquivos_totais += qtd
            if arquivos_party:
                for arq in arquivos_party:
                    texto_final_unificado += customizar_nicks_hh(arq.read().decode("utf-8", errors="ignore"), nick_party) + "\n\n"
                    arquivos_totais += 1

            if arquivos_totais > 0:
                st.markdown("---")
                st.success(f"🎉 Pronto! {arquivos_totais} arquivo(s) convertido(s)!")
                st.download_button(label="📥 Baixar Arquivo Convertido (.TXT)", data=texto_final_unificado, file_name="hands_convertidas.txt", mime="text/plain", use_container_width=True)

        else:
            # MODO DRIVE
            st.markdown("### 🔴 GGPoker `[GG]`")
            arquivos_gg = st.file_uploader("Arraste o seu arquivo .zip (ou .txt) da GGPoker", type=["txt", "zip"], accept_multiple_files=True, key="drive_gg")
            st.markdown("---")
            st.markdown("### 🧡 PartyPoker `[partypoker]`")
            arquivos_party = st.file_uploader("Arraste os arquivos .txt do PartyPoker", type=["txt"], accept_multiple_files=True, key="drive_party")
            st.markdown("---")
            st.markdown("### ♠️ PokerStars `[*]`")
            arquivos_stars = st.file_uploader("Arraste os arquivos .txt do PokerStars", type=["txt"], accept_multiple_files=True, key="drive_stars")
            st.markdown("---")
            st.markdown("### 🟦 WPN `[Winning Poker Network]`")
            arquivos_wpn = st.file_uploader("Arraste os arquivos .txt da WPN", type=["txt"], accept_multiple_files=True, key="drive_wpn")
            st.markdown("---")
            st.markdown("### 🪙 CoinPoker `[CHP]`")
            arquivos_coin = st.file_uploader("Arraste os arquivos .txt do CoinPoker", type=["txt"], accept_multiple_files=True, key="drive_coin")

            buffer_zip = io.BytesIO()
            with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as arquivo_zip:
                if arquivos_gg:
                    texto_gg, qtd = processar_arquivos_gg(arquivos_gg, nick_gg)
                    if texto_gg: arquivo_zip.writestr("GGPoker_convertido.txt", texto_gg); arquivos_totais += qtd
                if arquivos_party:
                    texto_party = "".join([customizar_nicks_hh(arq.read().decode("utf-8", errors="ignore"), nick_party) + "\n\n" for arq in arquivos_party])
                    arquivo_zip.writestr("PartyPoker_convertido.txt", texto_party); arquivos_totais += len(arquivos_party)
                if arquivos_stars:
                    texto_stars = "".join([arq.read().decode("utf-8", errors="ignore") + "\n\n" for arq in arquivos_stars])
                    arquivo_zip.writestr("PokerStars.txt", texto_stars); arquivos_totais += len(arquivos_stars)
                if arquivos_wpn:
                    texto_wpn = "".join([arq.read().decode("utf-8", errors="ignore") + "\n\n" for arq in arquivos_wpn])
                    arquivo_zip.writestr("WPN.txt", texto_wpn); arquivos_totais += len(arquivos_wpn)
                if arquivos_coin:
                    texto_coin = "".join([arq.read().decode("utf-8", errors="ignore") + "\n\n" for arq in arquivos_coin])
                    arquivo_zip.writestr("CoinPoker.txt", texto_coin); arquivos_totais += len(arquivos_coin)

            if arquivos_totais > 0:
                st.markdown("---")
                nome_zip_final = f"{datetime.now().strftime('[%Y.%m]')} {nome_jogador}.zip"
                st.success(f"📦 Pacote estruturado com sucesso! Total de {arquivos_totais} arquivos.")
                st.info("ℹ️ **Próximo passo:** Baixe o arquivo abaixo e coloque-o na sua pasta de Database no Google Drive!")
                buffer_zip.seek(0)
                st.download_button(label=f"📥 Baixar Pacote: {nome_zip_final}", data=buffer_zip, file_name=nome_zip_final, mime="application/zip", use_container_width=True)

# --- FAVORITOS (RODAPÉ DA ESQUERDA) ---
with col_esquerda:
    if acesso_liberado and (nick_gg or nick_party):
        st.markdown("---")
        with st.expander("💾 Salvar Configurações"):
            link_salvar = f"https://trocartick.streamlit.app/?token={token_inserido}&gg={nick_gg}&party={nick_party}&modo={modo.replace(' ', '%20')}"
            st.markdown("Adicione aos **Favoritos**:")
            st.code(link_salvar, language="text")
