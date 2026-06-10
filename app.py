import streamlit as str
import re
import io
import zipfile
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
str.set_page_config(
    page_title="HH Nick Changer", 
    page_icon="🃏", 
    layout="wide"  # Mudamos para wide para dar espaço perfeito para as duas colunas ao mesmo tempo
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

# --- INTERFACE INTERATIVA COM DIVISÃO FIXA ---
str.title("🃏 Conversor de Hand History por Plataforma")
str.markdown("---")

# Criamos duas colunas grandes fixas na tela: 
# Esquerda (Configurações - peso 1) e Direita (Uploads - peso 3)
col_esquerda, col_direita = str.columns([1, 3], gap="large")

# --- COLUNA DA ESQUERDA (CONFIGURAÇÕES FIXAS) ---
with col_esquerda:
    str.subheader("⚙️ Configurações")
    nome_jogador = str.text_input("Seu Nome e Sobrenome", value=default_nome, placeholder="Ex: Ramon Sfalsin")
    nick_gg = str.text_input("Nick no GGPoker", value=default_gg, placeholder="Seu nick na GG")
    nick_party = str.text_input("Nick no PartyPoker", value=default_party, placeholder="Seu nick na Party")
    
    str.markdown("---")
    str.subheader("🎯 Operação")
    modo = str.radio(
        "Escolha o modo:",
        ["Apenas trocar o nick", "Organizar para o Drive"],
        index=0 if default_modo == "Apenas trocar o nick" else 1
    )

# --- COLUNA DA DIREITA (ÁREA DE UPLOADS E DOWNLOAD) ---
with col_direita:
    arquivos_totais = 0

    # LÓGICA MODO: APENAS TROCAR O NICK
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
            str.markdown("---")
            str.info("💡 Insira os arquivos da GG ou Party acima para gerar o seu arquivo convertido.")

    # LÓGICA MODO: ORGANIZAR PARA O DRIVE
    else:
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

# --- BLOCO DE SALVAR NO RODAPÉ FINAL DA COLUNA DE CONFIGURAÇÕES ---
with col_esquerda:
    if nome_jogador or nick_gg or nick_party:
        str.markdown("---")
        with str.expander("💾 Salvar Configurações"):
            link_salvar = f"https://trocarnick.streamlit.app/?nome={nome_jogador.replace(' ', '%20')}&gg={nick_gg}&party={nick_party}&modo={modo.replace(' ', '%20')}"
            str.markdown("Adicione aos **Favoritos**:")
            str.code(link_salvar, language="text")
