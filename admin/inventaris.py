from modules import database
from modules.inventaris import obat_kedaluwarsa, stok_menipis
from modules.utils import (
    bersihkan_layar, jeda, format_rupiah, id_berikutnya, input_teks,
    input_angka, konfirmasi, pilih_menu, pilih_kunci, tampilkan_tabel, parse_tanggal
)


def input_kedaluwarsa(lama=None):
    while True:
        nilai = input_teks("Masukkan tanggal kedaluwarsa (YYYY-MM-DD): ", lama)

        if parse_tanggal(nilai) is not None:
            return nilai

        print("Format tanggal salah. Contoh: 2027-12-31")


def pilih_kondisi():
    daftar_kondisi = list(database.KONDISI_ALAT)
    return daftar_kondisi[pilih_menu("Pilih kondisi alat", daftar_kondisi) - 1]


def tampilkan_alat():
    baris = [
        (nomor, kode, data["nama"], data["jumlah"], data["kondisi"])
        for nomor, (kode, data) in enumerate(database.db["inventaris_alat"].items(), 1)
    ]

    tampilkan_tabel(
        "INVENTARIS ALAT",
        ("No", "ID", "Nama Alat", "Jumlah", "Kondisi"),
        baris,
        kiri=("Nama Alat",)
    )


def tampilkan_obat():
    baris = [
        (
            nomor,
            kode,
            data["nama"],
            data["kategori"],
            data["stok"],
            format_rupiah(data["harga"]) + "/" + data["satuan"],
            data["kedaluwarsa"],
            "Kedaluwarsa" if obat_kedaluwarsa(data) else ("Menipis" if stok_menipis(data) else "Aman")
        )
        for nomor, (kode, data) in enumerate(database.db["obat"].items(), 1)
    ]

    tampilkan_tabel(
        "INVENTARIS OBAT",
        ("No", "ID", "Nama Obat", "Kategori", "Stok", "Harga", "Kedaluwarsa", "Status"),
        baris,
        kiri=("Nama Obat", "Kategori"),
        kanan=("Harga",)
    )


def tambah_alat():
    nama = input_teks("Masukkan nama alat: ")
    nama_terdaftar = {data["nama"].lower() for data in database.db["inventaris_alat"].values()}

    if nama.lower() in nama_terdaftar:
        print("Nama alat sudah terdaftar")
        return

    jumlah = input_angka("Masukkan jumlah alat: ", 0)
    kondisi = pilih_kondisi()
    kode = id_berikutnya(database.db["inventaris_alat"])

    database.db["inventaris_alat"][kode] = {
        "nama": nama,
        "jumlah": jumlah,
        "kondisi": kondisi
    }
    database.simpan(database.db, ["inventaris_alat"])

    print("Alat berhasil ditambahkan dengan ID", kode)


