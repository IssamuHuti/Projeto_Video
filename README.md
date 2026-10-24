# Gravei

Aplicativo desktop para Windows que permite gravar a tela e o áudio do computador, visualizar o resultado e decidir se deseja salvar ou descartar a gravação.

O **Gravei** foi desenvolvido em Python com PySide6, utilizando FFmpeg para a captura de vídeo e PyAudioWPatch para a captura do áudio de saída do Windows.

## Funcionalidades

- **Gravação de tela:** capture a tela inteira, uma região selecionada ou um monitor específico.
- **Suporte a múltiplos monitores:** escolha uma tela específica ou grave todas as telas.
- **Captura de áudio:** grave o áudio de saída do computador utilizando WASAPI Loopback.
- **Revisão da gravação:** reproduza o vídeo antes de decidir o que fazer com ele.
- **Controles de reprodução:** ajuste o volume e avance ou retroceda no vídeo.
- **Gerenciamento de gravações:** salve o resultado ou descarte arquivos que não deseja manter.
- **Personalização:** escolha o tema da interface e a pasta de destino das gravações.

## Tecnologias utilizadas

| Tecnologia | Finalidade |
| --- | --- |
| Python 3.13 | Linguagem principal |
| PySide6 | Interface gráfica |
| FFmpeg | Captura, processamento e combinação de áudio e vídeo |
| PyAudioWPatch | Captura do áudio de saída do Windows |
| PyInstaller | Geração do executável para Windows |
| PowerShell | Automação da compilação e instalação |

## Requisitos

Para executar o projeto pelo código-fonte, você precisará de:

- Windows 10 ou posterior.
- Python 3.13 de 64 bits, recomendado.
- FFmpeg disponível no `PATH`.
- Dependências Python listadas em `requirements.txt`.

O FFmpeg deve incluir suporte a `gdigrab`, codificação H.264 com `libx264` e filtro `loudnorm`.

Download: [FFmpeg — site oficial](https://ffmpeg.org/download.html).

Após instalar o FFmpeg, abra um novo terminal do PowerShell e execute:

```powershell
ffmpeg -version
```

Se o comando exibir as informações da versão, o executável está acessível pelo `PATH`.

## Instalação e execução

### 1. Obtenha o código-fonte

Clone o repositório ou baixe o projeto e abra o PowerShell na pasta raiz.

### 2. Crie o ambiente virtual

```powershell
py -3.13 -m venv venv
```

### 3. Ative o ambiente virtual

```powershell
.\venv\Scripts\Activate.ps1
```

Se o PowerShell impedir a ativação devido à política de execução, você poderá utilizar diretamente o interpretador do ambiente virtual, conforme mostrado na seção alternativa abaixo.

### 4. Instale as dependências

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` contém as dependências Python necessárias para executar o aplicativo e gerar o executável.

### 5. Execute o aplicativo

```powershell
python main.py
```

### Alternativa: executar sem ativar o ambiente virtual

Se não conseguir ativar o ambiente virtual, execute os comandos abaixo na pasta raiz do projeto:

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe main.py
```

## Compilação e instalação no Windows

O projeto inclui um script PowerShell para automatizar a preparação do ambiente, a instalação das dependências e a compilação do executável.

### Gerar somente o executável

Na pasta raiz do projeto, execute:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -CompileOnly
```

Após a compilação, o executável será gerado em:

```text
dist\Gravei.exe
```

### Compilar e instalar

Para compilar e instalar o aplicativo no diretório padrão, execute:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

A instalação utiliza o diretório:

```text
C:\Program Files\Gravei\
```

O instalador cria o executável `Gravei.exe` e a pasta `Videos`, configurada para permitir que usuários comuns gravem arquivos nela.

**Observações:**

- A instalação em `C:\Program Files` pode exigir autorização de administrador do Windows.
- O executável gerado inclui o FFmpeg utilizado na compilação.
- Ao distribuir o aplicativo, verifique e cumpra os termos de licença do FFmpeg e das demais dependências utilizadas.

### Compilação pelo VS Code

Também é possível iniciar a compilação pelo VS Code:

1. Abra a paleta de comandos com `Ctrl + Shift + P`.
2. Selecione **Tasks: Run Task**.
3. Escolha **Compilar e instalar Gravei**.

## Onde as gravações são armazenadas?

O diretório padrão depende da forma de execução:

- **Código-fonte:** pasta `Gravei` na Área de Trabalho.
- **Executável instalado:** pasta `Videos` ao lado do executável, dentro do diretório de instalação padrão.

Você também pode alterar a pasta de destino nas configurações do aplicativo.

## Estrutura do projeto

```text
Gravei/
├── main.py
├── TelaPrincipal.py
├── Gravar.py
├── FuncoesRecorte.py
├── ConcentraFuncoes.py
├── Layouts.py
├── requirements.txt
├── scripts/
│   └── build_windows.ps1
└── ...
```

### Principais arquivos

- `main.py`: inicializa a aplicação Qt e abre a janela principal.
- `TelaPrincipal.py`: coordena as telas, o fluxo de gravação, a reprodução e as configurações.
- `Gravar.py`: controla a captura da tela e do áudio, o processamento das faixas e a janela de gravação.
- `FuncoesRecorte.py`: implementa a seleção da região da tela que será gravada.
- `ConcentraFuncoes.py`: reúne controles de vídeo e a barra de progresso.
- `Layouts.py`: reúne componentes visuais, botões e temas.
- `requirements.txt`: lista as dependências Python.
- `scripts/build_windows.ps1`: automatiza a compilação e, opcionalmente, a instalação do executável.

## Controle de versão

O `.gitignore` exclui arquivos que não precisam ser versionados, incluindo:

- Ambientes virtuais e caches do Python.
- Arquivos temporários.
- Gravações locais.
- Arquivos e diretórios gerados durante a compilação.

O repositório mantém o código-fonte, a documentação, as dependências e os arquivos compartilhados de configuração necessários ao desenvolvimento.

## Licenciamento

Antes de distribuir o aplicativo, verifique as condições de licenciamento do FFmpeg e das bibliotecas utilizadas.

A licença do próprio projeto deve ser definida separadamente, de acordo com a forma como você pretende disponibilizar e permitir o uso do código-fonte.
