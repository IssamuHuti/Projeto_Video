import os
import shutil
import subprocess
import threading
import pyaudiowpatch as pyaudio
import wave
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import QElapsedTimer, Qt, QTimer


class GravadorTela:

    def __init__(self):
        
        self.processo = None
        self.arquivo_saida = None
        self.arquivo_video_temp = None
        self.arquivo_audio_temp = None
        self.gravador_audio = None

    @staticmethod
    def localizar_ffmpeg():

        ffmpeg_no_path = shutil.which("ffmpeg")
        if ffmpeg_no_path:
            return ffmpeg_no_path

        caminhos = [
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/ffmpeg/bin/ffmpeg"),
            Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe"),
        ]

        for caminho in caminhos:
            if caminho.exists():
                return str(caminho)

        for pasta in os.environ.get("PATH", "").split(os.pathsep):
            if not pasta:
                continue
            candidato = Path(pasta) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if candidato.exists():
                return str(candidato)

        return None

    def iniciar(self, regiao=None):
        """
        regiao: (x, y, largura, altura)
        Se None, grava a tela principal inteira.
        """

        if self.processo is not None:
            raise RuntimeError("Já existe uma gravação em andamento.")

        if regiao is None:
            # Captura o monitor principal inteiro.
            tela = QApplication.primaryScreen()
            geometria = tela.geometry()

            x = geometria.x()
            y = geometria.y()
            largura = geometria.width()
            altura = geometria.height()

        else:
            x, y, largura, altura = regiao

        # H.264 com yuv420p requer dimensões pares.
        largura -= largura % 2
        altura -= altura % 2

        if largura < 32 or altura < 32:
            raise ValueError("A região selecionada é muito pequena.")

        nome = datetime.now().strftime(
            "gravacao_%Y%m%d_%H%M%S_%f.mp4"
        )
        pasta_projeto = Path(__file__).resolve().parent
        pasta_projeto.mkdir(parents=True, exist_ok=True)
        self.arquivo_saida = pasta_projeto / nome
        self.arquivo_video_temp = self.arquivo_saida.with_name(
            f"{self.arquivo_saida.stem}_video.mp4"
        )
        self.arquivo_audio_temp = self.arquivo_saida.with_name(
            f"{self.arquivo_saida.stem}_audio.wav"
        )

        ffmpeg_bin = self.localizar_ffmpeg()
        if ffmpeg_bin is None:
            raise FileNotFoundError(
                "FFmpeg não foi encontrado. Instale o FFmpeg e adicione a pasta 'bin' ao PATH."
            )

        comando = [
            ffmpeg_bin,
            "-y",
            "-f", "gdigrab",
            "-framerate", "30",
            "-offset_x", str(x),
            "-offset_y", str(y),
            "-video_size", f"{largura}x{altura}",
            "-i", "desktop",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            str(self.arquivo_video_temp),
        ]

        self.processo = subprocess.Popen(
            comando,
            stdin=subprocess.PIPE,
            cwd=str(pasta_projeto),
        )

        self.gravador_audio = GravadorAudio(self.arquivo_audio_temp)
        try:
            self.gravador_audio.iniciar()
        except RuntimeError:
            processo = self.processo
            try:
                if processo.poll() is None:
                    try:
                        processo.communicate(input=b"q\n", timeout=15)
                    except subprocess.TimeoutExpired:
                        processo.kill()
                        processo.communicate()
            finally:
                self.processo = None
                self.gravador_audio = None
            raise

        print("Gravação iniciada:", self.arquivo_saida)

    def parar(self):

        if self.processo is None:
            print("Não existe gravação em andamento.")
            return

        processo = self.processo
        erro_video = None

        try:
            if processo.poll() is None:
                try:
                    processo.communicate(input=b"q\n", timeout=15)
                except subprocess.TimeoutExpired:
                    processo.kill()
                    processo.communicate()
                    raise RuntimeError(
                        "O FFmpeg não encerrou a gravação no tempo esperado."
                    )

            if processo.returncode != 0:
                raise RuntimeError(
                    "O FFmpeg encerrou com erro. "
                    "Verifique a instalação e os argumentos."
                )

            print("Gravação finalizada:", self.arquivo_saida)

        except (OSError, RuntimeError) as erro:
            erro_video = erro
        finally:
            self.processo = None

        gravador_audio = self.gravador_audio
        self.gravador_audio = None
        erro_audio = None
        if gravador_audio is not None:
            try:
                gravador_audio.parar()
            except RuntimeError as erro:
                erro_audio = erro

        if erro_video is not None or erro_audio is not None:
            detalhes = []
            if erro_video is not None:
                detalhes.append(f"vídeo: {erro_video}")
            if erro_audio is not None:
                detalhes.append(f"áudio: {erro_audio}")
            raise RuntimeError(
                "Não foi possível concluir a gravação ("
                + "; ".join(detalhes)
                + ")."
            ) from erro_video or erro_audio

        self._combinar_audio_video()

    def _combinar_audio_video(self):

        arquivo_saida = self.arquivo_saida
        arquivo_video_temp = self.arquivo_video_temp
        arquivo_audio_temp = self.arquivo_audio_temp
        if (
            arquivo_saida is None
            or arquivo_video_temp is None
            or arquivo_audio_temp is None
        ):
            raise RuntimeError(
                "Os arquivos de vídeo e áudio não estão disponíveis."
            )

        ffmpeg_bin = self.localizar_ffmpeg()
        if ffmpeg_bin is None:
            raise FileNotFoundError(
                "FFmpeg não foi encontrado para combinar áudio e vídeo."
            )

        arquivo_muxado = arquivo_saida.with_name(
            f"{arquivo_saida.stem}_final.mp4"
        )
        comando = [
            ffmpeg_bin,
            "-y",
            "-i", str(arquivo_video_temp),
            "-i", str(arquivo_audio_temp),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(arquivo_muxado),
        ]

        try:
            subprocess.run(
                comando,
                check=True,
                capture_output=True,
                text=True,
                cwd=str(arquivo_saida.parent),
            )
            arquivo_muxado.replace(arquivo_saida)
        except subprocess.CalledProcessError as erro:
            if arquivo_muxado.exists():
                arquivo_muxado.unlink()
            detalhe = erro.stderr.strip() if erro.stderr else str(erro)
            raise RuntimeError(
                f"Falha ao adicionar o áudio ao vídeo: {detalhe}"
            ) from erro

        arquivo_video_temp.unlink()
        arquivo_audio_temp.unlink()
        print("Gravação com áudio finalizada:", arquivo_saida)

