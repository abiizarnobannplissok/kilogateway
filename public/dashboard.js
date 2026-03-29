function updateCurl() {
    var model = document.getElementById("model-select").value;
    if (!model) model = "minimax/minimax-m2.5:free";
    var prompt = document.getElementById("prompt-input").value;
    if (!prompt) prompt = "hi";
    var tokens = document.getElementById("max-tokens").value;
    if (!tokens) tokens = "65536";
    
    var curlCmd = "curl https://kilogateway.vercel.app/v1/chat/completions -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJwcm9kdWN0aW9uIiwia2lsb1VzZXJJZCI6IjhmYThhNmIwLTdkMWMtNDc0NC1hZjFiLWM3NmQ0NTMwMDBlOSIsImFwaVRva2VuUGVwcGVyIjpudWxsLCJ2ZXJzaW9uIjozLCJpYXQiOjE3NzQ3NzM5OTIsImV4cCI6MTkzMjQ1Mzk5Mn0.1XnFeHSpXJzb4-dN0VTJTc3dyz_hGvxiW8Krm54AUNQ' -H 'Content-Type: application/json' -d '{\"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + prompt + "\"}], \"max_tokens\": " + tokens + "}'";
    
    var curlStream = "curl https://kilogateway.vercel.app/v1/chat/completions -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJwcm9kdWN0aW9uIiwia2lsb1VzZXJJZCI6IjhmYThhNmIwLTdkMWMtNDc0NC1hZjFiLWM3NmQ0NTMwMDBlOSIsImFwaVRva2VuUGVwcGVyIjpudWxsLCJ2ZXJzaW9uIjozLCJpYXQiOjE3NzQ3NzM5OTIsImV4cCI6MTkzMjQ1Mzk5Mn0.1XnFeHSpXJzb4-dN0VTJTc3dyz_hGvxiW8Krm54AUNQ' -H 'Content-Type: application/json' -d '{\"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + prompt + "\"}], \"stream\": true}'";
    
    var pythonCode = "from openai import OpenAI\n\nclient = OpenAI(\n    api_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJwcm9kdWN0aW9uIiwia2lsb1VzZXJJZCI6IjhmYThhNmIwLTdkMWMtNDc0NC1hZjFiLWM3NmQ0NTMwMDBlOSIsImFwaVRva2VuUGVwcGVyIjpudWxsLCJ2ZXJzaW9uIjozLCJpYXQiOjE3NzQ3NzM5OTIsImV4cCI6MTkzMjQ1Mzk5Mn0.1XnFeHSpXJzb4-dN0VTJTc3dyz_hGvxiW8Krm54AUNQ',\n    base_url='https://kilogateway.vercel.app/v1'\n)\n\nresponse = client.chat.completions.create(\n    model='" + model + "',\n    messages=[{'role': 'user', 'content': '" + prompt + "'}]\n)\nprint(response.choices[0].message.content)";
    
    document.getElementById("curl-output").value = curlCmd;
    document.getElementById("curl-stream").value = curlStream;
    document.getElementById("python-code").value = pythonCode;
}

function copyText(id) {
    navigator.clipboard.writeText(document.getElementById(id).value);
    var msg = document.getElementById("copy-msg");
    msg.style.display = "block";
    setTimeout(function() { msg.style.display = "none"; }, 2000);
}

function testCurl() {
    var model = document.getElementById("model-select").value;
    if (!model) model = "minimax/minimax-m2.5:free";
    var prompt = document.getElementById("prompt-input").value;
    if (!prompt) prompt = "hi";
    var tokens = document.getElementById("max-tokens").value;
    if (!tokens) tokens = "65536";
    
    var responseArea = document.getElementById("curl-response");
    responseArea.value = "Loading...";
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://kilogateway.vercel.app/v1/chat/completions", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJwcm9kdWN0aW9uIiwia2lsb1VzZXJJZCI6IjhmYThhNmIwLTdkMWMtNDc0NC1hZjFiLWM3NmQ0NTMwMDBlOSIsImFwaVRva2VuUGVwcGVyIjpudWxsLCJ2ZXJzaW9uIjozLCJpYXQiOjE3NzQ3NzM5OTIsImV4cCI6MTkzMjQ1Mzk5Mn0.1XnFeHSpXJzb4-dN0VTJTc3dyz_hGvxiW8Krm54AUNQ");
    
    var requestData = {
        model: model,
        messages: [{ role: "user", content: prompt }],
        max_tokens: parseInt(tokens)
    };
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    responseArea.value = JSON.stringify(data, null, 2);
                    var content = "";
                    if (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) {
                        content = data.choices[0].message.content;
                    } else {
                        content = "No content found in response";
                    }
                    var contentOutput = document.getElementById("content-output");
                    contentOutput.innerHTML = formatContent(content);
                } catch (e) {
                    responseArea.value = "Error parsing: " + e.message;
                    document.getElementById("content-output").innerHTML = "Error: " + e.message;
                }
            } else {
                responseArea.value = "Error: " + xhr.status + " " + xhr.statusText;
                document.getElementById("content-output").innerHTML = "Error: " + xhr.status + " " + xhr.statusText;
            }
        }
    };
    
    xhr.send(JSON.stringify(requestData));
}

function formatContent(text) {
    if (!text) return "";
    var html = text;
    html = html.replace(/&/g, "&amp;");
    html = html.replace(/</g, "&lt;");
    html = html.replace(/>/g, "&gt;");
    html = html.replace(/\n/g, "<br>");
    return html;
}

function clearResponse() {
    document.getElementById("curl-response").value = "";
    document.getElementById("content-output").innerHTML = "Klik 'Test cURL' untuk melihat konten...";
}

setTimeout(updateCurl, 100);
