# Kilo Gateway - OpenAI Compatible API Specification

> **Version:** 1.0.0  
> **Base URL:** `https://api.kilo.ai/api/gateway/`  
> **Authentication:** Bearer Token (API Key)

## Overview

Kilo Gateway provides a unified API that routes requests to multiple AI providers behind a single endpoint and API key. It is designed as a **drop-in replacement for the OpenAI API**, meaning most OpenAI SDKs work by simply switching the base URL.

---

## Authentication

### API Key

Include your API key in the `Authorization` header:

```bash
Authorization: Bearer <your-kilocode-api-key>
```

### Environment Variable

```bash
export KILOCODE_API_KEY="<your-kilocode-api-key>"
```

---

## Supported Endpoints

### Chat Completions

**Endpoint:** `POST /v1/chat/completions`

The primary endpoint for generating conversational responses.

#### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | ✅ | Model identifier (see Model Naming) |
| `messages` | array | ✅ | Array of message objects |
| `temperature` | number | ❌ | Sampling temperature (0.0 to 2.0) |
| `max_tokens` | integer | ❌ | Maximum tokens in response |
| `top_p` | number | ❌ | Nucleus sampling (0.0 to 1.0) |
| `stream` | boolean | ❌ | Enable streaming (Server-Sent Events) |
| `stop` | string/array | ❌ | Stop sequences |
| `presence_penalty` | number | ❌ | -2.0 to 2.0 |
| `frequency_penalty` | number | ❌ | -2.0 to 2.0 |
| `user` | string | ❌ | User identifier for tracking |
| `tools` | array | ❌ | Function calling / tool definitions |
| `tool_choice` | string/object | ❌ | Control tool selection |
| `response_format` | object | ❌ | JSON mode (provider-specific) |

#### Message Format

```json
{
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Hello!" },
    { "role": "assistant", "content": "How can I help you?" }
  ]
}
```

#### Response Format

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699000000,
  "model": "kilocode/kilo/auto",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  },
  "provider": "anthropic",
  "latency_ms": 850
}
```

#### Additional Response Fields

Kilo Gateway adds observability fields:

| Field | Type | Description |
|-------|------|-------------|
| `provider` | string | Which provider handled the request |
| `latency_ms` | integer | Request latency in milliseconds |
| `routing_mode` | string | Routing mode used (if auto-routed) |
| `x_request_id` | string | Kilo Gateway request ID |

---

### List Models

**Endpoint:** `GET /v1/models`

Returns a list of available models for your account.

#### Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "kilocode/kilo/auto",
      "object": "model",
      "created": 1699000000,
      "owned_by": "kilocode"
    },
    {
      "id": "kilocode/anthropic/claude-sonnet-4",
      "object": "model",
      "created": 1699000000,
      "owned_by": "anthropic"
    }
  ]
}
```

---

## Model Naming Convention

### Standard Format

All models use the prefix `kilocode/`:

```
kilocode/{provider}/{model}
```

### Examples

| Model ID | Provider | Description |
|----------|----------|-------------|
| `kilocode/kilo/auto` | kilocode | Smart routing (default) |
| `kilocode/anthropic/claude-sonnet-4` | Anthropic | Claude Sonnet 4 |
| `kilocode/anthropic/claude-opus-4` | Anthropic | Claude Opus 4 |
| `kilocode/openai/gpt-5` | OpenAI | GPT-5 |
| `kilocode/openai/gpt-4o` | OpenAI | GPT-4o |
| `kilocode/google/gemini-3-pro` | Google | Gemini 3 Pro |
| `kilocode/deepseek/deepseek-chat` | DeepSeek | DeepSeek Chat |

---

## Auto-Routing Modes

Instead of specifying a fixed model, use intelligent routing:

### Available Modes

| Mode | Description |
|------|-------------|
| `kilocode/kilo/auto` | Smart routing - auto-selects best model (default) |
| `kilocode/kilo/quality` | Maximize quality (routes to Claude Opus) |
| `kilocode/kilo/speed` | Prioritize speed (routes to fastest available) |
| `kilocode/kilo/cost` | Minimize cost (routes to cheapest capable model) |
| `kilocode/kilo/balance` | Balance speed, cost, and quality |

### Smart Routing Behavior

The default `kilocode/kilo/auto` model automatically selects the best underlying model:

- **Planning, debugging, orchestration tasks** → route to Claude Opus
- **Code writing and exploration tasks** → route to Claude Sonnet
- **Simple classification/extraction** → route to cost-effective models

