from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


TEMAS_CORES = {
    "preto_cinza": {
        "nome": "Preto / Cinza",
        "fundo": "#171717",
        "texto": "#f2f2f2",
        "destaque": "#8a8a8a",
        "superficie": "#292929",
        "hover": "#3b3b3b",
    },
    "branco_preto": {
        "nome": "Branco / Preto",
        "fundo": "#f5f5f5",
        "texto": "#171717",
        "destaque": "#171717",
        "superficie": "#ffffff",
        "hover": "#e6e6e6",
    },
    "preto_azul": {
        "nome": "Preto / Azul",
        "fundo": "#111820",
        "texto": "#f2f6fa",
        "destaque": "#2196f3",
        "superficie": "#1c2935",
        "hover": "#263d52",
    },
    "preto_laranja": {
        "nome": "Preto / Laranja",
        "fundo": "#1c1712",
        "texto": "#fff6ed",
        "destaque": "#ff8c22",
        "superficie": "#302319",
        "hover": "#49321e",
    },
    "preto_amarelo": {
        "nome": "Preto / Amarelo",
        "fundo": "#1c1b12",
        "texto": "#fffde8",
        "destaque": "#f2d21b",
        "superficie": "#302d18",
        "hover": "#49421b",
    },
}


class OpcaoTema(QPushButton):

    selecionado = Signal(str)

    def __init__(self, chave, tema):

        super().__init__()
        self.chave = chave
        self.setCheckable(True)
        self.setAccessibleName(tema["nome"])
        self.setToolTip(tema["nome"])
        self.setFixedSize(48, 48)
        self.setIconSize(QSize(40, 40))
        self.setIcon(
            self._criar_amostra(tema["destaque"], tema["fundo"])
        )
        self.clicked.connect(self._emitir_selecao)

    @staticmethod
    def _criar_amostra(cor_secundaria, cor_principal):

        pixmap = QPixmap(44, 44)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        circulo = QPainterPath()
        circulo.addEllipse(2, 2, 40, 40)
        painter.setClipPath(circulo)
        painter.fillRect(2, 2, 20, 40, QColor(cor_secundaria))
        painter.fillRect(22, 2, 20, 40, QColor(cor_principal))
        painter.setClipping(False)
        painter.setPen(QPen(QColor("#777777"), 1))
        painter.drawEllipse(2, 2, 40, 40)
        painter.end()
        return QIcon(pixmap)

    def _emitir_selecao(self):

        self.selecionado.emit(self.chave)

    def atualizar_selecao(self, tema, selecionado):

        borda = tema["destaque"] if selecionado else "#777777"
        largura = 3 if selecionado else 1
        self.setStyleSheet(
            "QPushButton {"
            f"background-color: {tema['superficie']};"
            f"border: {largura}px solid {borda};"
            "border-radius: 24px;"
            "padding: 2px;"
            "}"
            "QPushButton:hover {"
            f"background-color: {tema['hover']};"
            "}"
        )


class BotaoQuadrado(QPushButton):

    def __init__(self, tipo_icone, texto="", descricao=""):

        super().__init__(texto)
        politica = QSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        politica.setHeightForWidth(True)
        self.setSizePolicy(politica)
        self.setMinimumSize(120, 120)
        self.setAccessibleName(descricao or texto.replace("\n", " "))
        self.setToolTip(descricao or texto.replace("\n", " "))
        self.setIconSize(QSize(48, 48))
        self.setIcon(self._criar_icone(tipo_icone, "#8a8a8a"))

    @staticmethod
    def _criar_icone(tipo, cor):

        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            QPen(
                QColor(cor),
                4,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        if tipo == "recorte":
            painter.drawLine(10, 24, 10, 10)
            painter.drawLine(10, 10, 24, 10)
            painter.drawLine(40, 10, 54, 10)
            painter.drawLine(54, 10, 54, 24)
            painter.drawLine(10, 40, 10, 54)
            painter.drawLine(10, 54, 24, 54)
            painter.drawLine(40, 54, 54, 54)
            painter.drawLine(54, 40, 54, 54)
        else:
            painter.drawRoundedRect(7, 10, 50, 36, 4, 4)
            painter.drawLine(32, 46, 32, 55)
            painter.drawLine(22, 56, 42, 56)
            painter.drawLine(13, 18, 23, 18)
            painter.drawLine(13, 18, 13, 27)
            painter.drawLine(51, 18, 41, 18)
            painter.drawLine(51, 18, 51, 27)

        painter.end()
        return QIcon(pixmap)

    def aplicar_tema(self, tema, tipo_icone):

        self.setIcon(self._criar_icone(tipo_icone, tema["destaque"]))
        self.setStyleSheet(
            "QPushButton {"
            f"background-color: {tema['superficie']};"
            f"color: {tema['texto']};"
            f"border: 2px solid {tema['destaque']};"
            "border-radius: 12px;"
            "padding: 12px;"
            "font-size: 18px;"
            "font-weight: bold;"
            "}"
            "QPushButton:hover {"
            f"background-color: {tema['hover']};"
            "}"
        )

    def hasHeightForWidth(self):

        return True

    def heightForWidth(self, width):

        return width


class PaginaGravacao(QWidget):

    def __init__(self):

        super().__init__()

        self.titulo = QLabel("Gravação")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.botao_recorte = BotaoQuadrado(
            "recorte",
            descricao="Recortar tela",
        )
        self.botao_tela_cheia = BotaoQuadrado(
            "tela",
            "Gravar tela\ncheia",
            "Gravar tela cheia",
        )

        self.layout_botao = QHBoxLayout()
        self.layout_botao.setSpacing(16)
        self.layout_botao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_botao.addWidget(self.botao_recorte)
        self.layout_botao.addWidget(self.botao_tela_cheia)

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(16, 12, 16, 16)
        self.layout_principal.setSpacing(12)
        self.layout_principal.addWidget(self.titulo)
        self.layout_principal.addLayout(self.layout_botao, 1)

    def resizeEvent(self, event):

        super().resizeEvent(event)
        margem = self.layout_principal.contentsMargins()
        espacamento_horizontal = self.layout_botao.spacing()
        largura_disponivel = (
            self.width()
            - margem.left()
            - margem.right()
            - espacamento_horizontal
        ) // 2
        altura_disponivel = (
            self.height()
            - margem.top()
            - margem.bottom()
            - self.titulo.sizeHint().height()
            - self.layout_principal.spacing() * 2
        )
        lado = max(120, min(largura_disponivel, altura_disponivel))
        tamanho = QSize(lado, lado)
        self.botao_recorte.setMaximumSize(tamanho)
        self.botao_tela_cheia.setMaximumSize(tamanho)
