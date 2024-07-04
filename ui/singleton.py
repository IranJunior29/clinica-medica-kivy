# singleton.py

class UsuarioLogadoSingleton:
    _instance = None
    _usuario_logado = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UsuarioLogadoSingleton, cls).__new__(cls)
        return cls._instance

    def set_usuario_logado(self, usuario_id):
        self._usuario_logado = usuario_id

    def get_usuario_logado(self):
        return self._usuario_logado

    def clear_usuario_logado(self):
        self._usuario_logado = None

    def is_usuario_logado(self):
        return self._usuario_logado is not None
