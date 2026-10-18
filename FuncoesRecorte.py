from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QPainter, QCursor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QRubberBand
)

class SeletorRegiao(QDialog):

    def __init__(self):
    
        super().__init__()

        tela = QApplication.primaryScreen()
        self.setGeometry(tela.geometry())

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self.inicio = None
        self.regiao = None

        # O retângulo pertence à janela de seleção.
        self.rubber_band = QRubberBand(
            QRubberBand.Shape.Rectangle, self
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(
            self.rect(), QColor(0, 0, 0, 90)
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.inicio = event.position().toPoint()

            self.rubber_band.setGeometry(
                QRect(self.inicio, self.inicio)
            )
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.inicio is not None:
            atual = event.position().toPoint()

            self.rubber_band.setGeometry(
                QRect(self.inicio, atual).normalized()
            )

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.inicio is not None
        ):
            retangulo = self.rubber_band.geometry()

            if retangulo.width() >= 32 and retangulo.height() >= 32:
                origem = self.mapToGlobal(retangulo.topLeft())

                self.regiao = (
                    origem.x(),
                    origem.y(),
                    retangulo.width(),
                    retangulo.height(),
                )
                self.accept()
            else:
                self.rubber_band.hide()
                self.inicio = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.regiao = None
            self.reject()
