param(
    [switch]$InstallOnly,
    [switch]$CompileOnly,
    [string]$SourceExecutable
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$destination = Join-Path $env:ProgramFiles "Gravei"
$videosFolder = Join-Path $destination "Videos"

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
}

function Install-Gravei {
    param([string]$Executable)

    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
        throw "Executável compilado não encontrado: $Executable"
    }

    if (-not (Test-IsAdministrator)) {
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -InstallOnly -SourceExecutable `"$Executable`""
        $process = Start-Process `
            -FilePath "powershell.exe" `
            -ArgumentList $arguments `
            -Verb RunAs `
            -Wait `
            -PassThru
        if ($process.ExitCode -ne 0) {
            throw "A instalação elevada falhou com código $($process.ExitCode)."
        }
        return
    }

    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    New-Item -ItemType Directory -Path $videosFolder -Force | Out-Null
    Copy-Item -LiteralPath $Executable `
        -Destination (Join-Path $destination "Gravei.exe") `
        -Force

    & icacls.exe $videosFolder /grant "*S-1-5-32-545:(OI)(CI)M" /T /C
    if ($LASTEXITCODE -ne 0) {
        throw "Não foi possível liberar a gravação na pasta $videosFolder."
    }

    Write-Host "Aplicativo instalado em: $destination"
    Write-Host "Vídeos serão salvos em: $videosFolder"
}

if ($InstallOnly) {
    if (-not (Test-IsAdministrator)) {
        throw "O modo de instalação precisa ser executado como administrador."
    }
    Install-Gravei -Executable $SourceExecutable
    exit 0
}

$venv = Join-Path $projectRoot "venv"
$python = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        & $pythonCommand.Source -m venv $venv
    }
    else {
        $pythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
        if (-not $pythonLauncher) {
            throw "Python não encontrado. Instale Python para Windows e tente novamente."
        }
        & $pythonLauncher.Source -3 -m venv $venv
    }

    if ($LASTEXITCODE -ne 0) {
        throw "Não foi possível criar o ambiente virtual em $venv."
    }

    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw "O ambiente virtual foi criado sem o interpretador esperado: $python"
    }
}

Write-Host "Instalando as dependências listadas em requirements.txt..."
& $python -m pip install -r (Join-Path $projectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao instalar as dependências de compilação."
}

$ffmpegCommand = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
if (-not $ffmpegCommand) {
    $ffmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue
}
if (-not $ffmpegCommand -or $ffmpegCommand.CommandType -ne "Application") {
    throw "FFmpeg não encontrado no PATH. Instale o FFmpeg e tente compilar novamente."
}
$ffmpegPath = $ffmpegCommand.Source
& $ffmpegPath -version *> $null
if ($LASTEXITCODE -ne 0) {
    throw "O executável FFmpeg encontrado não pôde ser iniciado: $ffmpegPath"
}

$entryPoint = Join-Path $projectRoot "main.py"
$ffmpegArgument = "$ffmpegPath;."
& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --noupx `
    --onefile `
    --windowed `
    --name Gravei `
    --collect-all pyaudiowpatch `
    --add-binary $ffmpegArgument `
    $entryPoint
if ($LASTEXITCODE -ne 0) {
    throw "A compilação do executável falhou."
}

$executable = Join-Path $projectRoot "dist\Gravei.exe"
if ($CompileOnly) {
    Write-Host "Executável compilado em: $executable"
    exit 0
}

Install-Gravei -Executable $executable
