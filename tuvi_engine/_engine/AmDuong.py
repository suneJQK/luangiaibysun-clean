# -*- coding: utf-8 -*-
from .Lich_HND import jdFromDate,S2L,L2S,ngayThangNam,canChiNgay,ngayThangNamCanChi

def _can(i):
    names=['','Giáp','Ất','Bính','Đinh','Mậu','Kỷ','Canh','Tân','Nhâm','Quý']; return names[i]
_can_info=[None,('G','Giáp','M',2,3,1),('A','Ất','M',2,4,-1),('B','Bính','H',4,6,1),('D','Đinh','H',4,7,-1),('M','Mậu','O',5,6,1),('K','Kỷ','O',5,7,-1),('C','Canh','K',1,9,1),('T','Tân','K',1,10,-1),('N','Nhâm','T',3,12,1),('Q','Quý','T',3,1,-1)]
thienCan=[{'id':0,'chuCaiDau':None,'tenCan':None,'nguHanh':None,'nguHanhID':None,'vitriDiaBan':None,'amDuong':None}]
for i,x in enumerate(_can_info[1:],1): thienCan.append({'id':i,'chuCaiDau':x[0],'tenCan':x[1],'nguHanh':x[2],'nguHanhID':x[3],'vitriDiaBan':x[4],'amDuong':x[5]})
_chi=[None,('Tý','T','ty1',1,'Tham lang','Linh tinh'),('Sửu','O','suu',-1,'Cự môn','Thiên tướng'),('Dần','M','dan',1,'Lộc tồn','Thiên lương'),('Mão','M','mao',-1,'Văn khúc','Thiên đồng'),('Thìn','O','thin',1,'Liêm trinh','Văn xương'),('Tỵ','H','ty2',-1,'Vũ khúc','Thiên cơ'),('Ngọ','H','ngo',1,'Phá quân','Hỏa tinh'),('Mùi','O','mui',-1,'Vũ khúc','Thiên tướng'),('Thân','K','than',1,'Liêm trinh','Thiên lương'),('Dậu','K','dau',-1,'Văn khúc','Thiên đồng'),('Tuất','O','tuat',1,'Lộc tồn','Văn xương'),('Hợi','T','hoi',-1,'Cự môn','Thiên cơ')]
diaChi=[{'id':0,'tenChi':'Không có','tenVietTat':'khongco','tenHanh':'T','amDuong':0}]
for i,x in enumerate(_chi[1:],1): diaChi.append({'id':i,'tenChi':x[0],'tenHanh':x[1],'tenVietTat':x[2],'menhChu':x[4],'thanChu':x[5],'amDuong':x[3]})

def nguHanh(h):
    m={'Kim':(1,4,'Kim tứ Cục','hanhKim'),'K':(1,4,'Kim tứ Cục','hanhKim'),'Moc':(2,3,'Mộc tam Cục','hanhMoc'),'M':(2,3,'Mộc tam Cục','hanhMoc'),'Thuy':(3,2,'Thủy nhị Cục','hanhThuy'),'T':(3,2,'Thủy nhị Cục','hanhThuy'),'Hoa':(4,6,'Hỏa lục Cục','hanhHoa'),'H':(4,6,'Hỏa lục Cục','hanhHoa'),'Tho':(5,5,'Thổ ngũ Cục','hanhTho'),'O':(5,5,'Thổ ngũ Cục','hanhTho')}
    if h not in m: raise Exception('Tên Hành không hợp lệ')
    i,c,n,css=m[h]; return {'id':i,'tenHanh':{'K':'Kim','M':'Mộc','T':'Thủy','H':'Hỏa','O':'Thổ'}.get(h,h),'cuc':c,'tenCuc':n,'css':css}

