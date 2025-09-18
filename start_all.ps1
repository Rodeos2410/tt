Start-Process powershell -ArgumentList 'cd "backend"; uvicorn main:app --reload'
Start-Process powershell -ArgumentList 'cd "frontend"; npm run dev'
