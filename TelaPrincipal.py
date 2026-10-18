from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QStackedWidget, QDialog, QMessageBox
)
from FuncoesRecorte import SeletorRegiao
from Gravar import GravadorTela, JanelaGravacao
from pathlib import Path
from datetime import datetime
import subprocess


class TelaPrincipal( QWidget ):

    def __init__( self, funcoes ):
        
        super().__init__()
        self.funcoes = funcoes

        self.setWindowTitle( 'Gravei' )
        self.resize( 500, 300 )

        self.Layout_Principal = QHBoxLayout()

        Layout_Menu = QVBoxLayout()

        Botao_Gravacao = QPushButton( 'Gravacao' )
        Botao_Execucao = QPushButton( 'Verificacao' )

        Gravacao         = QWidget()
        Layout_Gravacao  = QVBoxLayout( Gravacao )
        Layout_Gravacao.setContentsMargins( 0, 0, 0, 0 )
        Layout_Gravacao.setSpacing( 3 )
        Layout_Gravacao.addWidget( Botao_Gravacao )

        Execucao         = QWidget()
        Layout_Execucao  = QVBoxLayout( Execucao )
        Layout_Execucao.setContentsMargins( 0, 0, 0, 0 )
        Layout_Execucao.setSpacing( 3 )
        Layout_Execucao.addWidget( Botao_Execucao )

        Layout_Menu.addWidget( Gravacao )
        Layout_Menu.addWidget( Execucao )
        Layout_Menu.addStretch()

        # prepara variavies para gravacao
        self.gravador = GravadorTela()
        self.janela_gravacao = None
        self.processo = None
        self.audio = None
        self.video_temp = None
        self.audio_temp = None
        self.arquivo_saida = None
        
        self.Stack = QStackedWidget()
        self.Layout_Opcao_Gravacao()
        self.Layout_Opcao_Execucao()

        self.Layout_Principal.addLayout( Layout_Menu, 1 )
        self.Layout_Principal.addWidget( self.Stack, 9 )

        self.setLayout( self.Layout_Principal )

        Botao_Gravacao.clicked.connect( lambda: self.Stack.setCurrentIndex( 0 ) )
        Botao_Execucao.clicked.connect( lambda: self.Stack.setCurrentIndex( 1 ) )


    def Layout_Opcao_Gravacao( self ):
        
        pagina = QWidget()
        layout = QVBoxLayout()

        layout_botao = QHBoxLayout()

        titulo = QLabel( 'Gravacao' )

        botao_recorte = QPushButton( 'Recorte'    )
        botao_tela    = QPushButton( 'Tela Cheia' )
        botao_parar   = QPushButton( 'Parar'      )

        layout_botao.addWidget( botao_recorte )
        layout_botao.addWidget( botao_tela    )

        layout.addWidget( titulo       )
        layout.addLayout( layout_botao )
        layout.addWidget( botao_parar )

        pagina.setLayout( layout )
        self.Stack.addWidget( pagina )

        botao_recorte.clicked.connect( self.SelecionarRecorte )
        botao_tela.clicked.connect(
            lambda: self.iniciar_gravacao()
        )
        botao_parar.clicked.connect(self.parar_gravacao)


    def Layout_Opcao_Execucao( self ):

        pagina = QWidget()
        layout = QVBoxLayout()
        titulo = QLabel('Execucao')

        layout.addWidget( titulo )

        pagina.setLayout( layout )
        self.Stack.addWidget( pagina )

    def SelecionarRecorte( self ):

        self.hide()

        seletor = SeletorRegiao()
        resultado = seletor.exec()

        self.show()
        self.activateWindow()

        if resultado == QDialog.DialogCode.Accepted:
            self.iniciar_gravacao(seletor.regiao)
        else:
            print("Seleção cancelada.")

    def iniciar_gravacao(self, regiao=None):
        try:
            self.gravador.iniciar(regiao)
        except (OSError, RuntimeError, ValueError) as erro:
            QMessageBox.critical(
                self,
                "Erro ao iniciar gravação",
                str(erro),
            )
            return

        self.janela_gravacao = JanelaGravacao(
            self.parar_gravacao, self
        )
        self.janela_gravacao.iniciar()

    def parar_gravacao(self):
        if self.gravador.processo is None:
            return

        try:
            self.gravador.parar()
        except (OSError, RuntimeError) as erro:
            QMessageBox.critical(
                self,
                "Erro ao concluir gravação",
                str(erro),
            )
        finally:
            if self.janela_gravacao is not None:
                self.janela_gravacao.finalizar()
                self.janela_gravacao = None