---

## Provider-Specific Prefixes

Explicitly route to specific providers:

| Prefix | Provider | Example Model |
|--------|----------|---------------|
| `kilocode/openai/` | OpenAI | `kilocode/openai/gpt-5` |
| `kilocode/anthropic/` | Anthropic | `kilocode/anthropic/claude-sonnet-4` |
| `kilocode/google/` | Google | `kilocode/google/gemini-3-pro` |
| `kilocode/deepseek/` | DeepSeek | `kilocode/deepseek/deepseek-chat` |
| `kilocode/mistral/` | Mistral | `kilocode/mistral/mistral-large` |

---

## Usage Examples

### cURL

```bash
curl https://api.kilo.ai/api/gateway/v1/chat/completions \
  -H "Authorization: Bearer $KILOCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kilocode/kilo/auto",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### Python

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("KILOCODE_API_KEY"),
    base_url="https://api.kilo.ai/api/gateway/v1"
)

response = client.chat.completions.create(
    model="kilocode/kilo/auto",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in one paragraph."}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
print(f"Provider: {response.provider}")
```

### Node.js / TypeScript

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.KILOCODE_API_KEY,
  baseURL: 'https://api.kilo.ai/api/gateway/v1'
});

const response = await client.chat.completions.create({
  model: 'kilocode/kilo/auto',
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Hello!' }
  ],
  temperature: 0.7,
  max_tokens: 1000
});

console.log(response.choices[0].message.content);
```

---

## Streaming

Enable streaming for real-time responses using Server-Sent Events (SSE):

### Python

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("KILOCODE_API_KEY"),
    base_url="https://api.kilo.ai/api/gateway/v1"
)

stream = client.chat.completions.create(
    model="kilocode/kilo/auto",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    content = chunk.choices[0]?.delta.content or ""
    print(content, end="", flush=True)
```

### Node.js

```typescript
const stream = await client.chat.completions.create({
  model: 'kilocode/kilo/auto',
  messages: [{ role: 'user', content: 'Tell me a story' }],
  stream: true
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content || '';
  process.stdout.write(content);
}
```

---

## Function Calling / Tools

### Define Tools

```typescript
const tools = [{
  type: 'function',
  function: {
    name: 'get_weather',
    description: 'Get current weather for a location',
    parameters: {
      type: 'object',
      properties: {
        location: { type: 'string', description: 'City name' }
      },
      required: ['location']
    }
  }
}];

const response = await client.chat.completions.create({
  model: 'kilocode/kilo/auto',
  messages: [{ role: 'user', content: 'What is the weather in NYC?' }],
  tools
});
```

---

## Configuration

### OpenClaw Config

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" },
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" }
    }
  }
}
```

### CLI Setup

```bash
openclaw onboard --kilocode-api-key <key>
```

---

## Provider Compatibility Notes

| Feature | OpenAI | Anthropic | Google | DeepSeek |
|---------|--------|-----------|--------|----------|
| Streaming | ✅ | ✅ | ✅ | ✅ |
| Function Calling | ✅ | ✅ | ✅ | ✅ |
| JSON Mode | ✅ | ⚠️ | ⚠️ | ✅ |
| System Prompts | ✅ | ✅ | ✅ | ✅ |
| Token Counting | Standard | Varies | Varies | Varies |

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "authentication_error",
    "code": 401
  }
}
```

### Error Codes

| Code | Type | Description |
|------|------|-------------|
| 400 | `invalid_request_error` | Malformed request |
| 401 | `authentication_error` | Invalid or missing API key |
| 403 | `permission_error` | Access denied |
| 404 | `not_found_error` | Model not found |
| 429 | `rate_limit_error` | Rate limit exceeded |
| 500 | `server_error` | Internal server error |
| 503 | `service_unavailable` | Provider unavailable |

---

## Rate Limits

- Rate limits apply per API key across all models
- Limits vary by account tier
- Check `X-RateLimit-*` headers for limit details

---

## Metadata Tracking

Add custom metadata for analytics using the `user` field:

```json
{
  "model": "kilocode/kilo/auto",
  "messages": [...],
  "user": JSON.stringify({
    "user_id": "12345",
    "task": "code_review",
    "environment": "production"
  })
}
```

---

## Changelog

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-03-29 | Initial specification |

---

## See Also

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Model Providers](https://docs.openclaw.ai/concepts/model-providers)
- [API Keys Management](https://app.kilo.ai)