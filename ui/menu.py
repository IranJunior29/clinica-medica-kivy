# menu.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from pymongo import MongoClient
from bson.objectid import ObjectId
from kivy.lang import Builder
from ui.singleton import UsuarioLogadoSingleton

Builder.load_file('ui/menu.kv')

class Menu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Instância do singleton
        self.usuario_logado_singleton = UsuarioLogadoSingleton()
        # Atualiza o label com a identificação do usuario logado
        self.atualizar_labels()

# Inicia o banco
    def get_db(self):
        try:
            client = MongoClient('mongodb://root:12345@localhost:27017/')  # Substitua pela sua URI do MongoDB
            db = client['ultrasaude']  # Nome do banco de dados
            return db

        except Exception as e:
            self.show_popup(f'Erro ao se conectar ao banco: {e}')
            return None

# Popups para avisos
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

# Função para Identificação
    def usuario_logado_informacoes(self):

        # Inicia o banco
        db = self.get_db()
        # Recebe o ID do usuario logado
        usuario_logado = self.usuario_logado_singleton.get_usuario_logado()
        # Procura na coleção usuarios um usuario como id igual ao do usuario logado
        usuario = db.usuarios.find_one({"id_usuario": usuario_logado}, {"_id": 0})
        # Extrai o CPF do usuario encontrado na coleção
        cpf = usuario['cpf_funcionario']
        # Procura na coleção funcionarios um funcionario com cpf igual ao extraido do usuario
        funcionario_logado = db.funcionarios.find_one({"cpf": cpf}, {"_id": 0})
        # Extrai o nome do funcionario encontrado na coleção
        nome = funcionario_logado['nome']

        return nome, cpf
    def atualizar_labels(self):

        # armazena o nome e cpf encontrado na função usuario_logado_informacoes()
        funcionario_nome, cpf_funcionario = self.usuario_logado_informacoes()
        # Atualiza os campos de texto nos labels
        self.ids.identificador_id.text = funcionario_nome
        self.ids.identificador_cpf.text = cpf_funcionario

