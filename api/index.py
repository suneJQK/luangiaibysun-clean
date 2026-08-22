from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from tuvi_lap_so_engine import lap_la_so
from tu_vi_calculator import calculate_chart
from chart_sanitizer import normalize_engine_chart
from tuvi_engine.data_loader import load_cach_cuc
from tuvi_engine.rules.analysis import analyze_chart
from ai_providers.router import generate as generate_ai, normalize_provider

ROOT = Path(__file__).resolve().parent.parent
BOOKS_FILE = ROOT / "books_cache.json"
ROOT_PROMPT_FILE = ROOT / "system_prompt_tuvi.txt"
PROMPT_DIR = ROOT / "system_prompts"
AI_MODE_DIR = ROOT / "ai_modes"
WEB_INDEX = ROOT / "index.html"
AI_MODE_INDEX = ROOT / "ai_mode.html"
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

app = FastAPI(title="TV AI - Tử Vi Đẩu Số", version="2.9")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

class BirthRequest(BaseModel):
    ngay: int = Field(ge=1, le=31)
    thang: int = Field(ge=1, le=12)
    nam: int = Field(ge=1800, le=2200)
    gio_sinh: str | int
    gioi_tinh: str
    ten: str = ""
    duong_lich: bool = True
    time_zone: float = 7.0
    nam_xem: int | None = Field(default=None, ge=1800, le=2200)
    thang_xem: int | None = Field(default=None, ge=1, le=12)
    ngay_xem: int | None = Field(default=None, ge=1, le=31)
    gio_xem: int | None = Field(default=None, ge=1, le=12)

class AskRequest(BirthRequest):
    question: str = Field(min_length=1, max_length=8000)
    year: int | None = Field(default=None, ge=1800, le=2200)
    provider: str | None = None

def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default

def _system_prompt() -> str:
    parts: list[str] = []
    if ROOT_PROMPT_FILE.exists():
        parts.append(ROOT_PROMPT_FILE.read_text(encoding="utf-8").strip())
    if PROMPT_DIR.exists():
        for path in sorted(PROMPT_DIR.glob("*.txt")):
            text = path.read_text(encoding="utf-8").strip()
            if text:
                parts.append(text)
    return "\n\n".join(x for x in parts if x) or "Bạn là chuyên gia Tử Vi Đẩu Số."

