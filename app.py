"""
LP3H Monitoring Dashboard - Backend Flask
Aplikasi monitoring Lembaga Pendamping Proses Produk Halal (LP3H)
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
from functools import wraps
import json
import random

app = Flask(__name__)
app.secret_key = 'lp3h_monitoring_secret_key_2024'

# ─────────────────────────────────────────────────────────────────────────────
# DATA DUMMY REALISTIS
# ─────────────────────────────────────────────────────────────────────────────

# === USERS ===
USERS = [
    {"id": 1, "name": "Admin LP3H", "email": "admin@gmail.com", "password": "12345678",
     "role": "admin", "avatar": "AL"},
    {"id": 2, "name": "Ahmad Fauzi, S.T.", "email": "ahmad.fauzi@lp3h.ac.id", "password": "pendamping123",
     "role": "pendamping", "avatar": "AF", "pendamping_id": 1},
    {"id": 3, "name": "Sari Dewi (Keripik Bu Sari)", "email": "berkah@usaha.com", "password": "pelaku123",
     "role": "pelaku_usaha", "avatar": "SD", "nib": "8120400000001"},
]

# === PENDAMPING (2 PENDAMPING) ===
PENDAMPING = [
    {
        "id": 1, "nama": "Ahmad Fauzi, S.T.", "nik": "3201****010185001", "no_registrasi": "P3H-2023-001",
        "no_sk": "SK-LP3H-2023/001", "kontak": "081234567890", "email": "ahmad.fauzi@lp3h.ac.id",
        "wilayah": "Bandung", "status": "Aktif", "sk_berlaku_sampai": "2025-12-31",
        "no_sertifikat_kompetensi": "BNSP-P3H-2023-001", "penyelenggara_kompetensi": "BNSP",
        "tgl_terbit_kompetensi": "2023-03-15", "berlaku_kompetensi_sampai": "2026-03-15",
        "target_bulanan": 5, "total_binaan": 3, "sertifikat_terbit": 2, "proses": 1, "pending": 0,
        "avatar": "AF"
    },
    {
        "id": 2, "nama": "Dewi Lestari, S.Psi.", "nik": "3273****250392002", "no_registrasi": "P3H-2023-002",
        "no_sk": "SK-LP3H-2023/002", "kontak": "082345678901", "email": "dewi.lestari@lp3h.ac.id",
        "wilayah": "Cimahi", "status": "Aktif", "sk_berlaku_sampai": "2025-06-30",
        "no_sertifikat_kompetensi": "BNSP-P3H-2023-002", "penyelenggara_kompetensi": "BNSP",
        "tgl_terbit_kompetensi": "2023-06-01", "berlaku_kompetensi_sampai": "2026-06-01",
        "target_bulanan": 5, "total_binaan": 2, "sertifikat_terbit": 1, "proses": 1, "pending": 0,
        "avatar": "DL"
    },
]

# === STATUS LIST ===
STATUS_LIST = [
    "Belum Diajukan", "Proses Pendampingan", "Verifikasi & Validasi",
    "Menunggu Sidang Fatwa", "Perbaikan", "Sertifikat Terbit", "Ditolak"
]

JENIS_USAHA = ["Makanan & Minuman", "Katering", "UMKM Pangan", "Industri Rumahan", "Restoran"]
JENIS_PRODUK = ["Makanan ringan", "Minuman herbal", "Bumbu masak", "Olahan daging", "Kue & bakeri"]

# === PELAKU USAHA (5 PELAKU USAHA) ===
PELAKU_USAHA = [
    {
        "id": 1,
        "nama_usaha": "Keripik Pisang Bu Sari",
        "nama_pemilik": "Sari Dewi",
        "nik": "3201****120588001",
        "nib": "8120400000001",
        "alamat": "Jl. Terusan Buah Batu No. 12, Bandung",
        "kontak": "081234567891",
        "jenis_usaha": "Industri Rumahan",
        "jenis_produk": "Makanan ringan",
        "tanggal_mulai": "2024-01-10",
        "pendamping_id": 1,
        "status": "Sertifikat Terbit",
        "terakhir_update": "2024-05-15",
        "catatan": "Sertifikat halal telah terbit dan diserahkan kepada pelaku usaha.",
    },
    {
        "id": 2,
        "nama_usaha": "Bakso Sapi Mas Jono",
        "nama_pemilik": "Jono Prasetyo",
        "nik": "3201****240885002",
        "nib": "8120400000002",
        "alamat": "Jl. Sukabirus No. 45, Bandung",
        "kontak": "081234567892",
        "jenis_usaha": "UMKM Pangan",
        "jenis_produk": "Olahan daging",
        "tanggal_mulai": "2024-02-01",
        "pendamping_id": 1,
        "status": "Proses Pendampingan",
        "terakhir_update": "2024-06-10",
        "catatan": "Proses verifikasi dokumen bahan baku daging dan bumbu halal.",
    },
    {
        "id": 3,
        "nama_usaha": "Catering Ibu Tati",
        "nama_pemilik": "Tati Suryani",
        "nik": "3201****180390003",
        "nib": "8120400000003",
        "alamat": "Jl. Radio No. 8, Bandung",
        "kontak": "081234567893",
        "jenis_usaha": "Katering",
        "jenis_produk": "Makanan ringan",
        "tanggal_mulai": "2024-02-15",
        "pendamping_id": 1,
        "status": "Sertifikat Terbit",
        "terakhir_update": "2024-07-02",
        "catatan": "Sertifikat halal resmi terbit melalui skema self-declare.",
    },
    {
        "id": 4,
        "nama_usaha": "Sambal Roa Mama Nia",
        "nama_pemilik": "Nia Ramadhani",
        "nik": "3273****091192004",
        "nib": "8120400000004",
        "alamat": "Jl. Cimindi Raya No. 20, Cimahi",
        "kontak": "081234567894",
        "jenis_usaha": "Industri Rumahan",
        "jenis_produk": "Bumbu masak",
        "tanggal_mulai": "2024-03-05",
        "pendamping_id": 2,
        "status": "Verifikasi & Validasi",
        "terakhir_update": "2024-06-25",
        "catatan": "Pemeriksaan dokumen daftar bahan dan foto kemasan produk.",
    },
    {
        "id": 5,
        "nama_usaha": "Kopi Bubuk Mang Ade",
        "nama_pemilik": "Ade Sukarna",
        "nik": "3273****150787005",
        "nib": "8120400000005",
        "alamat": "Jl. Kolonel Masturi No. 55, Cimahi",
        "kontak": "081234567895",
        "jenis_usaha": "UMKM Pangan",
        "jenis_produk": "Minuman herbal",
        "tanggal_mulai": "2024-03-20",
        "pendamping_id": 2,
        "status": "Sertifikat Terbit",
        "terakhir_update": "2024-08-14",
        "catatan": "Semua bahan baku biji kopi terverifikasi halal tanpa zat tambahan.",
    },
]

# === STATUS HISTORY ===
def generate_status_history(pelaku_usaha_id, status_saat_ini):
    idx = STATUS_LIST.index(status_saat_ini) if status_saat_ini in STATUS_LIST else 0
    history = []
    tgl = datetime(2024, 1, 15)
    for i in range(idx + 1):
        history.append({
            "status": STATUS_LIST[i],
            "tanggal": (tgl + timedelta(days=i * 14)).strftime("%Y-%m-%d"),
            "catatan": f"Tahap {STATUS_LIST[i]} berhasil diverifikasi",
            "oleh": "Admin LP3H" if i == 0 else ("Ahmad Fauzi, S.T." if pelaku_usaha_id <= 3 else "Dewi Lestari, S.Psi.")
        })
    return history

# === TARGET ===
TARGETS = [
    {"pendamping_id": i + 1, "target_2024": PENDAMPING[i]["target_bulanan"] * 12,
     "realisasi_2024": PENDAMPING[i]["total_binaan"],
     "bulan_ini_target": PENDAMPING[i]["target_bulanan"],
     "bulan_ini_realisasi": PENDAMPING[i]["sertifikat_terbit"]} for i in range(len(PENDAMPING))
]

# === AUDIT LOG ===
AUDIT_LOG = [
    {"id": 1, "user": "Admin LP3H", "aksi": "Login", "detail": "Login berhasil", "ip": "192.168.1.1", "waktu": "2024-10-15 08:30:00"},
    {"id": 2, "user": "Admin LP3H", "aksi": "Tambah Pelaku Usaha", "detail": "Menambahkan Keripik Pisang Bu Sari", "ip": "192.168.1.1", "waktu": "2024-10-15 08:45:00"},
    {"id": 3, "user": "Ahmad Fauzi", "aksi": "Update Status", "detail": "Update status Bakso Sapi Mas Jono → Verifikasi & Validasi", "ip": "192.168.1.5", "waktu": "2024-10-15 09:10:00"},
    {"id": 4, "user": "Admin LP3H", "aksi": "Import Data", "detail": "Import 20 data dari SIHALAL", "ip": "192.168.1.1", "waktu": "2024-10-14 14:20:00"},
    {"id": 5, "user": "Dr. Ir. Siti Rahayu", "aksi": "Login", "detail": "Login berhasil", "ip": "192.168.1.2", "waktu": "2024-10-14 09:00:00"},
    {"id": 6, "user": "Dewi Lestari", "aksi": "Upload Dokumen", "detail": "Upload dokumen pendukung untuk Catering Ibu Tati", "ip": "192.168.1.8", "waktu": "2024-10-13 11:30:00"},
    {"id": 7, "user": "Admin LP3H", "aksi": "Assign Pendamping", "detail": "Assign Tahu Bulat Pak Udin ke Ahmad Fauzi", "ip": "192.168.1.1", "waktu": "2024-10-12 10:00:00"},
    {"id": 8, "user": "Admin LP3H", "aksi": "Ekspor Laporan", "detail": "Ekspor laporan bulan Oktober 2024 ke Excel", "ip": "192.168.1.1", "waktu": "2024-10-11 15:45:00"},
    {"id": 9, "user": "Rina Wulandari", "aksi": "Update Catatan", "detail": "Update catatan Tempe Goreng Crispy", "ip": "192.168.1.12", "waktu": "2024-10-10 13:20:00"},
    {"id": 10, "user": "Admin LP3H", "aksi": "Edit Pendamping", "detail": "Update data kompetensi Budi Santoso", "ip": "192.168.1.1", "waktu": "2024-10-09 16:00:00"},
]

# === DATA STATISTIK TREND ===
TREND_BULANAN = {
    "labels": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"],
    "pendampingan_baru": [8, 12, 15, 20, 18, 25, 22, 28, 30, 35, 32, 40],
    "sertifikat_terbit": [2, 4, 6, 8, 10, 12, 11, 15, 18, 20, 22, 25],
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_user_by_id(user_id):
    return next((u for u in USERS if u["id"] == user_id), None)

def get_user_by_email(email):
    return next((u for u in USERS if u["email"] == email), None)

def get_pendamping_by_id(pid):
    return next((p for p in PENDAMPING if p["id"] == pid), None)

def get_pelaku_by_id(pid):
    return next((p for p in PELAKU_USAHA if p["id"] == pid), None)

def get_pelaku_by_pendamping(pendamping_id):
    return [p for p in PELAKU_USAHA if p["pendamping_id"] == pendamping_id]

def get_pelaku_by_nib(nib):
    return next((p for p in PELAKU_USAHA if p["nib"] == nib), None)

def hitung_status_kompetensi(berlaku_sampai_str):
    try:
        berlaku = datetime.strptime(berlaku_sampai_str, "%Y-%m-%d")
        hari_sisa = (berlaku - datetime.now()).days
        if hari_sisa < 0:
            return "Kedaluwarsa", "danger"
        elif hari_sisa < 90:
            return "Segera Habis", "warning"
        else:
            return "Aktif", "success"
    except:
        return "Tidak Diketahui", "secondary"

def hitung_status_sk(berlaku_sampai_str):
    return hitung_status_kompetensi(berlaku_sampai_str)

def hitung_persen(realisasi, target):
    if target == 0:
        return 0
    return min(round((realisasi / target) * 100), 100)

def get_kpi_color(persen):
    if persen >= 80:
        return "success"
    elif persen >= 50:
        return "warning"
    else:
        return "danger"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            user = get_user_by_id(session["user_id"])
            if not user or user["role"] not in roles:
                flash("Anda tidak memiliki akses ke halaman ini.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated
    return decorator

def add_audit(user_name, aksi, detail):
    AUDIT_LOG.insert(0, {
        "id": len(AUDIT_LOG) + 1,
        "user": user_name,
        "aksi": aksi,
        "detail": detail,
        "ip": request.remote_addr or "127.0.0.1",
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ─────────────────────────────────────────────────────────────────────────────
# CONTEXT PROCESSOR
# ─────────────────────────────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    user = None
    if "user_id" in session:
        user = get_user_by_id(session["user_id"])
    # Notifikasi: pendamping dengan SK/kompetensi segera habis/kedaluwarsa
    notif_list = []
    for p in PENDAMPING:
        sk_status, sk_cls = hitung_status_sk(p["sk_berlaku_sampai"])
        komp_status, komp_cls = hitung_status_kompetensi(p["berlaku_kompetensi_sampai"])
        if sk_cls in ["warning", "danger"]:
            notif_list.append({"tipe": "SK", "nama": p["nama"], "status": sk_status, "cls": sk_cls})
        if komp_cls in ["warning", "danger"]:
            notif_list.append({"tipe": "Kompetensi", "nama": p["nama"], "status": komp_status, "cls": komp_cls})
    return dict(current_user=user, notif_list=notif_list[:5])

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: AUTH
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("web_awal/index.html")

@app.route("/tentang")
def tentang():
    return render_template("web_awal/tentang.html")

@app.route("/layanan")
def layanan():
    return render_template("web_awal/layanan.html")

@app.route("/kontak")
def kontak():
    return render_template("web_awal/kontak.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = get_user_by_email(email)

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            add_audit(user["name"], "Login", "Login berhasil")
            flash(f"Selamat datang, {user['name']}!", "success")

            if user["role"] == "pelaku_usaha":
                return redirect(url_for("portal_status"))
            return redirect(url_for("dashboard"))
        else:
            flash("Email atau password salah.", "danger")

    return render_template("login.html")

@app.route("/daftar", methods=["GET", "POST"])
def daftar():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nama = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        role = request.form.get("role", "pendamping").strip()
        no_telp = request.form.get("no_telp", "").strip()

        if password != confirm_password:
            flash("Konfirmasi kata sandi tidak cocok.", "danger")
            return render_template("daftar.html")

        if get_user_by_email(email):
            flash("Email sudah terdaftar. Silakan login atau gunakan email lain.", "danger")
            return render_template("daftar.html")

        new_user_id = len(USERS) + 1
        avatar = "".join([part[0].upper() for part in nama.split()[:2]]) or "US"

        if role == "pendamping":
            wilayah = request.form.get("wilayah", "Bandung").strip() or "Bandung"
            no_reg = request.form.get("no_registrasi", f"P3H-2024-{len(PENDAMPING)+1:03d}").strip()
            new_pid = len(PENDAMPING) + 1
            PENDAMPING.append({
                "id": new_pid,
                "nama": nama,
                "nik": f"3201****{new_pid:02d}0185{new_pid:03d}",
                "no_registrasi": no_reg or f"P3H-2024-{new_pid:03d}",
                "no_sk": f"SK-LP3H-2024/{new_pid:03d}",
                "kontak": no_telp or "081234567890",
                "email": email,
                "wilayah": wilayah,
                "status": "Aktif",
                "sk_berlaku_sampai": "2027-12-31",
                "no_sertifikat_kompetensi": f"BNSP-P3H-2024-{new_pid:03d}",
                "penyelenggara_kompetensi": "BNSP",
                "tgl_terbit_kompetensi": datetime.now().strftime("%Y-%m-%d"),
                "berlaku_kompetensi_sampai": (datetime.now() + timedelta(days=3*365)).strftime("%Y-%m-%d"),
                "target_bulanan": 5,
                "total_binaan": 0,
                "sertifikat_terbit": 0,
                "proses": 0,
                "pending": 0,
                "avatar": avatar,
            })
            USERS.append({
                "id": new_user_id,
                "name": nama,
                "email": email,
                "password": password,
                "role": "pendamping",
                "avatar": avatar,
                "pendamping_id": new_pid,
            })
            add_audit(nama, "Registrasi", f"Pendaftaran akun Pendamping P3H baru ({nama})")
        else: # pelaku_usaha
            nama_usaha = request.form.get("nama_usaha", f"Usaha {nama}").strip() or f"Usaha {nama}"
            nib = request.form.get("nib", f"{8120400000000 + len(PELAKU_USAHA) + 1}").strip() or f"{8120400000000 + len(PELAKU_USAHA) + 1}"
            jenis_produk = request.form.get("jenis_produk", "Makanan ringan").strip() or "Makanan ringan"
            alamat = request.form.get("alamat", "Bandung").strip() or "Bandung"
            new_puid = len(PELAKU_USAHA) + 1
            assigned_pend = PENDAMPING[0]["id"] if PENDAMPING else 1

            PELAKU_USAHA.append({
                "id": new_puid,
                "nama_usaha": nama_usaha,
                "nama_pemilik": nama,
                "nik": f"3201****{new_puid:02d}0185{new_puid:03d}",
                "nib": nib,
                "alamat": alamat,
                "kontak": no_telp or "081234567890",
                "jenis_usaha": "UMKM Pangan",
                "jenis_produk": jenis_produk,
                "tanggal_mulai": datetime.now().strftime("%Y-%m-%d"),
                "pendamping_id": assigned_pend,
                "status": "Belum Diajukan",
                "terakhir_update": datetime.now().strftime("%Y-%m-%d"),
                "catatan": "Baru mendaftar melalui sistem portal.",
            })
            if PENDAMPING:
                PENDAMPING[0]["total_binaan"] += 1

            USERS.append({
                "id": new_user_id,
                "name": nama,
                "email": email,
                "password": password,
                "role": "pelaku_usaha",
                "avatar": avatar,
                "nib": nib,
            })
            add_audit(nama, "Registrasi", f"Pendaftaran akun Pelaku Usaha baru ({nama_usaha})")

        flash("Pendaftaran berhasil! Silakan login menggunakan email dan kata sandi Anda.", "success")
        return redirect(url_for("login"))

    return render_template("daftar.html")

@app.route("/logout")
def logout():
    if "user_id" in session:
        user = get_user_by_id(session["user_id"])
        if user:
            add_audit(user["name"], "Logout", "Logout dari sistem")
    session.clear()
    flash("Anda telah berhasil logout.", "info")
    return redirect(url_for("login"))

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    role = user["role"]

    # Hitung statistik umum
    total_pendamping = len(PENDAMPING)
    aktif = sum(1 for p in PENDAMPING if p["status"] == "Aktif")
    nonaktif = total_pendamping - aktif

    total_pelaku = len(PELAKU_USAHA)
    status_count = {s: sum(1 for p in PELAKU_USAHA if p["status"] == s) for s in STATUS_LIST}
    sertifikat_bulan_ini = sum(1 for p in PELAKU_USAHA if p["status"] == "Sertifikat Terbit")

    # Pendamping dengan sertifikat/SK segera habis
    hampir_habis = 0
    for p in PENDAMPING:
        sk_status, sk_cls = hitung_status_sk(p["sk_berlaku_sampai"])
        komp_status, komp_cls = hitung_status_kompetensi(p["berlaku_kompetensi_sampai"])
        if sk_cls in ["warning", "danger"] or komp_cls in ["warning", "danger"]:
            hampir_habis += 1

    # Wilayah stats
    wilayah_stats = {}
    for p in PELAKU_USAHA:
        pend = get_pendamping_by_id(p["pendamping_id"])
        if pend:
            wil = pend["wilayah"]
            wilayah_stats[wil] = wilayah_stats.get(wil, 0) + 1

    # Top pendamping
    top_pendamping = sorted(PENDAMPING, key=lambda x: x["total_binaan"], reverse=True)[:5]

    # Untuk role pendamping: tampilkan data binaannya
    binaan_list = []
    if role == "pendamping":
        pend_id = user.get("pendamping_id")
        if pend_id:
            binaan_list = get_pelaku_by_pendamping(pend_id)
            pendamping_data = get_pendamping_by_id(pend_id)
        else:
            pendamping_data = None
    else:
        pendamping_data = None

    return render_template("dashboard.html",
        user=user,
        total_pendamping=total_pendamping, aktif=aktif, nonaktif=nonaktif,
        total_pelaku=total_pelaku, status_count=status_count,
        sertifikat_bulan_ini=sertifikat_bulan_ini, hampir_habis=hampir_habis,
        wilayah_stats=json.dumps(wilayah_stats),
        top_pendamping=top_pendamping,
        trend_data=json.dumps(TREND_BULANAN),
        binaan_list=binaan_list, pendamping_data=pendamping_data,
        hitung_persen=hitung_persen, get_kpi_color=get_kpi_color,
        hitung_status_sk=hitung_status_sk, hitung_status_kompetensi=hitung_status_kompetensi,
        STATUS_LIST=STATUS_LIST,
    )

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: PENDAMPING
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/pendamping")
@login_required
@role_required("admin", "pimpinan")
def daftar_pendamping():
    user = get_user_by_id(session["user_id"])
    pendamping_list = []
    for p in PENDAMPING:
        sk_status, sk_cls = hitung_status_sk(p["sk_berlaku_sampai"])
        komp_status, komp_cls = hitung_status_kompetensi(p["berlaku_kompetensi_sampai"])
        binaan = get_pelaku_by_pendamping(p["id"])
        persen = hitung_persen(p["total_binaan"], p["target_bulanan"] * 12)
        pendamping_list.append({
            **p,
            "sk_status": sk_status, "sk_cls": sk_cls,
            "komp_status": komp_status, "komp_cls": komp_cls,
            "jumlah_binaan": len(binaan),
            "persen_target": persen,
            "kpi_color": get_kpi_color(persen),
        })
    return render_template("pendamping/daftar.html", user=user, pendamping_list=pendamping_list)

@app.route("/pendamping/<int:pid>")
@login_required
@role_required("admin", "pimpinan")
def detail_pendamping(pid):
    user = get_user_by_id(session["user_id"])
    p = get_pendamping_by_id(pid)
    if not p:
        flash("Pendamping tidak ditemukan.", "danger")
        return redirect(url_for("daftar_pendamping"))

    sk_status, sk_cls = hitung_status_sk(p["sk_berlaku_sampai"])
    komp_status, komp_cls = hitung_status_kompetensi(p["berlaku_kompetensi_sampai"])
    binaan = get_pelaku_by_pendamping(pid)
    persen = hitung_persen(p["total_binaan"], p["target_bulanan"] * 12)
    status_dist = {s: sum(1 for b in binaan if b["status"] == s) for s in STATUS_LIST}
    return render_template("pendamping/detail.html",
        user=user, p=p, binaan=binaan,
        sk_status=sk_status, sk_cls=sk_cls,
        komp_status=komp_status, komp_cls=komp_cls,
        persen=persen, kpi_color=get_kpi_color(persen),
        status_dist=json.dumps(status_dist),
        STATUS_LIST=STATUS_LIST,
    )

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: PELAKU USAHA
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/pelaku-usaha")
@login_required
@role_required("admin", "pimpinan")
def daftar_pelaku_usaha():
    user = get_user_by_id(session["user_id"])
    # Filter
    q = request.args.get("q", "").lower()
    status_filter = request.args.get("status", "")
    wilayah_filter = request.args.get("wilayah", "")
    pendamping_filter = request.args.get("pendamping_id", "")

    filtered = PELAKU_USAHA
    if q:
        filtered = [p for p in filtered if q in p["nama_usaha"].lower() or q in p["nama_pemilik"].lower() or q in p["nib"]]
    if status_filter:
        filtered = [p for p in filtered if p["status"] == status_filter]
    if pendamping_filter:
        try:
            pid = int(pendamping_filter)
            filtered = [p for p in filtered if p["pendamping_id"] == pid]
        except:
            pass

    # Pagination
    page = int(request.args.get("page", 1))
    per_page = 20
    total = len(filtered)
    pages = (total + per_page - 1) // per_page
    paginated = filtered[(page - 1) * per_page: page * per_page]

    return render_template("pelaku/daftar.html",
        user=user, pelaku_list=paginated,
        total=total, page=page, pages=pages, per_page=per_page,
        STATUS_LIST=STATUS_LIST, PENDAMPING=PENDAMPING,
        q=q, status_filter=status_filter, wilayah_filter=wilayah_filter,
        get_pendamping_by_id=get_pendamping_by_id,
    )

@app.route("/pelaku-usaha/<int:pid>")
@login_required
@role_required("admin", "pimpinan", "pendamping")
def detail_pelaku_usaha(pid):
    user = get_user_by_id(session["user_id"])
    pu = get_pelaku_by_id(pid)
    if not pu:
        flash("Pelaku usaha tidak ditemukan.", "danger")
        return redirect(url_for("daftar_pelaku_usaha") if user["role"] != "pendamping" else url_for("dashboard"))

    # Pendamping hanya bisa lihat binaannya sendiri
    if user["role"] == "pendamping":
        pend_id = user.get("pendamping_id")
        if pu["pendamping_id"] != pend_id:
            flash("Anda tidak memiliki akses ke data ini.", "danger")
            return redirect(url_for("dashboard"))

    pendamping = get_pendamping_by_id(pu["pendamping_id"])
    history = generate_status_history(pid, pu["status"])
    return render_template("pelaku/detail.html",
        user=user, pu=pu, pendamping=pendamping,
        history=history, STATUS_LIST=STATUS_LIST,
    )

@app.route("/pelaku-usaha/<int:pid>/update-status", methods=["POST"])
@login_required
@role_required("admin", "pendamping")
def update_status_pelaku(pid):
    user = get_user_by_id(session["user_id"])
    pu = get_pelaku_by_id(pid)
    if not pu:
        return jsonify({"error": "Not found"}), 404

    new_status = request.form.get("status")
    catatan = request.form.get("catatan", "")
    if new_status in STATUS_LIST:
        pu["status"] = new_status
        pu["catatan"] = catatan
        pu["terakhir_update"] = datetime.now().strftime("%Y-%m-%d")
        add_audit(user["name"], "Update Status", f"Update status {pu['nama_usaha']} → {new_status}")
        flash(f"Status berhasil diperbarui menjadi: {new_status}", "success")
    else:
        flash("Status tidak valid.", "danger")
    return redirect(url_for("detail_pelaku_usaha", pid=pid))

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: PENUGASAN
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/penugasan")
@login_required
@role_required("admin")
def penugasan():
    user = get_user_by_id(session["user_id"])
    return render_template("penugasan.html",
        user=user, PELAKU_USAHA=PELAKU_USAHA, PENDAMPING=PENDAMPING,
        get_pendamping_by_id=get_pendamping_by_id,
        STATUS_LIST=STATUS_LIST,
    )

@app.route("/penugasan/assign", methods=["POST"])
@login_required
@role_required("admin")
def assign_pendamping():
    user = get_user_by_id(session["user_id"])
    pelaku_id = int(request.form.get("pelaku_id"))
    pendamping_id = int(request.form.get("pendamping_id"))
    pu = get_pelaku_by_id(pelaku_id)
    pend = get_pendamping_by_id(pendamping_id)
    if pu and pend:
        old_pend_id = pu["pendamping_id"]
        old_pend = get_pendamping_by_id(old_pend_id)
        pu["pendamping_id"] = pendamping_id
        add_audit(user["name"], "Assign Pendamping",
            f"Reassign {pu['nama_usaha']} dari {old_pend['nama'] if old_pend else '-'} ke {pend['nama']}")
        flash(f"Berhasil assign {pu['nama_usaha']} ke {pend['nama']}", "success")
    else:
        flash("Data tidak ditemukan.", "danger")
    return redirect(url_for("penugasan"))

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: TARGET & KINERJA
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/target-kinerja")
@login_required
@role_required("admin", "pimpinan")
def target_kinerja():
    user = get_user_by_id(session["user_id"])
    kinerja_data = []
    for p in PENDAMPING:
        binaan = get_pelaku_by_pendamping(p["id"])
        terbit = sum(1 for b in binaan if b["status"] == "Sertifikat Terbit")
        proses = sum(1 for b in binaan if b["status"] == "Proses Pendampingan")
        macet = sum(1 for b in binaan if b["status"] not in ["Sertifikat Terbit", "Ditolak"])
        target_tahunan = p["target_bulanan"] * 12
        persen = hitung_persen(terbit, target_tahunan)
        sk_status, sk_cls = hitung_status_sk(p["sk_berlaku_sampai"])
        kinerja_data.append({
            **p,
            "jumlah_binaan": len(binaan),
            "sertifikat_terbit": terbit,
            "proses": proses,
            "macet": macet,
            "target_tahunan": target_tahunan,
            "persen": persen,
            "kpi_color": get_kpi_color(persen),
            "sk_status": sk_status,
            "sk_cls": sk_cls,
        })
    return render_template("target_kinerja.html", user=user, kinerja_data=kinerja_data)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: IMPORT DATA
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/import-data", methods=["GET", "POST"])
@login_required
@role_required("admin")
def import_data():
    user = get_user_by_id(session["user_id"])
    terakhir_import = "29 Sep 2024, 14:30 WIB"
    preview_data = []
    errors = []
    if request.method == "POST":
        # Simulasi preview import
        preview_data = [
            {"no": 1, "nama_usaha": "Kue Lapis Bu Rini", "pemilik": "Rini Marlina", "nib": "8120400009999", "status": "OK"},
            {"no": 2, "nama_usaha": "Bakso Sapi Mas Jono", "pemilik": "Jono Prasetyo", "nib": "8120400000002", "status": "Duplikat (NIB sudah ada)"},
            {"no": 3, "nama_usaha": "Mie Pangsit Bu Dewi", "pemilik": "Dewi Sukma", "nib": "8120400009998", "status": "OK"},
            {"no": 4, "nama_usaha": "Catering Pak Budi", "pemilik": "", "nib": "", "status": "Error: NIB kosong"},
        ]
        errors = [d for d in preview_data if "Error" in d["status"] or "Duplikat" in d["status"]]
        flash(f"Preview import: {len(preview_data)} baris, {len(errors)} masalah terdeteksi.", "info")
    return render_template("import_data.html",
        user=user, terakhir_import=terakhir_import,
        preview_data=preview_data, errors=errors,
    )

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: LAPORAN
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/laporan")
@login_required
@role_required("admin", "pimpinan")
def laporan():
    user = get_user_by_id(session["user_id"])
    # Statistik per wilayah
    wilayah_stats = {}
    for p in PELAKU_USAHA:
        pend = get_pendamping_by_id(p["pendamping_id"])
        if pend:
            wil = pend["wilayah"]
            if wil not in wilayah_stats:
                wilayah_stats[wil] = {"total": 0, "sertifikat": 0, "proses": 0}
            wilayah_stats[wil]["total"] += 1
            if p["status"] == "Sertifikat Terbit":
                wilayah_stats[wil]["sertifikat"] += 1
            elif p["status"] == "Proses Pendampingan":
                wilayah_stats[wil]["proses"] += 1
    return render_template("laporan.html",
        user=user, PENDAMPING=PENDAMPING, PELAKU_USAHA=PELAKU_USAHA,
        STATUS_LIST=STATUS_LIST, wilayah_stats=wilayah_stats,
        trend_data=json.dumps(TREND_BULANAN),
        get_pelaku_by_pendamping=get_pelaku_by_pendamping,
        hitung_persen=hitung_persen,
    )

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: MANAJEMEN USER
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/manajemen-user")
@login_required
@role_required("admin")
def manajemen_user():
    user = get_user_by_id(session["user_id"])
    return render_template("manajemen_user.html", user=user, users=USERS)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: AUDIT LOG
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/audit-log")
@login_required
@role_required("admin")
def audit_log():
    user = get_user_by_id(session["user_id"])
    return render_template("audit_log.html", user=user, logs=AUDIT_LOG)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: PENGATURAN
# ─────────────────────────────────────────────────────────────────────────────

SETTINGS = {"portal_pelaku_aktif": True}

@app.route("/pengaturan", methods=["GET", "POST"])
@login_required
@role_required("admin")
def pengaturan():
    user = get_user_by_id(session["user_id"])
    if request.method == "POST":
        portal = request.form.get("portal_pelaku_aktif") == "on"
        SETTINGS["portal_pelaku_aktif"] = portal
        add_audit(user["name"], "Ubah Pengaturan", f"Portal Pelaku Usaha: {'Aktif' if portal else 'Nonaktif'}")
        flash("Pengaturan berhasil disimpan.", "success")
    return render_template("pengaturan.html", user=user, settings=SETTINGS)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES: PORTAL PELAKU USAHA (READ-ONLY)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/portal/cek-status", methods=["GET", "POST"])
def portal_cek_status():
    if not SETTINGS.get("portal_pelaku_aktif", True):
        return render_template("portal/nonaktif.html")

    data = None
    error = None
    if request.method == "POST":
        nib = request.form.get("nib", "").strip()
        pu = get_pelaku_by_nib(nib)
        if pu:
            pendamping = get_pendamping_by_id(pu["pendamping_id"])
            history = generate_status_history(pu["id"], pu["status"])
            data = {"pu": pu, "pendamping": pendamping, "history": history}
        else:
            error = "NIB tidak ditemukan. Pastikan NIB Anda sudah terdaftar di sistem LP3H."

    return render_template("portal/cek_status.html", data=data, error=error, STATUS_LIST=STATUS_LIST)

@app.route("/portal/status-saya")
@login_required
def portal_status():
    user = get_user_by_id(session["user_id"])
    if not SETTINGS.get("portal_pelaku_aktif", True) and user["role"] != "admin":
        flash("Portal Pelaku Usaha sedang tidak aktif.", "warning")
        return redirect(url_for("login"))

    if user["role"] != "pelaku_usaha":
        return redirect(url_for("dashboard"))

    nib = user.get("nib")
    pu = get_pelaku_by_nib(nib)
    if not pu:
        pu = PELAKU_USAHA[0]  # fallback demo

    pendamping = get_pendamping_by_id(pu["pendamping_id"])
    history = generate_status_history(pu["id"], pu["status"])
    return render_template("portal/status_saya.html",
        user=user, pu=pu, pendamping=pendamping,
        history=history, STATUS_LIST=STATUS_LIST,
    )

# ─────────────────────────────────────────────────────────────────────────────
# API ENDPOINTS (untuk chart)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/status-distribution")
@login_required
def api_status_dist():
    dist = {s: sum(1 for p in PELAKU_USAHA if p["status"] == s) for s in STATUS_LIST}
    return jsonify(dist)

@app.route("/api/wilayah-stats")
@login_required
def api_wilayah_stats():
    stats = {}
    for p in PELAKU_USAHA:
        pend = get_pendamping_by_id(p["pendamping_id"])
        if pend:
            wil = pend["wilayah"]
            stats[wil] = stats.get(wil, 0) + 1
    return jsonify(stats)

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE FILTER
# ─────────────────────────────────────────────────────────────────────────────

@app.template_filter("formatdate")
def formatdate(value, fmt="%d %b %Y"):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime(fmt)
    except:
        return value

@app.template_filter("persen")
def persen_filter(val, total):
    return hitung_persen(val, total)

# ─────────────────────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template("404.html"), 403


if __name__ == "__main__":
    app.run(debug=True, port=8000)
