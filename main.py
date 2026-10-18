import sys
from PySide6.QtWidgets import QApplication
from TelaPrincipal import TelaPrincipal
from ConcentraFuncoes import ConcentraFuncoes

app     = QApplication( sys.argv )
funcoes = ConcentraFuncoes()

app.setStyle( "Fusion" )

janela = TelaPrincipal( funcoes ) 
janela.show()

sys.exit( app.exec() )