# Funções Funcionario
    def visualizar_funcionario(self):

        # Obtem uma lista com todos funcionarios na coleção
        def obter_lista_funcionarios():

            # Inicia o banco
            db = self.get_db()

            # Obtendo os funcionários
            funcionarios = db.funcionarios.find({}, {
                "nome": 1, "rg": 1, "cpf": 1, "rua": 1, "numero": 1, "complemento": 1,
                "bairro": 1, "cidade": 1, "estado": 1, "cep": 1, "telefone_fixo": 1,
                "telefone_celular": 1, "numero_ctps": 1, "numero_pis": 1, "_id": 0
            })

            # Retornando lista de nomes de funcionários
            return list(funcionarios)

        grid = self.ids.funcionarios_grid
        grid.clear_widgets()
        funcionarios = obter_lista_funcionarios()

        for funcionario in funcionarios:
            row = BoxLayout(size_hint_y=None, height=30)
            for key in ["nome", "rg", "cpf", "rua", "numero", "complemento", "bairro", "cidade", "estado", "cep",
                        "telefone_fixo", "telefone_celular", "numero_ctps", "numero_pis"]:
                value = funcionario.get(key, '')
                row.add_widget(Label(text=str(value), size_hint_y=None, height=30, color=(0, 0, 0, 1)))
            grid.add_widget(row)

    def cadastrar_funcionario(self):

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
            self.ids.numero_ctps_cadastro.text = ''
            self.ids.numero_pis_cadastro.text = ''

        def inserir_funcionario(dados):
            # Insere no MongoDB
            try:
                db = self.get_db()
                colecao_funcionarios = db['funcionarios']
                colecao_funcionarios.insert_one(dados)
                self.show_popup('Sucesso', 'Funcionário cadastrado com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(funcionario):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in funcionario.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(funcionario):
            # Verifica duplicação de dados no MongoDB
            try:
                db = self.get_db()
                colecao_funcionarios = db['funcionarios']
                duplicado = colecao_funcionarios.find_one({
                    '$or': [
                        {'cpf': funcionario['cpf']},
                        {'rg': funcionario['rg']},
                        {'numero_ctps': funcionario['numero_ctps']},
                        {'numero_pis': funcionario['numero_pis']}
                    ]
                })
                return duplicado is None
            except Exception as e:
                self.show_popup('Erro', f'Erro ao verificar duplicidade: {e}')
                return False

        funcionario = {
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
            'numero_ctps': self.ids.numero_ctps_cadastro.text,
            'numero_pis': self.ids.numero_pis_cadastro.text,
        }

        if not campos_preenchidos(funcionario):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(funcionario):
            self.show_popup('Erro', 'Funcionario já cadastrado.')
            return

        inserir_funcionario(funcionario)
        limpar_campos()

    def buscar_funcionario(self):

        db = self.get_db()
        cpf_editar = self.ids.buscar_funcionarios_editar.text.strip()
        cpf_excluir = self.ids.buscar_funcionarios_excluir.text.strip()

        if cpf_editar:
            funcionario = db.funcionarios.find_one({"cpf": cpf_editar}, {"_id": 0})

            if funcionario:
                campos = ['nome_editar', 'rg_editar', 'cpf_editar', 'rua_editar', 'numero_editar', 'complemento_editar',
                          'bairro_editar', 'cidade_editar', 'estado_editar', 'cep_editar', 'telefone_fixo_editar',
                          'telefone_celular_editar', 'numero_ctps_editar', 'numero_pis_editar']

                valores = []

                for key, value in funcionario.items():
                    valores.append(value)

                funcionario_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in funcionario_novo.items():
                        self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Funcionário com CPF "{cpf_editar}" não encontrado.')

        else:
            funcionario = db.funcionarios.find_one({"cpf": cpf_excluir}, {"_id": 0})

            if funcionario:
                campos = ['nome_excluir', 'rg_excluir', 'cpf_excluir', 'rua_excluir', 'numero_excluir', 'complemento_excluir',
                          'bairro_excluir', 'cidade_excluir', 'estado_excluir', 'cep_excluir', 'telefone_fixo_excluir',
                          'telefone_celular_excluir', 'numero_ctps_excluir', 'numero_pis_excluir']

                valores = []

                for key, value in funcionario.items():
                    valores.append(value)

                funcionario_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in funcionario_novo.items():
                    self.ids[key].text = value
            else:
                self.show_popup('Erro', f'Funcionário com CPF "{cpf_excluir}" não encontrado.')

    def editar_funcionario(self):

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
            self.ids.numero_ctps_editar.text = ''
            self.ids.numero_pis_editar.text = ''

        def campos_preenchidos(funcionario):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in funcionario.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(funcionario, excecao_id=None):

            db = self.get_db()
            colecao_funcionarios = db['funcionarios']

            query = {
                '$or': [
                    {'cpf': funcionario['cpf']},
                    {'rg': funcionario['rg']},
                    {'numero_ctps': funcionario['numero_ctps']},
                    {'numero_pis': funcionario['numero_pis']}
                ]
            }

            # Adiciona condição para ignorar o documento com excecao_id
            if excecao_id:
                query['_id'] = {'$ne': ObjectId(excecao_id)}

            # Realiza a consulta no banco de dados
            duplicado = colecao_funcionarios.find_one(query)

            return duplicado is None


        db = self.get_db()
        cpf = self.ids.buscar_funcionarios_editar.text.strip()

        novo_funcionario = {}
        campos = ['nome_editar', 'rg_editar', 'cpf_editar', 'rua_editar', 'numero_editar', 'complemento_editar',
                  'bairro_editar', 'cidade_editar', 'estado_editar', 'cep_editar', 'telefone_fixo_editar',
                  'telefone_celular_editar', 'numero_ctps_editar', 'numero_pis_editar']

        for campo in campos:
            novo_funcionario[campo] = self.ids[campo].text.strip()

        campos_banco = ['nome', 'rg', 'cpf', 'rua', 'numero', 'complemento',
                  'bairro', 'cidade', 'estado', 'cep', 'telefone_fixo',
                  'telefone_celular', 'numero_ctps', 'numero_pis']

        valores = []

        for key, value in novo_funcionario.items():
            valores.append(value)

        funcionario_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_funcionario = db.funcionarios.find_one({"cpf": cpf})
        id = id_funcionario['_id']

        if not campos_preenchidos(funcionario_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(funcionario_final, excecao_id=id):
            self.show_popup('Erro', 'CPF, RG, CTPS ou PIS já estão em uso por outro funcionário.')
            return

        db.funcionarios.update_one({"cpf": cpf}, {"$set": funcionario_final})
        self.show_popup('Sucesso', 'Funcionário atualizado com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_funcionarios_editar.text = ''

    def excluir_funcionario(self):

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
            self.ids.numero_ctps_excluir.text = ''
            self.ids.numero_pis_excluir.text = ''

        db = self.get_db()
        cpf = self.ids.buscar_funcionarios_excluir.text.strip()

        db.funcionarios.delete_one({"cpf": cpf})
        self.show_popup('Sucesso', 'Funcionário excluido com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_funcionarios_excluir.text = ''

# Funções Convenio
    def cadastrar_convenio(self):

        def limpar_campos():

            # Limpa os campos do formulário
            self.ids.nome_empresa_cadastrar.text = ''
            self.ids.cnpj_cadastrar.text = ''
            self.ids.telefone_convenio_cadastrar.text = ''

        def inserir_convenio(dados):
            try:
                # Insere no MongoDB
                db = self.get_db()
                colecao_convenios = db['convenios']
                colecao_convenios.insert_one(dados)
                self.show_popup('Sucesso', 'Convenio cadastrado com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(convenio):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in convenio.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(convenio):

            # Verifica duplicação de dados no MongoDB
            db = self.get_db()
            colecao_convenios = db['convenios']
            duplicado = colecao_convenios.find_one({
                '$or': [
                    {'cnpj': convenio['cnpj']},
                ]
            })
            return duplicado is None

        convenio = {
            'nome_empresa': self.ids.nome_empresa_cadastrar.text,
            'cnpj': self.ids.cnpj_cadastrar.text,
            'telefone_convenio': self.ids.telefone_convenio_cadastrar.text,
        }

        if not campos_preenchidos(convenio):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(convenio):
            self.show_popup('Erro', 'Convenio já cadastrado.')
            return

        inserir_convenio(convenio)
        limpar_campos()

    def visualizar_convenio(self):

        def obter_lista_convenios():

            db = self.get_db()

            # Obtendo os convenios
            convenios = db.convenios.find({}, {
                "nome_empresa": 1, "cnpj": 1, "telefone_convenio": 1
            })

            # Retorna lista de nomes de convenios
            return list(convenios)

        grid = self.ids.convenios_grid
        grid.clear_widgets()
        convenios = obter_lista_convenios()

        for convenio in convenios:
            row = BoxLayout(size_hint_y=None, height=30)
            for key in ["nome_empresa", "cnpj", "telefone_convenio"]:
                value = convenio.get(key, '')
                row.add_widget(Label(text=str(value), size_hint_y=None, height=30, color=(0, 0, 0, 1)))
            grid.add_widget(row)

    def buscar_convenio(self):

        db = self.get_db()
        cnpj_editar = self.ids.buscar_convenio_editar.text.strip()
        cnpj_excluir = self.ids.buscar_convenio_excluir.text.strip()

        if cnpj_editar:
            convenio = db.convenios.find_one({"cnpj": cnpj_editar}, {"_id": 0})

            if convenio:
                campos = ['nome_empresa_editar', 'cnpj_editar', 'telefone_convenio_editar']

                valores = []

                for key, value in convenio.items():
                    valores.append(value)

                convenio_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in convenio_novo.items():
                    self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Convenio com CNPJ "{cnpj_editar}" não encontrado.')

        else:
            convenio = db.convenios.find_one({"cnpj": cnpj_excluir}, {"_id": 0})

            if convenio:
                campos = ['nome_empresa_excluir', 'cnpj_excluir', 'telefone_convenio_excluir']

                valores = []

                for key, value in convenio.items():
                    valores.append(value)

                convenio_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in convenio_novo.items():
                    self.ids[key].text = value
            else:
                self.show_popup('Erro', f'Convenio com CNPJ "{cnpj_excluir}" não encontrado.')

    def editar_convenio(self):

        def limpar_campos():

            # Limpa os campos do formulário
            self.ids.nome_empresa_editar.text = ''
            self.ids.cnpj_editar.text = ''
            self.ids.telefone_convenio_editar.text = ''

        def campos_preenchidos(convenio):

            # Verifica se os campos obrigatórios não estão vazios
            for key, value in convenio.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(convenio, excecao_id=None):

            db = self.get_db()
            colecao_convenios = db['convenios']

            query = {
                '$or': [
                    {'cnpj': convenio['cnpj']},
                ]
            }

            # Adiciona condição para ignorar o documento com excecao_id
            if excecao_id:
                query['_id'] = {'$ne': ObjectId(excecao_id)}

            # Realiza a consulta no banco de dados
            duplicado = colecao_convenios.find_one(query)

            return duplicado is None


        db = self.get_db()
        cnpj = self.ids.buscar_convenio_editar.text.strip()

        novo_convenio = {}
        campos = ['nome_empresa_editar', 'cnpj_editar', 'telefone_convenio_editar']

        for campo in campos:
            novo_convenio[campo] = self.ids[campo].text.strip()

        campos_banco = ['nome_empresa', 'cnpj', 'telefone_convenio']

        valores = []

        for key, value in novo_convenio.items():
            valores.append(value)

        convenio_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_convenio = db.convenios.find_one({"cnpj": cnpj})
        id = id_convenio['_id']

        if not campos_preenchidos(convenio_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(convenio_final, excecao_id=id):
            self.show_popup('Erro', 'CNPJ já está em uso por outra Empresa.')
            return

        db.convenios.update_one({"cnpj": cnpj}, {"$set": convenio_final})
        self.show_popup('Sucesso', 'Convenio atualizado com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_convenio_editar.text = ''

    def excluir_convenio(self):

        def limpar_campos():

            # Limpa os campos do formulário
            self.ids.nome_empresa_excluir.text = ''
            self.ids.cnpj_excluir.text = ''
            self.ids.telefone_convenio_excluir.text = ''

        db = self.get_db()
        cnpj = self.ids.buscar_convenio_excluir.text.strip()

        db.convenios.delete_one({"cnpj": cnpj})
        self.show_popup('Sucesso', 'Convenio excluido com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_convenio_excluir.text = ''

# Funções Especialidades

    def cadastrar_especialidade(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_especialidade_cadastrar.text = ''
            self.ids.descricao_especialidade_cadastrar.text = ''

        def inserir_especialidade(dados):
            try:
                # Insere no MongoDB
                db = self.get_db()
                colecao_especialidades = db['especialidades']
                colecao_especialidades.insert_one(dados)
                self.show_popup('Sucesso', 'Especialidade cadastrada com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(especialidade):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in especialidade.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(especialidade):

            # Verifica duplicação de dados no MongoDB
            db = self.get_db()
            colecao_especialidades = db['especialidades']
            duplicado = colecao_especialidades.find_one({
                '$or': [
                    {'nome_especialidade': especialidade['nome_especialidade']},
                ]
            })
            return duplicado is None

        especialidade = {
            'nome_especialidade': self.ids.nome_especialidade_cadastrar.text,
            'descricao_especialidade': self.ids.descricao_especialidade_cadastrar.text,
        }

        if not campos_preenchidos(especialidade):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(especialidade):
            self.show_popup('Erro', 'Especialidade já cadastrada.')
            return

        inserir_especialidade(especialidade)
        limpar_campos()

    def visualizar_especialidade(self):

        def obter_lista_especialidades():

            db = self.get_db()

            # Obtendo os convenios
            especialidades = db.especialidades.find({}, {
                "nome_especialidade": 1, "descricao_especialidade": 1
            })

            # Retorna lista de nomes de convenios
            return list(especialidades)

        grid = self.ids.especialidades_grid
        grid.clear_widgets()
        especialidades = obter_lista_especialidades()

        for especialidade in especialidades:
            row = BoxLayout(size_hint_y=None, height=30)
            for key in ["nome_especialidade", "descricao_especialidade"]:
                value = especialidade.get(key, '')
                row.add_widget(Label(text=str(value), size_hint_y=None, height=30, color=(0, 0, 0, 1)))
            grid.add_widget(row)

    def buscar_especialidade(self):

        db = self.get_db()
        nome_especialidade_editar = self.ids.buscar_especialidade_editar.text.strip()
        nome_especialidade_excluir = self.ids.buscar_especialidade_excluir.text.strip()

        if nome_especialidade_editar:
            especialidade = db.especialidades.find_one({"nome_especialidade": nome_especialidade_editar}, {"_id": 0})

            if especialidade:
                campos = ['nome_especialidade_editar', 'descricao_especialidade_editar']

                valores = []

                for key, value in especialidade.items():
                    valores.append(value)

                especialidade_nova = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in especialidade_nova.items():
                    self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Especialidade com Nome "{nome_especialidade_editar}" não encontrado.')

        else:
            especialidade = db.especialidades.find_one({"nome_especialidade": nome_especialidade_excluir}, {"_id": 0})

            if especialidade:
                campos = ['nome_especialidade_excluir', 'descricao_especialidade_excluir']

                valores = []

                for key, value in especialidade.items():
                    valores.append(value)

                especialidade_nova = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in especialidade_nova.items():
                    self.ids[key].text = value
            else:
                self.show_popup('Erro', f'Especialidade com Nome "{nome_especialidade_excluir}" não encontrado.')

    def editar_especialidade(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_especialidade_editar.text = ''
            self.ids.descricao_especialidade_editar.text = ''

        def campos_preenchidos(especialidade):

            # Verifica se os campos obrigatórios não estão vazios
            for key, value in especialidade.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(especialidade, excecao_id=None):

            db = self.get_db()
            colecao_especialidades = db['especialidades']

            query = {
                '$or': [
                    {'nome_especialidade': especialidade['nome_especialidade']},
                ]
            }

            # Adiciona condição para ignorar o documento com excecao_id
            if excecao_id:
                query['_id'] = {'$ne': ObjectId(excecao_id)}

            # Realiza a consulta no banco de dados
            duplicado = colecao_especialidades.find_one(query)

            return duplicado is None


        db = self.get_db()
        nome_especialidade = self.ids.buscar_especialidade_editar.text.strip()

        nova_especialidade = {}
        campos = ['nome_especialidade_editar', 'descricao_especialidade_editar']

        for campo in campos:
            nova_especialidade[campo] = self.ids[campo].text.strip()

        campos_banco = ['nome_especialidade', 'descricao_especialidade']

        valores = []

        for key, value in nova_especialidade.items():
            valores.append(value)

        especialidade_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_especialidade = db.especialidades.find_one({"nome_especialidade": nome_especialidade})
        id = id_especialidade['_id']

        if not campos_preenchidos(especialidade_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(especialidade_final, excecao_id=id):
            self.show_popup('Erro', 'Especialidade já está em uso.')
            return

        db.especialidades.update_one({"nome_especialidade": nome_especialidade}, {"$set": especialidade_final})
        self.show_popup('Sucesso', 'Especialidade atualizada com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_especialidade_editar.text = ''

    def excluir_especialidade(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_especialidade_excluir.text = ''
            self.ids.descricao_especialidade_excluir.text = ''

        db = self.get_db()
        nome_especialidade = self.ids.buscar_especialidade_excluir.text.strip()

        db.especialidades.delete_one({"nome_especialidade": nome_especialidade})
        self.show_popup('Sucesso', 'Especialidade excluida com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_especialidade_excluir.text = ''

# Funções Medicos
    def buscar_cpf_funcionario(self):

        global cpf_funcionario_medico

        db = self.get_db()
        cpf = self.ids.buscar_cpf_funcionario.text.strip()

        funcionario = db.funcionarios.find_one({"cpf": cpf}, {"_id": 0})

        if funcionario:

            campos = ['nome_medico_cadastrar', 'cpf_medico_cadastrar']

            valores = []

            for key, value in funcionario.items():
                if key == "nome" or key == "cpf":
                    valores.append(value)

            funcionario_novo = {campo: valor for campo, valor in zip(campos, valores)}

            # Adicione o CPF do funcionário à variável global
            cpf_funcionario_medico = funcionario.get("cpf", "")

            for key, value in funcionario_novo.items():
                self.ids[key].text = value

        else:
            self.show_popup('Erro', f'Funcionario com CPF "{cpf}" não encontrado.')

    def cadastrar_medico(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_medico_cadastrar.text = ''
            self.ids.cpf_medico_cadastrar.text = ''
            self.ids.crm_cadastrar.text = ''
            self.ids.especialidades_medico_cadastrar.text = ''

        def inserir_medico(dados):
            try:
                # Insere no MongoDB
                db = self.get_db()
                colecao_medicos = db['medicos']
                colecao_medicos.insert_one(dados)
                self.show_popup('Sucesso', 'Medico cadastrado com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(medico):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in medico.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(medico):

            # Verifica duplicação de dados no MongoDB
            db = self.get_db()
            colecao_medicos = db['medicos']
            duplicado = colecao_medicos.find_one({
                '$or': [
                    {'crm': medico['crm']},
                ]
            })
            return duplicado is None

        def verificar_especialidades(especialidades):
            # Conecta ao MongoDB e verifica especialidades
            db = self.get_db()
            colecao_especialidades = db[
                'especialidades']  # Supondo que a coleção de especialidades seja 'especialidades'

            especialidades_na_base = colecao_especialidades.find(
                {"nome_especialidade": {"$in": especialidades}},
                {"_id": 0, "nome_especialidade": 1}
            )

            especialidades_na_base = [especialidade["nome_especialidade"] for especialidade in especialidades_na_base]

            # Identifica especialidades que não estão na base
            especialidades_nao_encontradas = [
                especialidade for especialidade in especialidades if especialidade not in especialidades_na_base
            ]

            return especialidades_nao_encontradas

        medico = {
            'nome': self.ids.nome_medico_cadastrar.text,
            'crm': self.ids.crm_cadastrar.text,
            'especialidades': self.ids.especialidades_medico_cadastrar.text,
            'cpf_funcionario': cpf_funcionario_medico,
        }

        if not campos_preenchidos(medico):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(medico):
            self.show_popup('Erro', 'Medico já cadastrado.')
            return

        # Processa as especialidades
        especialidades = [e.strip() for e in medico['especialidades'].split(',')]
        especialidades_nao_encontradas = verificar_especialidades(especialidades)

        if especialidades_nao_encontradas:
            self.show_popup('Erro',
                            f'As seguintes especialidades não foram encontradas: {", ".join(especialidades_nao_encontradas)}')
            return

        inserir_medico(medico)
        limpar_campos()
        self.ids.buscar_cpf_funcionario.text = ''

    def visualizar_medico(self):

        def obter_lista_medicos():

            db = self.get_db()

            # Obtendo os convenios
            medicos = db.medicos.find({}, {
                "nome": 1, "crm": 1, "especialidades": 1, "cpf_funcionario": 1
            })

            # Retorna lista de nomes de convenios
            return list(medicos)

        grid = self.ids.medicos_grid
        grid.clear_widgets()
        medicos = obter_lista_medicos()

        for medico in medicos:
            row = BoxLayout(size_hint_y=None, height=30)
            for key in ["nome", "crm", "especialidades", "cpf_funcionario"]:
                value = medico.get(key, '')
                row.add_widget(Label(text=str(value), size_hint_y=None, height=30, color=(0, 0, 0, 1)))
            grid.add_widget(row)

    def buscar_medico(self):

        db = self.get_db()
        crm_editar = self.ids.buscar_medico_editar.text.strip()
        crm_excluir = self.ids.buscar_medico_excluir.text.strip()

        if crm_editar:
            medico = db.medicos.find_one({"crm": crm_editar}, {"_id": 0})

            if medico:
                campos = {
                    'nome': 'nome_medico_editar',
                    'cpf_funcionario': 'cpf_medico_editar',
                    'crm': 'crm_editar',
                    'especialidades': 'especialidades_medico_editar'
                }

                for campo_banco, campo_ui in campos.items():
                    if campo_banco in medico:
                        self.ids[campo_ui].text = medico[campo_banco]

            else:
                self.show_popup('Erro', f'Medico com CRM "{crm_editar}" não encontrado.')

        else:
            medico = db.medicos.find_one({"crm": crm_excluir}, {"_id": 0})

            if medico:
                campos = {
                    'nome': 'nome_medico_excluir',
                    'cpf_funcionario': 'cpf_medico_excluir',
                    'crm': 'crm_excluir',
                    'especialidades': 'especialidades_medico_excluir'
                }

                for campo_banco, campo_ui in campos.items():
                    if campo_banco in medico:
                        self.ids[campo_ui].text = medico[campo_banco]
            else:
                self.show_popup('Erro', f'Medico com CRM "{crm_excluir}" não encontrado.')

    def editar_medico(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_medico_editar.text = ''
            self.ids.cpf_medico_editar.text = ''
            self.ids.crm_editar.text = ''
            self.ids.especialidades_medico_editar.text = ''

        def campos_preenchidos(medico):

            # Verifica se os campos obrigatórios não estão vazios
            for key, value in medico.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(medico, excecao_id=None):

            db = self.get_db()
            colecao_medicos = db['medicos']

            query = {
                '$or': [
                    {'crm': medico['crm']},
                ]
            }

            # Adiciona condição para ignorar o documento com excecao_id
            if excecao_id:
                query['_id'] = {'$ne': ObjectId(excecao_id)}

            # Realiza a consulta no banco de dados
            duplicado = colecao_medicos.find_one(query)

            return duplicado is None

        def verificar_especialidades(especialidades):
            # Conecta ao MongoDB e verifica especialidades
            db = self.get_db()
            colecao_especialidades = db[
                'especialidades']  # Supondo que a coleção de especialidades seja 'especialidades'

            especialidades_na_base = colecao_especialidades.find(
                {"nome_especialidade": {"$in": especialidades}},
                {"_id": 0, "nome_especialidade": 1}
            )

            especialidades_na_base = [especialidade["nome_especialidade"] for especialidade in especialidades_na_base]

            # Identifica especialidades que não estão na base
            especialidades_nao_encontradas = [
                especialidade for especialidade in especialidades if especialidade not in especialidades_na_base
            ]

            return especialidades_nao_encontradas

        db = self.get_db()
        crm = self.ids.buscar_medico_editar.text.strip()

        novo_medico = {}
        campos = ['nome_medico_editar', 'cpf_medico_editar', 'crm_editar', 'especialidades_medico_editar']

        for campo in campos:
            novo_medico[campo] = self.ids[campo].text.strip()

        campos_banco = ['nome', 'cpf_funcionario', 'crm', 'especialidades']

        valores = []

        for key, value in novo_medico.items():
            valores.append(value)

        medico_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_medico = db.medicos.find_one({"crm": crm})
        id = id_medico['_id']

        if not campos_preenchidos(medico_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(medico_final, excecao_id=id):
            self.show_popup('Erro', 'CRM já está em uso por outro Medico.')
            return

        especialidades = [e.strip() for e in medico_final['especialidades'].split(',')]
        especialidades_nao_encontradas = verificar_especialidades(especialidades)

        if especialidades_nao_encontradas:
            self.show_popup('Erro',
                            f'As seguintes especialidades não foram encontradas: {", ".join(especialidades_nao_encontradas)}')
            return

        cpf = self.ids.cpf_medico_editar.text.strip()
        funcionario = db.funcionarios.find_one({"cpf": cpf}, {"_id": 0})
        if funcionario:
            db.medicos.update_one({"crm": crm}, {"$set": medico_final})
            self.show_popup('Sucesso', 'Medico atualizado com sucesso.')
            limpar_campos()
            # Limpa o campo de busca
            self.ids.buscar_medico_editar.text = ''
        else:
            self.show_popup('Erro', f'Funcionario com CPF "{cpf}" não encontrado.')

    def excluir_medico(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.nome_medico_excluir.text = ''
            self.ids.cpf_medico_excluir.text = ''
            self.ids.crm_excluir.text = ''
            self.ids.especialidades_medico_excluir.text = ''

        db = self.get_db()
        crm = self.ids.buscar_medico_excluir.text.strip()

        db.medicos.delete_one({"crm": crm})
        self.show_popup('Sucesso', 'Medico excluido com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_medico_excluir.text = ''

# Funções Usuario
    def buscar_cpf_funcionario_user(self):

        global cpf_funcionario_usuario

        db = self.get_db()
        cpf = self.ids.buscar_cpf_funcionario_user.text.strip()

        funcionario = db.funcionarios.find_one({"cpf": cpf}, {"_id": 0})

        if funcionario:
            campo = 'cpf_usuario_cadastrar'

            for key, value in funcionario.items():
                if key == "cpf":
                    valor = value

            funcionario_novo = {}
            funcionario_novo[campo] = valor

            # Adicione o CPF do funcionário à variável global
            cpf_funcionario_usuario = funcionario.get("cpf", "")

            for key, value in funcionario_novo.items():
                self.ids[key].text = value

        else:
            self.show_popup('Erro', f'Funcionario com CPF "{cpf}" não encontrado.')

    def cadastrar_usuario(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.id_usuario_cadastrar.text = ''
            self.ids.senha_cadastrar.text = ''
            self.ids.cpf_usuario_cadastrar.text = ''
            self.ids.permissao_cadastrar.text = 'Permissões'

        def inserir_usuario(dados):
            try:
                # Insere no MongoDB
                db = self.get_db()
                colecao_usuarios = db['usuarios']
                colecao_usuarios.insert_one(dados)
                self.show_popup('Sucesso', 'Usuario cadastrado com sucesso!')

            except Exception as e:
                self.show_popup('Erro', f'Ocorreu um erro: {e}')

        def campos_preenchidos(usuario):
            # Verifica se os campos obrigatórios não estão vazios
            for key, value in usuario.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(usuario):

            # Verifica duplicação de dados no MongoDB
            db = self.get_db()
            colecao_usuarios = db['usuarios']
            duplicado = colecao_usuarios.find_one({
                '$or': [
                    {'id_usuario': usuario['id_usuario']},
                ]
            })
            return duplicado is None

        usuario = {
            'id_usuario': self.ids.id_usuario_cadastrar.text,
            'senha': self.ids.senha_cadastrar.text,
            'permissao': self.ids.permissao_cadastrar.text,
            'cpf_funcionario': cpf_funcionario_usuario,
        }

        if not campos_preenchidos(usuario):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(usuario):
            self.show_popup('Erro', 'Usuario já cadastrado.')
            return

        inserir_usuario(usuario)
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_cpf_funcionario_user.text = ''

    def visualizar_usuario(self):

        def obter_lista_usuarios():

            db = self.get_db()

            # Obtendo os convenios
            usuarios = db.usuarios.find({}, {
                "id_usuario": 1, "senha": 1, "permissao": 1, "cpf_funcionario": 1
            })

            # Retorna lista de nomes de convenios
            return list(usuarios)

        grid = self.ids.usuarios_grid
        grid.clear_widgets()
        usuarios = obter_lista_usuarios()

        for usuario in usuarios:
            row = BoxLayout(size_hint_y=None, height=30)
            for key in ["id_usuario", "senha", "permissao", "cpf_funcionario"]:
                value = usuario.get(key, '')
                row.add_widget(Label(text=str(value), size_hint_y=None, height=30, color=(0, 0, 0, 1)))
            grid.add_widget(row)

    def buscar_usuario(self):

        db = self.get_db()
        id_usuario_editar = self.ids.buscar_usuario_editar.text.strip()
        id_usuario_excluir = self.ids.buscar_usuario_excluir.text.strip()

        if id_usuario_editar:
            usuario = db.usuarios.find_one({"id_usuario": id_usuario_editar}, {"_id": 0})

            if usuario:
                campos = ['id_usuario_editar', 'senha_editar', 'permissao_editar', 'cpf_usuario_editar']

                valores = []

                for key, value in usuario.items():
                    valores.append(value)

                usuario_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in usuario_novo.items():
                    self.ids[key].text = value

            else:
                self.show_popup('Erro', f'Usuario "{id_usuario_editar}" não encontrado.')

        else:
            usuario = db.usuarios.find_one({"id_usuario": id_usuario_excluir}, {"_id": 0})

            if usuario:
                campos = ['id_usuario_excluir', 'senha_excluir', 'permissao_excluir', 'cpf_usuario_excluir']

                valores = []

                for key, value in usuario.items():
                    valores.append(value)

                usuario_novo = {campo: valor for campo, valor in zip(campos, valores)}

                for key, value in usuario_novo.items():
                    self.ids[key].text = value
            else:
                self.show_popup('Erro', f'Usuario "{id_usuario_excluir}" não encontrado.')

    def editar_usuario(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.id_usuario_editar.text = ''
            self.ids.senha_editar.text = ''
            self.ids.cpf_usuario_editar.text = ''
            self.ids.permissao_editar.text = 'Permissões'

        def campos_preenchidos(usuario):

            # Verifica se os campos obrigatórios não estão vazios
            for key, value in usuario.items():
                if not value.strip():
                    return False
            return True

        def dados_nao_duplicados(usuario, excecao_id=None):

            db = self.get_db()
            colecao_usuarios = db['usuarios']

            query = {
                '$or': [
                    {'id_usuario': usuario['id_usuario']},
                ]
            }

            # Adiciona condição para ignorar o documento com excecao_id
            if excecao_id:
                query['_id'] = {'$ne': ObjectId(excecao_id)}

            # Realiza a consulta no banco de dados
            duplicado = colecao_usuarios.find_one(query)

            return duplicado is None

        db = self.get_db()
        id_usuario = self.ids.buscar_usuario_editar.text.strip()

        novo_usuario = {}
        campos = ['id_usuario_editar', 'senha_editar', 'permissao_editar', 'cpf_usuario_editar']

        for campo in campos:
            novo_usuario[campo] = self.ids[campo].text.strip()

        campos_banco = ['id_usuario', 'senha', 'permissao', 'cpf_funcionario']

        valores = []

        for key, value in novo_usuario.items():
            valores.append(value)

        usuario_final = {campo: valor for campo, valor in zip(campos_banco, valores)}

        id_user = db.usuarios.find_one({"id_usuario": id_usuario})
        id = id_user['_id']

        if not campos_preenchidos(usuario_final):
            self.show_popup('Erro', 'Todos os campos obrigatórios devem ser preenchidos.')
            return

        if not dados_nao_duplicados(usuario_final, excecao_id=id):
            self.show_popup('Erro', 'ID já está em uso por outro Usuario.')
            return

        cpf = self.ids.cpf_usuario_editar.text.strip()
        funcionario = db.funcionarios.find_one({"cpf": cpf}, {"_id": 0})
        if funcionario:
            db.usuarios.update_one({"id_usuario": id_usuario}, {"$set": usuario_final})
            self.show_popup('Sucesso', 'Usuario atualizado com sucesso.')
            limpar_campos()
            # Limpa o campo de busca
            self.ids.buscar_usuario_editar.text = ''
        else:
            self.show_popup('Erro', f'Funcionario com CPF "{cpf}" não encontrado.')

    def excluir_usuario(self):

        def limpar_campos():
            # Limpa os campos do formulário
            self.ids.id_usuario_excluir.text = ''
            self.ids.senha_excluir.text = ''
            self.ids.cpf_usuario_excluir.text = ''
            self.ids.permissao_excluir.text = 'Permissões'

        db = self.get_db()
        id_usuario = self.ids.buscar_usuario_excluir.text.strip()

        db.usuarios.delete_one({"id_usuario": id_usuario})
        self.show_popup('Sucesso', 'Usuario excluido com sucesso.')
        limpar_campos()
        # Limpa o campo de busca
        self.ids.buscar_usuario_excluir.text = ''

# Função sair
    def sair(self):
        self.parent.parent.current = 'screen_login'

class MenuApp(App):
    def build(self):
        return Menu()

if __name__ == '__main__':

    MenuApp().run()
