# -*- coding: utf-8 -*-
"""
"""
from .AmDuong import (  # nguHanhNapAm,
    diaChi,
    dichCung,
    ngayThangNam,
    ngayThangNamCanChi,
    nguHanh,
    thienCan,
    timCoThan,
    timCuc,
    timHoaLinh,
    timLuuTru,
    timPhaToai,
    timThienKhoi,
    timThienMa,
    timThienQuanThienPhuc,
    timTrangSinh,
    timTriet,
    timTuVi,
)
from .Sao import (
    saoAnQuang,
    saoBachHo,
    saoBacSy,
    saoBatToa,
    saoBenh,
    saoBenhPhu,
    saoCoThan,
    saoCuMon,
    saoDaiHao,
    saoDaLa,
    saoDaoHoa,
    saoDauQuan,
    saoDeVuong,
    saoDiaGiai,
    saoDiaKhong,
    saoDiaKiep,
    saoDiaVong,
    saoDieuKhach,
    saoDuong,
    saoDuongPhu,
    saoGiaiThan,
    saoHoaCai,
    saoHoaKhoa,
    saoHoaKy,
    saoHoaLoc,
    saoHoaQuyen,
    saoHoaTinh,
    saoHongLoan,
    saoHuuBat,
    saoHyThan,
    saoKiepSat,
    saoKinhDuong,
    saoLamQuan,
    saoLiemTrinh,
    saoLinhTinh,
    saoLocTon,
    saoLongDuc,
    saoLongTri,
    saoLucSi,
    saoLuuHa,
    saoMo,
    saoMocDuc,
    saoNguyetDuc,
    saoPhaQuan,
    saoPhaToai,
    saoPhiLiem,
    saoPhongCao,
    saoPhucBinh,
    saoPhucDuc,
    saoPhuongCac,
    saoQuanDoi,
    saoQuanPhu2,
    saoQuanPhu3,
    saoQuaTu,
    saoQuocAn,
    saoSuy,
    saoTamThai,
    saoTangMon,
    saoTaPhu,
    saoTauThu,
    saoThai,
    saoThaiAm,
    saoThaiDuong,
    saoThaiPhu,
    saoThaiTue,
    saoThamLang,
    saoThanhLong,
    saoThatSat,
    saoThienCo,
    saoThienDong,
    saoThienDuc,
    saoThienGiai,
    saoThienHinh,
    saoThienHu,
    saoThienHy,
    saoThienKhoc,
    saoThienKhoi,
    saoThienKhong,
    saoThienLa,
    saoThienLuong,
    saoThienMa,
    saoThienPhu,
    saoThienPhuc,
    saoThienQuan,
    saoThienQuy,
    saoThienRieu,
    saoThienSu,
    saoThienTai,
    saoThienTho,
    saoThienThuong,
    saoThienTru,
    saoThienTuong,
    saoThienViet,
    saoThienY,
    saoThieuAm,
    saoThieuDuong,
    saoTieuHao,
    saoTrangSinh,
    saoTrucPhu,
    saoTu,
    saoTuePha,
    saoTuongQuan,
    saoTuPhu,
    saoTuVi,
    saoTuyet,
    saoVanKhuc,
    saoVanTinh,
    saoVanXuong,
    saoVuKhuc,
)


