# 📘 Day 2 Walkthrough — Backend: Database + Auth

Dokumen ini adalah ringkasan progres dan penjelasan mendetail dari implementasi autentikasi (Day 2) pada project BridgeDocs. Tujuannya adalah sebagai bahan evaluasi dan pembelajaran mengenai bagaimana sistem registrasi, login, dan pengamanan route (proteksi API) bekerja di FastAPI.

---

## 🎯 Apa yang Telah Diselesaikan?

1. **Setup Environment Variabel & Virtual Environment:**
   - Menyalin konfigurasi `.env.example` menjadi `.env`.
   - Membuat *virtual environment* Python (`venv`) untuk mengisolasi dependensi.
   - Menginstall semua paket yang dibutuhkan melalui `requirements.txt` (termasuk `fastapi`, `passlib[bcrypt]`, `python-jose[cryptography]`, `sqlalchemy`, dll).

2. **Pembuatan File Utilitas Keamanan (`auth_utils.py`):**
   - Mengonfigurasi `passlib` untuk meng-hash password menggunakan algoritma **bcrypt**.
   - Mengonfigurasi pembuatan token JWT menggunakan `python-jose`.
   - Membuat fungsi Dependency Injection (`get_current_user`) untuk memvalidasi token JWT secara otomatis pada setiap request ke endpoint yang diproteksi.

3. **Pembuatan Router Autentikasi (`routers/auth.py`):**
   - `POST /auth/register`: Menerima input user, memvalidasi email duplikat, melakukan hashing password, dan menyimpan user baru ke database PostgreSQL.
   - `POST /auth/login`: Menerima email dan password, melakukan verifikasi password terhadap hash di database, lalu menerbitkan JWT access token.
   - `GET /auth/me`: Mengembalikan data profil user yang sedang login berdasarkan token JWT yang disisipkan pada header `Authorization`.

4. **Registrasi Router di `main.py`:**
   - Menyambungkan `auth_router` ke aplikasi utama FastAPI sehingga endpoint-endpoint tersebut aktif dan dapat diakses, contohnya melalui dokumentasi Swagger UI (`http://localhost:8000/docs`).

---

## 🧠 Konsep Penting yang Dipelajari

### 1. Kenapa Harus Melakukan Password Hashing?
Saat menyimpan password di database, kita **TIDAK BOLEH** menyimpannya dalam bentuk teks asli (*plain text*). Jika database bocor, password pengguna akan terekspos.
- **Solusi:** Kita menggunakan *hashing algorithm* bernama **Bcrypt**.
- **Kelebihan Bcrypt:** Algoritma ini sengaja dirancang agar "lambat" diproses komputer, sehingga sangat sulit untuk dibobol dengan teknik *brute-force* atau pencocokan *rainbow table*. Bcrypt otomatis menambahkan nilai acak (*salt*) ke dalam setiap password yang di-hash, sehingga password "12345" milik User A dan "12345" milik User B akan memiliki teks hash yang berbeda di database.
- **Implementasi:** Di file `auth_utils.py`, kita menggunakan `pwd_context.hash()` untuk membuat hash, dan `pwd_context.verify()` saat login.

### 2. Bagaimana JWT (JSON Web Token) Bekerja?
Sistem backend BridgeDocs ini berstatus *stateless*, artinya server tidak mengingat siapa saja yang sudah login di memori server. Sebagai gantinya, server memberikan sebuah "kartu identitas digital" bernama JWT.
- **Struktur JWT:** JWT terdiri dari 3 bagian: *Header* (algoritma), *Payload* (data user ID dan waktu kedaluwarsa/expiration), dan *Signature* (tanda tangan digital).
- **Keamanan:** Data dalam payload memang **tidak dienkripsi** (bisa dibaca oleh siapa saja yang melakukan decode). Namun, token ini **tidak bisa dimodifikasi** tanpa mengetahui `SECRET_KEY` yang tersimpan aman di server. Jika ada oknum yang mengubah isi token, Signature-nya akan tidak cocok dan token dianggap tidak valid.
- **Alur Login:** Saat user berhasil login, server memanggil `create_access_token` yang memuat `"sub": str(user.id)` dan waktu `exp` (expiration), lalu men-generate token menggunakan `SECRET_KEY`. 

### 3. Dependency Injection di FastAPI
Ini adalah salah satu fitur paling canggih di FastAPI. Kita bisa meminta fungsi tertentu dijalankan sebelum masuk ke logika utama endpoint.
- **Fungsi `get_current_user`:** Pada endpoint `GET /auth/me`, kita menuliskan parameter `current_user: User = Depends(get_current_user)`.
- **Yang Terjadi:** FastAPI otomatis akan menjalankan fungsi `get_current_user` terlebih dahulu. Fungsi ini akan mengambil token dari header HTTP, melakukan proses decode, memverifikasi masa berlakunya, lalu mencari data User di database berdasarkan user_id. Jika semuanya valid, barulah objek User dilempar masuk ke dalam fungsi endpoint. Jika token tidak valid, FastAPI langsung menolak dengan error `401 Unauthorized`.

### 4. Menghindari User Enumeration Attack
Pada proses login (`POST /auth/login`), sangat disarankan untuk memberikan pesan error yang generik, seperti `"Invalid email or password"`. 
- Jika kita membedakan pesan error menjadi "Email tidak ditemukan" dan "Password salah", seorang *hacker* bisa menggunakan form login tersebut untuk menebak-nebak (mengumpulkan) daftar email apa saja yang terdaftar di aplikasi kita. Ini disebut *User Enumeration Attack*.

---

## ✅ Cara Melakukan Pengujian (Testing)

Karena fitur autentikasi sudah sepenuhnya dihubungkan, langkah pengujian yang bisa Anda lakukan:

1. **Jalankan Database:** Pastikan kontainer docker (Postgres) sudah berjalan.
2. **Jalankan Server:** Masuk ke folder `backend`, aktifkan virtual environment (`source venv/bin/activate`), dan jalankan `uvicorn main:app --reload`.
3. **Buka Swagger UI:** Kunjungi `http://localhost:8000/docs` di browser.
4. **Register:** Cobalah buat user baru di endpoint `/auth/register`.
5. **Login:** Gunakan email dan password yang baru saja dibuat di endpoint `/auth/login`. Salin string `access_token` yang diberikan di response.
6. **Akses Data Profil:** Klik tombol **Authorize** (gembok) di kanan atas Swagger UI, lalu paste token Anda (FastAPI akan otomatis menambahkan kata `Bearer`). Setelah sukses authorize, cobalah memanggil `GET /auth/me`. Seharusnya data profil Anda akan dimunculkan.

---
*End of Day 2 Walkthrough*
