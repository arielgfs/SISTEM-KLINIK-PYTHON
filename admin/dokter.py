from modules import database
from modules.utils import (
    bersihkan_layar, jeda, format_rupiah, id_berikutnya, input_teks,
    input_angka, konfirmasi, pilih_menu, pilih_kunci, tampilkan_tabel
)


def tampilkan_dokter():
    baris = [
        (nomor, kode, data["nama"], data["spesialisasi"], format_rupiah(data["biaya_jasa"]))
        for nomor, (kode, data) in enumerate(database.db["dokter"].items(), 1)
    ]

    tampilkan_tabel(
        "DAFTAR DOKTER",
        ("No", "ID", "Nama Dokter", "Spesialis", "Biaya Jasa"),
        baris,
        kiri=("Nama Dokter", "Spesialis"),
        kanan=("Biaya Jasa",)
    )


def tambah_dokter():
    nama = input_teks("Masukkan nama dokter: ")
    nama_terdaftar = {data["nama"].lower() for data in database.db["dokter"].values()}

    if nama.lower() in nama_terdaftar:
        print("Nama dokter sudah terdaftar")
        return

    spesialis = input_teks("Masukkan spesialis dokter: ")
    biaya = input_angka("Masukkan biaya jasa dokter: ", 0)
    kode = id_berikutnya(database.db["dokter"])

    database.db["dokter"][kode] = {
        "nama": nama,
        "spesialisasi": spesialis,
        "biaya_jasa": biaya
    }
    database.simpan(database.db, ["dokter"])

    print("Dokter berhasil ditambahkan dengan ID", kode)


def edit_dokter():
    kode = pilih_kunci(database.db["dokter"], "Masukkan nomor dokter yang ingin diedit: ")

    if kode is None:
        return

    data = database.db["dokter"][kode]
    print("Kosongkan input jika tidak ingin mengubah data")

    nama = input_teks("Masukkan nama dokter baru: ", data["nama"])
    nama_lain = {
        isi["nama"].lower()
        for kode_lain, isi in database.db["dokter"].items()
        if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama dokter sudah terdaftar")
        return

    data["nama"] = nama
    data["spesialisasi"] = input_teks("Masukkan spesialis baru: ", data["spesialisasi"])
    data["biaya_jasa"] = input_angka("Masukkan biaya jasa baru: ", 0, data["biaya_jasa"])
    database.simpan(database.db, ["dokter"])

    print("Data dokter berhasil diedit")


def hapus_dokter():
    kode = pilih_kunci(database.db["dokter"], "Masukkan nomor dokter yang ingin dihapus: ")

    if kode is None:
        return

    if any(isi["id_dokter"] == kode for isi in database.db["jadwal"].values()):
        print("Dokter tidak bisa dihapus karena masih memiliki jadwal")
        return

    if any(isi["id_dokter"] == kode for isi in database.db["reservasi"].values()):
        print("Dokter tidak bisa dihapus karena sudah memiliki data reservasi")
        return

    if konfirmasi("Yakin menghapus " + database.db["dokter"][kode]["nama"]):
        del database.db["dokter"][kode]
        database.simpan(database.db, ["dokter"])
        print("Dokter berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_dokter():
    daftar_menu = [
        "Tambah Dokter",
        "Edit Dokter",
        "Hapus Dokter",
        "Kembali"
    ]

    while True:
        bersihkan_layar()
        tampilkan_dokter()

        pilihan = pilih_menu("KELOLA DOKTER", daftar_menu)

        if pilihan == 4:
            return

        if pilihan == 1:
            tambah_dokter()
        elif pilihan == 2:
            edit_dokter()
        elif pilihan == 3:
            hapus_dokter()

        jeda()
