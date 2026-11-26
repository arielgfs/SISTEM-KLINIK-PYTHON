import json
import os


FOLDER_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

SEMUA_TABEL = [
    "users", "dokter", "pasien", "layanan", "jadwal", "reservasi",
    "log_riwayat", "inventaris_alat", "obat", "transaksi"
]

DAFTAR_HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu")

KONDISI_ALAT = ("Baik", "Rusak", "Dalam perbaikan")
STATUS_RESERVASI = ("Menunggu", "Hadir", "Selesai", "Dibatalkan")
STATUS_AKTIF = {"Menunggu", "Hadir"}
BATAS_LOGIN = 3


db = {}


def jalur_tabel(nama_tabel):
    return os.path.join(FOLDER_DATA, nama_tabel + ".json")


def muat_tabel(nama_tabel):
    """Membaca satu file JSON. File yang belum ada / kosong dianggap data kosong."""
    jalur = jalur_tabel(nama_tabel)

    if not os.path.exists(jalur):
        return {}

    with open(jalur, "r", encoding="utf-8") as berkas:
        isi = berkas.read().strip()

    if isi == "":
        return {}

    return json.loads(isi)


def muat_database(daftar_tabel=None):
    """Membaca beberapa file JSON sekaligus -> dict {nama_tabel: data}."""
    if daftar_tabel is None:
        daftar_tabel = SEMUA_TABEL

    return {nama: muat_tabel(nama) for nama in daftar_tabel}


def simpan(data, daftar_tabel=None):
    """Menyimpan tabel-tabel yang disebut (default: semua yang ada di data)."""
    if daftar_tabel is None:
        daftar_tabel = list(data)

    os.makedirs(FOLDER_DATA, exist_ok=True)

    for nama in daftar_tabel:
        jalur = jalur_tabel(nama)
        sementara = jalur + ".tmp"

        with open(sementara, "w", encoding="utf-8") as berkas:
            json.dump(data[nama], berkas, indent=4, ensure_ascii=False)

        os.replace(sementara, jalur)


def muat_ulang():
    """Memuat ulang data bersama (database.db) dari file JSON."""
    db.clear()
    db.update(muat_database())
    return db