class JanelaGravacao(QDialog):

    def __init__(self, ao_parar, parent=None):

        super().__init__(parent)
        self.ao_parar = ao_parar
        self.finalizando = False

        self.setWindowTitle("Gravação")
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(250, 90)

        self.rotulo_tempo = QLabel("Gravando: 00:00:00")
        self.botao_parar = QPushButton("Parar e concluir gravação")

        layout = QVBoxLayout(self)
        layout.addWidget(self.rotulo_tempo)
        layout.addWidget(self.botao_parar)

        self.relogio = QElapsedTimer()
        self.atualizador = QTimer(self)
        self.atualizador.setInterval(1000)
        self.atualizador.timeout.connect(self.atualizar_tempo)
        self.botao_parar.clicked.connect(self.ao_parar)

    def iniciar(self):

        self.relogio.start()
        self.atualizador.start()
        self.show()

    def atualizar_tempo(self):

        segundos = self.relogio.elapsed() // 1000
        horas, restante = divmod(segundos, 3600)
        minutos, segundos = divmod(restante, 60)
        self.rotulo_tempo.setText(
            f"Gravando: {horas:02}:{minutos:02}:{segundos:02}"
        )

    def finalizar(self):

        self.finalizando = True
        self.atualizador.stop()
        self.close()

    def closeEvent(self, event):

        if self.finalizando:
            event.accept()
        else:
            event.ignore()
            self.ao_parar()


class GravadorAudio:

    def __init__(self, arquivo_saida):

        self.arquivo_saida = Path(arquivo_saida)
        self.parar_evento = threading.Event()
        self.iniciado = threading.Event()
        self.erro = None
        self.thread = threading.Thread(
            target=self._gravar,
            daemon=True,
        )

    def iniciar(self):

        self.thread.start()

        if not self.iniciado.wait(timeout=10):
            self.parar_evento.set()
            raise RuntimeError(
                "Tempo esgotado ao iniciar a captura de áudio."
            )

        if self.erro is not None:
            raise RuntimeError(
                f"Erro ao iniciar áudio: {self.erro}"
            )

    def _gravar(self):

        try:
            with pyaudio.PyAudio() as audio:
                dispositivo = audio.get_default_wasapi_loopback()

                canais = int(dispositivo["maxInputChannels"])
                taxa = int(dispositivo["defaultSampleRate"])

                if canais < 1:
                    raise RuntimeError(
                        "O dispositivo não possui canais de entrada."
                    )

                with wave.open(
                    str(self.arquivo_saida), "wb"
                ) as arquivo:
                    arquivo.setnchannels(canais)
                    arquivo.setsampwidth(
                        audio.get_sample_size(pyaudio.paInt16)
                    )
                    arquivo.setframerate(taxa)

                    with audio.open(
                        format=pyaudio.paInt16,
                        channels=canais,
                        rate=taxa,
                        input=True,
                        input_device_index=dispositivo["index"],
                        frames_per_buffer=1024,
                    ) as stream:
                        self.iniciado.set()

                        while not self.parar_evento.is_set():
                            dados = stream.read(
                                1024,
                                exception_on_overflow=False,
                            )
                            arquivo.writeframesraw(dados)

        except Exception as erro:
            self.erro = erro
            self.iniciado.set()

    def parar(self):
        
        self.parar_evento.set()
        self.thread.join(timeout=10)

        if self.thread.is_alive():
            raise RuntimeError(
                "A captura de áudio não encerrou corretamente."
            )

        if self.erro is not None:
            raise RuntimeError(
                f"Erro durante a captura de áudio: {self.erro}"
            )
