# TV AI Frontend — Modular

Frontend mới, độc lập với backend và giao diện cũ.

## Cấu trúc

- `index.html`: chỉ markup và link asset.
- `css/base.css`: biến, reset, nền chung.
- `css/layout.css`: sidebar, header, layout, responsive.
- `css/components.css`: button, panel, table, chat, relation card.
- `css/chart.css`: Thiên Bàn, 12 Địa Bàn, sao.
- `css/cach.css`: Cách Cục và Evidence.
- `css/ai.css`: AI/Audit.
- `js/core.js`: state, DOM helpers, API, dữ liệu chung.
- `js/profile.js`: quản lý hồ sơ + ID ổn định phía UI.
- `js/chart.js`: render Thiên Bàn/Địa Bàn.
- `js/relations.js`: Tam Hợp/Xung Chiếu/Nhị Hợp/Giáp Cung.
- `js/cach.js`: Cách Cục + Rule ID + Evidence.
- `js/van10.js`: bảng Vận 10 năm.
- `js/ai.js`: AI luận giải + Audit.
- `js/main.js`: điều phối các module.

## API giữ nguyên

- `POST /api/lap-so`
- `POST /api/luan-giai`

Frontend này chưa được nối vào `/` để tránh ảnh hưởng production hiện tại.
