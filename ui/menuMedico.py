# menuMedico.py

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from pymongo import MongoClient
from ui.singleton import UsuarioLogadoSingleton
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from datetime import datetime

Builder.load_file('ui/menuMedico.kv')

class MenuMedico(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_logado_singleton = UsuarioLogadoSingleton()  # Instância do singleton
        self.atualizar_labels()
        self.atualizar_labels_exame()
        self.atualizar_labels_medicamento()

    def get_db(self):
        try:
            client = MongoClient('mongodb://root:12345@localhost:27017/')  # Substitua pela sua URI do MongoDB
            db = client['ultrasaude']  # Nome do banco de dados
            return db

        except Exception as e:
            self.show_popup(f'Erro ao se conectar ao banco: {e}')
            return None
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def usuario_logado_informacoes(self):

        db = self.get_db()
        usuario_logado = self.usuario_logado_singleton.get_usuario_logado()
        usuario = db.usuarios.find_one({"id_usuario": usuario_logado}, {"_id": 0})
        print(f'Usuario: {usuario}')
        cpf = usuario['cpf_funcionario']
        print(f'CPF: {cpf}')
        medico_logado = db.medicos.find_one({"cpf_funcionario": cpf}, {"_id": 0})
        nome = medico_logado['nome']
        crm = medico_logado['crm']
        print(f'Nome: {nome}')

        return medico_logado, nome, cpf, crm

    def atualizar_labels(self):
        _, medico_nome, cpf_medico, _ = self.usuario_logado_informacoes()
        self.ids.identificador_id.text = medico_nome
        self.ids.identificador_cpf.text = cpf_medico

# Função para vizualizar consultas marcadas
    def visualizar_consulta(self):

        def obter_lista_consultas():
            db = self.get_db()
            medico_logado, _, _, _ = self.usuario_logado_informacoes()
            print(f"Médico logado: {medico_logado}")

            # Verificando se obtemos as informações do médico logado
            if medico_logado is None:
                self.show_popup("Erro", "Não foi possível obter informações do médico logado.")
                return []

            medico = ''
            for key, value in medico_logado.items():
                if key == 'nome':
                    medico = value

            print(medico)
            # Filtrando as consultas para o médico logado
            consultas = db.agendamentos.find({"medico": medico}, {
                "nome": 1, "cpf": 1, "telefone_fixo": 1, "telefone_celular": 1, "data_consulta": 1,
                "horario_consulta": 1, "tem_convenio": 1, "nome_convenio": 1, "medico": 1
            })

            consultas_list = list(consultas)
            print(f"Consultas encontradas: {consultas_list}")

            return consultas_list

        grid = self.ids.consultas_grid
        grid.clear_widgets()
        consultas = obter_lista_consultas()

        for consulta in consultas:
            row = BoxLayout(size_hint_y=None, height=30)
            for key in ["nome", "cpf", "telefone_fixo", "telefone_celular", "data_consulta", "horario_consulta",
                        "tem_convenio", "nome_convenio", "medico"]:
                value = consulta.get(key, '')
                row.add_widget(Label(text=str(value), size_hint_y=None, height=30, color=(0, 0, 0, 1)))
            grid.add_widget(row)

# Funções Prontuarios
    def buscar_paciente(self):

        db = self.get_db()
        cpf_novo = self.ids.buscar_paciente_novo.text.strip()
        cpf_editar = self.ids.buscar_paciente_editar.text.strip()
        cpf_excluir = self.ids.buscar_paciente_excluir.text.strip()

        if cpf_novo:
            paciente = db.pacientes.find_one({"cpf": cpf_novo}, {"_id": 0})

            if paciente:
                campos = {
                    'nome': 'nome_paciente_cadastrar',
                    'cpf': 'cpf_paciente_cadastrar',
                    'data_nascimento': 'data_nascimento_paciente_cadastrar',
                    'sexo': 'sexo_paciente_cadastrar'}

                for campo_banco, campo_ui in campos.items():
                    if campo_banco in paciente:
                        self.ids[campo_ui].text = paciente[campo_banco]

            else:
                self.show_popup('Erro', f'Paciente com CPF "{cpf_novo}" não encontrado.')

        elif cpf_editar:
            paciente = db.prontuarios.find_one({"cpf_paciente": cpf_editar}, {"_id": 0})

            if paciente:
                campos = ['nome_paciente_editar', 'cpf_paciente_editar', 'data_nascimento_paciente_editar',
                          'sexo_paciente_editar', 'problema_saude_editar', 'medicamentos_editar', 'exames_editar',
                          'tratamento_anteriores_editar', 'observacoes_editar']

                valores = []

                for key, value in paciente.items():
                    valores.append(value)

                paciente_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in paciente_novo.items():
                    self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Paciente com CPF "{cpf_editar}" não encontrado.')

        else:
            paciente = db.prontuarios.find_one({"cpf_paciente": cpf_excluir}, {"_id": 0})

            if paciente:
                campos = ['nome_paciente_excluir', 'cpf_paciente_excluir', 'data_nascimento_paciente_excluir',
                          'sexo_paciente_excluir', 'problema_saude_excluir', 'medicamentos_excluir', 'exames_excluir',
                          'tratamento_anteriores_excluir', 'observacoes_excluir']

                valores = []

                for key, value in paciente.items():
                    valores.append(value)

                paciente_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in paciente_novo.items():
                    self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Paciente com CPF "{cpf_excluir}" não encontrado.')

    def cadastrar_prontuario(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.buscar_paciente_novo.text = ''
            self.ids.nome_paciente_cadastrar.text = ''
            self.ids.cpf_paciente_cadastrar.text = ''
            self.ids.data_nascimento_paciente_cadastrar.text = ''
            self.ids.sexo_paciente_cadastrar.text = ''
            self.ids.problema_saude_cadastrar.text = ''
            self.ids.medicamentos_cadastrar.text = ''
            self.ids.exames_cadastrar.text = ''
            self.ids.tratamento_anteriores_cadastrar.text = ''
            self.ids.observacoes_cadastrar.text = ''

        def inserir_paciente(dados):
            # Insere no MongoDB
            try:
                db = self.get_db()
                colecao_prontuarios = db['prontuarios']
                colecao_prontuarios.insert_one(dados)
                self.show_popup('Sucesso', 'Prontuario criado com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(prontuario):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in prontuario.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(prontuario):
            # Verifica duplicação de dados no MongoDB
            try:
                db = self.get_db()
                colecao_prontuarios = db['prontuarios']
                duplicado = colecao_prontuarios.find_one({
                    '$or': [
                        {'cpf_paciente': prontuario['cpf_paciente']},
                    ]
                })
                return duplicado is None
            except Exception as e:
                self.show_popup('Erro', f'Erro ao verificar duplicidade: {e}')
                return False

        prontuario = {
            'nome_paciente': self.ids.nome_paciente_cadastrar.text,
            'cpf_paciente': self.ids.cpf_paciente_cadastrar.text,
            'data_nascimento_paciente': self.ids.data_nascimento_paciente_cadastrar.text,
            'sexo_paciente': self.ids.sexo_paciente_cadastrar.text,
            'problema_saude': self.ids.problema_saude_cadastrar.text,
            'medicamentos': self.ids.medicamentos_cadastrar.text,
            'exames': self.ids.exames_cadastrar.text,
            'tratamentos_anteriores': self.ids.tratamento_anteriores_cadastrar.text,
            'observacoes': self.ids.observacoes_cadastrar.text,
        }

        if not campos_preenchidos(prontuario):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(prontuario):
            self.show_popup('Erro', 'Paciente já possui prontuario.')
            return

        inserir_paciente(prontuario)
        limpar_campos()

    def editar_prontuario(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.buscar_paciente_editar.text = ''
            self.ids.nome_paciente_editar.text = ''
            self.ids.cpf_paciente_editar.text = ''
            self.ids.data_nascimento_paciente_editar.text = ''
            self.ids.sexo_paciente_editar.text = ''
            self.ids.problema_saude_editar.text = ''
            self.ids.medicamentos_editar.text = ''
            self.ids.exames_editar.text = ''
            self.ids.tratamento_anteriores_editar.text = ''
            self.ids.observacoes_editar.text = ''

        def campos_preenchidos(prontuario):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in prontuario.items():
                if not value.strip():
                    return False
            return True

        db = self.get_db()
        cpf = self.ids.buscar_paciente_editar.text.strip()

        novo_prontuario = {}
        campos = ['nome_paciente_editar', 'cpf_paciente_editar', 'data_nascimento_paciente_editar',
                  'sexo_paciente_editar', 'problema_saude_editar', 'medicamentos_editar',
                  'exames_editar', 'tratamento_anteriores_editar', 'observacoes_editar']

        for campo in campos:
            novo_prontuario[campo] = self.ids[campo].text.strip()

        campos_banco = ['nome_paciente', 'cpf_paciente', 'data_nascimento_paciente', 'sexo_paciente',
                        'problema_saude', 'medicamentos', 'exames', 'tratamentos_anteriores', 'observacoes']

        valores = []

        for key, value in novo_prontuario.items():
            valores.append(value)

        prontuario_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_prontuario = db.prontuarios.find_one({
            "cpf_paciente": cpf
        })
        id = id_prontuario['_id']

        if not campos_preenchidos(prontuario_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        db.prontuarios.update_one({"_id": id}, {"$set": prontuario_final})
        self.show_popup('Sucesso', 'Prontuario atualizado com sucesso.')
        limpar_campos()

    def excluir_prontuario(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.buscar_paciente_excluir.text = ''
            self.ids.nome_paciente_excluir.text = ''
            self.ids.cpf_paciente_excluir.text = ''
            self.ids.data_nascimento_paciente_excluir.text = ''
            self.ids.sexo_paciente_excluir.text = ''
            self.ids.problema_saude_excluir.text = ''
            self.ids.medicamentos_excluir.text = ''
            self.ids.exames_excluir.text = ''
            self.ids.tratamento_anteriores_excluir.text = ''
            self.ids.observacoes_excluir.text = ''

        db = self.get_db()
        cpf = self.ids.buscar_paciente_excluir.text.strip()

        db.prontuarios.delete_one({"cpf_paciente": cpf})
        self.show_popup('Sucesso', 'Prontuario excluido com sucesso.')
        limpar_campos()

# Funções Exames
    def atualizar_labels_exame(self):
        _, medico_nome, _, crm_exame = self.usuario_logado_informacoes()
        self.ids.medico_exame.text = medico_nome
        self.ids.crm_exame.text = crm_exame

    def imprimir_exame(self):
        # Pegue os valores dos TextInputs
        medico = self.ids.medico_exame.text
        crm = self.ids.crm_exame.text
        nome_paciente = self.ids.nome_paciente_exame.text
        cpf_paciente = self.ids.cpf_paciente_exame.text
        exames = self.ids.exames_exame.text
        data = self.ids.data_exame.text

        # Nome do arquivo PDF
        pdf_filename = "exame_formulario.pdf"

        # Cria o PDF
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['BodyText']
        heading_style = styles['Heading2']

        # Cabeçalho
        header_table = Table([
            ['Ultrasaúde', 'Documento de Exame'],
            ['Endereço: Rua Exemplo, 123', f'Data: {datetime.now().strftime("%d/%m/%Y")}'],
            ['Telefone: (99) 99999-9999', '']
        ])
        header_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),  # Une as colunas 0 e 1 na linha 0
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Dados do Exame
        elements.append(Paragraph("Dados do Exame", heading_style))
        data_table = Table([
            ['Médico:', medico],
            ['CRM:', crm],
            ['Nome do Paciente:', nome_paciente],
            ['CPF do Paciente:', cpf_paciente],
            ['Exames:', exames],
            ['Data:', data],
        ])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 11),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(data_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Rodapé
        footer_table = Table([
            ['Ultrasaúde - Qualidade e Segurança'],
        ])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.grey),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Oblique'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 12),
        ]))
        elements.append(footer_table)

        # Constrói o PDF
        pdf.build(elements)

        self.show_popup("Sucesso", f"PDF {pdf_filename} gerado com sucesso!")

# Funções Exames
    def atualizar_labels_medicamento(self):
        _, medico_nome, _, crm_exame = self.usuario_logado_informacoes()
        self.ids.medico_medicamento.text = medico_nome
        self.ids.crm_medicamento.text = crm_exame

    def imprimir_medicamento(self):
        # Pegue os valores dos TextInputs
        medico = self.ids.medico_medicamento.text
        crm = self.ids.crm_medicamento.text
        nome_paciente = self.ids.nome_paciente_medicamento.text
        cpf_paciente = self.ids.cpf_paciente_medicamento.text
        nome_medicamento = self.ids.nome_medicamento.text
        dosagem = self.ids.dosagem.text
        frequencia = self.ids.frequencia.text
        duracao = self.ids.duracao.text

        # Nome do arquivo PDF
        pdf_filename = "prescricao_medicamento.pdf"

        # Cria o PDF
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['BodyText']
        heading_style = styles['Heading2']

        # Cabeçalho
        header_table = Table([
            ['Ultrasaúde', 'Prescrição de Medicamento'],
            ['Endereço: Rua Exemplo, 123', f'Data: {datetime.now().strftime("%d/%m/%Y")}'],
            ['Telefone: (99) 99999-9999', '']
        ])
        header_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),  # Une as colunas 0 e 1 na linha 0
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Dados da Prescrição
        elements.append(Paragraph("Dados da Prescrição", heading_style))
        data_table = Table([
            ['Médico:', medico],
            ['CRM:', crm],
            ['Nome do Paciente:', nome_paciente],
            ['CPF do Paciente:', cpf_paciente],
            ['Nome do Medicamento:', nome_medicamento],
            ['Dosagem:', dosagem],
            ['Frequência:', frequencia],
            ['Duração:', duracao],
        ])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 11),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(data_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Rodapé
        footer_table = Table([
            ['Ultrasaúde - Qualidade e Segurança'],
        ])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.grey),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Oblique'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 12),
        ]))
        elements.append(footer_table)

        # Constrói o PDF
        pdf.build(elements)

        self.show_popup("Sucesso", f"PDF {pdf_filename} gerado com sucesso!")

# Função sair
    def sair(self):

        self.parent.parent.current = 'screen_login'
class MenuMedicoApp(App):
    def build(self):
        return MenuMedico()

if __name__ == '__main__':

    MenuMedicoApp().run()