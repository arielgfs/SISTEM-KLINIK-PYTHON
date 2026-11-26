from datetime import date, datetime

from modules import database
from modules.reservasi import HARI, tampilkan_jadwal
from modules.utils import (
    bersihkan_layar, jeda, id_berikutnya, jam_ke_menit, ke_angka, konfirmasi,
    menit_ke_jam, pilih_menu, pilih_kunci
)
from admin.dokter import tampilkan_dokter


def hitung_terisi(kode_jadwal):
    """Jumlah reservasi aktif (hari ini dan seterusnya) yang memakai jadwal ini."""
    jadwal = database.db["jadwal"][kode_jadwal]
    hari_ini = str(date.today())

    return sum(
        1 for isi in database.db["reservasi"].values()
        if isi["id_dokter"] == jadwal["id_dokter"]
        and isi["status"] in database.STATUS_AKTIF
        and isi["tanggal"] >= hari_ini
        and HARI[datetime.strptime(isi["tanggal"], "%Y-%m-%d").weekday()] == jadwal["hari"]
    )


def cek_bentrok(kode_dokter, hari, mulai, selesai, abaikan=None):
    """True bila rentang jam bertumpuk dengan jadwal lain dokter yang sama di hari yang sama."""
    return any(
        kode != abaikan
        and isi["id_dokter"] == kode_dokter
        and isi["hari"] == hari
        and mulai < jam_ke_menit(isi["jam_selesai"])
        and jam_ke_menit(isi["jam_mulai"]) < selesai
        for kode, isi in database.db["jadwal"].items()
    )


def baca_jadwal():
    """Meminta hari, jam mulai, jam selesai, kuota. Mengembalikan dict, atau None bila tidak valid."""
    hari = pilih_menu("Pilih hari praktik", list(database.DAFTAR_HARI))
    hari = database.DAFTAR_HARI[hari - 1]
    mulai = jam_ke_menit(input("Jam mulai (HH:MM): "))
    selesai = jam_ke_menit(input("Jam selesai (HH:MM): "))
    kuota = ke_angka(input("Kuota pasien per hari: "))

    if mulai is None or selesai is None or kuota is None or kuota < 1:
        print("Data kosong atau tidak valid")
        return None

    if selesai - mulai < 60:
        print("Data tidak valid: jam selesai minimal 1 jam setelah jam mulai")
        return None

    return {"hari": hari, "mulai": mulai, "selesai": selesai, "kuota": kuota}


def tampilkan_jadwal_admin():
    """Tampilkan_Jadwal: mengembalikan False bila data kosong."""
    return tampilkan_jadwal(database.db, "JADWAL PRAKTIK DOKTER")


def tambah_jadwal():
    if not tampilkan_dokter():
        return

    kode_dokter = pilih_kunci(database.db["dokter"], "Nomor dokter: ")

    if kode_dokter is None:
        return

    data = baca_jadwal()

    if data is None:
        return

    if cek_bentrok(kode_dokter, data["hari"], data["mulai"], data["selesai"]):
        print("Jadwal dokter pada hari dan jam tersebut bentrok dengan jadwal lain")
        return

    kode = id_berikutnya(database.db["jadwal"])
    database.db["jadwal"][kode] = {
        "id_dokter": kode_dokter,
        "hari": data["hari"],
        "jam_mulai": menit_ke_jam(data["mulai"]),
        "jam_selesai": menit_ke_jam(data["selesai"]),
        "kuota": data["kuota"]
    }
    database.simpan(database.db, ["jadwal"])
    print("Jadwal praktik berhasil ditambah dengan ID", kode)


def ubah_jadwal():
    if not tampilkan_jadwal_admin():
        return

    kode = pilih_kunci(database.db["jadwal"], "Nomor jadwal yang ingin diubah: ")

    if kode is None:
        return

    if hitung_terisi(kode) > 0:
        print("Jadwal tidak bisa diubah karena masih ada reservasi aktif:", hitung_terisi(kode))
        return

    data = baca_jadwal()

    if data is None:
        return

    jadwal = database.db["jadwal"][kode]

    if cek_bentrok(jadwal["id_dokter"], data["hari"], data["mulai"], data["selesai"], kode):
        print("Jadwal dokter pada hari dan jam tersebut bentrok dengan jadwal lain")
        return

    jadwal["hari"] = data["hari"]
    jadwal["jam_mulai"] = menit_ke_jam(data["mulai"])
    jadwal["jam_selesai"] = menit_ke_jam(data["selesai"])
    jadwal["kuota"] = data["kuota"]
    database.simpan(database.db, ["jadwal"])
    print("Data jadwal berhasil diubah")


def hapus_jadwal():
    if not tampilkan_jadwal_admin():
        return

    kode = pilih_kunci(database.db["jadwal"], "Nomor jadwal yang ingin dihapus: ")

    if kode is None:
        return

    if hitung_terisi(kode) > 0:
        print("Jadwal tidak bisa dihapus karena masih ada reservasi aktif:", hitung_terisi(kode))
        return

    if konfirmasi("Hapus jadwal " + kode):
        del database.db["jadwal"][kode]
        database.simpan(database.db, ["jadwal"])
        print("Data jadwal berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_jadwal():
    daftar_menu = [
        "Tambah Jadwal Praktik",
        "Tampilkan Jadwal Praktik",
        "Ubah Jadwal Praktik",
        "Hapus Jadwal Praktik",
        "Kembali ke Menu Admin"
    ]

    while True:
        bersihkan_layar()
        pilihan = pilih_menu("MENU KELOLA JADWAL", daftar_menu)

        if pilihan == 5:
            return

        if pilihan == 1:
            tambah_jadwal()
        elif pilihan == 2:
            tampilkan_jadwal_admin()
        elif pilihan == 3:
            ubah_jadwal()
        elif pilihan == 4:
            hapus_jadwal()

        jeda()
