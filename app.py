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

# --- DICIONÁRIO DE MESES PARA EXIBIÇÃO E FORMATAÇÃO ---
MESES_OPCOES = {
    "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
    "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
    "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
}

# --- FUNÇÃO PARA PEGAR O MÊS ANTERIOR COMO PADRÃO AUTOMÁTICO ---
def obter_mes_anterior_padrao():
    hoje = datetime.now()
    ano = hoje.year
    mes = hoje.month
    
    if mes == 1:
        return "Dezembro", ano - 1
    
    nomes_lista = list(MESES_OPCOES.keys())
    return nomes_lista[mes - 2], ano

# --- FUNÇÃO DE CONVERSÃO DE NICK ---
def customizar_nicks_hh(texto_hh, novo_nick):
    if not novo_nick:
        return texto_hh
    return re.sub(r'\bHero\b', novo_nick, texto_hh, flags=re.IGNORECASE)

# --- FUNÇÃO PARA FILTRAR SUMÁRIOS (POKERSTARS E WPN) ---
def eh_sumario_stars_ou_wpn(nome_arquivo):
    nome_lower = nome_arquivo.lower()
    if nome_lower.endswith("summary.txt") or "summary" in nome_lower:
        return True
    return False

# --- FUNÇÃO GENÉRICA PARA PROCESSAR QUALQUER SALA (SEM CABEÇALHO EXTRA) ---
def processar_arquivos_sala(arquivos_upados, nick_sala="", aplicar_filtro_sumario=False):
    texto_acumulado = ""
    contagem = 0
    
    for arq in arquivos_upados:
        name_arq = arq.name.lower()
        
        if name_arq.endswith(".zip"):
            try:
                with zipfile.ZipFile(arq) as z:
                    for filename in z.namelist():
                        if filename.startswith("__MACOSX") or filename.endswith("/"):
                            continue
                        
                        if filename.lower().endswith(".txt"):
                            if aplicar_filtro_sumario and eh_sumario_stars_ou_wpn(filename):
                                continue
                            
                            with z.open(filename) as f:
                                conteudo = f.read().decode("utf-8", errors="ignore")
                                if nick_sala.strip():
                                    conteudo = customizar_nicks_hh(conteudo, nick_sala)
                                texto_acumulado += conteudo + "\n\n"
                                contagem += 1
            except Exception:
                pass
        
        elif name_arq.endswith(".txt"):
            if aplicar_filtro_sumario and eh_sumario_stars_ou_wpn(name_arq):
                continue
                
            conteudo = arq.read().decode("utf-8", errors="ignore")
            if nick_sala.strip():
                conteudo = customizar_nicks_hh(conteudo, nick_sala)
            texto_acumulado += conteudo + "\n\n"
            contagem += 1
            
    return texto_acumulado, contagem

# --- CAPTURA DE CONFIGURAÇÕES VIA URL ---
default_nome = st.query_params.get("nome", "")
default_gg = st.query_params.get("gg", "")
default_party = st.query_params.get("party", "")
default_coin = st.query_params.get("coin", "")
default_modo = st.query_params.get("modo", "Organizar para o Drive")

# --- INTERFACE INTERATIVA ---
st.title("🃏 Organizador de Database")
st.markdown("---")

col_esquerda, col_direita = st.columns([1, 3], gap="large")

with col_esquerda:
    st.subheader("⚙️ Configurações Gerais")
    nome_jogador = st.text_input("Seu Nome e Sobrenome", value=default_nome, placeholder="Ex: José Silva")
    nick_gg = st.text_input("Nick no GGPoker", value=default_gg, placeholder="Seu nick na GG")
    nick_party = st.text_input("Nick no PartyPoker", value=default_party, placeholder="Seu nick na Party")
    nick_coin = st.text_input("Nick no CoinPoker", value=default_coin, placeholder="Seu nick na Coin")
    
    st.markdown("---")
    st.subheader("📅 Período da Database")
    
    # Calcula o mês anterior padrão automático
    mes_padrao_nome, ano_padrao_num = obter_mes_anterior_padrao()
    lista_nomes_meses = list(MESES_OPCOES.keys())
    idx_padrao = lista_nomes_meses.index(mes_padrao_nome)
    
    # Pergunta de confirmação Sim/Não (Default: Sim)
    eh_mes_anterior = st.radio(
        "Este arquivo é referente ao mês anterior?",
        ["Sim", "Não"],
        index=0
    )
    
    if eh_mes_anterior == "Sim":
        prefixo_data = f"[{ano_padrao_num}.{MESES_OPCOES[mes_padrao_nome]}]"
    else:
        mes_selecionado = st.selectbox("Selecione o mês das mãos:", lista_nomes_meses, index=idx_padrao)
        ano_selecionado = st.number_input("Ano correspondente:", min_value=ano_padrao_num - 5, max_value=ano_padrao_num + 1, value=ano_padrao_num, step=1)
        prefixo_data = f"[{ano_selecionado}.{MESES_OPCOES[mes_selecionado]}]"
    
    # Exibe em tempo real como o arquivo será nomeado para o Drive
    nome_exemplo_jogador = nome_jogador.strip() if nome_jogador.strip() else "Nome Do Aluno"
    st.info(f"💾 **O arquivo será salvo como:**\n`{prefixo_data} {nome_exemplo_jogador}.zip`")
    
    st.markdown("---")
    st.subheader("🎯 Operação")
    modo = st.radio(
        "Escolha o modo:", 
        ["Apenas trocar o nick", "Organizar para o Drive"], 
        index=1 if default_modo == "Organizar para o Drive" else 0
    )

    # --- SALVAR CONFIGURAÇÕES POSICIONADO EXATAMENTE NO FIM DA COLUNA DA ESQUERDA ---
    if nome_jogador or nick_gg or nick_party or nick_coin:
        st.markdown("---")
        with st.expander("💾 Salvar Minhas Configurações"):
            link_salvar = f"https://trocartick.streamlit.app/?nome={nome_jogador.replace(' ', '%20')}&gg={nick_gg}&party={nick_party}&coin={nick_coin}&modo={modo.replace(' ', '%20')}"
            st.markdown("Adicione aos **Favoritos**:")
            st.code(link_salvar, language="text")

