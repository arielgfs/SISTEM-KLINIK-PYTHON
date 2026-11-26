from modules import database
from modules.utils import (
    bersihkan_layar, jeda, id_berikutnya, konfirmasi,
    pilih_menu, pilih_kunci, tampilkan_tabel
)


def tampilkan_layanan():
    """Tampilkan_Layanan: mengembalikan False bila data kosong."""
    if len(database.db["layanan"]) == 0:
        print("\nData belum tersedia")
        return False

    baris = [
        (nomor, kode, data["nama"], data["keterangan"])
        for nomor, (kode, data) in enumerate(database.db["layanan"].items(), 1)
    ]

    tampilkan_tabel(
        "DAFTAR LAYANAN",
        ("No", "ID", "Nama Layanan", "Deskripsi"),
        baris,
        kiri=("Nama Layanan", "Deskripsi")
    )
    return True


def tambah_layanan():
    nama = input("Nama layanan: ").strip()
    deskripsi = input("Deskripsi: ").strip()

    if nama == "" or deskripsi == "":
        print("Data kosong atau tidak valid")
        return

    if nama.lower() in {data["nama"].lower() for data in database.db["layanan"].values()}:
        print("Nama layanan sudah terdaftar")
        return

    kode = id_berikutnya(database.db["layanan"])
    database.db["layanan"][kode] = {"nama": nama, "keterangan": deskripsi}
    database.simpan(database.db, ["layanan"])
    print("Layanan berhasil ditambah dengan ID", kode)


def ubah_layanan():
    if not tampilkan_layanan():
        return

    kode = pilih_kunci(database.db["layanan"], "Nomor layanan yang ingin diubah: ")

    if kode is None:
        return

    nama = input("Nama layanan baru: ").strip()
    deskripsi = input("Deskripsi baru: ").strip()

    if nama == "" or deskripsi == "":
        print("Data kosong atau tidak valid")
        return

    nama_lain = {
        isi["nama"].lower() for kode_lain, isi in database.db["layanan"].items() if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama layanan sudah terdaftar")
        return

    database.db["layanan"][kode] = {"nama": nama, "keterangan": deskripsi}
    database.simpan(database.db, ["layanan"])
    print("Data layanan berhasil diubah")


def hapus_layanan():
    if not tampilkan_layanan():
        return

    kode = pilih_kunci(database.db["layanan"], "Nomor layanan yang ingin dihapus: ")

    if kode is None:
        return

    if konfirmasi("Hapus " + database.db["layanan"][kode]["nama"]):
        del database.db["layanan"][kode]
        database.simpan(database.db, ["layanan"])
        print("Data layanan berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_layanan():
    daftar_menu = [
        "Tambah Data Layanan",
        "Tampilkan Data Layanan",
        "Ubah Data Layanan",
        "Hapus Data Layanan",
        "Kembali ke Menu Admin"
    ]

    while True:
        bersihkan_layar()
        pilihan = pilih_menu("MENU KELOLA LAYANAN", daftar_menu)

        if pilihan == 5:
            return

        if pilihan == 1:
            tambah_layanan()
        elif pilihan == 2:
            tampilkan_layanan()
        elif pilihan == 3:
            ubah_layanan()
        elif pilihan == 4:
            hapus_layanan()

        jeda()
