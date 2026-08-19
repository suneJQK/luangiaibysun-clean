import time
from .AmDuong import canChiNgay,diaChi,ngayThangNam,ngayThangNamCanChi,nguHanh,nguHanhNapAm,sinhKhac,thienCan,timCuc
class lapThienBan:
    def __init__(self,nn,tt,nnnn,gioSinh,gioiTinh,ten,diaBan,duongLich=True,timeZone=7):
        self.gioiTinh=1 if gioiTinh==1 else -1; self.namNu='Nam' if gioiTinh==1 else 'Nữ'; self.timeZone=timeZone
        self.chiGioSinh=diaChi[gioSinh]; self.canGioSinh=((int((nnnn+6)%10)+gioSinh-1)%10)+1; self.gioSinh='{} {}'.format(thienCan[self.canGioSinh]['tenCan'],self.chiGioSinh['tenChi'])
        self.ngayDuong,self.thangDuong,self.namDuong,self.ten=nn,tt,nnnn,ten
        if duongLich: self.ngayAm,self.thangAm,self.namAm,self.thangNhuan=ngayThangNam(nn,tt,nnnn,True,timeZone)
        else: self.ngayAm,self.thangAm,self.namAm=nn,tt,nnnn
        self.canThang,self.canNam,self.chiNam=ngayThangNamCanChi(self.ngayAm,self.thangAm,self.namAm,False,timeZone); self.chiThang=self.thangAm
        self.canThangTen=thienCan[self.canThang]['tenCan']; self.canNamTen=thienCan[self.canNam]['tenCan']; self.chiThangTen=diaChi[(self.thangAm+1)%12+1]['tenChi']; self.chiNamTen=diaChi[self.chiNam]['tenChi']
        self.canNgay,self.chiNgay=canChiNgay(nn,tt,nnnn,duongLich,timeZone); self.canNgayTen=thienCan[self.canNgay]['tenCan']; self.chiNgayTen=diaChi[self.chiNgay]['tenChi']
        cungAD=1 if diaBan.cungMenh%2 else -1; namAD=1 if self.chiNam%2 else -1; self.amDuongNamSinh='Dương' if namAD==1 else 'Âm'; self.amDuongMenh='Âm dương thuận lý' if cungAD*namAD==1 else 'Âm dương nghịch lý'
        cuc=timCuc(diaBan.cungMenh,self.canNam); self.hanhCuc=nguHanh(cuc)['id']; self.tenCuc=nguHanh(cuc)['tenCuc']; self.menhChu=diaChi[diaBan.cungMenh]['menhChu']; self.thanChu=diaChi[self.chiNam]['thanChu']; self.menh=nguHanhNapAm(self.chiNam,self.canNam); self.banMenh=nguHanhNapAm(self.chiNam,self.canNam,True)
        self.sinhKhac='Mệnh Cục bình hòa'
