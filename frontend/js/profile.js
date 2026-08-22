import {$,esc,profilePayload} from './core.js';
const KEY='tvai_profiles_modular_v1';
const read=()=>{try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch{return[]}};
const write=list=>localStorage.setItem(KEY,JSON.stringify(list));
const signature=p=>[p.ten.trim().toLowerCase()||'—',p.ngay,p.thang,p.nam,p.gio_sinh,p.gioi_tinh,p.duong_lich,p.time_zone].join('|');
const hash=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return `TV-${(h>>>0).toString(16).toUpperCase().padStart(8,'0')}`};
export function refreshProfiles(active=''){const sel=$('profileSelect');const list=read();sel.innerHTML='<option value="">Hồ sơ mới</option>'+list.map(p=>`<option value="${esc(p.id)}">${esc(p.name)} · ${esc(p.birth)}</option>`).join('');sel.value=active;const p=list.find(x=>x.id===active);$('profileId').textContent=`ID: ${p?.id||'—'}`}
export function saveCurrentProfile(){const p=profilePayload();const id=hash(signature(p));const item={id,name:p.ten.trim()||'Không tên',birth:`${String(p.ngay).padStart(2,'0')}/${String(p.thang).padStart(2,'0')}/${p.nam}`,...p};const list=read();const i=list.findIndex(x=>x.id===id);if(i>=0)list[i]={...list[i],...item};else list.unshift(item);write(list);refreshProfiles(id);return id}
export function loadProfile(id){const p=read().find(x=>x.id===id);if(!p)return;for(const k of ['ngay','thang','nam','gio_sinh','gioi_tinh','duong_lich','time_zone','ten','nam_xem']){const map={ngay:'day',thang:'month',nam:'year',gio_sinh:'hour',gioi_tinh:'gender',duong_lich:'calendar',time_zone:'tz',ten:'name',nam_xem:'viewYear'};if(p[k]!==undefined)$(map[k]).value=p[k]}$('profileId').textContent=`ID: ${p.id}`}
export function clearProfilesUi(){$('profileSelect').value='';$('profileId').textContent='ID: —'}
