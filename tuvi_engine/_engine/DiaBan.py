# -*- coding: utf-8 -*-
from .AmDuong import diaChi,dichCung,khoangCachCung,thienCan

class cungDiaBan:
    def __init__(self,cungID,canDiaBan=None):
        hanh=[None,'Thủy','Thổ','Mộc','Mộc','Thổ','Hỏa','Hỏa','Thổ','Kim','Kim','Thổ','Thủy']
        self.cungSo=cungID; self.hanhCung=hanh[cungID]; self.cungSao=[]; self.cungAmDuong=-1 if cungID%2==0 else 1
        self.cungTen='{} {}'.format(self.getCanDiaBan(canDiaBan,'tenCan'),diaChi[cungID]['tenChi']); self.cungDiaChi=diaChi[cungID]['tenVietTat']; self.cungHanh=diaChi[cungID]['tenHanh']; self.cungThan=False
    def getCanDiaBan(self,c,k): return c.get(k) if c and k in c else ''
    def themSao(self,sao):
        self.cungSao.append(sao.__dict__.copy()); return self
    def cungChu(self,t): self.cungChu=t; return self
    def daiHan(self,x): self.cungDaiHan=x; return self
    def tieuHan(self,x): self.cungTieuHan=diaChi[x+1]['tenChi']; return self
    def anCungThan(self): self.cungThan=True
    def anTuan(self): self.tuanTrung=True
    def anTriet(self): self.trietLo=True

class diaBan:
    def __init__(self,thangSinhAmLich,gioSinhAmLich,thienCanNam):
        self.thangSinhAmLich=thangSinhAmLich; self.gioSinhAmLich=gioSinhAmLich
        cs=self.canDiaBan(thienCanNam); self.thapNhiCung=[cungDiaBan(i,cs[i] if i<len(cs) else None) for i in range(13)]; self.nhapCungChu(); self.nhapCungThan()
    def canDiaBan(self,can):
        t=thienCan[1:]
        if can['chuCaiDau'] in ['G','K']: a,b=t[:2],t[2:]; last=t[2:4]
        elif can['chuCaiDau'] in ['A','C']: a,b=t[:4],t[4:]; last=t[4:6]
        elif can['chuCaiDau'] in ['B','T']: a,b=t[:6],t[6:]; last=t[6:8]
        elif can['chuCaiDau'] in ['D','N']: a,b=t[:8],t[8:]; last=t[8:10]
        else: last=t[:2]; return [thienCan[0]]+last+t
        return [thienCan[0]]+last+b+a
    def cungChu(self,thang,gio):
        self.cungThan=dichCung(3,thang-1,gio-1); self.cungMenh=dichCung(3,thang-1,-gio+1)
        ids=[('Mệnh',self.cungMenh),('Phụ mẫu',dichCung(self.cungMenh,1)),('Phúc đức',dichCung(self.cungMenh,2)),('Điền trạch',dichCung(self.cungMenh,3)),('Quan lộc',dichCung(self.cungMenh,4)),('Nô bộc',dichCung(self.cungMenh,5)),('Thiên di',dichCung(self.cungMenh,6)),('Tật ách',dichCung(self.cungMenh,7)),('Tài bạch',dichCung(self.cungMenh,8)),('Tử tức',dichCung(self.cungMenh,9)),('Phu thê',dichCung(self.cungMenh,10)),('Huynh đệ',dichCung(self.cungMenh,11))]
        self.cungNoboc=ids[5][1]; self.cungTatAch=ids[7][1]; return [{'tenCung':n,'cungSoDiaBan':p} for n,p in ids]
    def nhapCungChu(self):
        for x in self.cungChu(self.thangSinhAmLich,self.gioSinhAmLich): self.thapNhiCung[x['cungSoDiaBan']].cungChu(x['tenCung'])
    def nhapDaiHan(self,cucSo,gioiTinh):
        for c in self.thapNhiCung: c.daiHan(cucSo+khoangCachCung(c.cungSo,self.cungMenh,gioiTinh)*10)
        return self
    def nhapTieuHan(self,khoi,gioiTinh,chiNam):
        viTriCungTy1=dichCung(khoi,-gioiTinh*(chiNam-1))
        for c in self.thapNhiCung: c.tieuHan(khoangCachCung(c.cungSo,viTriCungTy1,gioiTinh))
        return self
    def nhapCungThan(self): self.thapNhiCung[self.cungThan].anCungThan()
    def nhapSao(self,cungSo,*args):
        for sao in args: self.thapNhiCung[cungSo].themSao(sao)
        return self
    def nhapTuan(self,*args):
        for c in args: self.thapNhiCung[c].anTuan()
        return self
    def nhapTriet(self,*args):
        for c in args: self.thapNhiCung[c].anTriet()
        return self
