from .AmDuong import *
from .Sao import *

def lapDiaBan(diaBan,nn,tt,nnnn,gioSinh,gioiTinh,duongLich,timeZone):
    if duongLich: nn,tt,nnnn,_=ngayThangNam(nn,tt,nnnn,True,timeZone)
    canThang,canNam,chiNam=ngayThangNamCanChi(nn,tt,nnnn,False,timeZone)
    db=diaBan(tt,gioSinh,thienCan[canNam]); ad=thienCan[canNam]['amDuong']; adc=diaChi[chiNam]['amDuong']
    cuc=nguHanh(timCuc(db.cungMenh,canNam)); cucSo=cuc['cuc']; db.nhapDaiHan(cucSo,gioiTinh*adc)
    db.nhapTieuHan(dichCung(11,-3*(chiNam-1)),gioiTinh,chiNam)
    tv=timTuVi(cucSo,nn); db.nhapSao(tv,saoTuVi)
    for off,star in [(4,saoLiemTrinh),(7,saoThienDong),(8,saoVuKhuc),(9,saoThaiDuong),(11,saoThienCo)]: db.nhapSao(dichCung(tv,off),star)
    tp=dichCung(3,3-tv)
    for off,star in [(0,saoThienPhu),(1,saoThaiAm),(2,saoThamLang),(3,saoCuMon),(4,saoThienTuong),(5,saoThienLuong),(6,saoThatSat),(10,saoPhaQuan)]: db.nhapSao(dichCung(tp,off),star)
    loc=thienCan[canNam]['vitriDiaBan']; db.nhapSao(loc,saoLocTon,saoBacSy)
    adnn=gioiTinh*ad
    for off,star in [(1,saoLucSi),(2,saoThanhLong),(3,saoTieuHao),(4,saoTuongQuan),(5,saoTauThu),(6,saoPhiLiem),(7,saoHyThan),(8,saoBenhPhu),(9,saoDaiHao),(10,saoPhucBinh),(11,saoQuanPhu2)]: db.nhapSao(dichCung(loc,off*adnn),star)
    ttpos=chiNam
    for off,star in [(0,saoThaiTue),(1,saoThieuDuong),(2,saoTangMon),(3,saoThieuAm),(4,saoQuanPhu3),(5,saoTuPhu),(6,saoTuePha),(7,saoLongDuc),(8,saoBachHo),(9,saoPhucDuc),(10,saoDieuKhach),(11,saoTrucPhu)]: db.nhapSao(dichCung(ttpos,off),star)
    ts=timTrangSinh(cucSo)
    trang=[saoTrangSinh,saoMocDuc,saoQuanDoi,saoLamQuan,saoDeVuong,saoSuy,saoBenh,saoTu,saoMo,saoTuyet,saoThai,saoDuong]
    for i,s in enumerate(trang): db.nhapSao(dichCung(ts,(i if i<9 else i-12)*gioiTinh*ad),s)
    db.nhapSao(dichCung(loc,-1),saoDaLa); db.nhapSao(dichCung(loc,1),saoKinhDuong)
    dj=dichCung(11,gioSinh); db.nhapSao(dj,saoDiaKiep); db.nhapSao(dichCung(12,12-dj),saoDiaKhong)
    h,l=timHoaLinh(chiNam,gioSinh,gioiTinh,ad); db.nhapSao(h,saoHoaTinh); db.nhapSao(l,saoLinhTinh)
    long=dichCung(5,chiNam-1); db.nhapSao(long,saoLongTri); db.nhapSao(dichCung(2,2-long),saoPhuongCac,saoGiaiThan)
    ta=dichCung(5,tt-1); db.nhapSao(ta,saoTaPhu); db.nhapSao(dichCung(2,2-ta),saoHuuBat)
    vk=dichCung(5,gioSinh-1); db.nhapSao(vk,saoVanKhuc); vx=dichCung(2,2-vk); db.nhapSao(vx,saoVanXuong)
    aq=dichCung(vx,nn-2); db.nhapSao(aq,saoAnQuang); db.nhapSao(dichCung(2,2-aq),saoThienQuy)
    tk=timThienKhoi(canNam); db.nhapSao(tk,saoThienKhoi); db.nhapSao(dichCung(5,5-tk),saoThienViet)
    db.nhapSao(dichCung(7,chiNam-1),saoThienHu); db.nhapSao(dichCung(7,-chiNam+1),saoThienKhoc)
    db.nhapSao(dichCung(db.cungMenh,chiNam-1),saoThienTai); db.nhapSao(dichCung(db.cungThan,chiNam-1),saoThienTho)
    hl=dichCung(4,-chiNam+1); db.nhapSao(hl,saoHongLoan); db.nhapSao(dichCung(hl,6),saoThienHy)
    tq,tf=timThienQuanThienPhuc(canNam); db.nhapSao(tq,saoThienQuan); db.nhapSao(tf,saoThienPhuc)
    th=dichCung(10,tt-1); db.nhapSao(th,saoThienHinh); db.nhapSao(dichCung(th,4),saoThienRieu,saoThienY)
    co=timCoThan(chiNam); db.nhapSao(co,saoCoThan); db.nhapSao(dichCung(co,-4),saoQuaTu)
    db.nhapSao(dichCung(dichCung(loc,1),2),saoVanTinh); db.nhapSao(dichCung(dichCung(loc,1),4),saoDuongPhu); db.nhapSao(dichCung(dichCung(loc,1),7),saoQuocAn)
    db.nhapSao(dichCung(vk,2),saoThaiPhu); db.nhapSao(dichCung(vk,-2),saoPhongCao)
    db.nhapSao(5,saoThienLa); db.nhapSao(11,saoDiaVong); db.nhapSao(db.cungNoboc,saoThienThuong); db.nhapSao(db.cungTatAch,saoThienSu)
    ma=timThienMa(chiNam); db.nhapSao(ma,saoThienMa); db.nhapSao(dichCung(ma,2),saoHoaCai); db.nhapSao(dichCung(ma,3),saoKiepSat); db.nhapSao(dichCung(ma,7),saoDaoHoa)
    # Phá Toái: công thức local, không phụ thuộc MCP
    db.nhapSao(timPhaToai(chiNam),saoPhaToai)
    dq=dichCung(chiNam,-tt+gioSinh); db.nhapSao(dq,saoDauQuan)
    hoa={1:(dichCung(tv,4),dichCung(tp,10),dichCung(tv,8),dichCung(tv,9)),2:(dichCung(tv,11),dichCung(tp,5),tv,dichCung(tp,1)),3:(dichCung(tv,7),dichCung(tv,11),vx,dichCung(tv,4)),4:(dichCung(tp,1),dichCung(tv,7),dichCung(tv,11),dichCung(tp,3)),5:(dichCung(tp,2),dichCung(tp,1),dichCung(2,2-ta),dichCung(tv,11)),6:(dichCung(tv,8),dichCung(tp,2),dichCung(tp,5),vk),7:(dichCung(tv,9),dichCung(tv,8),dichCung(tv,7),dichCung(tp,1)),8:(dichCung(tp,3),dichCung(tv,9),vk,vx),9:(dichCung(tp,5),tv,tp,dichCung(tv,8)),10:(dichCung(tp,10),dichCung(tp,3),dichCung(tp,1),dichCung(tp,2))}[canNam]
    for p,s in zip(hoa,[saoHoaLoc,saoHoaQuyen,saoHoaKhoa,saoHoaKy]): db.nhapSao(p,s)
    lh,tc=timLuuTru(canNam); db.nhapSao(lh,saoLuuHa); db.nhapSao(tc,saoThienTru)
    end=dichCung(chiNam,10-canNam); t1=dichCung(end,1); db.nhapTuan(t1,dichCung(t1,1)); tr1,tr2=timTriet(canNam); db.nhapTriet(tr1,tr2)
    return db