def _available_ai_modes() -> list[dict[str, str]]:
    modes: list[dict[str, str]] = []
    if not AI_MODE_DIR.exists(): return modes
    for path in sorted(AI_MODE_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        first_line = next((x.strip() for x in text.splitlines() if x.strip()), "")
        name = first_line.split(":", 1)[1].strip() if ":" in first_line else path.stem
        modes.append({"id": path.stem, "name": name, "file": path.name})
    return modes

def _load_ai_mode(mode_id: str | None) -> tuple[str, str]:
    modes = _available_ai_modes()
    if not modes: return "", "standard"
    wanted = (mode_id or "standard").strip().lower()
    path = AI_MODE_DIR / f"{wanted}.txt"
    if not path.exists():
        path = AI_MODE_DIR / f"{modes[0]['id']}.txt"
        wanted = modes[0]["id"]
    return path.read_text(encoding="utf-8").strip(), wanted

def _compact(value: Any, limit: int = 90000) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text if len(text) <= limit else text[:limit] + "..."

def _prepare_chart(req: BirthRequest) -> dict[str, Any]:
    chart = lap_la_so(req.ngay, req.thang, req.nam, req.gio_sinh, req.gioi_tinh, req.ten, req.duong_lich, req.time_zone)
    if len(chart.get("12_cung", {})) != 12: raise ValueError("Engine không tạo đủ 12 cung")
    analyzed = analyze_chart(chart)
    analyzed.setdefault("input", {})["lich"] = "Dương lịch" if req.duong_lich else "Âm lịch"
    return normalize_engine_chart(analyzed)

def _view_year(req: BirthRequest, explicit_year: int | None = None) -> int:
    return int(explicit_year if explicit_year is not None else (req.nam_xem if req.nam_xem is not None else date.today().year))

def _view_args(req: BirthRequest, default_year: int | None = None) -> dict[str, Any]:
    return {"year": _view_year(req, default_year), "month": req.thang_xem, "day": req.ngay_xem, "hour": req.gio_xem}

def _save_profile(req: BirthRequest) -> dict[str, Any]:
    try:
        from google_sheets_storage import save_user_profile
        created_at = datetime.now(timezone.utc).astimezone(VN_TZ).isoformat(timespec="seconds")
        name = req.ten.strip() or "—"
        birth_date = f"{req.ngay:02d}/{req.thang:02d}/{req.nam:04d}"
        return save_user_profile(
            user_id=str(uuid.uuid4()),
            name=name,
            ngay_sinh=birth_date,
            gio_sinh=str(req.gio_sinh),
            gioi_tinh=req.gioi_tinh,
            lich="Dương lịch" if req.duong_lich else "Âm lịch",
            time_zone=req.time_zone,
            created_at=created_at,
        )
    except Exception as exc:
        return {"saved": False, "error": f"{type(exc).__name__}: {exc}"}

def _assert_ai_payload_sync(calc: dict[str, Any], ai_context: dict[str, Any]) -> None:
    van = calc.get("van") or {}
    authoritative = van.get("tieu_van") or {}
    synced = (van.get("sync_contract") or {}).get("tieu_van_cung_so")
    if synced != authoritative.get("cung_so"): raise ValueError("Dữ liệu Tiểu vận nội bộ không đồng bộ")
    context_van = ai_context.get("van_han") or {}
    if (context_van.get("tieu_van") or {}) != authoritative: raise ValueError("AI context và Tiểu vận authoritative không đồng bộ")
    palaces = ai_context.get("palaces") or {}
    palace_items = palaces.values() if isinstance(palaces, dict) else palaces
    forbidden = {"dai_van", "tieu_van", "luu_nien", "luu_dai_van", "luu_nguyet", "luu_nhat", "luu_thoi"}
    for palace in palace_items:
        if isinstance(palace, dict) and forbidden.intersection(palace): raise ValueError("AI context còn chứa dynamic vận tĩnh trong từng cung")

def _ai_context_for_request(chart: dict[str, Any], calc: dict[str, Any]) -> dict[str, Any]:
    context = chart.get("ai_context")
    if not isinstance(context, dict): raise ValueError("Thiếu AI context authoritative")
    _assert_ai_payload_sync(calc, context)
    return context

def _inject_viewing_year_ui(html: str) -> str:
    marker = '<div class="field"><label>Giới tính</label>'
    year_field = '<div class="field view-year-field"><label>Năm xem</label><input id="viewYear" type="number" min="1800" max="2200" step="1" inputmode="numeric" aria-label="Năm xem"><div class="field-help">Năm dùng để tính Đại vận/Lưu niên Đại vận/Tiểu vận/Lưu niên năm. Không phải năm sinh.</div></div>'
    if 'id="viewYear"' not in html and marker in html: html = html.replace(marker, year_field + marker, 1)
    script = r'''
<script>
(function(){
  const currentYear=new Date().getFullYear(), MIN_YEAR=1800, MAX_YEAR=2200;
  const byId=id=>document.getElementById(id);
  const normalizeYear=value=>{const n=Number(value); if(!Number.isFinite(n)) return currentYear; return Math.min(MAX_YEAR,Math.max(MIN_YEAR,Math.trunc(n)));};
  const esc=v=>String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;');
  const BRANCH_NAMES={1:'Tý',2:'Sửu',3:'Dần',4:'Mão',5:'Thìn',6:'Tỵ',7:'Ngọ',8:'Mùi',9:'Thân',10:'Dậu',11:'Tuất',12:'Hợi',ty1:'Tý',ty2:'Tỵ',ty:'Tý',suu:'Sửu',dan:'Dần',mao:'Mão',thin:'Thìn',ngo:'Ngọ',mui:'Mùi',than:'Thân',dau:'Dậu',tuat:'Tuất',hoi:'Hợi'};
  const branchName=value=>{
    if(value==null) return '';
    const raw=String(value).trim();
    return BRANCH_NAMES[raw.toLowerCase()] || BRANCH_NAMES[Number(raw)] || raw;
  };
  const viewYear=byId('viewYear');
  if(viewYear){viewYear.min=String(MIN_YEAR);viewYear.max=String(MAX_YEAR);viewYear.step='1';viewYear.value=normalizeYear(viewYear.value||currentYear);viewYear.addEventListener('change',()=>{viewYear.value=normalizeYear(viewYear.value);});}
  const setViewYear=y=>{if(viewYear){viewYear.value=normalizeYear(y);viewYear.dispatchEvent(new Event('change'));}};
  const firstArray=(...vals)=>vals.find(v=>Array.isArray(v)&&v.length) || [];
  const luckList=van=>{const v=van||{};return firstArray(v.luu_nien_dai_van_10_nam,v.luu_dai_van_10_nam);};
  const smallList=van=>{const v=van||{};return firstArray(v.tieu_van_10_nam,v.luu_nien_tieu_van_10_nam);};
  const yearList=van=>{const v=van||{};return firstArray(v.luu_nien_nam_10_nam,v.luu_nien_tieu_van_10_nam);};
  const palaceName=x=>x?.cung || (x?.cung_so!=null?('Cung '+x.cung_so):'—');
  const compactCell=x=>{
    if(!x || typeof x!=='object') return esc(x??'—');
    const name=palaceName(x);
    const branch=branchName(x.chi_ten ?? x.dia_chi ?? x.chi);
    const canChi=x.can_chi || '';
    return '<b>'+esc(name)+'</b>'+(branch?' <span class="luck-branch">('+esc(branch)+(canChi?' · '+esc(canChi):'')+')</span>':'');
  };
  const normalizeText=v=>String(v??'').replace(/\s+/g,' ').trim().toLowerCase();
  const syncModifierPanel=()=>{
    const mod=byId('modList');
    const cach=byId('cachList');
    if(!mod) return;
    const card=mod.closest('.panel.card') || mod.parentElement;
    const cachNames=new Set();
    if(cach){
      cach.querySelectorAll('*').forEach(el=>{if(el.children.length===0){const t=normalizeText(el.textContent);if(t)cachNames.add(t);}});
    }
    const seen=new Set();
    [...mod.children].forEach(el=>{
      const key=normalizeText(el.textContent);
      if(!key) return;
      if(seen.has(key) || cachNames.has(key)) el.remove();
      else seen.add(key);
    });
    const text=normalizeText(mod.textContent);
    const empty=!text || /^(không có|không có modifier|chưa có|none|n\/a|—|-)$/.test(text);
    if(card) card.style.display=empty?'none':'';
  };
  const observeModifierPanel=()=>{
    const mod=byId('modList');
    if(!mod) return;
    syncModifierPanel();
    new MutationObserver(()=>syncModifierPanel()).observe(mod,{childList:true,subtree:true,characterData:true});
  };
  window.renderVan10=function(chart){
    const root=byId('van10Panel');
    if(!root) return;
    const van=chart?.van||{};
    const dvBase=(van.dai_van_10_nam && typeof van.dai_van_10_nam==='object' && !Array.isArray(van.dai_van_10_nam)) ? van.dai_van_10_nam : {};
    const lndv=luckList(van), tv=smallList(van), lnn=yearList(van), rows=[];
    for(let i=0;i<10;i++){
      const b=lndv[i]||{}, c=tv[i]||{}, d=lnn[i]||{};
      const year=b.nam ?? c.nam ?? d.nam ?? (i+1), tuoi=b.tuoi ?? c.tuoi ?? d.tuoi ?? '—';
      if(year==null) continue;
      const a={...dvBase,nam:year,tuoi:tuoi};
      rows.push('<tr data-year="'+esc(year)+'" class="'+(Number(year)===Number(viewYear?.value)?'is-viewing':'')+'"><td><button type="button" class="year-pick" data-year="'+esc(year)+'">'+esc(year)+'</button></td><td>'+esc(tuoi)+'</td><td>'+compactCell(a)+'</td><td>'+compactCell(b)+'</td><td>'+compactCell(c)+'</td><td>'+compactCell(d)+'</td></tr>');
    }
    root.innerHTML='<div class="panel card luck10-card"><div class="section-title"><h3>Vận 10 năm</h3><small>4 lớp vận hạn độc lập</small></div><div class="luck10-note">📌 Các năm dưới đây là các năm có thể chọn để đặt câu hỏi cho AI. Chọn đúng năm để AI luận Đại vận, Lưu niên Đại vận, Tiểu vận và Lưu niên năm của năm đó.</div><div class="luck10-wrap"><table class="luck10"><thead><tr><th>Năm</th><th>Tuổi</th><th>Đại vận</th><th>Lưu niên Đại vận</th><th>Tiểu vận</th><th>Lưu niên năm</th></tr></thead><tbody>'+(rows.join('')||'<tr><td colspan="6">Engine chưa trả dữ liệu 10 năm.</td></tr>')+'</tbody></table></div></div>';
    root.querySelectorAll('.year-pick').forEach(btn=>btn.addEventListener('click',()=>{const y=normalizeYear(btn.dataset.year);setViewYear(y);window.lapSo?.();}));
    observeModifierPanel();
  };
  try{
    const oldLoad=window.loadUserProfile;
    window.loadUserProfile=function(){if(typeof oldLoad==='function') oldLoad();const p=JSON.parse(localStorage.getItem('tvai_user_profile_v1')||'null');if(p&&p.viewYear!=null)setViewYear(p.viewYear);else setViewYear(currentYear);};
    const oldSave=window.saveUserProfile;
    window.saveUserProfile=function(){if(typeof oldSave==='function') oldSave();const p=JSON.parse(localStorage.getItem('tvai_user_profile_v1')||'{}');p.viewYear=normalizeYear(viewYear?.value||currentYear);localStorage.setItem('tvai_user_profile_v1',JSON.stringify(p));};
    const oldLap=window.lapSo;
    window.lapSo=async function(){await oldLap();window.renderVan10?.(window.chart);};
    document.addEventListener('click',e=>{
      const tab=e.target.closest?.('.tab[data-tab="cach"]');
      if(tab) setTimeout(observeModifierPanel,0);
    });
  }catch(err){console.warn('Vận 10 năm UI patch:',err);}
})();
</script>
'''
    style='<style>.luck10-card{margin:12px 0;padding:15px}.luck10-note{margin:9px 0;padding:9px 11px;border:1px solid #30435f;border-radius:10px;background:#09111e;color:#aebbd0;font-size:12px}.luck10-wrap{overflow:auto}.luck10{width:100%;border-collapse:collapse;min-width:860px}.luck10 th,.luck10 td{padding:8px 9px;border:1px solid #30435f;text-align:left;vertical-align:top}.luck10 th{background:#172238;color:#f4d996;font-size:12px}.luck10 td{background:#0b111d;color:#dfe7f6;font-size:12px}.luck10 tr.is-viewing td{background:#211b11;border-color:#876e3d}.luck10 .year-pick{border:1px solid #8a7040;background:#172238;color:#f4d996;border-radius:7px;padding:4px 8px;cursor:pointer;font-weight:800}.luck10 .year-pick:hover{background:#211b11}.luck-branch{color:#93a0b6;font-size:10px}</style>'
    return html.replace('</head>', style + '</head>').replace('<div id="dashboard" style="display:none">','<div id="dashboard" style="display:none"><div id="van10Panel"></div>',1).replace('</body>', script + '</body>')

@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    if not WEB_INDEX.exists(): raise HTTPException(status_code=500, detail="Thiếu index.html")
    return HTMLResponse(_inject_viewing_year_ui(WEB_INDEX.read_text(encoding="utf-8")))

@app.get("/ai-mode", response_class=FileResponse)
def ai_mode_page() -> FileResponse:
    if not AI_MODE_INDEX.exists(): raise HTTPException(status_code=500, detail="Thiếu ai_mode.html")
    return FileResponse(AI_MODE_INDEX, media_type="text/html")

@app.get("/api/health")
def health() -> dict[str, Any]: return {"status":"ok","service":"tv-ai","version":"2.9"}

@app.get("/api/ai-modes")
def ai_modes() -> dict[str, Any]: return {"modes":_available_ai_modes()}

@app.get("/api/ai-providers")
def ai_providers() -> dict[str, Any]: return {"providers":[{"id":"gemini","name":"Gemini","env_key":"GEMINI_API_KEY","model_env":"GEMINI_MODEL"},{"id":"openai","name":"ChatGPT / OpenAI","env_key":"OPENAI_API_KEY","model_env":"OPENAI_MODEL"}]}

@app.get("/api/google-sheets-test")
def google_sheets_test() -> dict[str, Any]:
    try:
        import google_sheets_storage as storage
        result = storage.save_user_profile(user_id="diagnostic",name="_TEST_",ngay_sinh="01/01/2000",gio_sinh="Tý",gioi_tinh="Nam",lich="Dương lịch",time_zone=7,created_at=datetime.now(timezone.utc).astimezone(VN_TZ).isoformat(timespec="seconds"))
        return {"ok":True,"result":result}
    except Exception as exc: return {"ok":False,"error_type":type(exc).__name__,"error":str(exc)}

@app.get("/api/cach-cuc")
def cach_cuc() -> dict[str, Any]: return {"count":len(load_cach_cuc()),"items":load_cach_cuc()}

@app.post("/api/lap-so")
def lap_so(req: BirthRequest) -> dict[str, Any]:
    try:
        chart=_prepare_chart(req);calc=calculate_chart(chart,**_view_args(req));chart["van"]=calc.get("van",{});chart.setdefault("viewing",{})["year"]=_view_year(req);chart.setdefault("storage",{})["user_profile"]=_save_profile(req);return chart
    except Exception as exc: raise HTTPException(status_code=400,detail=f"Không thể lập lá số: {type(exc).__name__}: {exc}") from exc

@app.post("/api/luan-giai")
def luan_giai(req: AskRequest, request: Request) -> dict[str, Any]:
    try:
        viewing_year=_view_year(req,req.year);req.nam_xem=viewing_year;chart=_prepare_chart(req);calc=calculate_chart(chart,**_view_args(req,viewing_year));chart["van"]=calc.get("van",{});chart.setdefault("viewing",{})["year"]=viewing_year
        context=_ai_context_for_request(chart,calc);mode_text,mode_id=_load_ai_mode(request.cookies.get("tv_ai_mode", "standard"));books=_load_json(BOOKS_FILE,[])
        payload={"question":req.question,"year":viewing_year,"mode":mode_id,"mode_prompt":mode_text,"chart_context":context,"books":books}
        prompt=_compact(payload);system=_system_prompt();answer,selected_provider=generate_ai(provider=normalize_provider(req.provider or request.cookies.get("tv_ai_provider","gemini")),system_instruction=system,prompt=prompt)
        return {"chart":chart,"calculation":calc,"answer":answer,"ai_status":"ok","ai_mode":mode_id,"ai_provider":selected_provider,"year":viewing_year}
    except Exception as exc: raise HTTPException(status_code=500,detail=f"Không thể luận giải: {type(exc).__name__}: {exc}") from exc