def edit_alat():
    kode = pilih_kunci(database.db["inventaris_alat"], "Masukkan nomor alat yang ingin diedit: ")

    if kode is None:
        return

    data = database.db["inventaris_alat"][kode]
    print("Kosongkan input jika tidak ingin mengubah data")

    nama = input_teks("Masukkan nama alat baru: ", data["nama"])
    nama_lain = {
        isi["nama"].lower()
        for kode_lain, isi in database.db["inventaris_alat"].items()
        if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama alat sudah terdaftar")
        return

    data["nama"] = nama
    data["jumlah"] = input_angka("Masukkan jumlah alat baru: ", 0, data["jumlah"])
    data["kondisi"] = pilih_kondisi()
    database.simpan(database.db, ["inventaris_alat"])

    print("Data alat berhasil diedit")


def hapus_alat():
    kode = pilih_kunci(database.db["inventaris_alat"], "Masukkan nomor alat yang ingin dihapus: ")

    if kode is None:
        return

    if konfirmasi("Yakin menghapus " + database.db["inventaris_alat"][kode]["nama"]):
        del database.db["inventaris_alat"][kode]
        database.simpan(database.db, ["inventaris_alat"])
        print("Alat berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def tambah_obat():
    nama = input_teks("Masukkan nama obat: ")
    nama_terdaftar = {data["nama"].lower() for data in database.db["obat"].values()}

    if nama.lower() in nama_terdaftar:
        print("Nama obat sudah terdaftar")
        return

    kategori = input_teks("Masukkan kategori obat: ")
    satuan = input_teks("Masukkan satuan obat (strip/botol/dll): ")
    stok = input_angka("Masukkan stok obat: ", 0)
    harga = input_angka("Masukkan harga obat per satuan: ", 0)
    kedaluwarsa = input_kedaluwarsa()
    kode = id_berikutnya(database.db["obat"])

    database.db["obat"][kode] = {
        "nama": nama,
        "kategori": kategori,
        "satuan": satuan,
        "harga": harga,
        "stok": stok,
        "kedaluwarsa": kedaluwarsa
    }
    database.simpan(database.db, ["obat"])

    print("Obat berhasil ditambahkan dengan ID", kode)


def edit_obat():
    kode = pilih_kunci(database.db["obat"], "Masukkan nomor obat yang ingin diedit: ")

    if kode is None:
        return

    data = database.db["obat"][kode]
    print("Kosongkan input jika tidak ingin mengubah data")

    nama = input_teks("Masukkan nama obat baru: ", data["nama"])
    nama_lain = {
        isi["nama"].lower()
        for kode_lain, isi in database.db["obat"].items()
        if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama obat sudah terdaftar")
        return

    data["nama"] = nama
    data["kategori"] = input_teks("Masukkan kategori baru: ", data["kategori"])
    data["satuan"] = input_teks("Masukkan satuan baru: ", data["satuan"])
    data["stok"] = input_angka("Masukkan stok obat baru: ", 0, data["stok"])
    data["harga"] = input_angka("Masukkan harga obat baru: ", 0, data["harga"])
    data["kedaluwarsa"] = input_kedaluwarsa(data["kedaluwarsa"])
    database.simpan(database.db, ["obat"])

    print("Data obat berhasil diedit")


def hapus_obat():
    kode = pilih_kunci(database.db["obat"], "Masukkan nomor obat yang ingin dihapus: ")

    if kode is None:
        return

    if konfirmasi("Yakin menghapus " + database.db["obat"][kode]["nama"]):
        del database.db["obat"][kode]
        database.simpan(database.db, ["obat"])
        print("Obat berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_alat():
    daftar_menu = [
        "Tambah Alat",
        "Edit Alat",
        "Hapus Alat",
        "Kembali"
    ]

    while True:
        bersihkan_layar()
        tampilkan_alat()

        pilihan = pilih_menu("KELOLA INVENTARIS ALAT", daftar_menu)

        if pilihan == 4:
            return

        if pilihan == 1:
            tambah_alat()
        elif pilihan == 2:
            edit_alat()
        elif pilihan == 3:
            hapus_alat()

        jeda()


def menu_obat():
    daftar_menu = [
        "Tambah Obat",
        "Edit Obat",
        "Hapus Obat",
        "Kembali"
    ]

    while True:
        bersihkan_layar()
        tampilkan_obat()

        pilihan = pilih_menu("KELOLA INVENTARIS OBAT", daftar_menu)

        if pilihan == 4:
            return

        if pilihan == 1:
            tambah_obat()
        elif pilihan == 2:
            edit_obat()
        elif pilihan == 3:
            hapus_obat()

        jeda()


def menu_inventaris():
    daftar_menu = [
        "Kelola Alat",
        "Kelola Obat",
        "Kembali"
    ]

    while True:
        bersihkan_layar()
        tampilkan_alat()
        tampilkan_obat()

        pilihan = pilih_menu("KELOLA INVENTARIS", daftar_menu)

        if pilihan == 1:
            menu_alat()
        elif pilihan == 2:
            menu_obat()
        else:
            return
