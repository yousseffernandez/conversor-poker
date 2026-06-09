import streamlit as str
import re
import io
import zipfile

# Configuração da página
str.set_page_config(page_title="HH Nick Changer", page_icon="🃏", layout="centered")

# --- FUNÇÃO DE CONVERSÃO ---
def customizar_nicks_hh(texto_hh, novo_nick):
    """Substitui a palavra 'Hero' pelo nick configurado (case-insensitive)."""
    if not novo_nick:
        return texto_hh
    # Substituição exata de "Hero" isolado
    texto_atualizado = re.sub(r'\bHero\b', novo_nick, texto_hh, flags=re.IGNORECASE)
    return texto_atualizado

# --- CAPTURA DE NICKS VIA URL (SALVAR CONFIGURAÇÃO) ---
# Se o link tiver ?gg=MeuNick, ele usa. Se não, deixa o padrão "Hero" ou vazio.
query_params = str.query_params
default_gg = query_params.get("gg", "")
default_party = query_params.get("party", "")

# --- INTERFACE INTERATIVA (STREAMLIT) ---
str.title("🃏 Conversor de Hand History por Plataforma")

str.markdown("---")

# 1. Configuração dos Nicks na Barra Lateral
str.sidebar.header("⚙️ Configuração de Nicks")
nick_gg = str.sidebar.text_input("Seu Nick no GGPoker", value=default_gg, placeholder="Digite seu nick da GG")
nick_party = str.sidebar.text_input("Seu Nick no PartyPoker", value=default_party, placeholder="Digite seu nick da Party")

# Link dinâmico para o usuário salvar nos favoritos
str.sidebar.markdown("---")
str.sidebar.markdown("### 💾 Salvar meus Nicks")
if nick_gg or nick_party:
    link_salvar = f"https://trocarnick.streamlit.app/?gg={nick_gg}&party={nick_party}"
    str.sidebar.markdown("Para salvar estes nicks, adicione o link abaixo aos seus **Favoritos** do navegador:")
    str.sidebar.code(link_salvar, language="text")
else:
    str.sidebar.info("Digite os nicks acima para gerar o seu link personalizado.")

# Criar um único arquivo ZIP na memória para a entrega final
buffer_zip = io.BytesIO()
arquivos_totais_convertidos = 0

# --- PROCESSAR OS ARQUIVOS E FECHAR O ZIP ---
with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as arquivo_zip:

    # --- SEÇÃO GGPOKER (CONSOLIDADA) ---
    str.markdown("### 🔥 GGPoker (Todos os arquivos serão unidos em apenas 1)")
    arquivos_gg = str.file_uploader(
        "Arraste aqui os arquivos .txt da GGPOKER", 
        type=["txt"], 
        accept_multiple_files=True,
        key="uploader_gg"
    )
    
    if arquivos_gg:
        texto_gg_consolidado = ""
        for arquivo in arquivos_gg:
            conteudo = arquivo.read().decode("utf-8", errors="ignore")
            texto_convertido = customizar_nicks_hh(conteudo, nick_gg)
            texto_gg_consolidado += texto_convertido + "\n\n"
            arquivos_totais_convertidos += 1
            
        arquivo_zip.writestr("GG_COMPLETO_convertido.txt", texto_gg_consolidado)
        str.success(f"📦 {len(arquivos_gg)} arquivos da GG foram unidos com sucesso em um único arquivo!")

    str.markdown("---")

    # --- SEÇÃO PARTYPOKER (MANTIDO INDIVIDUAL) ---
    str.markdown("### 🎯 PartyPoker")
    arquivos_party = str.file_uploader(
        "Arraste aqui os arquivos .txt do PARTYPOKER", 
        type=["txt"], 
        accept_multiple_files=True,
        key="uploader_party"
    )
    
    if arquivos_party:
        for arquivo in arquivos_party:
            conteudo = arquivo.read().decode("utf-8", errors="ignore")
            texto_convertido = customizar_nicks_hh(conteudo, nick_party)
            arquivo_zip.writestr(f"Party_convertido_{arquivo.name}", texto_convertido)
            arquivos_totais_convertidos += 1
        str.success(f"🔹 {len(arquivos_party)} arquivos do PartyPoker processados.")

# --- EXIBIR O BOTÃO DE DOWNLOAD ---
if arquivos_totais_convertidos > 0:
    str.markdown("---")
    str.success(f"🎉 Processamento concluído de {arquivos_totais_convertidos} arquivos!")
    buffer_zip.seek(0)
    
    str.download_button(
        label="📥 Clique aqui para Baixar o Pacote Convertido (.ZIP)",
        data=buffer_zip,
        file_name="hands_convertidas_filtros.zip",
        mime="application/zip",
        use_container_width=True
    )
else:
    str.markdown("---")
    str.info("💡 Insira os seus arquivos num dos campos acima para gerar o botão de download.")