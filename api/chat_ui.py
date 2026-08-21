from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

app = FastAPI(title="TV AI UI Wrapper")

INJECT = r'''
<style>
.ai-thinking{display:flex;align-items:center;gap:10px;max-width:88%;padding:10px 13px;margin:0 0 10px;border-radius:13px;background:#131e31;color:#aebbd0;border:1px solid #263750;animation:aiFadeIn .22s ease-out}
.ai-thinking-label{font-size:12px;font-weight:700}
.ai-thinking-spinner{width:14px;height:14px;border:2px solid #3a4e6f;border-top-color:#e6c56d;border-radius:50%;animation:aiSpin .8s linear infinite;flex:0 0 auto}
.ai-thinking-dots{display:inline-flex;gap:3px;align-items:center;margin-left:2px}
.ai-thinking-dots span{width:4px;height:4px;border-radius:50%;background:#e6c56d;animation:aiDot 1.1s infinite ease-in-out}
.ai-thinking-dots span:nth-child(2){animation-delay:.15s}.ai-thinking-dots span:nth-child(3){animation-delay:.3s}
@keyframes aiSpin{to{transform:rotate(360deg)}}
@keyframes aiDot{0%,60%,100%{opacity:.25;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}
@keyframes aiFadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
</style>
<script>
(function(){
  const install=()=>{
    if(typeof window.askAI!=='function'||window.__tvAiThinkingInstalled)return;
    window.__tvAiThinkingInstalled=true;
    const originalAskAI=window.askAI;
    function removeThinking(){
      const node=document.getElementById('aiThinkingBubble');
      if(node)node.remove();
    }
    function showThinking(){
      removeThinking();
      const box=document.getElementById('chatbox');
      if(!box)return;
      const node=document.createElement('div');
      node.id='aiThinkingBubble';
      node.className='ai-thinking';
      node.innerHTML='<span class="ai-thinking-spinner"></span><span class="ai-thinking-label">AI đang trả lời</span><span class="ai-thinking-dots"><span></span><span></span><span></span></span>';
      box.appendChild(node);
      box.scrollTop=box.scrollHeight;
    }
    window.askAI=async function(){
      const question=document.getElementById('question');
      const q=question?.value?.trim();
      if(!q)return originalAskAI();
      showThinking();
      try{return await originalAskAI();}
      finally{removeThinking();}
    };
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(install,0));
  else setTimeout(install,0);
})();
</script>
'''

@app.get("/", response_class=HTMLResponse)
def root() -> str:
    if not INDEX.exists():
        return "<h1>Thiếu index.html</h1>"
    html = INDEX.read_text(encoding="utf-8")
    marker = "</body>"
    return html.replace(marker, INJECT + marker, 1)
