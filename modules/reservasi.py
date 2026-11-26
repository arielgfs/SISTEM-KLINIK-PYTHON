"""Fungsi reservasi yang dipakai bersama oleh resepsionis/ dan pasien/.
Semua fungsi menerima `db` (dict hasil database.muat_database) dan langsung menyimpan perubahan ke JSON."""
from datetime import date

from modules import database
from modules.utils import (
    id_berikutnya, jam_ke_menit, ke_angka, menit_ke_jam, nama_dari,
    parse_tanggal, sekarang, tampilkan_tabel
)

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def catat_log(db, id_reservasi, id_pasien, aksi, detail, user):
    """Log_jadwal: riwayat perubahan reservasi pasien (tabel log_riwayat, jenis 'reservasi')."""
    id_log = id_berikutnya(db["log_riwayat"])
    db["log_riwayat"][id_log] = {
        "jenis": "reservasi",
        "id_reservasi": id_reservasi,
        "id_pasien": id_pasien,
        "aksi": aksi,
        "detail": detail,
        "oleh": user,
        "waktu": sekarang()
    }


def catat_log_inventaris(db, jenis, id_item, nama, aksi, detail, user, jumlah=0):
    """Log perubahan alat (jenis 'alat') atau obat (jenis 'obat') di tabel log_riwayat."""
    id_log = id_berikutnya(db["log_riwayat"])
    db["log_riwayat"][id_log] = {
        "jenis": jenis,
        "id_item": id_item,
        "nama": nama,
        "aksi": aksi,
        "jumlah": jumlah,
        "detail": detail,
        "oleh": user,
        "waktu": sekarang()
    }


def log_jenis(db, jenis):
    """Log berjenis tertentu (log lama tanpa jenis dianggap 'reservasi'), urut waktu."""
    daftar = [isi for isi in db["log_riwayat"].values() if isi.get("jenis", "reservasi") == jenis]
    return sorted(daftar, key=lambda isi: isi["waktu"])


def daftar_slot(jadwal):
    """Slot per jam dari jam_mulai sampai jam_selesai, mis. 08:00-11:00 -> 08:00, 09:00, 10:00."""
    mulai = jam_ke_menit(jadwal["jam_mulai"])
    selesai = jam_ke_menit(jadwal["jam_selesai"])
    return [menit_ke_jam(menit) for menit in range(mulai, selesai - 59, 60)]


def jadwal_dokter_hari(db, id_dokter, hari):
    return [
        isi for isi in db["jadwal"].values()
        if isi["id_dokter"] == id_dokter and isi["hari"] == hari
    ]


def jam_terisi(db, id_dokter, tanggal, kecuali_id=None):
    """Jam yang sudah dipesan (status bukan Dibatalkan) pada dokter dan tanggal tertentu."""
    return [
        isi["jam"] for id_res, isi in db["reservasi"].items()
        if isi["id_dokter"] == id_dokter and isi["tanggal"] == str(tanggal)
        and isi["status"] != "Dibatalkan" and id_res != kecuali_id
    ]


def sisa_kuota(db, id_dokter, tanggal, kecuali_id=None):
    hari = HARI[tanggal.weekday()]
    kuota = sum(isi["kuota"] for isi in jadwal_dokter_hari(db, id_dokter, hari))
    return max(0, kuota - len(jam_terisi(db, id_dokter, tanggal, kecuali_id)))


def slot_tersedia(db, id_dokter, tanggal, kecuali_id=None):
    """Mengembalikan (daftar jam yang masih kosong, nama hari).
    Kosong bila dokter tidak praktik, kuota hari itu habis, atau semua jam terisi."""
    hari = HARI[tanggal.weekday()]
    semua_jam = []

    for jadwal in jadwal_dokter_hari(db, id_dokter, hari):
        for jam in daftar_slot(jadwal):
            if jam not in semua_jam:
                semua_jam.append(jam)

    if sisa_kuota(db, id_dokter, tanggal, kecuali_id) == 0:
        return [], hari

    terisi = jam_terisi(db, id_dokter, tanggal, kecuali_id)
    return sorted(jam for jam in semua_jam if jam not in terisi), hari


