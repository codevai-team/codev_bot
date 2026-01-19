@echo off
chcp 65001 >nul
echo ========================================
echo 📝 Добавление проекта в портфолио
echo ========================================
echo.
echo Выберите способ добавления:
echo.
echo 1. Интерактивный режим (вводите данные)
echo 2. Пример проекта Cosmonaft
echo 3. Выход
echo.
set /p choice="Ваш выбор (1-3): "

if "%choice%"=="1" (
    echo.
    echo Запуск интерактивного режима...
    python add_project_interactive.py
) else if "%choice%"=="2" (
    echo.
    echo Добавление примера проекта Cosmonaft...
    python example_add_cosmonaft.py
) else if "%choice%"=="3" (
    echo.
    echo Выход...
    exit /b 0
) else (
    echo.
    echo ❌ Неверный выбор!
    pause
    exit /b 1
)

echo.
pause
