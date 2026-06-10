import streamlit as st
import re
import io
import zipfile
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="HH Nick Changer - PokerLab", page_icon="🃏", layout="wide")

# --- FUNÇÃO PARA EXTRAIR O ID DO LINK DO DRIVE ---
def extrair_id_drive(link):
    if not link:
        return ""
    # Procura pelo padrão padrão de IDs de pastas do Google Drive
    match = re.search(r'folders/([a-zA-Z0-9-_]+)', link)
    if match:
        return match.group(1)
    # Se o aluno colar apenas o ID direto em vez do link, retorna o próprio ID
    return link.strip()

# --- CONEXÃO COM O GOOGLE DRIVE ---
def conectar_google_drive():
    try:
        info_chaves = dict(st.secrets["gcp_service_account"])
        info_chaves["private_key"] = info_chaves["private_key"].replace("\\n", "\n")
        
        credenciais = service_account.Credentials.from_service_account_info(
            info_chaves, 
            scopes=["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        )
        return build('drive', 'v3', credentials=credenciais)
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Drive: {e}")
        return None

def upload_para_drive(buffer_arquivo, nome_arquivo, pasta_id):
    servico = conectar_google_drive()
    if not servico:
        return False
    
    metadados = {
        'name': nome_arquivo,
        'parents': [pasta_id]
    }
    
    media = MediaIoBaseUpload(buffer_arquivo, mime_type='application/zip', resumable=True)
    
    try:
        servico.files().create(body=metadados, media_body=media, fields='id').execute()
        return True
    except Exception as e:
        st.error(f"Erro ao enviar o arquivo. Verifique se a sua pasta foi compartilhada com o e-mail do robô. Detalhes: {e}")
        return False

# --- FUNÇÕES DE CONVERSÃO ---
def customizar_nicks_hh(texto_hh, novo_nick):
    if not novo_nick: return texto_hh
    return re.sub(r'\bHero\b', novo_nick, texto_hh, flags=re.IGNORECASE)

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
            except Exception: pass
        elif name_arq.endswith(".txt"):
            texto_acumulado += customizar_nicks_hh(arq.read().decode("utf-8", errors="ignore"), nick) + "\n\n"
            contagem += 1
    return texto_acumulado, contagem

# --- CAPTURA DE CONFIGURAÇÕES VIA URL (MEMÓRIA DOS FAVORITOS) ---
default_nome = st.query_params.get("nome", "")
default_gg = st.query_params.get("gg", "")
default_party = st.query_params.get("party", "")
default_drive = st.query_params.get("drive", "")

# --- INTERFACE ---
st.title("🃏 Conversor de Hand History (PokerLab Cloud)")
st.markdown("---")

col_esquerda, col_direita = st.columns([1, 3], gap="large")

# --- COLUNA DA ESQUERDA (CONFIGURAÇÕES GERAIS) ---
with col_esquerda:
    st.subheader("⚙️ Suas Informações")
    nome_jogador = st.text_input("Seu Nome e Sobrenome", value=default_nome, placeholder="Ex: Ramon Sfalsin")
    nick_gg = st.text_input("Nick no GGPoker", value=default_gg, placeholder="Seu nick na GG")
    nick_party = st.text_input("Nick no PartyPoker", value=default_party, placeholder="Seu nick na Party")
    
    st.markdown("---")
    st.subheader("📁 Destino da Database")
    link_drive = st.text_input("Link da sua pasta no Google Drive", value=default_drive, placeholder="Cole o link completo da sua pasta aqui")
    
    id_pasta_destino = extrair_id_drive(link_drive)

# --- COLUNA DA DIREITA (ÁREA DE TRABALHO) ---
with col_direita:
    st.markdown("### 📥 Área de Envio Compartilhada")
    
    if not nome_jogador.strip() or not id_pasta_destino:
        st.info("👈 Por favor, preencha o seu **Nome** e cole o **Link da sua pasta do Drive** na barra lateral para liberar o painel.")
    else:
        st.success(f"Sistema pronto para: **{nome_jogador}**")
        
        arquivos_gg = st.file_uploader("GGPoker (.zip ou .txt)", type=["txt", "zip"], accept_multiple_files=True, key="d_gg")
        arquivos_party = st.file_uploader("PartyPoker (.txt)", type=["txt"], accept_multiple_files=True, key="d_party")
        arquivos_stars = st.file_uploader("PokerStars (.txt)", type=["txt"], accept_multiple_files=True, key="d_stars")
        arquivos_wpn = st.file_uploader("WPN (.txt)", type=["txt"], accept_multiple_files=True, key="d_wpn")
        arquivos_coin = st.file_uploader("CoinPoker (.txt)", type=["txt"], accept_multiple_files=True, key="d_coin")

        arquivos_totais = 0
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
            nome_zip_final = f"{datetime.now().strftime('[%Y.%m]')} {nome_jogador.strip()}.zip"
            
            if st.button("🚀 ENVIAR CONVERSÃO DIRETO PARA O MEU DRIVE", use_container_width=True, type="primary"):
                with st.spinner("Processando mãos e enviando para a sua pasta..."):
                    buffer_zip.seek(0)
                    
                    sucesso = upload_para_drive(buffer_zip, nome_zip_final, id_pasta_destino)
                    if sucesso:
                        st.success(f"✅ Feito, {nome_jogador}! O arquivo '{nome_zip_final}' já está salvo na sua pasta do Drive.")
                    else:
                        st.error("❌ Falha no envio automático. Certifique-se de que você compartilhou essa sua pasta com o e-mail do robô da PokerLab dando permissão de 'Editor'.")

# --- BLOCO DE SALVAR NOS FAVORITOS (RODAPÉ DA ESQUERDA) ---
with col_esquerda:
    if nome_jogador.strip() or nick_gg or nick_party or link_drive:
        st.markdown("---")
        with st.expander("💾 Salvar Minhas Configurações"):
            # Codifica os parâmetros para a URL de favoritos incluir o link do drive também
            link_salvar = f"https://trocartick.streamlit.app/?nome={nome_jogador.replace(' ', '%20')}&gg={nick_gg}&party={nick_party}&drive={link_drive.replace('/', '%2F').replace(':', '%3A')}"
            st.markdown("Adicione esta URL aos **Favoritos** do seu navegador para não precisar preencher nunca mais:")
            st.code(link_salvar, language="text")