def pilih_slot(db, id_dokter, abaikan=None, tanggal_lama=None):
    """Input tanggal lalu jam. Mengembalikan (tanggal, jam), atau None bila jadwal tidak valid / slot penuh."""
    petunjuk = "Tanggal (YYYY-MM-DD)"
    if tanggal_lama:
        petunjuk += ", Enter = tetap " + tanggal_lama

    teks = input(petunjuk + ": ").strip()
    if teks == "" and tanggal_lama:
        teks = tanggal_lama

    tanggal = parse_tanggal(teks)

    if tanggal is None:
        print("Jadwal tidak valid: format tanggal salah. Contoh: 2026-11-12")
        return None

    if tanggal < date.today():
        print("Jadwal tidak valid: tanggal sudah lewat")
        return None

    tersedia, hari = slot_tersedia(db, id_dokter, tanggal, abaikan)

    if len(tersedia) == 0:
        print("Reservasi ditolak: dokter tidak praktik pada hari", hari, "atau slot penuh")
        return None

    tampilkan_tabel(
        "SLOT TERSEDIA - " + hari + ", " + str(tanggal)
        + " (sisa kuota " + str(sisa_kuota(db, id_dokter, tanggal, abaikan)) + ")",
        ("No", "Jam"),
        [(nomor, jam) for nomor, jam in enumerate(tersedia, 1)]
    )
    nomor = ke_angka(input("Pilih nomor jam: "))

    if nomor is None or nomor < 1 or nomor > len(tersedia):
        print("Jadwal tidak valid: pilihan jam tidak ada")
        return None

    return tanggal, tersedia[nomor - 1]


def buat_reservasi(db, id_pasien, id_dokter, tanggal, jam, user):
    """Menyimpan reservasi baru (status Menunggu) dan mencatat log. Mengembalikan ID reservasi."""
    id_baru = id_berikutnya(db["reservasi"])
    db["reservasi"][id_baru] = {
        "id_pasien": id_pasien,
        "id_dokter": id_dokter,
        "tanggal": str(tanggal),
        "jam": jam,
        "status": "Menunggu",
        "dibuat_oleh": user
    }
    catat_log(db, id_baru, id_pasien, "BUAT",
              str(tanggal) + " " + jam + " dengan " + nama_dari(db["dokter"], id_dokter), user)
    database.simpan(db, ["reservasi", "log_riwayat"])
    return id_baru


def ubah_jadwal(db, id_res, tanggal, jam, user):
    data = db["reservasi"][id_res]
    lama = data["tanggal"] + " " + data["jam"]
    data["tanggal"] = str(tanggal)
    data["jam"] = jam
    catat_log(db, id_res, data["id_pasien"], "UBAH", lama + " -> " + data["tanggal"] + " " + data["jam"], user)
    database.simpan(db, ["reservasi", "log_riwayat"])


def batalkan_reservasi(db, id_res, user):
    data = db["reservasi"][id_res]
    data["status"] = "Dibatalkan"
    catat_log(db, id_res, data["id_pasien"], "BATAL", data["tanggal"] + " " + data["jam"], user)
    database.simpan(db, ["reservasi", "log_riwayat"])


def tampilkan_reservasi(db, daftar, judul_tabel="RESERVASI"):
    baris = [
        (
            kode,
            nama_dari(db["pasien"], db["reservasi"][kode]["id_pasien"]),
            nama_dari(db["dokter"], db["reservasi"][kode]["id_dokter"]),
            db["reservasi"][kode]["tanggal"],
            db["reservasi"][kode]["jam"],
            db["reservasi"][kode]["status"]
        )
        for kode in daftar
    ]

    tampilkan_tabel(
        judul_tabel,
        ("ID", "Pasien", "Dokter", "Tanggal", "Jam", "Status"),
        baris,
        kiri=("Pasien", "Dokter", "Status")
    )


def tampilkan_jadwal(db, judul_tabel="JADWAL PRAKTIK DOKTER"):
    """Tabel jadwal praktik. Mengembalikan False (dan mencetak pesan) bila belum ada data."""
    if len(db["jadwal"]) == 0:
        print("\nData belum tersedia")
        return False

    baris = []
    for kode, data in db["jadwal"].items():
        dokter = db["dokter"].get(data["id_dokter"])
        baris.append((
            kode,
            data["id_dokter"],
            nama_dari(db["dokter"], data["id_dokter"]),
            dokter["spesialisasi"] if dokter else "-",
            data["hari"],
            data["jam_mulai"] + " - " + data["jam_selesai"],
            data["kuota"]
        ))

    tampilkan_tabel(
        judul_tabel,
        ("ID", "ID Dokter", "Dokter", "Spesialisasi", "Hari", "Jam Praktik", "Kuota/Hari"),
        baris,
        kiri=("Dokter", "Spesialisasi")
    )
    return True
