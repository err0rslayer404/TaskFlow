# TaskFlow ko aaj Vercel par live karein

Is repository ko GitHub par push karke **do Vercel projects** banane hain: backend aur frontend.

## 1) PostgreSQL database banayein

Neon, Supabase, Railway ya kisi managed PostgreSQL provider par database banayein aur connection string copy karein. Production mein SQLite use na karein.

## 2) Backend deploy karein

1. Vercel → Add New → Project → GitHub repository import.
2. Project name: `taskflow-api`.
3. **Root Directory:** `backend`.
4. Environment Variables add karein:
   - `DATABASE_URL` = PostgreSQL connection string
   - `JWT_SECRET_KEY` = ek long random secret
   - `SECRET_KEY` = doosra long random secret
   - `FRONTEND_URL` = abhi `*` rakhein; frontend deploy hone ke baad exact URL set karein
5. Deploy karein.
6. Check: `https://YOUR-BACKEND.vercel.app/api/health` — JSON mein `status: healthy` aana chahiye.

Random secrets generate karne ke liye terminal mein do baar run karein:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 3) Frontend deploy karein

1. Same GitHub repository ko naya Vercel project bana kar import karein.
2. Project name: `taskflow-web`.
3. **Root Directory:** `frontend`.
4. Framework preset: **Vite**.
5. Build command: `npm run build`.
6. Output directory: `dist`.
7. Environment Variable:
   - `VITE_API_URL` = `https://YOUR-BACKEND.vercel.app/api`
8. Deploy karein.

## 4) CORS lock karein

Frontend URL milne ke baad backend project ke `FRONTEND_URL` ko `https://YOUR-FRONTEND.vercel.app` set karein aur backend redeploy karein.

## 5) Final smoke test

- Frontend open hota hai.
- Naya student account register hota hai.
- Login hota hai.
- Task create, complete aur delete hota hai.
- Smart Scheduler next task show karta hai.
- `/api/health` healthy response deta hai.

## Common fixes

- **Frontend says backend unreachable:** `VITE_API_URL` mein `/api` aur `https://` verify karein, phir frontend redeploy.
- **Database driver error:** ensure updated `requirements.txt` deployed hai.
- **CORS error:** backend ka `FRONTEND_URL` exact frontend origin ho; trailing slash na ho.
- **Database connection error:** provider ki pooled/serverless PostgreSQL URL try karein aur SSL requirement provider ke instructions ke according set karein.
