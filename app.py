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

# --- FUNÇÃO PARA CALCULAR O MÊS ANTERIOR AUTOMATICAMENTE ---
def obtener_ano_mes_retroativo():
    hoje = datetime.now()
    ano = hoje.year
    mes = hoje.month
    
    # Se for janeiro (1), o mês anterior é dezembro (12) do ano passado
    if mes == 1:
        mes_anterior = 12
        ano_anterior = ano - 1
    else:
        mes_anterior = mes - 1
        ano_anterior = ano
        
    return f"[{ano_anterior}.{mes_anterior:02d}]"

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
        
        # Ignora arquivos que contenham 'summary' no nome
        if "summary" in name_arq:
            continue
            
        if name_arq.endswith(".zip"):
            try:
                with zipfile.ZipFile(arq) as z:
                    for filename in z.namelist():
                        filename_lower = filename.lower()
                        # Ignora arquivos internos do zip que contenham 'summary'
                        if "summary" in filename_lower:
                            continue
                        if filename_lower.endswith(".txt"):
                            with z.open(filename) as f:
                                texto_acumulado += customizar_nicks_hh(f.read().decode("utf-8", errors="ignore"), nick) + "\n\n"
                                contagem += 1
            except Exception:
                pass
        elif name_arq.endswith(".txt"):
            texto_acumulado += customizar_nicks_hh(arq.read().decode("utf-8", errors="ignore"), nick) + "\n\n"
            contagem += 1
    return texto_acumulado, contagem

# --- CAPTURA DE CONFIGURAÇÕES VIA URL (MEMÓRIA DOS FAVORITOS) ---
default_nome = st.query_params.get("nome", "")
default_gg = st.query_params.get("gg", "")
default_party = st.query_params.get("party", "")
default_modo = st.query_params.get("modo", "Organizar para o Drive")

# --- INTERFACE INTERATIVA ---
st.title("🃏 Conversor de Hand History por Plataforma")
st.markdown("---")

col_esquerda, col_direita = st.columns([1, 3], gap="large")

# --- COLUNA DA ESQUERDA (CONFIGURAÇÕES GERAIS) ---
with col_esquerda:
    st.subheader("⚙️ Configurações Gerais")
    nome_jogador = st.text_input("Seu Nome e Sobrenome", value=default_nome, placeholder="Ex: Ramon Sfalsin")
    nick_gg = st.text_input("Nick no GGPoker", value=default_gg, placeholder="Seu nick na GG")
    nick_party = st.text_input("Nick no PartyPoker", value=default_party, placeholder="Seu nick na Party")
    
    st.markdown("---")
    st.subheader("🎯 Operação")
    modo = st.radio("Escolha o modo:", ["Apenas trocar o nick", "Organizar para o Drive"], index=1 if default_modo == "Organizar para o Drive" else 0)

# --- COLUNA DA DIREITA (ÁREA DE UPLOADS) ---
with col_direita:
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
                if "summary" in arq.name.lower():
                    continue
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
                # Nome do arquivo interno ajustado de 'GGPoker_convertido.txt' para 'GGPoker.txt'
                if texto_gg: arquivo_zip.writestr("GGPoker.txt", texto_gg); arquivos_totais += qtd
            if arquivos_party:
                texto_party = "".join([customizar_nicks_hh(arq.read().decode("utf-8", errors="ignore"), nick_party) + "\n\n" for arq in arquivos_party if "summary" not in arq.name.lower()])
                # Nome do arquivo interno ajustado de 'PartyPoker_convertido.txt' para 'PartyPoker.txt'
                if texto_party: arquivo_zip.writestr("PartyPoker.txt", texto_party); arquivos_totais += len(arquivos_party)
            if arquivos_stars:
                texto_stars = "".join([arq.read().decode("utf-8", errors="ignore") + "\n\n" for arq in arquivos_stars if "summary" not in arq.name.lower()])
                if texto_stars: arquivo_zip.writestr("PokerStars.txt", texto_stars); arquivos_totais += len(arquivos_stars)
            if archivos_wpn:
                texto_wpn = "".join([arq.read().decode("utf-8", errors="ignore") + "\n\n" for arq in arquivos_wpn if "summary" not in arq.name.lower()])
                if texto_wpn: arquivo_zip.writestr("WPN.txt", texto_wpn); arquivos_totais += len(arquivos_wpn)
            if arquivos_coin:
                texto_coin = "".join([arq.read().decode("utf-8", errors="ignore") + "\n\n" for arq in arquivos_coin if "summary" not in arq.name.lower()])
                if texto_coin: arquivo_zip.writestr("CoinPoker.txt", texto_coin); arquivos_totais += len(arquivos_coin)

        if arquivos_totais > 0:
            st.markdown("---")
            
            prefixo_data = obter_ano_mes_retroativo()
            nome_zip_final = f"{prefixo_data} {nome_jogador.strip() if nome_jogador.strip() else 'Jogador Sem Nome'}.zip"
            
            st.success(f"📦 Pacote estruturado com sucesso! Total de {arquivos_totais} arquivos válidos (arquivos 'summary' ignorados).")
            st.info("ℹ️ **Próximo passo:** Baixe o arquivo abaixo e coloque-o na sua pasta de Database no Google Drive!")
            buffer_zip.seek(0)
            st.download_button(label=f"📥 Baixar Pacote: {nome_zip_final}", data=buffer_zip, file_name=nome_zip_final, mime="application/zip", use_container_width=True)

# --- FAVORITOS (RODAPÉ DA ESQUERDA) ---
with col_esquerda:
    if nome_jogador or nick_gg or nick_party:
        st.markdown("---")
        with st.expander("💾 Salvar Minhas Configurações"):
            link_salvar = f"https://trocartick.streamlit.app/?nome={nome_jogador.replace(' ', '%20')}&gg={nick_gg}&party={nick_party}&modo={modo.replace(' ', '%20')}"
            st.markdown("Adicione aos **Favoritos**:")
            st.code(link_salvar, language="text")
