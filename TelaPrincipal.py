import re
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QInputDialog,
    QStackedWidget, QDialog, QMessageBox, QSlider, QFileDialog, QLineEdit
)
from FuncoesRecorte import SeletorRegiao
from Gravar import GravadorTela, JanelaGravacao
from ConcentraFuncoes import ConfigSlider, VideoWidgetInterativo
from Layouts import (
    TEMAS_CORES,
    OpcaoTema,
    PaginaGravacao,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QPoint, QCoreApplication, QSettings, QStandardPaths, Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class TelaPrincipal( QWidget ):

    def __init__( self, funcoes ):
        
        super().__init__()
        self.funcoes = funcoes

        self.setWindowTitle( 'Gravei' )
        self.resize( 500, 300 )

        self.configuracoes = QSettings("Gravei", "Gravei")
        tema_salvo = self.configuracoes.value(
            "tema_cores", "preto_cinza", type=str
        )
        self.tema_atual: str = (
            tema_salvo
            if isinstance(tema_salvo, str) and tema_salvo in TEMAS_CORES
            else "preto_cinza"
        )
        self.opcoes_tema = []
        if getattr(sys, "frozen", False):
            pasta_padrao = Path(sys.executable).resolve().parent / "Videos"
        else:
            desktop = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DesktopLocation
            )
            pasta_padrao = Path(desktop or Path.home() / "Desktop") / "Gravei"
        pasta_configurada = self.configuracoes.value(
            "pasta_videos", str(pasta_padrao), type=str
        )
        self.pasta_videos = Path(str(pasta_configurada))

        self.Layout_Principal = QHBoxLayout()

        Layout_Menu = QVBoxLayout()

        Botao_Gravacao = QPushButton( 'Gravacao' )
        Botao_Execucao = QPushButton( 'Verificacao' )
        Botao_Configuracao = QPushButton( 'Configuracao' )

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
        Layout_Menu.addWidget( Botao_Configuracao )
        Layout_Menu.addStretch()

        self.gravador = GravadorTela(self.pasta_videos)
        self.janela_gravacao = None
        self.processo = None
        self.audio = None
        self.video_temp = None
        self.audio_temp = None
        self.arquivo_saida = None
        
        self.Stack = QStackedWidget()
        self.Layout_Opcao_Gravacao()
        self.Layout_Opcao_Execucao()
        self.Layout_Opcao_Configuracao()

        self.Layout_Principal.addLayout( Layout_Menu, 1 )
        self.Layout_Principal.addWidget( self.Stack, 9 )

        self.setLayout( self.Layout_Principal )

        Botao_Gravacao.clicked.connect( lambda: self.Stack.setCurrentIndex( 0 ) )
        Botao_Execucao.clicked.connect(self.abrir_video_gravado)
        Botao_Configuracao.clicked.connect(
            lambda: self.Stack.setCurrentIndex(2)
        )
        self.aplicar_tema()


    def Layout_Opcao_Gravacao( self ):
        
        self.pagina_gravacao = PaginaGravacao()
        self.Stack.addWidget(self.pagina_gravacao)

        self.pagina_gravacao.botao_recorte.clicked.connect(self.SelecionarRecorte)
        self.pagina_gravacao.botao_tela_cheia.clicked.connect(self.selecionar_tela_cheia)


    def Layout_Opcao_Execucao( self ):

        pagina = QWidget()
        layout = QVBoxLayout()

        self.videoWidget = VideoWidgetInterativo(self)
        self.player      = QMediaPlayer(self)
        self.audioOutput = QAudioOutput(self)
        self.player.setAudioOutput(self.audioOutput)
        self.player.setVideoOutput(self.videoWidget)

        self.slider = ConfigSlider(Qt.Orientation.Horizontal)
        self.slider.setMouseTracking(True)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.tempoAtual = ''
        self.tempoTotal = ''

        self.temporizador = QLabel("00:00:00 / 00:00:00")

        self.avancar = QPushButton('+5')
        self.voltar  = QPushButton('-5')

        self.volumeSlider = QSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(100)
        self.audioOutput.setVolume(1.0)

        layoutSlider = QHBoxLayout()
        layoutSlider.addWidget(self.temporizador)
        layoutSlider.addWidget(self.voltar)
        layoutSlider.addWidget(self.avancar)
        layoutSlider.addWidget(self.slider, 6)
        layoutSlider.addWidget(self.volumeSlider, 1)

        layoutReprodutor = QVBoxLayout()
        layoutReprodutor.addWidget(self.videoWidget)
        layoutReprodutor.addLayout(layoutSlider)

        layout.addLayout(layoutReprodutor)

        layout_decisao = QHBoxLayout()
        self.botao_salvar = QPushButton("Salvar gravação")
        self.botao_descartar = QPushButton("Descartar gravação")
        layout_decisao.addWidget(self.botao_salvar)
        layout_decisao.addWidget(self.botao_descartar)
        layout.addLayout(layout_decisao)

        pagina.setLayout( layout )
        self.Stack.addWidget( pagina )

        self.videoWidget.select.connect(self.alternarPlayPause)
        self.player.durationChanged.connect(self.atualizar_duracao)
        self.player.positionChanged.connect(self.atualizar_posicao)
        self.slider.sliderMoved.connect(self.player.setPosition)
        self.volumeSlider.valueChanged.connect(
            lambda volume: self.audioOutput.setVolume(volume / 100)
        )
        self.avancar.clicked.connect(
            lambda: self.player.setPosition(self.player.position() + 5000)
        )
        self.voltar.clicked.connect(
            lambda: self.player.setPosition(max(0, self.player.position() - 5000))
        )
        self.player.errorOccurred.connect(self.mostrar_erro_reproducao)
        self.botao_salvar.clicked.connect(self.salvar_gravacao)
        self.botao_descartar.clicked.connect(self.descartar_gravacao)

    def Layout_Opcao_Configuracao(self):

        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout_cores = QHBoxLayout()
        layout_cores.setSpacing(8)
        layout_cores.addWidget(QLabel("Cor"))
        for chave, tema in TEMAS_CORES.items():
            opcao = OpcaoTema(chave, tema)
            opcao.selecionado.connect(self.selecionar_tema)
            self.opcoes_tema.append(opcao)
            layout_cores.addWidget(opcao)
        layout_cores.addStretch()

        layout_pasta = QHBoxLayout()
        layout_pasta.addWidget(QLabel("Pasta"))
        self.rotulo_pasta_videos = QLineEdit(str(self.pasta_videos))
        self.rotulo_pasta_videos.setReadOnly(True)
        self.rotulo_pasta_videos.setAccessibleName(
            "Pasta para salvar os vídeos"
        )
        layout_pasta.addWidget(self.rotulo_pasta_videos, 1)
        botao_escolher_pasta = QPushButton("Escolher")
        botao_escolher_pasta.setAccessibleName(
            "Escolher pasta para salvar os vídeos"
        )
        layout_pasta.addWidget(botao_escolher_pasta)

        layout.addLayout(layout_cores)
        layout.addLayout(layout_pasta)
        layout.addStretch()
        self.Stack.addWidget(pagina)

        botao_escolher_pasta.clicked.connect(self.escolher_pasta_videos)

    def selecionar_tema(self, chave):

        self.tema_atual = chave
        self.configuracoes.setValue("tema_cores", chave)
        self.aplicar_tema()

    def aplicar_tema(self):

        tema = TEMAS_CORES[self.tema_atual]
        self.setStyleSheet(
            "QWidget {"
            f"background-color: {tema['fundo']};"
            f"color: {tema['texto']};"
            "}"
            "QPushButton {"
            f"background-color: {tema['superficie']};"
            f"color: {tema['texto']};"
            f"border: 1px solid {tema['destaque']};"
            "border-radius: 5px;"
            "padding: 5px;"
            "}"
            "QPushButton:hover {"
            f"background-color: {tema['hover']};"
            "}"
            "QSlider::groove:horizontal {"
            f"background-color: {tema['superficie']};"
            "height: 8px;"
            "}"
            "QSlider::handle:horizontal {"
            f"background-color: {tema['destaque']};"
            "width: 16px;"
            "margin: -4px 0;"
            "border-radius: 8px;"
            "}"
            "QSlider::sub-page:horizontal {"
            f"background-color: {tema['destaque']};"
            "}"
        )
        self.pagina_gravacao.titulo.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {tema['texto']};"
        )
        self.pagina_gravacao.botao_recorte.aplicar_tema(tema, "recorte")
        self.pagina_gravacao.botao_tela_cheia.aplicar_tema(tema, "tela")
        for opcao in self.opcoes_tema:
            selecionado = opcao.chave == self.tema_atual
            opcao.setChecked(selecionado)
            opcao.atualizar_selecao(tema, selecionado)

    def escolher_pasta_videos(self):

        pasta = QFileDialog.getExistingDirectory(
            self,
            "Escolher pasta para salvar os vídeos",
            str(self.pasta_videos),
        )
        if not pasta:
            return

        self.pasta_videos = Path(pasta)
        self.gravador.pasta_saida = self.pasta_videos
        self.configuracoes.setValue("pasta_videos", str(self.pasta_videos))
        self.rotulo_pasta_videos.setText(str(self.pasta_videos))

    def abrir_video_gravado(self):

        arquivo = self.arquivo_saida
        if arquivo is None or not arquivo.is_file():
            arquivo = self.localizar_ultima_gravacao()

        if arquivo is None:
            QMessageBox.information(
                self,
                "Vídeo não encontrado",
                "Nenhuma gravação foi encontrada. Grave um vídeo antes de abrir esta página.",
            )
            return

        self.arquivo_saida = arquivo
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(str(arquivo)))
        self.Stack.setCurrentIndex(1)

    def localizar_ultima_gravacao(self):

        pasta_projeto = Path(__file__).resolve().parent
        padrao = re.compile(r"gravacao_\d{8}_\d{6}_\d+\.mp4$")
        pastas = {self.pasta_videos, pasta_projeto}
        gravacoes = {
            arquivo
            for pasta in pastas
            for arquivo in pasta.glob("gravacao_*.mp4")
            if padrao.fullmatch(arquivo.name) and arquivo.is_file()
        }
        return max(
            gravacoes,
            key=lambda arquivo: arquivo.stat().st_mtime,
            default=None,
        )

    def liberar_video(self):

        self.player.stop()
        self.player.setSource(QUrl())
        QCoreApplication.processEvents()

    def salvar_gravacao(self):

        arquivo = self.arquivo_saida
        if arquivo is None or not arquivo.is_file():
            QMessageBox.warning(
                self,
                "Gravação não encontrada",
                "Não foi possível localizar a gravação para salvar.",
            )
            return

        self.liberar_video()
        self.arquivo_saida = None
        QMessageBox.information(
            self,
            "Gravação salva",
            f"O vídeo foi mantido em:\n{arquivo}",
        )
        self.Stack.setCurrentIndex(0)

    def descartar_gravacao(self):

        arquivo = self.arquivo_saida
        if arquivo is None:
            QMessageBox.warning(
                self,
                "Gravação não encontrada",
                "Não há uma gravação selecionada para descartar.",
            )
            return

        self.liberar_video()
        try:
            arquivo.unlink(missing_ok=True)
        except OSError as erro:
            self.player.setSource(QUrl.fromLocalFile(str(arquivo)))
            QMessageBox.critical(
                self,
                "Erro ao descartar gravação",
                f"Não foi possível excluir o vídeo:\n{erro}",
            )
            return

        self.arquivo_saida = None
        if self.gravador.arquivo_saida == arquivo:
            self.gravador.arquivo_saida = None
        self.Stack.setCurrentIndex(0)

    def atualizar_duracao(self, duracao):

        self.slider.setMaximum(duracao)
        self.tempoTotal = self.formatar_tempo(duracao)
        self.atualizar_rotulo_tempo()

    def atualizar_posicao(self, posicao):

        self.slider.setValue(posicao)
        self.tempoAtual = self.formatar_tempo(posicao)
        self.atualizar_rotulo_tempo()

    @staticmethod
    def formatar_tempo(milissegundos):

        segundos = max(0, milissegundos // 1000)
        horas, restante = divmod(segundos, 3600)
        minutos, segundos = divmod(restante, 60)
        return f"{horas:02}:{minutos:02}:{segundos:02}"

    def atualizar_rotulo_tempo(self):

        self.temporizador.setText(
            f"{self.tempoAtual} / {self.tempoTotal}"
        )

    def mostrar_erro_reproducao(self, erro, mensagem):

        QMessageBox.critical(
            self,
            "Erro ao reproduzir vídeo",
            mensagem or f"O player não conseguiu abrir este arquivo ({erro}).",
        )


    def SelecionarRecorte( self ):

        self.hide()

        seletor = SeletorRegiao()
        resultado = seletor.exec()

        if resultado == QDialog.DialogCode.Accepted:
            self.iniciar_gravacao(seletor.regiao)
        else:
            self.show()
            self.activateWindow()
            print("Seleção cancelada.")

    def selecionar_tela_cheia(self):

        telas = QGuiApplication.screens()
        if not telas:
            QMessageBox.critical(
                self,
                "Nenhuma tela encontrada",
                "Não foi possível localizar uma tela para gravar.",
            )
            return

        if len(telas) == 1:
            tela = telas[0]
            self.iniciar_gravacao(
                self._regiao_da_tela(tela.geometry()),
                tela.availableGeometry(),
            )
            return

        opcoes = [
            f"Tela {indice + 1} — {tela.name()} "
            f"({tela.geometry().width()} x {tela.geometry().height()})"
            for indice, tela in enumerate(telas)
        ]
        opcao_todas = "Todas as telas"
        opcoes.append(opcao_todas)

        escolha, confirmou = QInputDialog.getItem(
            self,
            "Escolher tela",
            "Qual tela deseja gravar?",
            opcoes,
            0,
            False,
        )
        if not confirmou:
            return

        if escolha == opcao_todas:
            geometria = telas[0].geometry()
            for tela in telas[1:]:
                geometria = geometria.united(tela.geometry())
            area_controle = QGuiApplication.primaryScreen().availableGeometry()
        else:
            indice = opcoes.index(escolha)
            tela = telas[indice]
            geometria = tela.geometry()
            area_controle = tela.availableGeometry()

        self.iniciar_gravacao(
            self._regiao_da_tela(geometria),
            area_controle,
        )

    @staticmethod
    def _regiao_da_tela(geometria):

        return (
            geometria.x(),
            geometria.y(),
            geometria.width(),
            geometria.height(),
        )

    def iniciar_gravacao(self, regiao=None, geometria_controle=None):

        if regiao is None:
            tela_controle = QGuiApplication.primaryScreen()
        else:
            tela_controle = QGuiApplication.screenAt(
                QPoint(regiao[0], regiao[1])
            )
            if tela_controle is None:
                tela_controle = QGuiApplication.primaryScreen()

        if geometria_controle is None and tela_controle is not None:
            geometria_controle = tela_controle.availableGeometry()

        self.hide()
        try:
            self.gravador.iniciar(regiao)
        except (OSError, RuntimeError, ValueError) as erro:
            self.show()
            self.activateWindow()
            QMessageBox.critical(
                self,
                "Erro ao iniciar gravação",
                str(erro),
            )
            return

        self.janela_gravacao = JanelaGravacao(
            self.parar_gravacao, self, geometria_controle
        )
        self.janela_gravacao.iniciar()

    def parar_gravacao(self):

        if self.gravador.processo is None:
            return

        gravacao_concluida = False
        try:
            self.gravador.parar()
        except (OSError, RuntimeError) as erro:
            QMessageBox.critical(
                self,
                "Erro ao concluir gravação",
                str(erro),
            )
        else:
            gravacao_concluida = True

        finally:
            if self.janela_gravacao is not None:
                self.janela_gravacao.finalizar()
                self.janela_gravacao = None
            self.show()
            self.activateWindow()

        if gravacao_concluida:
            arquivo = self.gravador.arquivo_saida
            if arquivo is None or not arquivo.is_file():
                QMessageBox.critical(
                    self,
                    "Gravação não encontrada",
                    "A gravação foi encerrada, mas o arquivo de vídeo não foi encontrado.",
                )
                return

            self.arquivo_saida = arquivo
            self.player.stop()
            self.player.setSource(QUrl.fromLocalFile(str(arquivo)))
            self.Stack.setCurrentIndex(1)

    def alternarPlayPause(self):
        if (
            self.player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        ):
            self.player.pause()
        else:
            self.player.play()
