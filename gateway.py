"""
Kilo Gateway - OpenAI Compatible API Server
Based on https://docs.openclaw.ai/providers/kilocode

This is a wrapper for the Vercel-compatible API version.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from api.index import app, AVAILABLE_MODELS

if __name__ == "__main__":
    import uvicorn
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    KILO GATEWAY v1.0.0                       ║
║            OpenAI-Compatible API Gateway                     ║
╠═══════════════════════════════════════════════════════════════╣
║  Base URL: http://localhost:8000                             ║
║  API Key: demo-key (or set KILOCODE_API_KEY env var)          ║
║  Models: {len(AVAILABLE_MODELS):3d} available                        ║
║                                                               ║
║  Endpoints:                                                  ║
║    GET  /v1/models        - List available models            ║
║    POST /v1/chat/completions - Create chat completion        ║
║    GET  /docs             - Swagger UI                      ║
║                                                               ║
║  Example:                                                    ║
║    curl -X POST http://localhost:8000/v1/chat/completions \\  ║
║      -H "Authorization: Bearer demo-key" \\                   ║
║      -H "Content-Type: application/json" \\                   ║
║      -d '{{"model": "anthropic/claude-sonnet-4", "messages": [{{"role": "user", "content": "Hello"}}]}}'
╚═══════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)