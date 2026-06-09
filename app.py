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

# --- INTERFACE INTERATIVA (STREAMLIT) ---
str.title("🃏 Conversor de Hand History por Plataforma")
str.subheader("GGPOKER consolidada em arquivo único!")

str.markdown("---")

# 1. Configuração dos Nicks na Barra Lateral
str.sidebar.header("⚙️ Configuração de Nicks")
nick_gg = str.sidebar.text_input("Seu Nick no GGPoker", value="MeuNickGG")
nick_party = str.sidebar.text_input("Seu Nick no PartyPoker", value="MeuNickParty")

# Criar um único arquivo ZIP na memória para a entrega final
buffer_zip = io.BytesIO()
arquivos_totais_convertidos = 0

# --- PASSO 1: PROCESSAR OS ARQUIVOS E FECHAR O ZIP ---
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
        # Juntar e converter o texto de todos os arquivos enviados
        for arquivo in arquivos_gg:
            conteudo = arquivo.read().decode("utf-8", errors="ignore")
            texto_convertido = customizar_nicks_hh(conteudo, nick_gg)
            # Adiciona o texto convertido ao bloco único, pulando linha
            texto_gg_consolidado += texto_convertido + "\n\n"
            arquivos_totais_convertidos += 1
            
        # Salva apenas UM arquivo grande da GG dentro do ZIP
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
            # Salva no ZIP de forma individual
            arquivo_zip.writestr(f"Party_convertido_{arquivo.name}", texto_convertido)
            arquivos_totais_convertidos += 1
        str.success(f"🔹 {len(arquivos_party)} arquivos do PartyPoker processados.")

# --- PASSO 2: EXIBIR O BOTÃO DE DOWNLOAD (FORA E DEPOIS DO BLOCO WITH) ---
if arquivos_totais_convertidos > 0:
    str.markdown("---")
    str.success(f"🎉 Processamento concluído de {arquivos_totais_convertidos} arquivos!")
    
    # Reposiciona o ponteiro do buffer para o início
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