from __future__ import annotations

from pathlib import Path

from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parent

THEME_CSS = r'''
/* Ngũ hành cho sao: chỉ tác động phần Địa Bàn, không thay đổi dữ liệu engine. */
.star-element { font-weight: 800; }
.star-element.moc { color: #52d273 !important; border-color: #2f7d45 !important; background: rgba(43,132,70,.16) !important; }
.star-element.hoa { color: #ff6b6b !important; border-color: #9b3d3d !important; background: rgba(180,52,52,.16) !important; }
.star-element.tho { color: #e5bd66 !important; border-color: #8d713b !important; background: rgba(173,128,45,.16) !important; }
.star-element.kim { color: #e7edf5 !important; border-color: #718096 !important; background: rgba(205,214,226,.14) !important; }
.star-element.thuy { color: #5da9ff !important; border-color: #356fa7 !important; background: rgba(47,115,190,.16) !important; }
.ngu-hanh-legend{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px;font-size:9px;color:#93a0b6}
.nh-item{padding:2px 7px;border-radius:999px;border:1px solid #30435f;font-weight:700}
.nh-moc{color:#52d273;border-color:#2f7d45}.nh-hoa{color:#ff6b6b;border-color:#9b3d3d}.nh-tho{color:#e5bd66;border-color:#8d713b}.nh-kim{color:#e7edf5;border-color:#718096}.nh-thuy{color:#5da9ff;border-color:#356fa7}
'''

THEME_JS = r'''
(() => {
  const ELEMENT_ALIASES = {
    moc: ['M','Mộc','wood'], hoa: ['H','Hỏa','Hoả','fire'], tho: ['O','Thổ','earth'],
    kim: ['K','Kim','metal'], thuy: ['T','Thủy','Thuỷ','water']
  };
  function normalizeElement(v){
    const s = String(v ?? '').trim().toLowerCase();
    for (const [key, vals] of Object.entries(ELEMENT_ALIASES)) {
      if (vals.some(x => s === String(x).toLowerCase())) return key;
    }
    return '';
  }
  function starElement(x){
    return normalizeElement(x?.ngu_hanh ?? x?.nguHanh ?? x?.sao_ngu_hanh ?? x?.element ?? x?.nguhanh ?? x?.hanh ?? '');
  }
  function colorizeStars(){
    document.querySelectorAll('#board .chip, #detail .chip').forEach(el => {
      const text = el.textContent || '';
      const current = el.dataset.nh;
      if (current) return;
      const candidates = window.__tvai_chart_star_index || [];
      const match = candidates.find(s => {
        const n = String(s?.ten ?? s?.name ?? s?.sao ?? '').trim();
        return n && text.startsWith(n);
      });
      const nh = starElement(match);
      if (nh) {
        el.classList.add('star-element', nh);
        el.dataset.nh = nh;
      }
    });
  }
  function buildStarIndex(c){
    const out=[];
    for (const p of Object.values(c?.['12_cung'] || {})) {
      for (const listName of ['chinh_tinh','phu_tinh']) {
        for (const s of (p?.[listName] || [])) out.push(s);
      }
    }
    window.__tvai_chart_star_index = out;
  }
  function addLegend(){
    const chartPane=document.querySelector('#chart .chart');
    const legend=chartPane?.querySelector('.legend');
    if(!legend || legend.dataset.nhLegend==='1') return;
    legend.dataset.nhLegend='1';
    legend.insertAdjacentHTML('afterend','<div class="ngu-hanh-legend"><span class="nh-item nh-moc">Mộc</span><span class="nh-item nh-hoa">Hỏa</span><span class="nh-item nh-tho">Thổ</span><span class="nh-item nh-kim">Kim</span><span class="nh-item nh-thuy">Thủy</span></div>');
  }
  const originalRender = window.render;
  if (typeof originalRender === 'function') {
    window.render = function(c){
      const result = originalRender.apply(this, arguments);
      buildStarIndex(c); addLegend(); colorizeStars();
      return result;
    };
  }
  const originalShowDetail = window.showDetail;
  if (typeof originalShowDetail === 'function') {
    window.showDetail = function(p){
      const result = originalShowDetail.apply(this, arguments);
      colorizeStars();
      return result;
    };
  }
  const observer = new MutationObserver(() => colorizeStars());
  observer.observe(document.body, {subtree:true, childList:true});
})();
'''


def themed_index() -> HTMLResponse:
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    html = html.replace('</style>', THEME_CSS + '\n</style>', 1)
    html = html.replace('</body>', '<script>' + THEME_JS + '</script>\n</body>', 1)
    return HTMLResponse(html, media_type='text/html; charset=utf-8')
