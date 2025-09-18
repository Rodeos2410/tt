Запуск проекта в Docker

Требования:
- Docker Desktop установлен и запущен

Сборка и запуск всех сервисов (backend + frontend):

PowerShell:
```powershell
cd "c:\Users\Родион\OneDrive\Рабочий стол\коды"
docker compose up --build
```

После старта:
- Frontend доступен по адресу http://localhost:5173
- Backend API — http://localhost:8000 (доступна документация: http://localhost:8000/docs)

Заметки:
- При разработке можно включать монтирование директорий вместо сборки (в `docker-compose.yml` backend уже смонтирован).
- Если Docker не установлен, используйте локальный запуск (см. предыдущие инструкции по `uvicorn` и `npm run dev`).
