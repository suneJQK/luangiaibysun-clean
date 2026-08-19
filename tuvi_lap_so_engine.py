from __future__ import annotations
from typing import Any
from tuvi_engine._engine import diaBan, lapDiaBan, lapThienBan
BRANCH_TO_INDEX={'Tý':1,'Sửu':2,'Dần':3,'Mão':4,'Thìn':5,'Tỵ':6,'Tị':6,'Ngọ':7,'Mùi':8,'Thân':9,'Dậu':10,'Tuất':11,'Hợi':12}

def _gender_value(v):
    if isinstance(v,int): return 1 if v==1 else -1
    s=str(v).strip().lower()
    if s in {'nam','male','m','1','+1'}: return 1
    if s in {'nữ','nu','female','f','0','-1'}: return -1
    raise ValueError('gioi_tinh phải là Nam/Nữ hoặc 1/-1')
def _hour_branch(v):
    if isinstance(v,int):
        if 1<=v<=12:return v
        raise ValueError('gio_sinh phải nằm trong 1..12')
    s=str(v).strip()
    return _hour_branch(int(s)) if s.isdigit() else BRANCH_TO_INDEX[s]
def _star_dict(s): return {'id':s.get('saoID'),'ten':s.get('saoTen'),'ngu_hanh':s.get('saoNguHanh'),'loai':s.get('saoLoai'),'phuong_vi':s.get('saoPhuongVi'),'am_duong':s.get('saoAmDuong'),'dac_tinh':s.get('saoDacTinh'),'vong_trang_sinh':bool(s.get('vongTrangSinh'))}
def _palace_json(c):
    stars=[_star_dict(x) for x in getattr(c,'cungSao',[])]
    return {'cung':getattr(c,'cungChu',''),'can_chi':getattr(c,'cungTen','').strip(),'dia_chi':getattr(c,'cungDiaChi',''),'ngu_hanh':getattr(c,'cungHanh',''),'am_duong':'Dương' if getattr(c,'cungAmDuong',0)==1 else 'Âm','than_cu':bool(getattr(c,'cungThan',False)),'tuan':bool(getattr(c,'tuanTrung',False)),'triet':bool(getattr(c,'trietLo',False)),'dai_van':{'tuoi_bat_dau':getattr(c,'cungDaiHan',None)},'tieu_van':{'chi':getattr(c,'cungTieuHan',None)},'chinh_tinh':[x for x in stars if x.get('loai')==1],'phu_tinh':[x for x in stars if x.get('loai')!=1 and not x.get('vong_trang_sinh')],'vong_trang_sinh':next((x['ten'] for x in stars if x.get('vong_trang_sinh')),None),'sao':stars}
def lap_la_so(ngay:int,thang:int,nam:int,gio_sinh:str|int,gioi_tinh:str|int,ten:str='',duong_lich:bool=True,time_zone:int=7)->dict[str,Any]:
    gender=_gender_value(gioi_tinh); hour=_hour_branch(gio_sinh)
    db=lapDiaBan(diaBan,ngay,thang,nam,hour,gender,duong_lich,time_zone); tb=lapThienBan(ngay,thang,nam,hour,gender,ten,db,duong_lich,time_zone)
    cungs={}
    for i in range(1,13):
        r=_palace_json(db.thapNhiCung[i]); cungs[r['cung'] or r['dia_chi'] or str(i)]=r
    return {'schema_version':'engine_2.0','source':'local_tuvi_engine','input':{'ngay':ngay,'thang':thang,'nam':nam,'gio_sinh':hour,'gioi_tinh':'Nam' if gender==1 else 'Nữ','duong_lich':duong_lich,'time_zone':time_zone},'thien_ban':{'ten':getattr(tb,'ten',ten),'nam_nu':getattr(tb,'namNu',None),'gio_sinh':getattr(tb,'gioSinh',None),'can_nam':getattr(tb,'canNamTen',None),'chi_nam':getattr(tb,'chiNamTen',None),'can_thang':getattr(tb,'canThangTen',None),'can_ngay':getattr(tb,'canNgayTen',None),'menh':getattr(tb,'menh',None),'ban_menh':getattr(tb,'banMenh',None),'ten_cuc':getattr(tb,'tenCuc',None),'menh_chu':getattr(tb,'menhChu',None),'than_chu':getattr(tb,'thanChu',None),'am_duong_menh':getattr(tb,'amDuongMenh',None),'sinh_khac':getattr(tb,'sinhKhac',None)},'12_cung':cungs}