with col_direita:
    if modo == "Apenas trocar o nick":
        st.markdown("### 🔴 GGPoker")
        arquivos_gg = st.file_uploader("Arraste sua pasta do (PokerCraft .zip) da GGPoker", type=["txt", "zip"], accept_multiple_files=True, key="gg_txt")
        st.markdown("---")
        st.markdown("### 🧡 PartyPoker")
        arquivos_party = st.file_uploader("Arraste sua (pasta) ou (.txt) ou (.zip) do PartyPoker", type=["txt", "zip"], accept_multiple_files=True, key="party_txt")
        st.markdown("---")
        st.markdown("### 🪙 CoinPoker")
        arquivos_coin = st.file_uploader("Arraste os arquivos .txt ou .zip do CoinPoker", type=["txt", "zip"], accept_multiple_files=True, key="coin_txt")

        st.markdown(" ")
        if st.button("🚀 Converter e Unificar Nicks", use_container_width=True, type="primary"):
            texto_final_unificado = ""
            arquivos_totais = 0
            
            if arquivos_gg:
                texto_gg, qtd = processar_arquivos_sala(arquivos_gg, nick_sala=nick_gg)
                texto_final_unificado += texto_gg; arquivos_totais += qtd
            if arquivos_party:
                texto_party, qtd = processar_arquivos_sala(arquivos_party, nick_sala=nick_party)
                texto_final_unificado += texto_party; arquivos_totais += qtd
            if arquivos_coin:
                texto_coin, qtd = processar_arquivos_sala(arquivos_coin, nick_sala=nick_coin)
                texto_final_unificado += texto_coin; arquivos_totais += qtd

            if arquivos_totais > 0:
                st.success(f"🎉 Pronto! {arquivos_totais} arquivo(s) convertido(s)!")
                st.download_button(label="📥 Baixar Arquivo Convertido (.TXT)", data=texto_final_unificado, file_name="hands_convertidas.txt", mime="text/plain", use_container_width=True)
            else:
                st.error("⚠️ Nenhum arquivo foi enviado para processamento.")

    else:
        # MODO DRIVE
        st.markdown("### 🔴 GGPoker")
        arquivos_gg = st.file_uploader("Arraste sua pasta do (PokerCraft .zip) da GGPoker", type=["txt", "zip"], accept_multiple_files=True, key="drive_gg")
        st.markdown("---")
        st.markdown("### 🧡 PartyPoker")
        arquivos_party = st.file_uploader("Arraste sua (pasta) ou (.txt) ou (.zip) do PartyPoker", type=["txt", "zip"], accept_multiple_files=True, key="drive_party")
        st.markdown("---")
        st.markdown("### ♠️ PokerStars")
        arquivos_stars = st.file_uploader("Arraste sua (pasta) ou (.txt) ou (.zip) do PokerStars", type=["txt", "zip"], accept_multiple_files=True, key="drive_stars")
        st.markdown("---")
        st.markdown("### 🟦 WPN")
        arquivos_wpn = st.file_uploader("Arraste sua (pasta) ou (.txt) ou (.zip) da WPN", type=["txt", "zip"], accept_multiple_files=True, key="drive_wpn")
        st.markdown("---")
        st.markdown("### 🪙 CoinPoker")
        arquivos_coin = st.file_uploader("Arraste sua (pasta) ou (.txt) ou (.zip) do CoinPoker", type=["txt", "zip"], accept_multiple_files=True, key="drive_coin")

        st.markdown(" ")
        if st.button("🚀 Estruturar e Gerar Pacote para o Drive", use_container_width=True, type="primary"):
            buffer_zip = io.BytesIO()
            arquivos_totais = 0
            
            with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as arquivo_zip:
                if arquivos_gg:
                    texto_gg, qtd = processar_arquivos_sala(arquivos_gg, nick_sala=nick_gg)
                    if texto_gg: arquivo_zip.writestr("GGPoker.txt", texto_gg); arquivos_totais += qtd
                        
                if arquivos_party:
                    texto_party, qtd = processar_arquivos_sala(arquivos_party, nick_sala=nick_party)
                    if texto_party: arquivo_zip.writestr("PartyPoker.txt", texto_party); arquivos_totais += qtd
                
                if arquivos_stars:
                    texto_stars, qtd = processar_arquivos_sala(arquivos_stars, aplicar_filtro_sumario=True)