def nguHanhNapAm(diaChi, thienCan, xuatBanMenh=False):
    banMenh={
        'K1':'HẢI TRUNG KIM','T1':'GIÁNG HẠ THỦY','H1':'TÍCH LỊCH HỎA','O1':'BÍCH THƯỢNG THỔ','M1':'TANG ÐỐ MỘC',
        'T2':'ÐẠI KHÊ THỦY','H2':'LƯ TRUNG HỎA','O2':'THÀNH ÐẦU THỔ','M2':'TÒNG BÁ MỘC','K2':'KIM BẠCH KIM',
        'H3':'PHÚ ÐĂNG HỎA','O3':'SA TRUNG THỔ','M3':'ÐẠI LÂM MỘC','K3':'BẠCH LẠP KIM','T3':'TRƯỜNG LƯU THỦY',
        'K4':'SA TRUNG KIM','T4':'THIÊN HÀ THỦY','H4':'THIÊN THƯỢNG HỎA','O4':'LỘ BÀN THỔ','M4':'DƯƠNG LIỄU MỘC',
        'T5':'TRUYỀN TRUNG THỦY','H5':'SƠN HẠ HỎA','O5':'ÐẠI TRẠCH THỔ','M5':'THẠCH LỰU MỘC','K5':'KIẾM PHONG KIM',
        'H6':'SƠN ÐẦU HỎA','O6':'ỐC THƯỢNG THỔ','M6':'BÌNH ĐỊA MỘC','K6':'XOA XUYẾN KIM','T6':'ÐẠI HẢI THỦY'}
    matranNapAm=[
        [0,'G','Ất','Bính','Đinh','Mậu','Kỷ','Canh','Tân','N','Q'],
        [1,'K1',False,'T1',False,'H1',False,'O1',False,'M1',False],
        [2,False,'K1',False,'T1',False,'H1',False,'O1',False,'M1'],
        [3,'T2',False,'H2',False,'O2',False,'M2',False,'K2',False],
        [4,False,'T2',False,'H2',False,'O2',False,'M2',False,'K2'],
        [5,'H3',False,'O3',False,'M3',False,'K3',False,'T3',False],
        [6,False,'H3',False,'O3',False,'M3',False,'K3',False,'T3'],
        [7,'K4',False,'T4',False,'H4',False,'O4',False,'M4',False],
        [8,False,'K4',False,'T4',False,'H4',False,'O4',False,'M4'],
        [9,'T5',False,'H5',False,'O5',False,'M5',False,'K5',False],
        [10,False,'T5',False,'H5',False,'O5',False,'M5',False,'K5'],
        [11,'H6',False,'O6',False,'M6',False,'K6',False,'T6',False],
        [12,False,'H6',False,'O6',False,'M6',False,'K6',False,'T6']]
    try:
        nh=matranNapAm[diaChi][thienCan]
        if nh and isinstance(nh,str) and nh[0] in ['K','M','T','H','O']:
            return banMenh[nh] if xuatBanMenh else nh[0]
    except Exception:
        pass
    raise Exception('Không tìm được Ngũ Hành Nạp Âm')

def sinhKhac(a,b):
    mat=[[None,None,None,None,None,None],[None,0,-1,1,-1j,1j],[None,-1j,0,1j,1,-1],[None,1j,1,0,1,-1j],[None,-1,1j,-1j,0,1],[None,1,-1j,-1,1j,0]]; return mat[a][b]
def dichCung(cungBanDau,*args):
    n=int(cungBanDau)+sum(int(x) for x in args); return 12 if n%12==0 else n%12
def khoangCachCung(c1,c2,chieu=1): return (c1-c2+12)%12 if chieu==1 else (c2-c1+12)%12
def timCuc(viTriCungMenhTrenDiaBan,canNamSinh):
    canThangGieng=(canNamSinh*2+1)%10; canThangMenh=((viTriCungMenhTrenDiaBan-3)%12+canThangGieng)%10; canThangMenh=10 if canThangMenh==0 else canThangMenh; return nguHanhNapAm(viTriCungMenhTrenDiaBan,canThangMenh)
def timTuVi(cuc,ngaySinhAmLich):
    if cuc not in [2,3,4,5,6]: raise Exception('Số cục phải là 2..6')
    cung=3; c=cuc
    while c<ngaySinhAmLich: c+=cuc; cung+=1
    sai=c-ngaySinhAmLich
    if sai%2: sai=-sai
    return dichCung(cung,sai)
def timTrangSinh(cucSo): return {6:3,4:6,2:9,5:9,3:12}[cucSo]
def timHoaLinh(chiNamSinh,gioSinh,gioiTinh,amDuongNamSinh):
    if chiNamSinh in [3,7,11]: h,l=2,4
    elif chiNamSinh in [1,5,9]: h,l=3,11
    elif chiNamSinh in [6,10,2]: h,l=11,4
    else: h,l=10,11
    if gioiTinh*amDuongNamSinh==-1: return [dichCung(h+1,-gioSinh),dichCung(l-1,gioSinh)]
    return [dichCung(h-1,gioSinh),dichCung(l+1,-gioSinh)]
def timThienKhoi(canNam): return [None,2,1,12,10,8,1,8,7,6,4][canNam]
def timThienQuanThienPhuc(canNam): return ([None,8,5,6,3,4,10,12,10,11,7][canNam],[None,10,9,1,12,4,3,7,6,7,6][canNam])
def timCoThan(chiNam): return 3 if chiNam in [12,1,2] else 6 if chiNam in [3,4,5] else 9 if chiNam in [6,7,8] else 12
def timThienMa(chiNam): return {1:3,2:12,3:9,0:6}[chiNam%4]
def timPhaToai(chiNam):
    if chiNam in (1,4,7,10): return 6
    if chiNam in (3,6,9,12): return 10
    if chiNam in (2,5,8,11): return 2
    raise Exception('Không tìm được Phá Toái')
def timTriet(canNam): return {1:(9,10),6:(9,10),2:(7,8),7:(7,8),3:(5,6),8:(5,6),4:(3,4),9:(3,4),5:(1,2),10:(1,2)}[canNam]
def timLuuTru(canNam): return ([None,10,11,8,5,6,7,9,4,12,3][canNam],[None,6,7,1,6,7,9,3,7,10,11][canNam])
