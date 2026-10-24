from PySide6.QtCore import Signal
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QLabel, QSlider


class ConcentraFuncoes:

    def __init__( self ):
        ...


class VideoWidgetInterativo(QVideoWidget):

    select = Signal()

    def mousePressEvent(self, event):

        self.select.emit()
        super().mousePressEvent(event)


class ConfigSlider(QSlider):

    def __init__(self, orientacao, parent=None):

        super().__init__(orientacao, parent)
        self.setMouseTracking(True)
        self.setMinimum(0)
        self.setMaximum(100000)

        self.inicio_recorte = None
        self.fim_recorte = None
        self.setFixedHeight(30)

        self.recortes = []
        self.inicio_temp = None

        self.caixaFlutuante = QLabel("00:00:00", self)
        self.caixaFlutuante.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 12px;
                background: #ccc;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #0078d7;
                width: 16px;
                height: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)
        self.caixaFlutuante.setVisible(False)

    def leaveEvent(self, _event):

        self.caixaFlutuante.setVisible(False)
