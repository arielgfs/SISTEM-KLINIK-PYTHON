from modules import database
from modules.utils import (
    bersihkan_layar, jeda, format_rupiah, id_berikutnya, input_teks,
    input_angka, konfirmasi, pilih_menu, pilih_kunci, tampilkan_tabel
)


def tampilkan_layanan():
    baris = [
        (nomor, kode, data["nama"], format_rupiah(data["harga"]), data["keterangan"])
        for nomor, (kode, data) in enumerate(database.db["layanan"].items(), 1)
    ]

    tampilkan_tabel(
        "DAFTAR LAYANAN",
        ("No", "ID", "Nama Layanan", "Harga", "Keterangan"),
        baris,
        kiri=("Nama Layanan", "Keterangan"),
        kanan=("Harga",)
    )


def tambah_layanan():
    nama = input_teks("Masukkan nama layanan: ")
    nama_terdaftar = {data["nama"].lower() for data in database.db["layanan"].values()}

    if nama.lower() in nama_terdaftar:
        print("Nama layanan sudah terdaftar")
        return

    harga = input_angka("Masukkan harga layanan: ", 0)
    keterangan = input_teks("Masukkan keterangan layanan: ")
    kode = id_berikutnya(database.db["layanan"])

    database.db["layanan"][kode] = {"nama": nama, "harga": harga, "keterangan": keterangan}
    database.simpan(database.db, ["layanan"])

    print("Layanan berhasil ditambahkan dengan ID", kode)


def edit_layanan():
    kode = pilih_kunci(database.db["layanan"], "Masukkan nomor layanan yang ingin diedit: ")

    if kode is None:
        return

    data = database.db["layanan"][kode]
    print("Kosongkan input jika tidak ingin mengubah data")

    nama = input_teks("Masukkan nama layanan baru: ", data["nama"])
    nama_lain = {
        isi["nama"].lower()
        for kode_lain, isi in database.db["layanan"].items()
        if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama layanan sudah terdaftar")
        return

    data["nama"] = nama
    data["harga"] = input_angka("Masukkan harga layanan baru: ", 0, data["harga"])
    data["keterangan"] = input_teks("Masukkan keterangan baru: ", data["keterangan"])
    database.simpan(database.db, ["layanan"])

    print("Layanan berhasil diedit")


def hapus_layanan():
    kode = pilih_kunci(database.db["layanan"], "Masukkan nomor layanan yang ingin dihapus: ")

    if kode is None:
        return

    if konfirmasi("Yakin menghapus " + database.db["layanan"][kode]["nama"]):
        del database.db["layanan"][kode]
        database.simpan(database.db, ["layanan"])
        print("Layanan berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_layanan():
    daftar_menu = [
        "Tambah Layanan",
        "Edit Layanan",
        "Hapus Layanan",
        "Kembali"
    ]

    while True:
        bersihkan_layar()
        tampilkan_layanan()

        pilihan = pilih_menu("KELOLA LAYANAN", daftar_menu)

        if pilihan == 4:
            return

        if pilihan == 1:
            tambah_layanan()
        elif pilihan == 2:
            edit_layanan()
        elif pilihan == 3:
            hapus_layanan()

        jeda()
