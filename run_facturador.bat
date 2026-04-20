@echo off
REM ================================================================
REM Facturador AFIP - Script de ejecución con opciones de pausas
REM ================================================================

chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║        FACTURADOR AUTOMÁTICO AFIP - SELECTOR DE MODO       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Seleccione el modo de ejecución:
echo.
echo   [1] RÁPIDO - Sin pausas (testing)
echo        └─ Ejecuta todas las facturas lo más rápido posible
echo.
echo   [2] ALEATORIO - Pausas aleatorias 30-60s entre facturas ⭐
echo        └─ Recomendado: Parece más humano, evita detección
echo.
echo   [3] HUMANIZADO - Pausas largas 60-120s entre facturas
echo        └─ Ultra realista: Muy lento pero imposible detectar
echo.
echo ════════════════════════════════════════════════════════════════
echo.

set /p opcion="Ingrese su opción (1, 2 o 3): "

if "%opcion%"=="1" (
    echo.
    echo ⚡ Iniciando en modo RÁPIDO...
    echo.
    python main.py --ahora --modo 1
    goto fin
) else if "%opcion%"=="2" (
    echo.
    echo 🎲 Iniciando en modo ALEATORIO...
    echo.
    python main.py --ahora --modo 2
    goto fin
) else if "%opcion%"=="3" (
    echo.
    echo 🤖 Iniciando en modo HUMANIZADO...
    echo.
    python main.py --ahora --modo 3
    goto fin
) else (
    echo.
    echo ❌ Opción inválida. Por favor ingrese 1, 2 o 3.
    echo.
    timeout /t 2
    goto salida
)

:fin
echo.
echo ═══════════════════════════════════════════════════════════════
echo Ejecución completada.
echo.
pause

:salida
exit /b
