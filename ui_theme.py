from __future__ import annotations

from pathlib import Path
from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parent

STAR_ELEMENTS = {
    'Tử vi':'tho','Liêm trinh':'hoa','Thiên đồng':'tho','Vũ khúc':'kim','Thái Dương':'hoa','Thiên cơ':'mộc',
    'Thiên phủ':'tho','Thái âm':'tho','Tham lang':'tho','Cự môn':'tho','Thiên tướng':'tho','Thiên lương':'tho','Thất sát':'kim','Phá quân':'tho',
    'Thái tuế':'hoa','Thiếu dương':'hoa','Tang môn':'mộc','Thiếu âm':'thủy','Quan phù':'hoa','Tử phù':'kim','Tuế phá':'hoa','Long đức':'thủy','Bạch hổ':'kim','Phúc đức':'tho','Điếu khách':'hoa','Trực phù':'kim',
    'Lộc tồn':'tho','Bác sỹ':'thủy','Lực sĩ':'hoa','Thanh long':'thủy','Tiểu hao':'hoa','Tướng quân':'mộc','Tấu thư':'kim','Phi liêm':'hoa','Hỷ thần':'hoa','Bệnh phù':'tho','Đại hao':'hoa','Phục binh':'hoa',
    'Tràng sinh':'thủy','Mộc dục':'thủy','Quan đới':'kim','Lâm quan':'kim','Đế vượng':'kim','Suy':'thủy','Bệnh':'hoa','Tử':'hoa','Mộ':'tho','Tuyệt':'tho','Thai':'tho','Dưỡng':'mộc',
    'Đà la':'kim','Kình dương':'kim','Địa không':'hoa','Địa kiếp':'hoa','Linh tinh':'hoa','Hỏa tinh':'hoa',
    'Văn xương':'kim','Văn Khúc':'thủy','Thiên khôi':'hoa','Thiên việt':'hoa','Tả phù':'tho','Hữu bật':'thủy','Long trì':'thủy','Phượng các':'tho','Tam thai':'tho','Bát tọa':'tho','Ân quang':'mộc','Thiên quý':'tho',
    'Thiên khốc':'thủy','Thiên hư':'thủy','Thiên đức':'hoa','Nguyệt đức':'hoa','Thiên hình':'hoa','Thiên riêu':'thủy','Thiên y':'thủy','Quốc ấn':'tho','Đường phù':'mộc','Đào hoa':'mộc','Hồng loan':'thủy','Thiên hỷ':'thủy','Thiên giải':'hoa','Địa giải':'tho','Giải thần':'mộc','Thai phụ':'tho','Phong cáo':'tho','Thiên tài':'tho','Thiên thọ':'tho','Thiên thương':'tho','Thiên sứ':'thủy','Thiên la':'tho','Địa võng':'tho',
    'Hóa khoa':'kim','Hóa quyền':'hoa','Hóa lộc':'mộc','Hóa kỵ':'thủy','Cô thần':'tho','Quả tú':'tho','Thiên mã':'hoa','Phá toái':'hoa','Thiên quan':'hoa','Thiên phúc':'hoa','Lưu hà':'thủy','Thiên trù':'tho','Kiếp sát':'hoa','Hoa cái':'kim','LN. Văn tinh':'hoa','Đẩu quân':'hoa','Thiên không':'hoa',
}

THEME_CSS = r'''
/* Ngũ hành có độ ưu tiên cao hơn màu Chính tinh/Hung tinh cũ. */
#board .chip.star-element,#detail .chip.star-element{font-weight:850!important;background:#172640!important}
#board .chip.star-element.nh-moc,#detail .chip.star-element.nh-moc{color:#54d477!important;border-color:#2f7d45!important;background:rgba(43,132,70,.16)!important}
#board .chip.star-element.nh-hoa,#detail .chip.star-element.nh-hoa{color:#ff6868!important;border-color:#9b3d3d!important;background:rgba(180,52,52,.16)!important}
#board .chip.star-element.nh-tho,#detail .chip.star-element.nh-tho{color:#e6bd68!important;border-color:#8d713b!important;background:rgba(173,128,45,.16)!important}
#board .chip.star-element.nh-kim,#detail .chip.star-element.nh-kim{color:#edf2f8!important;border-color:#748091!important;background:rgba(205,214,226,.15)!important}
#board .chip.star-element.nh-thuy,#detail .chip.star-element.nh-thuy{color:#5aa9ff!important;border-color:#356fa7!important;background:rgba(47,115,190,.16)!important}
.ngu-hanh-legend{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px;font-size:9px;color:#93a0b6}
.nh-item{padding:2px 7px;border-radius:999px;border:1px solid #30435f;font-weight:750}
.nh-moc{color:#54d477;border-color:#2f7d45}.nh-hoa{color:#ff6868;border-color:#9b3d3d}.nh-tho{color:#e6bd68;border-color:#8d713b}.nh-kim{color:#edf2f8;border-color:#748091}.nh-thuy{color:#5aa9ff;border-color:#356fa7}
'''

