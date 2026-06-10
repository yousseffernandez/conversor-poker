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
    st.
