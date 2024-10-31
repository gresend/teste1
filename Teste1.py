import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
from fpdf import FPDF  
from io import BytesIO
import tempfile

# csv
csv_file = 'pacientes.csv'
consultas_file = 'consultas.csv'

# criar dataframe
if os.path.exists(csv_file):
    st.session_state.pacientes = pd.read_csv(csv_file)
    st.session_state.pacientes['CPF'] = st.session_state.pacientes['CPF'].astype(str)
else:
    st.session_state.pacientes = pd.DataFrame(columns=['Nome', 'CPF', 'Data de Nascimento', 'Endereço', 'Telefone'])

# criar dataframe consultas
if os.path.exists(consultas_file):
    st.session_state.consultas = pd.read_csv(consultas_file)
else:
    st.session_state.consultas = pd.DataFrame(columns=['Nome Paciente', 'Médico', 'Data/Hora'])

# adicionar paciente
def add_paciente(nome, cpf, data_nascimento, endereco, telefone):
    novopaciente = pd.DataFrame({
        'Nome': [nome],
        'CPF': [cpf],
        'Data de Nascimento': [data_nascimento],
        'Endereço': [endereco],
        'Telefone': [telefone]
    })

    if not st.session_state.pacientes[st.session_state.pacientes['CPF'] == cpf].empty:
        st.warning("Paciente com este CPF já cadastrado.")
        return

    st.session_state.pacientes = pd.concat([st.session_state.pacientes, novopaciente], ignore_index=True)
    st.session_state.pacientes.to_csv(csv_file, index=False)

# agendar consulta
def agendar_consulta(nome_paciente, medico, data_hora):
    nova_consulta = pd.DataFrame({
        'Nome Paciente': [nome_paciente],
        'Médico': [medico],
        'Data/Hora': [data_hora]
    })
    st.session_state.consultas = pd.concat([st.session_state.consultas, nova_consulta], ignore_index=True)
    st.session_state.consultas.to_csv(consultas_file, index=False)

# gerar receita em pdf
def gerar_pdf(nome_paciente, medico, data_consulta, receitas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="--- RECEITA MÉDICA ---", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Paciente: {nome_paciente}", ln=True)
    pdf.cell(200, 10, txt="Observações:", ln=True)
    pdf.cell(200, 10, txt="", ln=True)

    for receita in receitas:
        pdf.cell(200, 10, txt=receita, ln=True)
    pdf.cell(200, 10, txt=f"Médico Responsável: {medico}", ln=True)
    pdf.cell(200, 10, txt="Assinatura:__________________________", ln=True)
    pdf.cell(200, 10, txt=f"Data da Consulta: {data_consulta}", ln=True)
    pdf.cell(200, 10, txt="Coronel Xavier Chaves, Minas Gerais", ln=True)

    # Salvar o PDF em um arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# menu lateral
st.image('cabecalho.png', caption=None, channels="RGB")
st.sidebar.image('consultas.png', caption=None, channels="RGB")
opcao = st.sidebar.selectbox("Escolha uma opção", ["Cadastrar Paciente", "Buscar Paciente", "Editar Paciente", "Iniciar Consulta", "Agendar Consulta", "Ver Consultas Agendadas"])

if opcao == "Cadastrar Paciente":
    st.header("Cadastro de Paciente")
    nome = st.text_input("Nome", placeholder="Digite o nome...")
    cpf = st.text_input("CPF", placeholder="Digite o CPF...", max_chars=11)
    data_nascimento = st.date_input("Data de Nascimento", format="DD/MM/YYYY")
    endereco = st.text_input("Endereço", placeholder="Rua, número e bairro...")
    telefone = st.text_input("Telefone", placeholder="(XX) X XXXX-XXXX", max_chars=11)

    if st.button("Cadastrar Paciente"):
        add_paciente(nome, cpf, data_nascimento, endereco, telefone)

elif opcao == "Buscar Paciente":
    st.header("Buscar Paciente")
    buscar = st.text_input("Digite o CPF do paciente", max_chars=11)

    if buscar:
        paciente_encontrado = st.session_state.pacientes[st.session_state.pacientes['CPF'].str.contains(buscar, case=False)]
        if not paciente_encontrado.empty:
            st.write(paciente_encontrado)
        else:
            st.warning("Paciente não encontrado.")

elif opcao == "Editar Paciente":
    st.header("Editar Paciente")
    buscar_edit = st.text_input("Digite o CPF do paciente", max_chars=11)

    if buscar_edit:
        paciente_encontrado_edit = st.session_state.pacientes[st.session_state.pacientes['CPF'].str.contains(buscar_edit, case=False)]
        if not paciente_encontrado_edit.empty:
            if len(paciente_encontrado_edit) > 1:
                st.warning("Mais de um paciente encontrado. Por favor, seja mais específico.")
            else:
                paciente = paciente_encontrado_edit.iloc[0]
                
                nome = st.text_input("Nome", value=paciente['Nome'])
                cpf = st.text_input("CPF", value=paciente['CPF'])
                data_nascimento = st.date_input("Data de Nascimento", value=pd.to_datetime(paciente['Data de Nascimento']))
                endereco = st.text_input("Endereço", value=paciente['Endereço'])
                telefone = st.text_input("Telefone", value=paciente.get('Telefone', '')) 

                if st.button("Atualizar Paciente"):
                    add_paciente(nome, cpf, data_nascimento, endereco, telefone) 
        else:
            st.warning("Paciente não encontrado.")

elif opcao == "Iniciar Consulta":
    st.header("Iniciar Consulta Médica")
    st.subheader("Buscar Paciente")
    buscar1 = st.text_input("Digite o CPF do paciente", placeholder="Digite o CPF do paciente...", max_chars=11)

    if buscar1:
        paciente_encontrado1 = st.session_state.pacientes[st.session_state.pacientes['CPF'].str.contains(buscar1, case=False)]
        if not paciente_encontrado1.empty:
            st.write(paciente_encontrado1)
            if len(paciente_encontrado1) > 1:
                st.warning("Mais de um paciente encontrado. Por favor, seja mais específico.")
            else:
                selected_paciente = paciente_encontrado1.iloc[0]
                st.session_state.selected_paciente = selected_paciente

                data_nascimento_str = pd.to_datetime(selected_paciente['Data de Nascimento']).strftime("%d/%m/%Y")
                st.write(f"Data de Nascimento: {data_nascimento_str}")

        else:
            st.warning("Paciente não encontrado.")

    if 'selected_paciente' in st.session_state:
        medico = st.selectbox("Médico Responsável", ["Dr. Felipe", "Dr. Mateus", "Dr. João"]) 

        sintomas = st.multiselect("Quais os sintomas do paciente?", ["Febre", "Garganta Inflamada", "Náusea", "Resfriado", "Outro"], placeholder="Selecione uma opção")

        if st.button("Gerar Receita"):
            if 'selected_paciente' not in st.session_state:
                st.warning("Por favor, selecione um paciente antes de gerar a receita.")
            else:
                nome_paciente = st.session_state.selected_paciente['Nome']
                data_consulta = datetime.now().strftime("%d/%m/%Y")
                receitas = []

                if "Febre" in sintomas:
                    receitas.append("Remédio: Febrilina__________500mg - 1 cp - 6h/6h")
                if "Garganta Inflamada" in sintomas:
                    receitas.append("Remédio: Gargalix__________gargarejos com 10ml - 4h/4h")
                if "Náusea" in sintomas:
                    receitas.append("Remédio: Nausex__________250mg - 1 cp - 8h/8h")
                if "Resfriado" in sintomas:
                    receitas.append("Remédio: Resfriadin__________200mg - 1 cp - 12h/12h")

                st.write("--- RECEITA MÉDICA ---")
                st.write(f"Paciente: {nome_paciente}")
                st.write(f"Médico Responsável: {medico}")
                st.write(f"Data da Consulta: {data_consulta}")
                st.write("Coronel Xavier Chaves, Minas Gerais")

                for receita in receitas:
                    st.write(receita)

                if receitas:
                    pdf_file = gerar_pdf(nome_paciente, medico, data_consulta, receitas)
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="Clique aqui para baixar a receita",
                            data=f,
                            file_name=f"receita_{nome_paciente.replace(' ', '_')}_{data_consulta.replace('/', '-')}.pdf",
                            mime='application/pdf'
                        )
                else:
                    st.success("Nenhum sintoma selecionado. Receita não gerada.")

