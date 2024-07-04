#main.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from ui.tela_login import TelaLogin
from ui.menu import Menu
from ui.menuMedico import MenuMedico
from ui.menuAgendamento import MenuAgendamento

class TelaMain(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = ScreenManager()
        self.add_widget(self.screen_manager)
        self.adicionar_tela_login()

    def adicionar_tela_login(self):
        tela_login = Screen(name='screen_login')
        tela_login.add_widget(TelaLogin(login_callback=self.on_login_success))
        self.screen_manager.add_widget(tela_login)
        self.screen_manager.current = 'screen_login'

    def criar_telas_apos_login(self, permissao):
        if permissao == 'Administrador':
            tela_administrador = Screen(name='screen_administrador')
            tela_administrador.add_widget(Menu())
            self.screen_manager.add_widget(tela_administrador)
            self.screen_manager.current = 'screen_administrador'
        elif permissao == 'Medico':
            tela_medico = Screen(name='screen_medico')
            tela_medico.add_widget(MenuMedico())
            self.screen_manager.add_widget(tela_medico)
            self.screen_manager.current = 'screen_medico'
        elif permissao == 'Agendamento':
            tela_agendamento = Screen(name='screen_agendamento')
            tela_agendamento.add_widget(MenuAgendamento())
            self.screen_manager.add_widget(tela_agendamento)
            self.screen_manager.current = 'screen_agendamento'

    def on_login_success(self, permissao):
        self.reiniciar_telas()
        self.criar_telas_apos_login(permissao)

    def reiniciar_telas(self):
        # Remover todas as telas menos a de login
        telas_para_remover = [screen for screen in self.screen_manager.screens if screen.name != 'screen_login']
        for screen in telas_para_remover:
            self.screen_manager.remove_widget(screen)

        # Adicionar novamente a tela de login e resetar o ScreenManager
        self.screen_manager.current = 'screen_login'
        self.adicionar_tela_login()

class MainApp(App):
    def build(self):
        self.main_widget = TelaMain()
        return self.main_widget

    def reiniciar_tela(self):
        self.main_widget.reiniciar_telas()


if __name__ == '__main__':

    MainApp().run()
