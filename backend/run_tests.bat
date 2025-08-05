@echo off
setlocal

REM Configuración - CAMBIAR ESTOS VALORES
set PROJECT_KEY=your-project-key
set SONAR_HOST=http://sonarqube:9000

REM Solicitar token si no está configurado
if "%SONAR_TOKEN%"=="" (
    echo ⚠️  Variable SONAR_TOKEN no configurada
    set /p SONAR_TOKEN="Ingresa tu token de SonarQube: "
)

echo  Verificando que SonarQube esté ejecutándose...
docker-compose -f docker-compose.sonar.yml ps sonarqube

if %errorlevel% neq 0 (
    echo  Levantando SonarQube...
    docker-compose -f docker-compose.sonar.yml up -d sonarqube
    echo  Esperando que SonarQube esté listo... (esto puede tomar unos minutos)
    timeout /t 60 /nobreak
)

echo  Ejecutando tests con coverage...

REM Limpiar archivos anteriores
if exist coverage.xml del coverage.xml
if exist test-results.xml del test-results.xml
if exist htmlcov rmdir /s /q htmlcov

REM Ejecutar tests con coverage
coverage run --source=. manage.py test --keepdb
if %errorlevel% neq 0 (
    echo  Error en los tests
    exit /b 1
)

REM Generar reportes
echo  Generando reportes de coverage...
coverage report
coverage html
coverage xml

echo  Ejecutando análisis de SonarQube...
docker-compose -f docker-compose.sonar.yml run --rm sonar-scanner sonar-scanner -Dsonar.projectKey=%PROJECT_KEY% -Dsonar.sources=. -Dsonar.host.url=%SONAR_HOST% -Dsonar.login=%SONAR_TOKEN%

if %errorlevel% equ 0 (
    echo  Análisis completado exitosamente!
    echo  Ve los resultados en: http://localhost:9000
) else (
    echo Error en el análisis de SonarQube
)

endlocal