"""
Kilo Gateway - OpenAI Compatible API Server
Based on https://docs.openclaw.ai/providers/kilocode

This is a mock implementation for demonstration purposes.
Deployed on Vercel as serverless function.
"""

import os
import time
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Generator
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse, Response
from pydantic import BaseModel, Field
import httpx

# ============================================================================
# Configuration
# ============================================================================

API_KEY = os.getenv("KILOCODE_API_KEY", "demo-key")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kilo Gateway - API Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f1a; color: #fff; min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; color: #00d4ff; }
        .card { background: #1a1a2e; border-radius: 12px; padding: 24px; margin-bottom: 20px; border: 1px solid #333; }
        .card h2 { margin-bottom: 16px; color: #00d4ff; font-size: 18px; }
        label { display: block; margin-bottom: 8px; color: #aaa; font-size: 14px; }
        select, textarea, input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #333; background: #0f0f1a; color: #fff; font-size: 14px; margin-bottom: 12px; }
        select:focus, textarea:focus, input:focus { outline: none; border-color: #00d4ff; }
        textarea { resize: vertical; min-height: 120px; font-family: 'Courier New', monospace; font-size: 13px; }
        .btn { background: #00d4ff; color: #000; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-right: 10px; margin-top: 10px; }
        .btn:hover { background: #00b8e6; }
        .btn-secondary { background: #333; color: #fff; }
        .info { background: #1a1a2e; border-left: 4px solid #00d4ff; padding: 16px; margin-bottom: 20px; border-radius: 8px; }
        .info p { margin-bottom: 8px; font-size: 14px; }
        .info strong { color: #00d4ff; }
        .copy-msg { color: #00ff88; font-size: 12px; margin-top: 8px; display: none; }
        .content-output { background: #0f0f1a; border: 1px solid #333; border-radius: 8px; padding: 20px; min-height: 200px; font-size: 15px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; color: #e0e0e0; }
        .content-output strong { color: #00d4ff; font-weight: bold; }
        .content-output em { color: #00ff88; font-style: italic; }
        .content-output code { background: #1a1a2e; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Kilo Gateway</h1>
        <div class="info">
            <p><strong>Base URL:</strong> <span>https://kilogateway.vercel.app/v1</span></p>
            <p><strong>API Key:</strong> <span style="word-break: break-all;">eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJwcm9kdWN0aW9uIiwia2lsb1VzZXJJZCI6IjhmYThhNmIwLTdkMWMtNDc0NC1hZjFiLWM3NmQ0NTMwMDBlOSIsImFwaVRva2VuUGVwcGVyIjpudWxsLCJ2ZXJzaW9uIjozLCJpYXQiOjE3NzQ3NzM5OTIsImV4cCI6MTkzMjQ1Mzk5Mn0.1XnFeHSpXJzb4-dN0VTJTc3dyz_hGvxiW8Krm54AUNQ</span></p>
            <p><strong>Status:</strong> Active</p>
        </div>
        <div class="card">
            <h2>Copy cURL Command</h2>
            <label>Pilih Model</label>
            <select id="model-select" onchange="updateCurl()">
                <optgroup label="FREE Models">
                    <option value="minimax/minimax-m2.5:free" selected>MiniMax M2.5 (Free)</option>
                    <option value="xiaomi/mimo-v2-pro:free">Xiaomi MiMo V2 Pro (Free)</option>
                    <option value="xiaomi/mimo-v2-omni:free">Xiaomi MiMo V2 Omni (Free)</option>
                    <option value="x-ai/grok-code-fast-1:optimized:free">Grok Code Fast 1 (Free)</option>
                    <option value="stepfun/step-3.5-flash:free">StepFun 3.5 Flash (Free)</option>
                    <option value="nvidia/nemotron-3-super-120b-a12b:free">NVIDIA Nemotron 3 Super (Free)</option>
                    <option value="arcee-ai/trinity-large-preview:free">Arcee Trinity Large (Free)</option>
                </optgroup>
                <optgroup label="Popular Models">
                    <option value="anthropic/claude-sonnet-4">Claude Sonnet 4</option>
                    <option value="anthropic/claude-opus-4">Claude Opus 4</option>
                    <option value="openai/gpt-5">GPT-5</option>
                    <option value="openai/gpt-5-mini">GPT-5 Mini</option>
                    <option value="openai/gpt-4o">GPT-4o</option>
                    <option value="google/gemini-2.5-pro">Gemini 2.5 Pro</option>
                    <option value="deepseek/deepseek-chat">DeepSeek Chat</option>
                    <option value="qwen/qwen3-coder">Qwen3 Coder</option>
                    <option value="x-ai/grok-3">Grok 3</option>
                    <option value="moonshotai/kimi-k2.5">Kimi K2.5</option>
                    <option value="z-ai/glm-5">GLM 5</option>
                </optgroup>
            </select>
            <label>Input Prompt</label>
            <textarea id="prompt-input" oninput="updateCurl()">hi</textarea>
            <label>Max Tokens</label>
            <input type="number" id="max-tokens" value="65536" oninput="updateCurl()">
            <label>cURL Command</label>
            <textarea id="curl-output" readonly></textarea>
            <button class="btn" onclick="copyText('curl-output')">Copy cURL</button>
            <button class="btn" onclick="testCurl()" style="background: #00ff88; color: #000;">Test cURL</button>
            <button class="btn btn-secondary" onclick="copyText('curl-stream')">Copy Streaming</button>
            <button class="btn btn-secondary" onclick="copyText('python-code')">Copy Python</button>
            <p class="copy-msg" id="copy-msg">Copied!</p>
        </div>
        <div class="card">
            <h2>Test cURL Response</h2>
            <label>Response</label>
            <textarea id="curl-response" readonly placeholder="Klik 'Test cURL' untuk melihat response..."></textarea>
            <button class="btn btn-secondary" onclick="clearResponse()">Clear</button>
        </div>
        <div class="card">
            <h2>Content</h2>
            <div id="content-output" class="content-output">Klik 'Test cURL' untuk melihat konten...</div>
        </div>
        <div class="card">
            <h2>Streaming cURL</h2>
            <textarea id="curl-stream" readonly></textarea>
        </div>
        <div class="card">
            <h2>Python Code</h2>
            <textarea id="python-code" readonly></textarea>
        </div>
        <div class="card">
            <h2>Daftar Model Free</h2>
            <ul style="list-style: none; line-height: 2;">
                <li><code>minimax/minimax-m2.5:free</code> - MiniMax M2.5</li>
                <li><code>xiaomi/mimo-v2-pro:free</code> - Xiaomi MiMo V2 Pro</li>
                <li><code>xiaomi/mimo-v2-omni:free</code> - Xiaomi MiMo V2 Omni</li>
                <li><code>x-ai/grok-code-fast-1:optimized:free</code> - Grok Code Fast 1</li>
                <li><code>stepfun/step-3.5-flash:free</code> - StepFun 3.5 Flash</li>
                <li><code>nvidia/nemotron-3-super-120b-a12b:free</code> - NVIDIA Nemotron 3 Super</li>
                <li><code>arcee-ai/trinity-large-preview:free</code> - Arcee Trinity Large</li>
            </ul>
        </div>
        <footer style="text-align: center; color: #666; margin-top: 40px; padding: 20px;">
            <p>Kilo Gateway API | <a href="/health" style="color: #00d4ff;">Health Check</a> | <a href="/v1/models" style="color: #00d4ff;">All Models</a></p>
        </footer>
    </div>
    <script>
var API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJwcm9kdWN0aW9uIiwia2lsb1VzZXJJZCI6IjhmYThhNmIwLTdkMWMtNDc0NC1hZjFiLWM3NmQ0NTMwMDBlOSIsImFwaVRva2VuUGVwcGVyIjpudWxsLCJ2ZXJzaW9uIjozLCJpYXQiOjE3NzQ3NzM5OTIsImV4cCI6MTkzMjQ1Mzk5Mn0.1XnFeHSpXJzb4-dN0VTJTc3dyz_hGvxiW8Krm54AUNQ";
var BASE_URL = "https://kilogateway.vercel.app/v1";
var NL = "\n";
function updateCurl() {
    var model = document.getElementById("model-select").value || "minimax/minimax-m2.5:free";
    var prompt = document.getElementById("prompt-input").value || "hi";
    var tokens = document.getElementById("max-tokens").value || "65536";
    var bodyData = JSON.stringify({model: model, messages: [{role: "user", content: prompt}], max_tokens: parseInt(tokens)});
    var bodyStream = JSON.stringify({model: model, messages: [{role: "user", content: prompt}], stream: true});
    var curlCmd = "curl " + BASE_URL + "/chat/completions" + NL + "  -H 'Authorization: Bearer " + API_KEY + "'" + NL + "  -H 'Content-Type: application/json'" + NL + "  -d '" + bodyData + "'";
    var curlStream = "curl " + BASE_URL + "/chat/completions" + NL + "  -H 'Authorization: Bearer " + API_KEY + "'" + NL + "  -H 'Content-Type: application/json'" + NL + "  -d '" + bodyStream + "'";
    var pythonCode = "from openai import OpenAI" + NL + NL + "client = OpenAI(" + NL + "    api_key='" + API_KEY + "'," + NL + "    base_url='" + BASE_URL + "'" + NL + ")" + NL + NL + "response = client.chat.completions.create(" + NL + "    model='" + model + "'," + NL + "    messages=[{'role': 'user', 'content': '" + prompt.replace(/'/g, "\\'") + "'}]" + NL + ")" + NL + "print(response.choices[0].message.content)";
    document.getElementById("curl-output").value = curlCmd;
    document.getElementById("curl-stream").value = curlStream;
    document.getElementById("python-code").value = pythonCode;
}
function copyText(id) {
    var el = document.getElementById(id);
    el.select();
    document.execCommand("copy");
    var msg = document.getElementById("copy-msg");
    msg.style.display = "block";
    setTimeout(function() { msg.style.display = "none"; }, 2000);
}
function testCurl() {
    var model = document.getElementById("model-select").value || "minimax/minimax-m2.5:free";
    var prompt = document.getElementById("prompt-input").value || "hi";
    var tokens = document.getElementById("max-tokens").value || "65536";
    var responseArea = document.getElementById("curl-response");
    responseArea.value = "Loading...";
    var xhr = new XMLHttpRequest();
    xhr.open("POST", BASE_URL + "/chat/completions", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", "Bearer " + API_KEY);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                responseArea.value = JSON.stringify(data, null, 2);
                var content = "";
                if (data.choices && data.choices[0] && data.choices[0].message) {
                    content = data.choices[0].message.content || "No content";
                }
                document.getElementById("content-output").innerHTML = content.replace(/\n/g, "<br>");
            } else {
                responseArea.value = "Error " + xhr.status + ": " + xhr.responseText;
            }
        }
    };
    xhr.send(JSON.stringify({model: model, messages: [{role: "user", content: prompt}], max_tokens: parseInt(tokens)}));
}
function clearResponse() {
    document.getElementById("curl-response").value = "";
    document.getElementById("content-output").innerHTML = "Klik Test cURL";
}
setTimeout(updateCurl, 100);
    </script>
</body>
</html>"""

# ============================================================================
# Models
# ============================================================================

class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    top_p: Optional[float] = None
    stream: Optional[bool] = False
    stop: Optional[str | List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    user: Optional[str] = None
    tools: Optional[List[Dict]] = None
    tool_choice: Optional[str | Dict] = None
    response_format: Optional[Dict] = None

class Choice(BaseModel):
    index: int
    message: Dict[str, str]
    finish_reason: str

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict]
    usage: Dict
    provider: Optional[str] = None
    latency_ms: Optional[int] = None

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str

class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

# ============================================================================
# Mock Data - All Kilo Models
# ============================================================================

AVAILABLE_MODELS = [
    # Kilo Smart Routing
    {"id": "kilo-auto/frontier", "owned_by": "kilocode"},
    {"id": "kilo-auto/balanced", "owned_by": "kilocode"},
    {"id": "kilo-auto/free", "owned_by": "kilocode"},
    {"id": "kilo-auto/small", "owned_by": "kilocode"},
    {"id": "kilocode/kilo/auto", "owned_by": "kilocode"},
    {"id": "kilocode/kilo/quality", "owned_by": "kilocode"},
    {"id": "kilocode/kilo/speed", "owned_by": "kilocode"},
    {"id": "kilocode/kilo/cost", "owned_by": "kilocode"},
    {"id": "kilocode/kilo/balance", "owned_by": "kilocode"},
    {"id": "openrouter/auto", "owned_by": "openrouter"},
    {"id": "openrouter/free", "owned_by": "openrouter"},
    {"id": "openrouter/bodybuilder", "owned_by": "openrouter"},
    {"id": "switchpoint/router", "owned_by": "switchpoint"},
    {"id": "corethink:free", "owned_by": "corethink"},
    
    # AI21
    {"id": "ai21/jamba-large-1.7", "owned_by": "ai21"},
    
    # AionLabs
    {"id": "aion-labs/aion-1.0", "owned_by": "aion-labs"},
    {"id": "aion-labs/aion-1.0-mini", "owned_by": "aion-labs"},
    {"id": "aion-labs/aion-2.0", "owned_by": "aion-labs"},
    {"id": "aion-labs/aion-rp-llama-3.1-8b", "owned_by": "aion-labs"},
    
    # AlfredPros
    {"id": "alfredpros/codellama-7b-instruct-solidity", "owned_by": "alfredpros"},
    
    # AllenAI
    {"id": "allenai/olmo-2-0325-32b-instruct", "owned_by": "allenai"},
    {"id": "allenai/olmo-3-32b-think", "owned_by": "allenai"},
    {"id": "allenai/olmo-3.1-32b-instruct", "owned_by": "allenai"},
    {"id": "allenai/olmo-3.1-32b-think", "owned_by": "allenai"},
    
    # Amazon
    {"id": "amazon/nova-2-lite-v1", "owned_by": "amazon"},
    {"id": "amazon/nova-lite-v1", "owned_by": "amazon"},
    {"id": "amazon/nova-micro-v1", "owned_by": "amazon"},
    {"id": "amazon/nova-premier-v1", "owned_by": "amazon"},
    {"id": "amazon/nova-pro-v1", "owned_by": "amazon"},
    
    # Anthropic
    {"id": "anthropic/claude-3-haiku", "owned_by": "anthropic"},
    {"id": "anthropic/claude-3.5-haiku", "owned_by": "anthropic"},
    {"id": "anthropic/claude-3.5-sonnet", "owned_by": "anthropic"},
    {"id": "anthropic/claude-3.7-sonnet", "owned_by": "anthropic"},
    {"id": "anthropic/claude-3.7-sonnet:thinking", "owned_by": "anthropic"},
    {"id": "anthropic/claude-haiku-4.5", "owned_by": "anthropic"},
    {"id": "anthropic/claude-opus-4", "owned_by": "anthropic"},
    {"id": "anthropic/claude-opus-4.1", "owned_by": "anthropic"},
    {"id": "anthropic/claude-opus-4.5", "owned_by": "anthropic"},
    {"id": "anthropic/claude-sonnet-4", "owned_by": "anthropic"},
    {"id": "anthropic/claude-sonnet-4.5", "owned_by": "anthropic"},
    
    # Arcee AI
    {"id": "arcee-ai/coder-large", "owned_by": "arcee-ai"},
    {"id": "arcee-ai/maestro-reasoning", "owned_by": "arcee-ai"},
    {"id": "arcee-ai/spotlight", "owned_by": "arcee-ai"},
    {"id": "arcee-ai/trinity-mini", "owned_by": "arcee-ai"},
    {"id": "arcee-ai/trinity-large-preview", "owned_by": "arcee-ai", "free": True},
    {"id": "arcee-ai/virtuoso-large", "owned_by": "arcee-ai"},
    
    # Baidu
    {"id": "baidu/ernie-4.5-21b-a3b", "owned_by": "baidu"},
    {"id": "baidu/ernie-4.5-21b-a3b-thinking", "owned_by": "baidu"},
    {"id": "baidu/ernie-4.5-300b-a47b", "owned_by": "baidu"},
    {"id": "baidu/ernie-4.5-vl-28b-a3b", "owned_by": "baidu"},
    {"id": "baidu/ernie-4.5-vl-424b-a47b", "owned_by": "baidu"},
    
    # ByteDance
    {"id": "bytedance-seed/seed-1.6", "owned_by": "bytedance-seed"},
    {"id": "bytedance-seed/seed-1.6-flash", "owned_by": "bytedance-seed"},
    {"id": "bytedance-seed/seed-2.0-lite", "owned_by": "bytedance-seed"},
    {"id": "bytedance-seed/seed-2.0-mini", "owned_by": "bytedance-seed"},
    {"id": "bytedance/ui-tars-1.5-7b", "owned_by": "bytedance"},
    
    # Cohere
    {"id": "cohere/command-a", "owned_by": "cohere"},
    {"id": "cohere/command-r-08-2024", "owned_by": "cohere"},
    {"id": "co82024", "owned_by": "cohere"},
    {"id": "cohere/command-r7b-12-2024", "owned_by": "cohere"},
    
    # DeepCogito
    {"id": "deepcogito/cogito-v2.1-671b", "owned_by": "deepcogito"},
    
    # DeepSeek
    {"id": "deepseek/deepseek-chat", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-chat-v3-0324", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-chat-v3.1", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-v3.1-terminus", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-v3.2", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-v3.2-exp", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-v3.2-speciale", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-r1", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-r1-0528", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-r1-distill-llama-70b", "owned_by": "deepseek"},
    {"id": "deepseek/deepseek-r1-distill-qwen-32b", "owned_by": "deepseek"},
    
    # EleutherAI
    {"id": "eleutherai/llemma_7b", "owned_by": "eleutherai"},
    
    # EssentialAI
    {"id": "essentialai/rnj-1-instruct", "owned_by": "essentialai"},
    
    # Goliath
    {"id": "alpindale/goliath-120b", "owned_by": "alpindale"},
    
    # Google
    {"id": "google/gemini-2.0-flash-001", "owned_by": "google"},
    {"id": "google/gemini-2.0-flash-lite-001", "owned_by": "google"},
    {"id": "google/gemini-2.5-flash", "owned_by": "google"},
    {"id": "google/gemini-2.5-flash-lite", "owned_by": "google"},
    {"id": "google/gemini-2.5-flash-lite-preview-09-2025", "owned_by": "google"},
    {"id": "google/gemini-2.5-pro", "owned_by": "google"},
    {"id": "google/gemini-2.5-pro-preview-05-06", "owned_by": "google"},
    {"id": "google/gemini-2.5-pro-preview", "owned_by": "google"},
    {"id": "google/gemini-3-flash-preview", "owned_by": "google"},
    {"id": "google/gemini-3.1-flash-lite-preview", "owned_by": "google"},
    {"id": "google/gemini-3.1-pro-preview-customtools", "owned_by": "google"},
    {"id": "google/gemini-2.5-flash-image", "owned_by": "google"},
    {"id": "google/gemini-3.1-flash-image-preview", "owned_by": "google"},
    {"id": "google/gemini-3-pro-image-preview", "owned_by": "google"},
    {"id": "google/gemma-2-27b-it", "owned_by": "google"},
    {"id": "google/gemma-2-9b-it", "owned_by": "google"},
    {"id": "google/gemma-3-12b-it", "owned_by": "google"},
    {"id": "google/gemma-3-27b-it", "owned_by": "google"},
    {"id": "google/gemma-3-4b-it", "owned_by": "google"},
    {"id": "google/gemma-3n-e4b-it", "owned_by": "google"},
    
    # IBM
    {"id": "ibm-granite/granite-4.0-h-micro", "owned_by": "ibm-granite"},
    
    # Inception
    {"id": "inception/mercury", "owned_by": "inception"},
    {"id": "inception/mercury-2", "owned_by": "inception"},
    {"id": "inception/mercury-coder", "owned_by": "inception"},
    
    # Inflection
    {"id": "inflection/inflection-3-pi", "owned_by": "inflection"},
    {"id": "inflection/inflection-3-productivity", "owned_by": "inflection"},
    
    # Kwaipilot
    {"id": "kwaipilot/kat-coder-pro", "owned_by": "kwaipilot"},
    {"id": "kwaipilot/kat-coder-pro-v2", "owned_by": "kwaipilot"},
    
    # LiquidAI
    {"id": "liquid/lfm-2.2-6b", "owned_by": "liquid"},
    {"id": "liquid/lfm-2-24b-a2b", "owned_by": "liquid"},
    {"id": "liquid/lfm2-8b-a1b", "owned_by": "liquid"},
    
    # Meta
    {"id": "meta-llama/llama-guard-3-8b", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3-70b-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3-8b-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3.1-70b-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3.1-8b-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3.2-11b-vision-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3.2-1b-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3.2-3b-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-3.3-70b-instruct", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-4-maverick", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-4-scout", "owned_by": "meta-llama"},
    {"id": "meta-llama/llama-guard-4-12b", "owned_by": "meta-llama"},
    
    # Magnum
    {"id": "anthracite-org/magnum-v4-72b", "owned_by": "anthracite-org"},
    
    # Mancer
    {"id": "mancer/weaver", "owned_by": "mancer"},
    
    # Meituan
    {"id": "meituan/longcat-flash-chat", "owned_by": "meituan"},
    
    # Microsoft
    {"id": "microsoft/phi-4", "owned_by": "microsoft"},
    {"id": "microsoft/wizardlm-2-8x22b", "owned_by": "microsoft"},
    
    # MiniMax
    {"id": "minimax/minimax-m1", "owned_by": "minimax"},
    {"id": "minimax/minimax-m2", "owned_by": "minimax"},
    {"id": "minimax/minimax-m2-her", "owned_by": "minimax"},
    {"id": "minimax/minimax-m2.1", "owned_by": "minimax"},
    {"id": "minimax/minimax-m2.5", "owned_by": "minimax"},
    {"id": "minimax/minimax-m2.5:free", "owned_by": "minimax", "free": True},
    {"id": "minimax/minimax-01", "owned_by": "minimax"},
    
    # Mistral
    {"id": "mistralai/mistral-large", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-large-2407", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-large-2411", "owned_by": "mistralai"},
    {"id": "mistralai/codestral-2508", "owned_by": "mistralai"},
    {"id": "mistralai/devstral-2512", "owned_by": "mistralai"},
    {"id": "mistralai/devstral-medium", "owned_by": "mistralai"},
    {"id": "mistralai/devstral-small", "owned_by": "mistralai"},
    {"id": "mistralai/ministral-14b-2512", "owned_by": "mistralai"},
    {"id": "mistralai/ministral-3b-2512", "owned_by": "mistralai"},
    {"id": "mistralai/ministral-8b-2512", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-7b-instruct-v0.1", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-large-2512", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-medium-3", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-medium-3.1", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-nemo", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-small-24b-instruct-2501", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-small-3.1-24b-instruct", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-small-3.2-24b-instruct", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-small-2603", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-small-creative", "owned_by": "mistralai"},
    {"id": "mistralai/mixtral-8x22b-instruct", "owned_by": "mistralai"},
    {"id": "mistralai/mixtral-8x7b-instruct", "owned_by": "mistralai"},
    {"id": "mistralai/pixtral-large-2411", "owned_by": "mistralai"},
    {"id": "mistralai/mistral-saba", "owned_by": "mistralai"},
    {"id": "mistralai/voxtral-small-24b-2507", "owned_by": "mistralai"},
    
    # MoonshotAI
    {"id": "moonshotai/kimi-k2", "owned_by": "moonshotai"},
    {"id": "moonshotai/kimi-k2-0905", "owned_by": "moonshotai"},
    {"id": "moonshotai/kimi-k2-thinking", "owned_by": "moonshotai"},
    {"id": "moonshotai/kimi-k2.5", "owned_by": "moonshotai"},
    
    # Morph
    {"id": "morph/morph-v3-fast", "owned_by": "morph"},
    {"id": "morph/morph-v3-large", "owned_by": "morph"},
    
    # Goliath
    {"id": "gryphe/mythomax-l2-13b", "owned_by": "gryphe"},
    
    # Nex AGI
    {"id": "nex-agi/deepseek-v3.1-nex-n1", "owned_by": "nex-agi"},
    
    # Nous Research
    {"id": "nousresearch/hermes-3-llama-3.1-405b", "owned_by": "nousresearch"},
    {"id": "nousresearch/hermes-3-llama-3.1-70b", "owned_by": "nousresearch"},
    {"id": "nousresearch/hermes-4-405b", "owned_by": "nousresearch"},
    {"id": "nousresearch/hermes-4-70b", "owned_by": "nousresearch"},
    {"id": "nousresearch/hermes-2-pro-llama-3-8b", "owned_by": "nousresearch"},
    
    # NVIDIA
    {"id": "nvidia/llama-3.1-nemotron-70b-instruct", "owned_by": "nvidia"},
    {"id": "nvidia/llama-3.1-nemotron-ultra-253b-v1", "owned_by": "nvidia"},
    {"id": "nvidia/llama-3.3-nemotron-super-49b-v1.5", "owned_by": "nvidia"},
    {"id": "nvidia/nemotron-3-nano-30b-a3b", "owned_by": "nvidia"},
    {"id": "nvidia/nemotron-3-super-120b-a12b", "owned_by": "nvidia", "free": True},
    {"id": "nvidia/nemotron-nano-12b-v2-vl", "owned_by": "nvidia"},
    {"id": "nvidia/nemotron-nano-9b-v2", "owned_by": "nvidia"},
    
    # OpenAI
    {"id": "openai/gpt-audio", "owned_by": "openai"},
    {"id": "openai/gpt-audio-mini", "owned_by": "openai"},
    {"id": "openai/gpt-3.5-turbo", "owned_by": "openai"},
    {"id": "openai/gpt-3.5-turbo-0613", "owned_by": "openai"},
    {"id": "openai/gpt-3.5-turbo-16k", "owned_by": "openai"},
    {"id": "openai/gpt-3.5-turbo-instruct", "owned_by": "openai"},
    {"id": "openai/gpt-4", "owned_by": "openai"},
    {"id": "openai/gpt-4-0314", "owned_by": "openai"},
    {"id": "openai/gpt-4-turbo", "owned_by": "openai"},
    {"id": "openai/gpt-4-1106-preview", "owned_by": "openai"},
    {"id": "openai/gpt-4-turbo-preview", "owned_by": "openai"},
    {"id": "openai/gpt-4.1", "owned_by": "openai"},
    {"id": "openai/gpt-4.1-mini", "owned_by": "openai"},
    {"id": "openai/gpt-4.1-nano", "owned_by": "openai"},
    {"id": "openai/gpt-4o", "owned_by": "openai"},
    {"id": "openai/gpt-4o-2024-05-13", "owned_by": "openai"},
    {"id": "openai/gpt-4o-2024-08-06", "owned_by": "openai"},
    {"id": "openai/gpt-4o-2024-11-20", "owned_by": "openai"},
    {"id": "openai/gpt-4o:extended", "owned_by": "openai"},
    {"id": "openai/gpt-4o-audio-preview", "owned_by": "openai"},
    {"id": "openai/gpt-4o-search-preview", "owned_by": "openai"},
    {"id": "openai/gpt-4o-mini", "owned_by": "openai"},
    {"id": "openai/gpt-4o-mini-2024-07-18", "owned_by": "openai"},
    {"id": "openai/gpt-4o-mini-search-preview", "owned_by": "openai"},
    {"id": "openai/gpt-5", "owned_by": "openai"},
    {"id": "openai/gpt-5-chat", "owned_by": "openai"},
    {"id": "openai/gpt-5-codex", "owned_by": "openai"},
    {"id": "openai/gpt-5-image", "owned_by": "openai"},
    {"id": "openai/gpt-5-image-mini", "owned_by": "openai"},
    {"id": "openai/gpt-5-mini", "owned_by": "openai"},
    {"id": "openai/gpt-5-nano", "owned_by": "openai"},
    {"id": "openai/gpt-5-pro", "owned_by": "openai"},
    {"id": "openai/gpt-5.1", "owned_by": "openai"},
    {"id": "openai/gpt-5.1-chat", "owned_by": "openai"},
    {"id": "openai/gpt-5.1-codex", "owned_by": "openai"},
    {"id": "openai/gpt-5.1-codex-max", "owned_by": "openai"},
    {"id": "openai/gpt-5.1-codex-mini", "owned_by": "openai"},
    {"id": "openai/gpt-5.2", "owned_by": "openai"},
    {"id": "openai/gpt-5.2-chat", "owned_by": "openai"},
    {"id": "openai/gpt-5.2-pro", "owned_by": "openai"},
    {"id": "openai/gpt-5.2-codex", "owned_by": "openai"},
    {"id": "openai/gpt-5.3-chat", "owned_by": "openai"},
    {"id": "openai/gpt-5.3-codex", "owned_by": "openai"},
    {"id": "openai/gpt-5.4-mini", "owned_by": "openai"},
    {"id": "openai/gpt-5.4-nano", "owned_by": "openai"},
    {"id": "openai/gpt-5.4-pro", "owned_by": "openai"},
    {"id": "openai/gpt-oss-120b", "owned_by": "openai"},
    {"id": "openai/gpt-oss-20b", "owned_by": "openai"},
    {"id": "openai/gpt-oss-safeguard-20b", "owned_by": "openai"},
    {"id": "openai/o1", "owned_by": "openai"},
    {"id": "openai/o1-pro", "owned_by": "openai"},
    {"id": "openai/o3", "owned_by": "openai"},
    {"id": "openai/o3-deep-research", "owned_by": "openai"},
    {"id": "openai/o3-mini", "owned_by": "openai"},
    {"id": "openai/o3-mini-high", "owned_by": "openai"},
    {"id": "openai/o3-pro", "owned_by": "openai"},
    {"id": "openai/o4-mini", "owned_by": "openai"},
    {"id": "openai/o4-mini-deep-research", "owned_by": "openai"},
    {"id": "openai/o4-mini-high", "owned_by": "openai"},
    
    # Perplexity
    {"id": "perplexity/sonar", "owned_by": "perplexity"},
    {"id": "perplexity/sonar-deep-research", "owned_by": "perplexity"},
    {"id": "perplexity/sonar-pro", "owned_by": "perplexity"},
    {"id": "perplexity/sonar-pro-search", "owned_by": "perplexity"},
    {"id": "perplexity/sonar-reasoning-pro", "owned_by": "perplexity"},
    
    # Prime Intellect
    {"id": "prime-intellect/intellect-3", "owned_by": "prime-intellect"},
    
    # Qwen
    {"id": "qwen/qwen-plus-2025-07-28", "owned_by": "qwen"},
    {"id": "qwen/qwen-plus-2025-07-28:thinking", "owned_by": "qwen"},
    {"id": "qwen/qwen-vl-max", "owned_by": "qwen"},
    {"id": "qwen/qwen-vl-plus", "owned_by": "qwen"},
    {"id": "qwen/qwen-max", "owned_by": "qwen"},
    {"id": "qwen/qwen-plus", "owned_by": "qwen"},
    {"id": "qwen/qwen-turbo", "owned_by": "qwen"},
    {"id": "qwen/qwen-2.5-7b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen2.5-coder-7b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen2.5-vl-32b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen2.5-vl-72b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen3-14b", "owned_by": "qwen"},
    {"id": "qwen/qwen3-235b-a22b", "owned_by": "qwen"},
    {"id": "qwen/qwen3-235b-a22b-2507", "owned_by": "qwen"},
    {"id": "qwen/qwen3-235b-a22b-thinking-2507", "owned_by": "qwen"},
    {"id": "qwen/qwen3-30b-a3b", "owned_by": "qwen"},
    {"id": "qwen/qwen3-30b-a3b-instruct-2507", "owned_by": "qwen"},
    {"id": "qwen/qwen3-30b-a3b-thinking-2507", "owned_by": "qwen"},
    {"id": "qwen/qwen3-32b", "owned_by": "qwen"},
    {"id": "qwen/qwen3-8b", "owned_by": "qwen"},
    {"id": "qwen/qwen3-coder-30b-a3b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen3-coder", "owned_by": "qwen"},
    {"id": "qwen/qwen3-coder-flash", "owned_by": "qwen"},
    {"id": "qwen/qwen3-coder-next", "owned_by": "qwen"},
    {"id": "qwen/qwen3-coder-plus", "owned_by": "qwen"},
    {"id": "qwen/qwen3-max", "owned_by": "qwen"},
    {"id": "qwen/qwen3-max-thinking", "owned_by": "qwen"},
    {"id": "qwen/qwen3-next-80b-a3b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen3-next-80b-a3b-thinking", "owned_by": "qwen"},
    {"id": "qwen/qwen3-vl-235b-a22b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen3-vl-235b-a22b-thinking", "owned_by": "qwen"},
    {"id": "qwen/qwen3-vl-30b-a3b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen3-vl-30b-a3b-thinking", "owned_by": "qwen"},
    {"id": "qwen/qwen3-vl-32b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen3-vl-8b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen3-vl-8b-thinking", "owned_by": "qwen"},
    {"id": "qwen/qwen3.5-397b-a17b", "owned_by": "qwen"},
    {"id": "qwen/qwen3.5-plus-02-15", "owned_by": "qwen"},
    {"id": "qwen/qwen3.5-122b-a10b", "owned_by": "qwen"},
    {"id": "qwen/qwen3.5-27b", "owned_by": "qwen"},
    {"id": "qwen/qwen3.5-35b-a3b", "owned_by": "qwen"},
    {"id": "qwen/qwen3.5-9b", "owned_by": "qwen"},
    {"id": "qwen/qwen3.5-flash-02-23", "owned_by": "qwen"},
    {"id": "qwen/qwq-32b", "owned_by": "qwen"},
    {"id": "qwen/qwen-2.5-72b-instruct", "owned_by": "qwen"},
    {"id": "qwen/qwen-2.5-coder-32b-instruct", "owned_by": "qwen"},
    
    # Reka
    {"id": "reka/reka-edge", "owned_by": "reka"},
    
    # Relace
    {"id": "relace/relace-apply-3", "owned_by": "relace"},
    {"id": "relace/relace-search", "owned_by": "relace"},
    
    # ReMM
    {"id": "undi95/remm-slerp-l2-13b", "owned_by": "undi95"},
    
    # Sao10K
    {"id": "sao10k/l3-lunaris-8b", "owned_by": "sao10k"},
    {"id": "sao10k/l3-euryale-70b", "owned_by": "sao10k"},
    {"id": "sao10k/l3.1-70b-hanami-x1", "owned_by": "sao10k"},
    {"id": "sao10k/l3.1-euryale-70b", "owned_by": "sao10k"},
    {"id": "sao10k/l3.3-euryale-70b", "owned_by": "sao10k"},
    
    # StepFun
    {"id": "stepfun/step-3.5-flash", "owned_by": "stepfun"},
    {"id": "stepfun/step-3.5-flash:free", "owned_by": "stepfun", "free": True},
    
    # Tencent
    {"id": "tencent/hunyuan-a13b-instruct", "owned_by": "tencent"},
    
    # TheDrummer
    {"id": "thedrummer/cydonia-24b-v4.1", "owned_by": "thedrummer"},
    {"id": "thedrummer/rocinante-12b", "owned_by": "thedrummer"},
    {"id": "thedrummer/skyfall-36b-v2", "owned_by": "thedrummer"},
    {"id": "thedrummer/unslopnemo-12b", "owned_by": "thedrummer"},
    
    # TNG
    {"id": "tngtech/deepseek-r1t2-chimera", "owned_by": "tngtech"},
    
    # Tongyi
    {"id": "alibaba/tongyi-deepresearch-30b-a3b", "owned_by": "alibaba"},
    
    # Upstage
    {"id": "upstage/solar-pro-3", "owned_by": "upstage"},
    
    # Writer
    {"id": "writer/palmyra-x5", "owned_by": "writer"},
    
    # xAI
    {"id": "x-ai/grok-3", "owned_by": "x-ai"},
    {"id": "x-ai/grok-3-beta", "owned_by": "x-ai"},
    {"id": "x-ai/grok-3-mini", "owned_by": "x-ai"},
    {"id": "x-ai/grok-3-mini-beta", "owned_by": "x-ai"},
    {"id": "x-ai/grok-4", "owned_by": "x-ai"},
    {"id": "x-ai/grok-4-fast", "owned_by": "x-ai"},
    {"id": "x-ai/grok-4.1-fast", "owned_by": "x-ai"},
    {"id": "x-ai/grok-4.20-beta", "owned_by": "x-ai"},
    {"id": "x-ai/grok-4.20-multi-agent-beta", "owned_by": "x-ai"},
    {"id": "x-ai/grok-code-fast-1:optimized:free", "owned_by": "x-ai", "free": True},
    
    # Xiaomi
    {"id": "xiaomi/mimo-v2-flash", "owned_by": "xiaomi"},
    {"id": "xiaomi/mimo-v2-omni", "owned_by": "xiaomi"},
    {"id": "xiaomi/mimo-v2-omni:free", "owned_by": "xiaomi", "free": True},
    {"id": "xiaomi/mimo-v2-pro", "owned_by": "xiaomi"},
    {"id": "xiaomi/mimo-v2-pro:free", "owned_by": "xiaomi", "free": True},
    
    # Z.ai
    {"id": "z-ai/glm-4-32b", "owned_by": "z-ai"},
    {"id": "z-ai/glm-4.5", "owned_by": "z-ai"},
    {"id": "z-ai/glm-4.5-air", "owned_by": "z-ai"},
    {"id": "z-ai/glm-4.5v", "owned_by": "z-ai"},
    {"id": "z-ai/glm-4.6", "owned_by": "z-ai"},
    {"id": "z-ai/glm-4.6v", "owned_by": "z-ai"},
    {"id": "z-ai/glm-4.7", "owned_by": "z-ai"},
    {"id": "z-ai/glm-4.7-flash", "owned_by": "z-ai"},
    {"id": "z-ai/glm-5", "owned_by": "z-ai"},
    {"id": "z-ai/glm-5-turbo", "owned_by": "z-ai"},
]

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Kilo Gateway",
    description="OpenAI-compatible API Gateway for multiple AI providers",
    version="1.0.0"
)

# ============================================================================
# Helper Functions
# ============================================================================

def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format. Use: Bearer <api-key>")
    return authorization.replace("Bearer ", "")

def parse_model(model: str) -> tuple[str, str]:
    parts = model.split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail=f"Invalid model format: {model}. Expected: provider/model")
    provider = parts[0]
    actual_model = "/".join(parts[1:])
    return provider, actual_model

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return HTMLResponse(content=HTML_DASHBOARD, status_code=200)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/v1/models", response_model=Dict)
async def list_models(authorization: Optional[str] = Header(None)):
    verify_api_key(authorization)
    return {
        "object": "list",
        "data": [
            {
                "id": m["id"],
                "object": "model",
                "created": 1699000000,
                "owned_by": m["owned_by"]
            }
            for m in AVAILABLE_MODELS
        ]
    }


def normalize_tool_call_response(result: Dict) -> Dict:
    for choice in result.get("choices", []):
        msg = choice.get("message", {})
        if msg.get("tool_calls") and msg.get("content") is None:
            msg["content"] = ""
    return result


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None)
):
    start_time = time.time()
    api_key = verify_api_key(authorization)
    provider, actual_model = parse_model(request.model)
    
    # Call real Kilo Gateway API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.kilo.ai/api/gateway/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": request.model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "stream": request.stream,
                    **({"tools": request.tools} if request.tools else {}),
                    **({"tool_choice": request.tool_choice} if request.tool_choice else {})
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_detail = response.text
                raise HTTPException(status_code=response.status_code, detail=f"API Error: {error_detail}")
            
            if request.stream:
                return StreamingResponse(
                    stream_response_from_api(response),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Request-ID": str(uuid.uuid4())
                    }
                )
            
            result = response.json()
            result = normalize_tool_call_response(result)
            return result
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

async def stream_response_from_api(response) -> Generator[str, None, None]:
    async for chunk in response.aiter_text():
        yield chunk

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "invalid_request_error" if exc.status_code == 400 else "authentication_error" if exc.status_code == 401 else "server_error",
                "code": exc.status_code
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": str(exc),
                "type": "server_error",
                "code": 500
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)