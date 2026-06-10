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

# --- FUNÇÃO DE VALIDAÇÃO DE ACESSO ---
def verificar_acesso_pokerlab(email_usuario):
    if not email_usuario:
        return False
    # Garante que termine exatamente com @pokerlab.com.br
    return email_usuario.strip().lower().endswith("@pokerlab.com.br")

# --- FUNÇÃO DE CONVERSÃO ---
def customizar_nicks_hh(texto_hh, novo_nick):
    """Substitui a palavra 'Hero' pelo nick configurado (case-insensitive)."""
    if not novo_nick:
        return texto_hh
    texto_atualizado = re.sub(r'\bHero\b', novo_nick, texto_hh, flags=re.IGNORECASE)
    return texto_atualizado

# --- FUNÇÃO PARA PROCESSAR INPUTS DA GG (TXT OU ZIP) ---
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
default_nome = st.query_params.get("nome", "")
default_gg = st.query_params.get("gg", "")
default_party = st.query_params.get("party", "")
default_modo = st.query_params.get("modo", "Apenas trocar o nick")
default_email = st.query_params.get("email", "")

# --- INTERFACE INTERATIVA ---
st.title("🃏 Conversor de Hand History por Plataforma")
st.markdown("---")

col_esquerda, col_direita = st.columns([1, 3], gap="large")

# --- COLUNA DA ESQUERDA (AUTENTICAÇÃO E CONFIGURAÇÕES) ---
with col_esquerda:
    st.subheader("🔐 Acesso Organizacional")
    email_corp = st.text_input("E-mail corporativo PokerLab", value=default_email, placeholder="seu.nome@pokerlab.com.br")
    
    if not verificar_acesso_pokerlab(email_corp):
        st.error("❌ Acesso negado. Utilize seu e-mail corporativo para liberar o sistema.")
        acesso_liberado = False
    else:
        st.success("✅ Acesso Liberado!")
        acesso_liberado = True
        
    if acesso_liberado:
        st.markdown("---")
        st.subheader("⚙️ Configurações")
        nome_jogador = st.text_input("Seu Nome e Sobrenome", value=default_nome, placeholder="Ex: Ramon Sfalsin")
        nick_gg = st.text_input("Nick no GGPoker", value=default_gg, placeholder="Seu nick na GG")
        nick_party = st.text_input("Nick no PartyPoker", value=default_party, placeholder="Seu nick na Party")
        
        st.markdown("---")
        st.subheader("🎯 Operação")
        modo = st.radio(
            "Escolha o modo:",
            ["Apenas trocar o nick", "Organizar para o Drive"],
            index=0 if default_modo == "Apenas trocar o nick" else 1
        )

# --- COLUNA DA DIREITA (ÁREA DE TRABALHO PROTEGIDA) ---
with col_direita:
    if not acesso_liberado:
        st.info("🔒 Por motivos de segurança, utilize o seu e-mail corporativo da organização na barra lateral para liberar o painel.")
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
                    conteudo = arq.read().decode("utf-8", errors="ignore")
                    texto_final_unificado += customizar_nicks_hh(conteudo, nick_party) + "\n\n"
                    arquivos_totais += 1

            if arquivos_totais > 0:
                st.markdown("---")
                st.success(f"🎉 Pronto! {arquivos_totais} arquivo(s) de mãos convertido(s) com sucesso!")
                st.download_button(
                    label="📥 Baixar Arquivo Convertido (.TXT)",
                    data=texto_final_unificado,
                    file_name="hands_convertidas.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.markdown("---")
                st.info("💡 Insira os arquivos da GG ou Party acima para gerar o seu arquivo convertido.")

        else:
            # MODO DRIVE
            st.markdown("### 🔴 GGPoker `[GG]`")
            arquivos_gg = st.file_uploader("Arraste o seu arquivo .zip (ou .txt) da GGPoker", type=["txt", "zip"], accept_multiple_files=True, key="drive_gg")
            
            st.markdown("---")
            st.markdown("### 🧡 PartyPoker `[partypoker]`")
            arquivos_party = st.file_uploader("Arraste os arquivos .txt do PartyPoker", type=["txt"], accept_multiple_files=True, key="drive_party")
            
            st.markdown("---")
            st.markdown("### ♠️ PokerStars `[*]` (Apenas envelopar)")
            arquivos_stars = st.file_uploader("Arraste os arquivos .txt do PokerStars", type=["txt"], accept_multiple_files=True, key="drive_stars")
            
            st.markdown("---")
            st.markdown("### 🟦 WPN `[Winning Poker Network]` (Apenas envelopar)")
            arquivos_wpn = st.file_uploader("Arraste os arquivos .txt da WPN", type=["txt"], accept_multiple_files=True, key="drive_wpn")
            
            st.markdown("---")
            st.markdown("### 🪙 CoinPoker `[CHP]` (Apenas envelopar)")
            arquivos_coin = st.file_uploader("Arraste os arquivos .txt do CoinPoker", type=["txt"], accept_multiple_files=True, key="drive_coin")

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
                st.markdown("---")
                ano_mes = datetime.now().strftime("[%Y.%m]")
                nome_limpo = nome_jogador.strip() if nome_jogador.strip() else "Jogador Sem Nome"
                nome_zip_final = f"{ano_mes} {nome_limpo}.zip"
                st.success(f"📦 Pacote estruturado com sucesso! Total de {arquivos_totais} arquivos de mãos organizados.")
                st.info(f"ℹ️ **Próximo passo:** Baixe o arquivo abaixo e coloque-o diretamente na sua pasta de **Database** no Google Drive!")
                buffer_zip.seek(0)
                st.download_button(
                    label=f"📥 Baixar Pacote: {nome_zip_final}",
                    data=buffer_zip,
                    file_name=nome_zip_final,
                    mime="application/zip",
                    use_container_width=True
                )
            else:
                st.markdown("---")
                st.info("💡 Insira os arquivos das salas desejadas acima para gerar o pacote do Drive.")

# --- BLOCO DE SALVAR NOS FAVORITOS (RODAPÉ DA ESQUERDA) ---
with col_esquerda:
    if acesso_liberado and (nome_jogador or nick_gg or nick_party):
        st.markdown("---")
        with st.expander("💾 Salvar Configurações"):
            link_salvar = f"https://trocartick.streamlit.app/?email={email_corp}&nome={nome_jogador.replace(' ', '%20')}&gg={nick_gg}&party={nick_party}&modo={modo.replace(' ', '%20')}"
            st.markdown("Adicione aos **Favoritos**:")
            st.code(link_salvar, language="text")