elif opcao == "Agendar Consulta":
    st.header("Agendar Consulta")
    cpf_input = st.text_input("Digite o CPF do Paciente", placeholder="Digite o CPF do paciente...", max_chars=11)
    medico = st.selectbox("Selecione o Médico", ["Dr. Felipe", "Dr. Mateus", "Dr. João"]) 
    data_hora = st.date_input("Data da Consulta", value=datetime.now())
    hora = st.time_input("Hora da Consulta", value=datetime.now().time())

    if cpf_input:
        paciente_encontrado = st.session_state.pacientes[st.session_state.pacientes['CPF'] == cpf_input]
        if not paciente_encontrado.empty:
            paciente_nome = paciente_encontrado.iloc[0]['Nome']
            st.write(f"Paciente encontrado: {paciente_nome}")
        else:
            st.warning("Paciente não encontrado.")

    if st.button("Agendar Consulta"):
        if not paciente_encontrado.empty:
            data_hora_completa = datetime.combine(data_hora, hora)
            agendar_consulta(paciente_nome, medico, data_hora_completa.strftime("%d/%m/%Y %H:%M"))
            st.success("Consulta agendada com sucesso!")
        else:
            st.error("Não foi possível agendar a consulta, pois o paciente não foi encontrado.")

elif opcao == "Ver Consultas Agendadas":
    st.header("Consultas Agendadas")

    # Selecionar data
    data_filtro = st.date_input("Filtrar por Data", value=date.today())

    # Filtrar pela data
    consultas_filtradas = st.session_state.consultas[st.session_state.consultas['Data/Hora'].str.startswith(data_filtro.strftime("%d/%m/%Y"))]

    if not consultas_filtradas.empty:
        st.write(consultas_filtradas)
    else:
        st.warning("Não há consultas agendadas para essa data.")

st.sidebar.image('adm.png', caption=None, channels="RGB")
st.sidebar.selectbox("Escolha uma opção", ["Cadastrar Médico"])

st.sidebar.image('relatorios.png', caption=None, channels="RGB")
st.sidebar.selectbox("Escolha uma opção", ["Relatórios de Consultas"])
