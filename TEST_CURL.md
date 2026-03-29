# Kilo Gateway - Test cURL Commands

**Base URL:** `https://kilogateway.vercel.app/v1`

---

## 1. Health Check

```bash
curl https://kilogateway.vercel.app/health
```

---

## 2. List All Models

```bash
curl https://kilogateway.vercel.app/v1/models \
  -H "Authorization: Bearer demo-key"
```

---

## 3. MiniMax M2.5 Free

```bash
curl https://kilogateway.vercel.app/v1/chat/completions \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax/minimax-m2.5:free",
    "messages": [
      {"role": "user", "content": "Halo, siapa kamu?"}
    ],
    "max_tokens": 200
  }'
```

---

## 4. Xiaomi MiMo V2 Pro Free

```bash
curl https://kilogateway.vercel.app/v1/chat/completions \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "xiaomi/mimo-v2-pro:free",
    "messages": [
      {"role": "user", "content": "Halo, siapa kamu?"}
    ],
    "max_tokens": 200
  }'
```

---

## 5. Streaming Response (MiniMax M2.5 Free)

```bash
curl https://kilogateway.vercel.app/v1/chat/completions \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax/minimax-m2.5:free",
    "messages": [
      {"role": "user", "content": "Ceritakan tentang AI dalam 3 kalimat"}
    ],
    "max_tokens": 200,
    "stream": true
  }'
```

---

## 6. Streaming Response (MiMo V2 Pro Free)

```bash
curl https://kilogateway.vercel.app/v1/chat/completions \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "xiaomi/mimo-v2-pro:free",
    "messages": [
      {"role": "user", "content": "Ceritakan tentang AI dalam 3 kalimat"}
    ],
    "max_tokens": 200,
    "stream": true
  }'
```