THEME_JS = r"""
(() => {
  const STAR_ELEMENTS = %r;
  const COLORS = {
    moc:  {color:'#54d477', border:'#2f7d45', bg:'rgba(43,132,70,.16)'},
    hoa:  {color:'#ff6868', border:'#9b3d3d', bg:'rgba(180,52,52,.16)'},
    tho:  {color:'#e6bd68', border:'#8d713b', bg:'rgba(173,128,45,.16)'},
    kim:  {color:'#edf2f8', border:'#748091', bg:'rgba(205,214,226,.15)'},
    thuy: {color:'#5aa9ff', border:'#356fa7', bg:'rgba(47,115,190,.16)'}
  };
  const normalize = v => String(v ?? '').trim().replace(/\s+/g,' ').toLowerCase();
  const elementOf = name => {
    const s = String(name ?? '').trim();
    if (STAR_ELEMENTS[s]) return STAR_ELEMENTS[s];
    const key = Object.keys(STAR_ELEMENTS).find(k => normalize(k) === normalize(s));
    return key ? STAR_ELEMENTS[key] : '';
  };
  function colorizeStars(){
    document.querySelectorAll('#board .chip, #detail .chip').forEach(el => {
      const name = String(el.textContent || '').split(' [')[0].trim();
      const nh = elementOf(name);
      if (!nh || !COLORS[nh]) return;
      const c = COLORS[nh];
      el.classList.remove('main','bad','moc','hoa','tho','kim','thuy');
      el.classList.add('star-element','nh-'+nh);
      el.dataset.nguHanh = nh;
      el.dataset.starName = name;
      el.style.setProperty('color', c.color, 'important');
      el.style.setProperty('border-color', c.border, 'important');
      el.style.setProperty('background', c.bg, 'important');
    });
  }
  function addLegend(){
    const legend=document.querySelector('#chart .legend');
    if(!legend || legend.dataset.nhLegend==='1') return;
    legend.dataset.nhLegend='1';
    legend.insertAdjacentHTML('afterend','<div class="ngu-hanh-legend"><span class="nh-item nh-moc">Mộc</span><span class="nh-item nh-hoa">Hỏa</span><span class="nh-item nh-tho">Thổ</span><span class="nh-item nh-kim">Kim</span><span class="nh-item nh-thuy">Thủy</span></div>');
  }
  const originalRender=window.render;
  if(typeof originalRender==='function') window.render=function(){const r=originalRender.apply(this,arguments);setTimeout(()=>{addLegend();colorizeStars()},0);return r};
  const originalDetail=window.showDetail;
  if(typeof originalDetail==='function') window.showDetail=function(){const r=originalDetail.apply(this,arguments);setTimeout(colorizeStars,0);return r};
  if(document.body) new MutationObserver(colorizeStars).observe(document.body,{subtree:true,childList:true});
  if(document.readyState!=='loading'){addLegend();colorizeStars()}else document.addEventListener('DOMContentLoaded',()=>{addLegend();colorizeStars()});
})();
""" % STAR_ELEMENTS


def themed_index() -> HTMLResponse:
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    html = html.replace('</style>', THEME_CSS + '\n</style>', 1)
    html = html.replace('</body>', '<script>' + THEME_JS + '</script>\n</body>', 1)
    return HTMLResponse(html, media_type='text/html; charset=utf-8')
