# tela_login.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from pymongo import MongoClient
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from ui.singleton import UsuarioLogadoSingleton

# Carregar o arquivo .kv
Builder.load_file('ui/tela_login.kv')

class TelaLogin(BoxLayout):
    def __init__(self, login_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.usuario_logado_singleton = UsuarioLogadoSingleton()
        self.login_callback = login_callback
    def get_db(self):
        try:
            client = MongoClient('mongodb://root:12345@localhost:27017/')  # Substitua pela sua URI do MongoDB
            db = client['ultrasaude']  # Nome do banco de dados
            return db

        except Exception as e:
            self.show_popup(f'Erro ao se conectar ao banco: {e}')
            return None

    def login(self):
        db = self.get_db()
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        usuario = db.usuarios.find_one({"id_usuario": username}, {"_id": 0})

        if usuario and username == usuario['id_usuario'] and password == usuario['senha']:
            self.usuario_logado_singleton.set_usuario_logado(username)
            if self.login_callback:
                self.login_callback(usuario['permissao'])
        else:
            self.show_popup('Login Falhou', 'Senha ou ID Inválido.')

        self.ids.username.text = ''
        self.ids.password.text = ''
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

class LoginApp(App):
    def build(self):
        return TelaLogin()

if __name__ == '__main__':
    LoginApp().run()
