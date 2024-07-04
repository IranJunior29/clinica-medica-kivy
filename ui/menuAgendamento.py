# menuAgendamento.py

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from pymongo import MongoClient
from bson.objectid import ObjectId
from ui.singleton import UsuarioLogadoSingleton

Builder.load_file('ui/menuAgendamento.kv')

class MenuAgendamento(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_logado_singleton = UsuarioLogadoSingleton()  # Instância do singleton
        self.atualizar_labels()
        self.carregar_convenios()
        self.carregar_convenios_editar()
        self.carregar_convenios_agendar()
        self.carregar_medicos_agendar()
        self.carregar_convenios_agendar_editar()
        self.carregar_medicos_agendar_editar()

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

# Função Identificação
    def usuario_logado_informacoes(self):

        db = self.get_db()
        usuario_logado = self.usuario_logado_singleton.get_usuario_logado()
        usuario = db.usuarios.find_one({"id_usuario": usuario_logado}, {"_id": 0})
        cpf = usuario['cpf_funcionario']
        funcionario_logado = db.funcionarios.find_one({"cpf": cpf}, {"_id": 0})
        nome = funcionario_logado['nome']

        return funcionario_logado, nome, cpf
    def atualizar_labels(self):
        _, funcionario_nome, cpf_funcionario = self.usuario_logado_informacoes()
        self.ids.identificador_id.text = funcionario_nome
        self.ids.identificador_cpf.text = cpf_funcionario

# Funções Agendamento

    def buscar_paciente_agendamento(self):

        db = self.get_db()
        cpf_editar = self.ids.buscar_pacientes_agendamento.text.strip()

        paciente = db.pacientes.find_one({"cpf": cpf_editar}, {"_id": 0})

        if paciente:
            campos = {'nome': 'nome_agendar',
                      'cpf': 'cpf_agendar',
                      'telefone_fixo': 'telefone_fixo_agendar',
                      'telefone_celular': 'telefone_celular_agendar'}

            for campo_banco, campo_ui in campos.items():
                if campo_banco in paciente:
                    self.ids[campo_ui].text = paciente[campo_banco]

        else:
            self.show_popup('Erro', f'Paciente com CPF "{cpf_editar}" não encontrado.')
    def carregar_convenios_agendar(self):

        db = self.get_db()
        colecao_convenios = db['convenios']
        self.convenios_agendar = [convenio['nome_empresa'] for convenio in
                                    colecao_convenios.find({}, {'nome_empresa': 1})]

        # Atualizar o Spinner
        spinner = self.ids.get('nome_convenio_agendar')
        if spinner:
            spinner.values = self.convenios_agendar
    def carregar_medicos_agendar(self):

        db = self.get_db()
        colecao_medicos = db['medicos']
        self.medicos_disponiveis = [medico['nome'] for medico in
                                    colecao_medicos.find({}, {'nome': 1})]

        # Atualizar o Spinner
        spinner = self.ids.get('medico_agendar')
        if spinner:
            spinner.values = self.medicos_disponiveis

    def agendar_consulta(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_agendar.text = ''
            self.ids.cpf_agendar.text = ''
            self.ids.telefone_fixo_agendar.text = ''
            self.ids.telefone_celular_agendar.text = ''
            self.ids.data_consulta_agendar.text = ''
            self.ids.horario_consulta_agendar.text = ''
            self.ids.tem_convenio_agendar.text = 'Opções'
            self.ids.nome_convenio_agendar.text = 'Não Possui'
            self.ids.medico_agendar.text = 'Médicos'

        def inserir_agendamento(dados):
            # Insere no MongoDB
            try:
                db = self.get_db()
                colecao_agendamentos = db['agendamentos']
                colecao_agendamentos.insert_one(dados)
                self.show_popup('Sucesso', 'Consulta marcada com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(agendamento):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in agendamento.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(agendamento):
            # Verifica duplicação de dados no MongoDB
            try:
                db = self.get_db()
                colecao_agendamentos = db['agendamentos']
                duplicado = colecao_agendamentos.find_one({
                    'data_consulta': agendamento['data_consulta'],
                    'horario_consulta': agendamento['horario_consulta'],
                    'medico': agendamento['medico']
                })

                return duplicado is None

            except Exception as e:
                self.show_popup('Erro', f'Erro ao verificar duplicidade: {e}')
                return False

        agendamento = {
            'nome': self.ids.nome_agendar.text,
            'cpf': self.ids.cpf_agendar.text,
            'telefone_fixo': self.ids.telefone_fixo_agendar.text,
            'telefone_celular': self.ids.telefone_celular_agendar.text,
            'data_consulta': self.ids.data_consulta_agendar.text,
            'horario_consulta': self.ids.horario_consulta_agendar.text,
            'tem_convenio': self.ids.tem_convenio_agendar.text,
            'nome_convenio': self.ids.nome_convenio_agendar.text,
            'medico': self.ids.medico_agendar.text,
        }

        if not campos_preenchidos(agendamento):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(agendamento):
            self.show_popup('Erro', 'Data e Horario não disponivel.')
            return

        inserir_agendamento(agendamento)
        limpar_campos()
        self.ids.buscar_pacientes_agendamento.text = ''

    def visualizar_consulta(self):

        def obter_lista_consultas():

            db = self.get_db()

            # Obtendo os consultas
            consultas = db.agendamentos.find({}, {
                "nome": 1, "cpf": 1, "telefone_fixo": 1, "telefone_celular": 1, "data_consulta": 1,
                "horario_consulta": 1, "tem_convenio": 1, "nome_convenio": 1, "medico": 1
            })

            # Retorna lista de nomes de convenios
            return list(consultas)

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

    def buscar_consulta(self):

        db = self.get_db()
        cpf_editar = self.ids.buscar_consultas_cpf_editar.text.strip()
        data_editar = self.ids.buscar_consultas_data_editar.text.strip()
        horario_editar = self.ids.buscar_consultas_horario_editar.text.strip()
        medico_editar = self.ids.buscar_consultas_medico_editar.text.strip()
        cpf_excluir = self.ids.buscar_consultas_cpf_excluir.text.strip()
        data_excluir = self.ids.buscar_consultas_data_excluir.text.strip()
        horario_excluir = self.ids.buscar_consultas_horario_excluir.text.strip()
        medico_excluir = self.ids.buscar_consultas_medico_excluir.text.strip()

        if cpf_editar and data_editar and horario_editar and medico_editar:
            consulta = db.agendamentos.find_one({
                "cpf": cpf_editar,
                "data_consulta": data_editar,
                "horario_consulta": horario_editar,
                "medico": medico_editar
            }, {"_id": 0})

            if consulta:
                campos = ['nome_agendar_editar', 'cpf_agendar_editar', 'telefone_fixo_agendar_editar',
                          'telefone_celular_agendar_editar', 'data_consulta_agendar_editar',
                          'horario_consulta_agendar_editar', 'tem_convenio_agendar_editar',
                          'nome_convenio_agendar_editar', 'medico_agendar_editar']

                valores = []

                for key, value in consulta.items():
                    valores.append(value)

                consulta_nova = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in consulta_nova.items():
                        self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Consulta do paciente com CPF "{cpf_editar}" não encontrada.')

        elif cpf_excluir and data_excluir and horario_excluir and medico_excluir:

            consulta = db.agendamentos.find_one({
                "cpf": cpf_excluir,
                "data_consulta": data_excluir,
                "horario_consulta": horario_excluir,
                "medico": medico_excluir
            }, {"_id": 0})

            if consulta:
                campos = ['nome_agendar_excluir', 'cpf_agendar_excluir', 'telefone_fixo_agendar_excluir',
                          'telefone_celular_agendar_excluir', 'data_consulta_agendar_excluir',
                          'horario_consulta_agendar_excluir', 'tem_convenio_agendar_excluir',
                          'nome_convenio_agendar_excluir', 'medico_agendar_excluir']

                valores = []

                for key, value in consulta.items():
                    valores.append(value)

                consulta_nova = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in consulta_nova.items():
                    self.ids[key].text = value
            else:
                self.show_popup('Erro', f'Consulta do paciente com CPF "{cpf_excluir}" não encontrada.')
        else:
            self.show_popup('Erro', f'Preencha todos os campos de busca.')
    def carregar_convenios_agendar_editar(self):

        db = self.get_db()
        colecao_convenios = db['convenios']
        self.convenios_agendar_editar = [convenio['nome_empresa'] for convenio in
                                    colecao_convenios.find({}, {'nome_empresa': 1})]

        # Atualizar o Spinner
        spinner = self.ids.get('nome_convenio_agendar_editar')
        if spinner:
            spinner.values = self.convenios_agendar_editar
    def carregar_medicos_agendar_editar(self):

        db = self.get_db()
        colecao_medicos = db['medicos']
        self.medicos_disponiveis_editar = [medico['nome'] for medico in
                                    colecao_medicos.find({}, {'nome': 1})]

        # Atualizar o Spinner
        spinner = self.ids.get('medico_agendar_editar')
        if spinner:
            spinner.values = self.medicos_disponiveis_editar

    def editar_consulta(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_agendar_editar.text = ''
            self.ids.cpf_agendar_editar.text = ''
            self.ids.telefone_fixo_agendar_editar.text = ''
            self.ids.telefone_celular_agendar_editar.text = ''
            self.ids.data_consulta_agendar_editar.text = ''
            self.ids.horario_consulta_agendar_editar.text = ''
            self.ids.tem_convenio_agendar_editar.text = 'Opções'
            self.ids.nome_convenio_agendar_editar.text = 'Não Possui'
            self.ids.medico_agendar_editar.text = 'Médicos'

        def campos_preenchidos(consulta):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in consulta.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(consulta, excecao_id=None):

            db = self.get_db()
            colecao_agendamentos = db['agendamentos']

            query = {
                'data_consulta': consulta['data_consulta'],
                'horario_consulta': consulta['horario_consulta'],
                'medico': consulta['medico']
            }

            # Adiciona condição para ignorar o documento com excecao_id
            if excecao_id:
                query['_id'] = {'$ne': ObjectId(excecao_id)}

            # Realiza a consulta no banco de dados
            duplicado = colecao_agendamentos.find_one(query)

            return duplicado is None


        db = self.get_db()
        data = self.ids.buscar_consultas_data_editar.text.strip()
        horario = self.ids.buscar_consultas_horario_editar.text.strip()
        medico = self.ids.buscar_consultas_medico_editar.text.strip()

        nova_consulta = {}
        campos = ['nome_agendar_editar', 'cpf_agendar_editar', 'telefone_fixo_agendar_editar',
                  'telefone_celular_agendar_editar', 'data_consulta_agendar_editar', 'horario_consulta_agendar_editar',
                  'tem_convenio_agendar_editar', 'nome_convenio_agendar_editar', 'medico_agendar_editar']

        for campo in campos:
            nova_consulta[campo] = self.ids[campo].text.strip()

        campos_banco = ['nome', 'cpf', 'telefone_fixo', 'telefone_celular', 'data_consulta', 'horario_consulta',
                        'tem_convenio', 'nome_convenio', 'medico']

        valores = []

        for key, value in nova_consulta.items():
            valores.append(value)

        consulta_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_consulta = db.agendamentos.find_one({
            "data_consulta": data,
            "horario_consulta": horario,
            "medico": medico
        })
        id = id_consulta['_id']

        if not campos_preenchidos(consulta_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(consulta_final, excecao_id=id):
            self.show_popup('Erro', 'Data e Horario indisponivel.')
            return

        db.agendamentos.update_one({"_id": id}, {"$set": consulta_final})
        self.show_popup('Sucesso', 'Consulta atualizada com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_consultas_cpf_editar.text = ''
        self.ids.buscar_consultas_data_editar.text = ''
        self.ids.buscar_consultas_horario_editar.text = ''
        self.ids.buscar_consultas_medico_editar.text = ''

    def excluir_consulta(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_agendar_excluir.text = ''
            self.ids.cpf_agendar_excluir.text = ''
            self.ids.telefone_fixo_agendar_excluir.text = ''
            self.ids.telefone_celular_agendar_excluir.text = ''
            self.ids.data_consulta_agendar_excluir.text = ''
            self.ids.horario_consulta_agendar_excluir.text = ''
            self.ids.tem_convenio_agendar_excluir.text = 'Opções'
            self.ids.nome_convenio_agendar_excluir.text = 'Não Possui'
            self.ids.medico_agendar_excluir.text = 'Médicos'

        db = self.get_db()
        data = self.ids.buscar_consultas_data_excluir.text.strip()
        horario = self.ids.buscar_consultas_horario_excluir.text.strip()
        medico = self.ids.buscar_consultas_medico_excluir.text.strip()

        id_consulta = db.agendamentos.find_one({
            "data_consulta": data,
            "horario_consulta": horario,
            "medico": medico
        })
        id = id_consulta['_id']

        db.agendamentos.delete_one({"_id": id})
        self.show_popup('Sucesso', 'Consulta excluida com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_consultas_cpf_excluir.text = ''
        self.ids.buscar_consultas_data_excluir.text = ''
        self.ids.buscar_consultas_horario_excluir.text = ''
        self.ids.buscar_consultas_medico_excluir.text = ''

# Funções Paciente
    def carregar_convenios(self):

        db = self.get_db()
        convenios_collection = db['convenios']
        self.convenios_cadastrar = [convenio['nome_empresa'] for convenio in
                                    convenios_collection.find({}, {'nome_empresa': 1})]

        # Atualizar o Spinner
        spinner = self.ids.get('nome_convenio_cadastro')
        if spinner:
            spinner.values = self.convenios_cadastrar

    def cadastrar_paciente(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_cadastro.text = ''
            self.ids.rg_cadastro.text = ''
            self.ids.cpf_cadastro.text = ''
            self.ids.rua_cadastro.text = ''
            self.ids.numero_cadastro.text = ''
            self.ids.complemento_cadastro.text = ''
            self.ids.bairro_cadastro.text = ''
            self.ids.cidade_cadastro.text = ''
            self.ids.estado_cadastro.text = ''
            self.ids.cep_cadastro.text = ''
            self.ids.telefone_fixo_cadastro.text = ''
            self.ids.telefone_celular_cadastro.text = ''
            self.ids.data_nascimento_cadastro.text = ''
            self.ids.sexo_cadastro.text = 'Sexo'
            self.ids.tem_convenio_cadastro.text = 'Opções'
            self.ids.nome_convenio_cadastro.text = 'Não Possui'

        def inserir_paciente(dados):
            # Insere no MongoDB
            try:
                db = self.get_db()
                colecao_pacientes = db['pacientes']
                colecao_pacientes.insert_one(dados)
                self.show_popup('Sucesso', 'Paciente cadastrado com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(paciente):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in paciente.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(paciente):
            # Verifica duplicação de dados no MongoDB
            try:
                db = self.get_db()
                colecao_pacientes = db['pacientes']
                duplicado = colecao_pacientes.find_one({
                    '$or': [
                        {'cpf': paciente['cpf']},
                        {'rg': paciente['rg']}
                    ]
                })
                return duplicado is None
            except Exception as e:
                self.show_popup('Erro', f'Erro ao verificar duplicidade: {e}')
                return False

        paciente = {
            'nome': self.ids.nome_cadastro.text,
            'rg': self.ids.rg_cadastro.text,
            'cpf': self.ids.cpf_cadastro.text,
            'rua': self.ids.rua_cadastro.text,
            'numero': self.ids.numero_cadastro.text,
            'complemento': self.ids.complemento_cadastro.text,
            'bairro': self.ids.bairro_cadastro.text,
            'cidade': self.ids.cidade_cadastro.text,
            'estado': self.ids.estado_cadastro.text,
            'cep': self.ids.cep_cadastro.text,
            'telefone_fixo': self.ids.telefone_fixo_cadastro.text,
            'telefone_celular': self.ids.telefone_celular_cadastro.text,
            'data_nascimento': self.ids.data_nascimento_cadastro.text,
            'sexo': self.ids.sexo_cadastro.text,
            'tem_convenio': self.ids.tem_convenio_cadastro.text,
            'nome_convenio': self.ids.nome_convenio_cadastro.text,
        }

        if not campos_preenchidos(paciente):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(paciente):
            self.show_popup('Erro', 'Paciente já possui cadastro.')
            return

        inserir_paciente(paciente)
        limpar_campos()

    def visualizar_paciente(self):

        def obter_lista_pacientes():

            db = self.get_db()

            # Obtendo os Pacientes
            pacientes = db.pacientes.find({}, {
                "nome": 1, "rg": 1, "cpf": 1, "rua": 1, "numero": 1, "complemento": 1,
                "bairro": 1, "cidade": 1, "estado": 1, "cep": 1, "telefone_fixo": 1,
                "telefone_celular": 1, "data_nascimento": 1, "sexo": 1, "tem_convenio": 1, "nome_convenio": 1, "_id": 0
            })

            # Retornando lista de nomes de pacientes
            return list(pacientes)

        grid = self.ids.pacientes_grid
        grid.clear_widgets()
        pacientes = obter_lista_pacientes()

        for paciente in pacientes:
            row = BoxLayout(size_hint_y=None, height=30)
            for key in ["nome", "rg", "cpf", "rua", "numero", "complemento", "bairro", "cidade", "estado", "cep",
                        "telefone_fixo", "telefone_celular", "data_nascimento", "sexo", "tem_convenio",
                        "nome_convenio"]:
                value = paciente.get(key, '')
                row.add_widget(Label(text=str(value), size_hint_y=None, height=30, color=(0, 0, 0, 1)))
            grid.add_widget(row)

    def buscar_paciente(self):

        db = self.get_db()
        cpf_editar = self.ids.buscar_pacientes_editar.text.strip()
        cpf_excluir = self.ids.buscar_pacientes_excluir.text.strip()

        if cpf_editar:
            paciente = db.pacientes.find_one({"cpf": cpf_editar}, {"_id": 0})

            if paciente:
                campos = ['nome_editar', 'rg_editar', 'cpf_editar', 'rua_editar', 'numero_editar', 'complemento_editar',
                          'bairro_editar', 'cidade_editar', 'estado_editar', 'cep_editar', 'telefone_fixo_editar',
                          'telefone_celular_editar', 'data_nascimento_editar', 'sexo_editar', 'tem_convenio_editar',
                          'nome_convenio_editar']

                valores = []

                for key, value in paciente.items():
                    valores.append(value)

                paciente_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in paciente_novo.items():
                        self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Paciente com CPF "{cpf_editar}" não encontrado.')

        else:
            paciente = db.pacientes.find_one({"cpf": cpf_excluir}, {"_id": 0})

            if paciente:
                campos = ['nome_excluir', 'rg_excluir', 'cpf_excluir', 'rua_excluir', 'numero_excluir', 'complemento_excluir',
                          'bairro_excluir', 'cidade_excluir', 'estado_excluir', 'cep_excluir', 'telefone_fixo_excluir',
                          'telefone_celular_excluir', 'data_nascimento_excluir', 'sexo_excluir', 'tem_convenio_excluir',
                          'nome_convenio_excluir']

                valores = []

                for key, value in paciente.items():
                    valores.append(value)

                paciente_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in paciente_novo.items():
                    self.ids[key].text = value
            else:
                self.show_popup('Erro', f'Paciente com CPF "{cpf_excluir}" não encontrado.')
    def carregar_convenios_editar(self):

        db = self.get_db()
        colecao_convenios = db['convenios']
        self.convenios_editar = [convenio['nome_empresa'] for convenio in
                                    colecao_convenios.find({}, {'nome_empresa': 1})]
        print("Convênios carregados:", self.convenios_cadastrar)  # Debug: Verificar se os convênios são carregados

        # Atualizar o Spinner
        spinner = self.ids.get('nome_convenio_editar')
        if spinner:
            spinner.values = self.convenios_editar

    def editar_paciente(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_editar.text = ''
            self.ids.rg_editar.text = ''
            self.ids.cpf_editar.text = ''
            self.ids.rua_editar.text = ''
            self.ids.numero_editar.text = ''
            self.ids.complemento_editar.text = ''
            self.ids.bairro_editar.text = ''
            self.ids.cidade_editar.text = ''
            self.ids.estado_editar.text = ''
            self.ids.cep_editar.text = ''
            self.ids.telefone_fixo_editar.text = ''
            self.ids.telefone_celular_editar.text = ''
            self.ids.data_nascimento_editar.text = ''
            self.ids.sexo_editar.text = 'Sexo'
            self.ids.tem_convenio_editar.text = 'Opções'
            self.ids.nome_convenio_editar.text = 'Não Possui'

        def campos_preenchidos(paciente):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in paciente.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(paciente, excecao_id=None):

            db = self.get_db()
            colecao_pacientes = db['pacientes']

            query = {
                '$or': [
                    {'cpf': paciente['cpf']},
                    {'rg': paciente['rg']},
                ]
            }

            # Adiciona condição para ignorar o documento com excecao_id
            if excecao_id:
                query['_id'] = {'$ne': ObjectId(excecao_id)}

            # Realiza a consulta no banco de dados
            duplicado = colecao_pacientes.find_one(query)

            return duplicado is None

        db = self.get_db()
        cpf = self.ids.buscar_pacientes_editar.text.strip()

        novo_paciente = {}
        campos = ['nome_editar', 'rg_editar', 'cpf_editar', 'rua_editar', 'numero_editar', 'complemento_editar',
                  'bairro_editar', 'cidade_editar', 'estado_editar', 'cep_editar', 'telefone_fixo_editar',
                  'telefone_celular_editar', 'data_nascimento_editar', 'sexo_editar', 'tem_convenio_editar',
                  'nome_convenio_editar']

        for campo in campos:
            novo_paciente[campo] = self.ids[campo].text.strip()

        campos_banco = ['nome', 'rg', 'cpf', 'rua', 'numero', 'complemento',
                        'bairro', 'cidade', 'estado', 'cep', 'telefone_fixo',
                        'telefone_celular', 'data_nascimento', 'sexo', 'tem_convenio', 'nome_convenio']

        valores = []

        for key, value in novo_paciente.items():
            valores.append(value)

        paciente_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_paciente = db.pacientes.find_one({"cpf": cpf})
        id = id_paciente['_id']

        if not campos_preenchidos(paciente_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(paciente_final, excecao_id=id):
            self.show_popup('Erro', 'CPF ou RG já estão em uso por outro paciente.')
            return

        db.pacientes.update_one({"cpf": cpf}, {"$set": paciente_final})
        self.show_popup('Sucesso', 'Paciente atualizado com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_pacientes_editar.text = ''

    def excluir_paciente(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_excluir.text = ''
            self.ids.rg_excluir.text = ''
            self.ids.cpf_excluir.text = ''
            self.ids.rua_excluir.text = ''
            self.ids.numero_excluir.text = ''
            self.ids.complemento_excluir.text = ''
            self.ids.bairro_excluirtext = ''
            self.ids.cidade_excluir.text = ''
            self.ids.estado_excluir.text = ''
            self.ids.cep_excluir.text = ''
            self.ids.telefone_fixo_excluir.text = ''
            self.ids.telefone_celular_excluir.text = ''
            self.ids.data_nascimento_excluir.text = ''
            self.ids.sexo_excluir.text = 'Sexo'
            self.ids.tem_convenio_excluir.text = 'Opções'
            self.ids.nome_convenio_excluir.text = 'Não Possui'

        db = self.get_db()
        cpf = self.ids.buscar_pacientes_excluir.text.strip()

        db.pacientes.delete_one({"cpf": cpf})
        self.show_popup('Sucesso', 'Paciente excluido com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_pacientes_excluir.text = ''

# Função sair
    def sair(self):
        self.parent.parent.current = 'screen_login'
class MenuAgendamentoApp(App):
    def build(self):
        return MenuAgendamento()

if __name__ == '__main__':

    MenuAgendamentoApp().run()
