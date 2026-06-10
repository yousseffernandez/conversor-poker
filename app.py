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
def obter_ano_mes_retroativo():
    hoje = datetime.now()
    ano = hoje.year
    mes = hoje.month
    
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
        
        if "summary" in name_arq:
            continue
            
        if name_arq.endswith(".zip"):
            try:
                with zipfile.ZipFile(arq) as z:
                    for filename in z.namelist():
                        filename_lower = filename.lower()
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
st.title("🃏 Organizador de Database")
st.markdown("---")

col_esquerda, col_direita = st.columns([1, 3], gap="large")

# --- COLUNA DA ESQUERDA (CONFIGURAÇÕES GERAIS) ---
with col_esquerda:
    st.subheader("⚙️ Configurações Gerais")
    nome_jogador = st.text_input("Seu Nome e Sobrenome", value=default_nome, placeholder="Ex: José Silva")
    nick_gg = st.text_input("Nick no GGPoker", value=default_gg, placeholder="Seu nick na GG")
    nick_party = st.text_input("Nick no PartyPoker", value=default_party, placeholder="Seu nick na Party")
    
    st.markdown("---")
    st.subheader("🎯 Operação")
    modo = st.radio(
        "Escolha o modo:", 
        ["Apenas trocar o nick", "Organizar para o Drive"], 
        index=1 if default_modo == "Organizar para o Drive" else 0
    )

# --- COLUNA DA DIREITA (ÁREA DE UPLOADS) ---
with col_direita:
    arquivos_totais = 0

    if modo == "Apenas trocar o nick":
        st.markdown("### 🔴 GGPoker")
        arquivos_gg = st.file_uploader(
            "Arraste o seu arquivo .zip (ou .txt) da GGPoker", 
            type=["txt", "zip"], accept_multiple_files=True, key="gg_txt"
        )
        st.markdown("---")
        st.markdown("### 🧡 PartyPoker")
        arquivos_party = st.file_uploader(
            "Arraste os arquivos .txt do PartyPoker", 
            type=["txt"], accept_multiple_files=True, key="party_txt"
        )

        texto_final_unificado = ""
        if archivos_gg := arquivos_gg:
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
            st.download_button(
                label="📥 Baixar Arquivo Convertido (.TXT)", 
                data=texto_final_unificado, file_name="hands_convertidas.txt", 
                mime="text
