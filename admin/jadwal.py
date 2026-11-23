from datetime import date, datetime

from modules import database
from modules.reservasi import HARI
from modules.utils import (
    bersihkan_layar, jeda, id_berikutnya, konfirmasi,
    pilih_menu, pilih_kunci, tampilkan_tabel
)
from admin.dokter import tampilkan_dokter


def buat_slot(shift):
    """Shift ("08:00", "12:00") -> slot per jam ["08:00", "09:00", "10:00", "11:00"]."""
    jam_mulai = int(shift[0][:2])
    jam_selesai = int(shift[1][:2])
    return [f"{jam:02d}:00" for jam in range(jam_mulai, jam_selesai)]


def format_jam(slot):
    return slot[0] + " - " + slot[-1]


def hitung_terisi(kode_jadwal):
    """Jumlah reservasi aktif (hari ini dan seterusnya) yang memakai jadwal ini."""
    jadwal = database.db["jadwal"][kode_jadwal]
    hari_ini = str(date.today())
    jumlah = 0

    for isi in database.db["reservasi"].values():
        if (
            isi["id_dokter"] == jadwal["id_dokter"]
            and isi["status"] in database.STATUS_AKTIF
            and isi["tanggal"] >= hari_ini
            and isi["jam"] in jadwal["jam"]
            and HARI[datetime.strptime(isi["tanggal"], "%Y-%m-%d").weekday()] == jadwal["hari"]
        ):
            jumlah += 1

    return jumlah


def cek_bentrok(kode_dokter, hari, slot, abaikan=None):
    return any(
        kode != abaikan
        and isi["id_dokter"] == kode_dokter
        and isi["hari"] == hari
        and set(isi["jam"]) & set(slot)
        for kode, isi in database.db["jadwal"].items()
    )


def pilih_hari():
    daftar_hari = list(database.DAFTAR_HARI)
    return daftar_hari[pilih_menu("Pilih hari praktik", daftar_hari) - 1]


def pilih_jam():
    daftar_shift = [shift[0] + " - " + shift[1] for shift in database.JAM_PRAKTIK]
    shift = database.JAM_PRAKTIK[pilih_menu("Pilih jam praktik", daftar_shift) - 1]
    return buat_slot(shift)


def tampilkan_jadwal():
    baris = [
        (
            nomor,
            kode,
            database.db["dokter"].get(data["id_dokter"], {"nama": "(data dihapus)"})["nama"],
            data["hari"],
            format_jam(data["jam"]),
            len(data["jam"]),
            hitung_terisi(kode)
        )
        for nomor, (kode, data) in enumerate(database.db["jadwal"].items(), 1)
    ]

    tampilkan_tabel(
        "JADWAL DOKTER",
        ("No", "ID", "Dokter", "Hari", "Jam Praktik", "Slot/Hari", "Reservasi Aktif"),
        baris,
        kiri=("Dokter",)
    )


def tambah_jadwal():
    if len(database.db["dokter"]) == 0:
        print("Data dokter masih kosong, tambahkan dokter terlebih dahulu")
        return

    tampilkan_dokter()
    kode_dokter = pilih_kunci(database.db["dokter"], "Pilih nomor dokter: ")

    if kode_dokter is None:
        return

    hari = pilih_hari()
    slot = pilih_jam()

    if cek_bentrok(kode_dokter, hari, slot):
        print("Jadwal dokter pada hari dan jam tersebut sudah ada")
        return

    kode = id_berikutnya(database.db["jadwal"])

    database.db["jadwal"][kode] = {
        "id_dokter": kode_dokter,
        "hari": hari,
        "jam": slot
    }
    database.simpan(database.db, ["jadwal"])

    print("Jadwal berhasil ditambahkan dengan ID", kode)


def edit_jadwal():
    kode = pilih_kunci(database.db["jadwal"], "Masukkan nomor jadwal yang ingin diedit: ")

    if kode is None:
        return

    data = database.db["jadwal"][kode]
    print("Dokter pada jadwal:", database.db["dokter"].get(data["id_dokter"], {"nama": "(data dihapus)"})["nama"])

    terisi = hitung_terisi(kode)

    if terisi > 0:
        print("Jadwal tidak bisa diubah karena masih ada reservasi aktif:", terisi)
        return

    hari = pilih_hari()
    slot = pilih_jam()

    if cek_bentrok(data["id_dokter"], hari, slot, kode):
        print("Jadwal dokter pada hari dan jam tersebut sudah ada")
        return

    data["hari"] = hari
    data["jam"] = slot
    database.simpan(database.db, ["jadwal"])

    print("Jadwal berhasil diedit")


def hapus_jadwal():
    kode = pilih_kunci(database.db["jadwal"], "Masukkan nomor jadwal yang ingin dihapus: ")

    if kode is None:
        return

    terisi = hitung_terisi(kode)

    if terisi > 0:
        print("Jadwal tidak bisa dihapus karena masih ada reservasi aktif:", terisi)
        return

    if konfirmasi("Yakin menghapus jadwal " + kode):
        del database.db["jadwal"][kode]
        database.simpan(database.db, ["jadwal"])
        print("Jadwal berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_jadwal():
    daftar_menu = [
        "Tambah Jadwal",
        "Edit Jadwal",
        "Hapus Jadwal",
        "Kembali"
    ]

    while True:
        bersihkan_layar()
        tampilkan_jadwal()

        pilihan = pilih_menu("KELOLA JADWAL DOKTER", daftar_menu)

        if pilihan == 4:
            return

        if pilihan == 1:
            tambah_jadwal()
        elif pilihan == 2:
            edit_jadwal()
        elif pilihan == 3:
            hapus_jadwal()

        jeda()
