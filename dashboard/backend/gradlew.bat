@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
set "GRADLE_VERSION=%SPECYN_GRADLE_VERSION%"
if "%GRADLE_VERSION%"=="" set "GRADLE_VERSION=8.14"
set "LOCAL_GRADLE=%REPO_ROOT%\.specyn\tools\gradle-%GRADLE_VERSION%\bin\gradle.bat"

if exist "%LOCAL_GRADLE%" (
  call "%LOCAL_GRADLE%" %*
  exit /b %ERRORLEVEL%
)

where gradle >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  gradle %*
  exit /b %ERRORLEVEL%
)

where docker >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  docker run --rm -v "%CD%":/home/gradle/project -w /home/gradle/project gradle:8.14.0-jdk21 gradle %*
  exit /b %ERRORLEVEL%
)

echo repo-local Gradle(.specyn\tools), 시스템 gradle, 또는 docker가 필요합니다. 먼저 루트에서 make bootstrap 또는 python scripts/specyn_tasks.py bootstrap 을 실행해 로컬 Gradle 준비를 시도하세요. 1>&2
exit /b 1
