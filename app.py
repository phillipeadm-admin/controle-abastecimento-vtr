import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval
import os

# 1. CONFIGURAÇÃO DA INTELIGÊNCIA (AI STUDIO)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Erro: Configure a GOOGLE_API_KEY nos Secrets do Streamlit.")

# 2. LISTAS OFICIAIS
POLICIAIS = ["Selecione o Policial..."] + ["ST J. CARLOS", "SGT VALTER", "SGT JOSÉ LOPES", "SGT MARCOS PAULO", "SGT RODRIGUES", "SGT ADELSON", "SGT DANTAS", "SGT ELSON", "SGT JOSÉ", "SGT LEANDRO", "SGT MARCONI", "SGT MARCELO", "SGT CARVALHO", "SGT ANDERSON", "SGT NILTON", "SGT R. MARQUES", "CB ANDERSON", "CB ROBSON", "CB LUCIANO", "CB GOMES", "CB ISRAEL", "CB DOUGLAS", "CB C. LEITE", "SD RAQUEL", "SD L. DIAS", "SD CARLOS", "SD PEREIRA", "SD BRUNO"]
EQUIPAMENTOS = ["Selecione o Equipamento..."] + ["GERADOR QCG", "GERADOR APMB", "GERADOR 1º BPM", "GERADOR 2º BPM", "GERADOR 3º BPM", "GERADOR 4º BPM", "GERADOR 5º BPM", "GERADOR 6º BPM", "GERADOR 7º BPM", "GERADOR 8º BPM", "GERADOR 9º BPM", "GERADOR 10º BPM", "GERADOR 11º BPM", "GERADOR 12º BPM", "GERADOR 13º BPM", "GERADOR 14º BPM", "GERADOR 15º BPM", "GERADOR CMT GERAL", "GERADOR SUB CMT GERAL"]

# 3. LÓGICA DE PERSISTÊNCIA (BANCO DE DADOS)
DB_FILE = "abastecimentos.csv"

def salvar_dados(dados):
    df = pd.DataFrame([dados])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, header=True)
    else:
        df.to_csv(DB_FILE, mode='a', index=False, header=False)

def carregar_dados():
    if os.path.isfile(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], dayfirst=True)
        return df
    return pd.DataFrame(columns=["Data/Hora", "Policial", "Equipamento", "Litros", "Localizacao"])

# --- HORÁRIO E LOCALIZAÇÃO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_br)
agora_str = agora.strftime("%d/%m/%Y %H:%M:%S")

pos_json = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(success => { return {lat: success.coords.latitude, lon: success.coords.longitude} })", key="geo_location")

st.set_page_config(page_title="Abastecimento VTR", layout="centered")
st.title("⛽ Sistema de Abastecimento")

tab1, tab2 = st.tabs(["📝 Registro", "📊 Dashboard de Pesquisa"])

with tab1:
    st.subheader("Novo Lançamento")
    st.info(f"📅 Horário: {agora_str}")
    
    with st.form("form_abastecimento", clear_on_submit=True):
        policial_select = st.selectbox("Policial:", POLICIAIS)
        equip_select = st.selectbox("Equipamento:", EQUIPAMENTOS)
        litros_input = st.number_input("Litros:", min_value=0.0, step=0.1)
        foto_anexo = st.file_uploader("Anexar Comprovante (Obrigatório)", type=['png', 'jpg', 'jpeg'])
        
        enviar = st.form_submit_button("Realizar Registro")
        
        if enviar:
            if policial_select != "Selecione o Policial..." and equip_select != "Selecione o Equipamento..." and litros_input > 0 and foto_anexo is not None:
                loc_info = f"{pos_json['lat']}, {pos_json['lon']}" if pos_json else "GPS não disponível"
                
                # Criar dicionário de dados
                novo_registro = {
                    "Data/Hora": agora_str,
                    "Policial": policial_select,
                    "Equipamento": equip_select,
                    "Litros": litros_input,
                    "Localizacao": loc_info
                }
                
                salvar_dados(novo_registro)
                st.success("✅ REGISTRO SALVO NO BANCO DE DADOS!")
                st.balloons()
            else:
                st.error("⚠️ Erro: Todos os campos são obrigatórios!")

with tab2:
    st.subheader("🔎 Pesquisa de Registros")
    df_historico = carregar_dados()

    if not df_historico.empty:
        # Menus de Seleção por Ano e Mês
        anos = sorted(df_historico['Data/Hora'].dt.year.unique(), reverse=True)
        meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
                 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        
        col1, col2 = st.columns(2)
        with col1:
            ano_sel = st.selectbox("Filtrar por Ano:", anos)
        with col2:
            mes_sel_num = st.selectbox("Filtrar por Mês:", list(meses.keys()), format_func=lambda x: meses[x], index=agora.month-1)

        # Filtragem dos dados
        df_filtrado = df_historico[(df_historico['Data/Hora'].dt.year == ano_sel) & 
                                   (df_historico['Data/Hora'].dt.month == mes_sel_num)]

        if not df_filtrado.empty:
            st.write(f"Exibindo registros de **{meses[mes_sel_num]} de {ano_sel}**:")
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Gráfico Real baseado nos filtros
            st.bar_chart(data=df_filtrado, x='Equipamento', y='Litros')
            
            # Análise IA
            if st.button("Analisar este período com Gemini"):
                prompt = f"Analise o consumo de combustível deste mês ({meses[mes_sel_num]}): {df_filtrado.to_string()}"
                res = model.generate_content(prompt)
                st.write("🤖 **Análise da IA:**")
                st.write(res.text)
        else:
            st.warning(f"Nenhum registro encontrado para {meses[mes_sel_num]} de {ano_sel}.")
    else:
        st.info("O banco de dados está vazio. Os registros aparecerão aqui assim que forem realizados.")