def lapDiaBan(diaBan, nn, tt, nnnn, gioSinh, gioiTinh, duongLich, timeZone):
    if duongLich is True:
        nn, tt, nnnn, thangNhuan = \
            ngayThangNam(nn, tt, nnnn, duongLich, timeZone)
    canThang, canNam, chiNam = \
        ngayThangNamCanChi(nn, tt, nnnn, False, timeZone)

    diaBan = diaBan(tt, gioSinh, thienCan[canNam])

    amDuongNamSinh = thienCan[canNam]["amDuong"]
    amDuongChiNamSinh = diaChi[chiNam]["amDuong"]

    hanhCuc = timCuc(diaBan.cungMenh, canNam)
    cuc = nguHanh(hanhCuc)
    cucSo = cuc['cuc']

    diaBan = diaBan.nhapDaiHan(cucSo, gioiTinh * amDuongChiNamSinh)

    khoiHan = dichCung(11, -3 * (chiNam - 1))
    diaBan = diaBan.nhapTieuHan(khoiHan, gioiTinh, chiNam)

    viTriTuVi = timTuVi(cucSo, nn)
    diaBan.nhapSao(viTriTuVi, saoTuVi)

    viTriLiemTrinh = dichCung(viTriTuVi, 4)
    diaBan.nhapSao(viTriLiemTrinh, saoLiemTrinh)

    viTriThienDong = dichCung(viTriTuVi, 7)
    diaBan.nhapSao(viTriThienDong, saoThienDong)

    viTriVuKhuc = dichCung(viTriTuVi, 8)
    diaBan.nhapSao(viTriVuKhuc, saoVuKhuc)

    vitriThaiDuong = dichCung(viTriTuVi, 9)
    diaBan.nhapSao(vitriThaiDuong, saoThaiDuong)

    viTriThienCo = dichCung(viTriTuVi, 11)
    diaBan.nhapSao(viTriThienCo, saoThienCo)

    viTriThienPhu = dichCung(3, 3 - viTriTuVi)
    diaBan.nhapSao(viTriThienPhu, saoThienPhu)

    viTriThaiAm = dichCung(viTriThienPhu, 1)
    diaBan.nhapSao(viTriThaiAm, saoThaiAm)

    viTriThamLang = dichCung(viTriThienPhu, 2)
    diaBan.nhapSao(viTriThamLang, saoThamLang)

    viTriCuMon = dichCung(viTriThienPhu, 3)
    diaBan.nhapSao(viTriCuMon, saoCuMon)

    viTriThienTuong = dichCung(viTriThienPhu, 4)
    diaBan.nhapSao(viTriThienTuong, saoThienTuong)

    viTriThienLuong = dichCung(viTriThienPhu, 5)
    diaBan.nhapSao(viTriThienLuong, saoThienLuong)

    viTriThatSat = dichCung(viTriThienPhu, 6)
    diaBan.nhapSao(viTriThatSat, saoThatSat)

    viTriPhaQuan = dichCung(viTriThienPhu, 10)
    diaBan.nhapSao(viTriPhaQuan, saoPhaQuan)

    viTriLocTon = thienCan[canNam]['vitriDiaBan']
    diaBan.nhapSao(viTriLocTon, saoLocTon, saoBacSy)

    amDuongNamNu = gioiTinh * amDuongNamSinh

    viTriLucSi = dichCung(viTriLocTon, 1 * amDuongNamNu)
    diaBan.nhapSao(viTriLucSi, saoLucSi)

    viTriThanhLong = dichCung(viTriLocTon, 2 * amDuongNamNu)
    diaBan.nhapSao(viTriThanhLong, saoThanhLong)

    viTriTieuHao = dichCung(viTriLocTon, 3 * amDuongNamNu)
    diaBan.nhapSao(viTriTieuHao, saoTieuHao)

    viTriTuongQuan = dichCung(viTriLocTon, 4 * amDuongNamNu)
    diaBan.nhapSao(viTriTuongQuan, saoTuongQuan)

    viTriTauThu = dichCung(viTriLocTon, 5 * amDuongNamNu)
    diaBan.nhapSao(viTriTauThu, saoTauThu)

    viTriPhiLiem = dichCung(viTriLocTon, 6 * amDuongNamNu)
    diaBan.nhapSao(viTriPhiLiem, saoPhiLiem)

    viTriHyThan = dichCung(viTriLocTon, 7 * amDuongNamNu)
    diaBan.nhapSao(viTriHyThan, saoHyThan)

    viTriBenhPhu = dichCung(viTriLocTon, 8 * amDuongNamNu)
    diaBan.nhapSao(viTriBenhPhu, saoBenhPhu)

    viTriDaiHao = dichCung(viTriLocTon, 9 * amDuongNamNu)
    diaBan.nhapSao(viTriDaiHao, saoDaiHao)

    viTriPhucBinh = dichCung(viTriLocTon, 10 * amDuongNamNu)
    diaBan.nhapSao(viTriPhucBinh, saoPhucBinh)

    viTriQuanPhu2 = dichCung(viTriLocTon, 11 * amDuongNamNu)
    diaBan.nhapSao(viTriQuanPhu2, saoQuanPhu2)

    viTriThaiTue = chiNam
    diaBan.nhapSao(viTriThaiTue, saoThaiTue)

    viTriThieuDuong = dichCung(viTriThaiTue, 1)
    diaBan.nhapSao(viTriThieuDuong, saoThieuDuong, saoThienKhong)

    viTriTangMon = dichCung(viTriThaiTue, 2)
    diaBan.nhapSao(viTriTangMon, saoTangMon)

    viTriThieuAm = dichCung(viTriThaiTue, 3)
    diaBan.nhapSao(viTriThieuAm, saoThieuAm)

    viTriQuanPhu3 = dichCung(viTriThaiTue, 4)
    diaBan.nhapSao(viTriQuanPhu3, saoQuanPhu3)

    viTriTuPhu = dichCung(viTriThaiTue, 5)
    diaBan.nhapSao(viTriTuPhu, saoTuPhu, saoNguyetDuc)

    viTriTuePha = dichCung(viTriThaiTue, 6)
    diaBan.nhapSao(viTriTuePha, saoTuePha)

    viTriLongDuc = dichCung(viTriThaiTue, 7)
    diaBan.nhapSao(viTriLongDuc, saoLongDuc)

    viTriBachHo = dichCung(viTriThaiTue, 8)
    diaBan.nhapSao(viTriBachHo, saoBachHo)

    viTriPhucDuc = dichCung(viTriThaiTue, 9)
    diaBan.nhapSao(viTriPhucDuc, saoPhucDuc, saoThienDuc)

    viTriDieuKhach = dichCung(viTriThaiTue, 10)
    diaBan.nhapSao(viTriDieuKhach, saoDieuKhach)

    viTriTrucPhu = dichCung(viTriThaiTue, 11)
    diaBan.nhapSao(viTriTrucPhu, saoTrucPhu)

    viTriTrangSinh = timTrangSinh(cucSo)
    diaBan.nhapSao(viTriTrangSinh, saoTrangSinh)

    viTriMocDuc = dichCung(viTriTrangSinh, amDuongNamNu * 1)
    diaBan.nhapSao(viTriMocDuc, saoMocDuc)

    viTriQuanDoi = dichCung(viTriTrangSinh, amDuongNamNu * 2)
    diaBan.nhapSao(viTriQuanDoi, saoQuanDoi)

    viTriLamQuan = dichCung(viTriTrangSinh, amDuongNamNu * 3)
    diaBan.nhapSao(viTriLamQuan, saoLamQuan)

    viTriDeVuong = dichCung(viTriTrangSinh, amDuongNamNu * 4)
    diaBan.nhapSao(viTriDeVuong, saoDeVuong)

    viTriSuy = dichCung(viTriTrangSinh, amDuongNamNu * 5)
    diaBan.nhapSao(viTriSuy, saoSuy)

    viTriBenh = dichCung(viTriTrangSinh, amDuongNamNu * 6)
    diaBan.nhapSao(viTriBenh, saoBenh)

    viTriTu = dichCung(viTriTrangSinh, amDuongNamNu * 7)
    diaBan.nhapSao(viTriTu, saoTu)

    viTriMo = dichCung(viTriTrangSinh, amDuongNamNu * 8)
    diaBan.nhapSao(viTriMo, saoMo)

    viTriTuyet = dichCung(viTriTrangSinh, amDuongNamNu * 9)
    diaBan.nhapSao(viTriTuyet, saoTuyet)

    viTriThai = dichCung(viTriTrangSinh, amDuongNamNu * (-1))
    diaBan.nhapSao(viTriThai, saoThai)

    viTriDuong = dichCung(viTriTrangSinh, amDuongNamNu * (-2))
    diaBan.nhapSao(viTriDuong, saoDuong)

    viTriDaLa = dichCung(viTriLocTon, -1)
    diaBan.nhapSao(viTriDaLa, saoDaLa)

    viTriKinhDuong = dichCung(viTriLocTon, 1)
    diaBan.nhapSao(viTriKinhDuong, saoKinhDuong)

    viTriDiaKiep = dichCung(11, gioSinh)
    diaBan.nhapSao(viTriDiaKiep, saoDiaKiep)

    viTriDiaKhong = dichCung(12, 12 - viTriDiaKiep)
    diaBan.nhapSao(viTriDiaKhong, saoDiaKhong)

    viTriHoaTinh, viTriLinhTinh = timHoaLinh(chiNam, gioSinh,
                                             gioiTinh, amDuongNamSinh)
    diaBan.nhapSao(viTriHoaTinh, saoHoaTinh)
    diaBan.nhapSao(viTriLinhTinh, saoLinhTinh)

    viTriLongTri = dichCung(5, chiNam - 1)
    diaBan.nhapSao(viTriLongTri, saoLongTri)

    viTriPhuongCac = dichCung(2, 2 - viTriLongTri)
    diaBan.nhapSao(viTriPhuongCac, saoPhuongCac, saoGiaiThan)

    viTriTaPhu = dichCung(5, tt - 1)
    diaBan.nhapSao(viTriTaPhu, saoTaPhu)

    viTriHuuBat = dichCung(2, 2 - viTriTaPhu)
    diaBan.nhapSao(viTriHuuBat, saoHuuBat)

    viTriVanKhuc = dichCung(5, gioSinh - 1)
    diaBan.nhapSao(viTriVanKhuc, saoVanKhuc)

    viTriVanXuong = dichCung(2, 2 - viTriVanKhuc)
    diaBan.nhapSao(viTriVanXuong, saoVanXuong)

    viTriTamThai = dichCung(5, tt + nn - 2)
    diaBan.nhapSao(viTriTamThai, saoTamThai)

    viTriBatToa = dichCung(2, 2 - viTriTamThai)
    diaBan.nhapSao(viTriBatToa, saoBatToa)

    viTriAnQuang = dichCung(viTriVanXuong, nn - 2)
    diaBan.nhapSao(viTriAnQuang, saoAnQuang)

    viTriThienQuy = dichCung(2, 2 - viTriAnQuang)
    diaBan.nhapSao(viTriThienQuy, saoThienQuy)

    viTriThienKhoi = timThienKhoi(canNam)
    diaBan.nhapSao(viTriThienKhoi, saoThienKhoi)

    viTriThienViet = dichCung(5, 5 - viTriThienKhoi)
    diaBan.nhapSao(viTriThienViet, saoThienViet)

    viTriThienHu = dichCung(7, chiNam - 1)
    diaBan.nhapSao(viTriThienHu, saoThienHu)

    viTriThienKhoc = dichCung(7, -chiNam + 1)
    diaBan.nhapSao(viTriThienKhoc, saoThienKhoc)

    viTriThienTai = dichCung(diaBan.cungMenh, chiNam - 1)
    diaBan.nhapSao(viTriThienTai, saoThienTai)

    viTriThienTho = dichCung(diaBan.cungThan, chiNam - 1)
    diaBan.nhapSao(viTriThienTho, saoThienTho)

    viTriHongLoan = dichCung(4, -chiNam + 1)
    diaBan.nhapSao(viTriHongLoan, saoHongLoan)

    viTriThienHy = dichCung(viTriHongLoan, 6)
    diaBan.nhapSao(viTriThienHy, saoThienHy)

    viTriThienQuan, viTriThienPhuc = timThienQuanThienPhuc(canNam)
    diaBan.nhapSao(viTriThienQuan, saoThienQuan)
    diaBan.nhapSao(viTriThienPhuc, saoThienPhuc)

    viTriThienHinh = dichCung(10, tt - 1)
    diaBan.nhapSao(viTriThienHinh, saoThienHinh)

    viTriThienRieu = dichCung(viTriThienHinh, 4)
    diaBan.nhapSao(viTriThienRieu, saoThienRieu, saoThienY)

    viTriCoThan = timCoThan(chiNam)
    diaBan.nhapSao(viTriCoThan, saoCoThan)

    viTriQuaTu = dichCung(viTriCoThan, -4)
    diaBan.nhapSao(viTriQuaTu, saoQuaTu)

    viTriVanTinh = dichCung(viTriKinhDuong, 2)
    diaBan.nhapSao(viTriVanTinh, saoVanTinh)

    viTriDuongPhu = dichCung(viTriVanTinh, 2)
    diaBan.nhapSao(viTriDuongPhu, saoDuongPhu)

    viTriQuocAn = dichCung(viTriDuongPhu, 3)
    diaBan.nhapSao(viTriQuocAn, saoQuocAn)

    viTriThaiPhu = dichCung(viTriVanKhuc, 2)
    diaBan.nhapSao(viTriThaiPhu, saoThaiPhu)

    viTriPhongCao = dichCung(viTriVanKhuc, -2)
    diaBan.nhapSao(viTriPhongCao, saoPhongCao)

    viTriThienGiai = dichCung(9, (2 * tt) - 2)
    diaBan.nhapSao(viTriThienGiai, saoThienGiai)

    viTriDiaGiai = dichCung(viTriTaPhu, 3)
    diaBan.nhapSao(viTriDiaGiai, saoDiaGiai)

    viTriThienLa = 5
    diaBan.nhapSao(viTriThienLa, saoThienLa)

    viTriDiaVong = 11
    diaBan.nhapSao(viTriDiaVong, saoDiaVong)

    viTriThienThuong = diaBan.cungNoboc
    diaBan.nhapSao(viTriThienThuong, saoThienThuong)

    viTriThienSu = diaBan.cungTatAch
    diaBan.nhapSao(viTriThienSu, saoThienSu)

    viTriThienMa = timThienMa(chiNam)
    diaBan.nhapSao(viTriThienMa, saoThienMa)

    viTriHoaCai = dichCung(viTriThienMa, 2)
    diaBan.nhapSao(viTriHoaCai, saoHoaCai)

    viTriKiepSat = dichCung(viTriThienMa, 3)
    diaBan.nhapSao(viTriKiepSat, saoKiepSat)

    viTriDaoHoa = dichCung(viTriKiepSat, 4)
    diaBan.nhapSao(viTriDaoHoa, saoDaoHoa)

    viTriPhaToai = timPhaToai(chiNam)
    diaBan.nhapSao(viTriPhaToai, saoPhaToai)

    viTriDauQuan = dichCung(chiNam, -tt + gioSinh)
    diaBan.nhapSao(viTriDauQuan, saoDauQuan)

    if canNam == 1:
        viTriHoaLoc = viTriLiemTrinh
        viTriHoaQuyen = viTriPhaQuan
        viTriHoaKhoa = viTriVuKhuc
        viTriHoaKy = vitriThaiDuong
    elif canNam == 2:
        viTriHoaLoc = viTriThienCo
        viTriHoaQuyen = viTriThienLuong
        viTriHoaKhoa = viTriTuVi
        viTriHoaKy = viTriThaiAm
    elif canNam == 3:
        viTriHoaLoc = viTriThienDong
        viTriHoaQuyen = viTriThienCo
        viTriHoaKhoa = viTriVanXuong
        viTriHoaKy = viTriLiemTrinh
    elif canNam == 4:
        viTriHoaLoc = viTriThaiAm
        viTriHoaQuyen = viTriThienDong
        viTriHoaKhoa = viTriThienCo
        viTriHoaKy = viTriCuMon
    elif canNam == 5:
        viTriHoaLoc = viTriThamLang
        viTriHoaQuyen = viTriThaiAm
        viTriHoaKhoa = viTriHuuBat
        viTriHoaKy = viTriThienCo
    elif canNam == 6:
        viTriHoaLoc = viTriVuKhuc
        viTriHoaQuyen = viTriThamLang
        viTriHoaKhoa = viTriThienLuong
        viTriHoaKy = viTriVanKhuc
    elif canNam == 7:
        viTriHoaLoc = vitriThaiDuong
        viTriHoaQuyen = viTriVuKhuc
        viTriHoaKhoa = viTriThienDong
        viTriHoaKy = viTriThaiAm
    elif canNam == 8:
        viTriHoaLoc = viTriCuMon
        viTriHoaQuyen = vitriThaiDuong
        viTriHoaKhoa = viTriVanKhuc
        viTriHoaKy = viTriVanXuong
    elif canNam == 9:
        viTriHoaLoc = viTriThienLuong
        viTriHoaQuyen = viTriTuVi
        viTriHoaKhoa = viTriThienPhu
        viTriHoaKy = viTriVuKhuc
    elif canNam == 10:
        viTriHoaLoc = viTriPhaQuan
        viTriHoaQuyen = viTriCuMon
        viTriHoaKhoa = viTriThaiAm
        viTriHoaKy = viTriThamLang

    diaBan.nhapSao(viTriHoaLoc, saoHoaLoc)
    diaBan.nhapSao(viTriHoaQuyen, saoHoaQuyen)
    diaBan.nhapSao(viTriHoaKhoa, saoHoaKhoa)
    diaBan.nhapSao(viTriHoaKy, saoHoaKy)

    viTriLuuHa, viTriThienTru = timLuuTru(canNam)
    diaBan.nhapSao(viTriLuuHa, saoLuuHa)
    diaBan.nhapSao(viTriThienTru, saoThienTru)

    ketThucTuan = dichCung(chiNam, 10 - canNam)
    viTriTuan1 = dichCung(ketThucTuan, 1)
    viTriTuan2 = dichCung(viTriTuan1, 1)
    diaBan.nhapTuan(viTriTuan1, viTriTuan2)

    viTriTriet1, viTriTriet2 = timTriet(canNam)
    diaBan.nhapTriet(viTriTriet1, viTriTriet2)
    return (diaBan)
