from modules import database
from modules.reservasi import catat_log_inventaris, log_jenis
from modules.utils import (
    bersihkan_layar, jeda, id_berikutnya, ke_angka, konfirmasi,
    parse_tanggal, pilih_kunci, pilih_menu, tampilkan_tabel
)

USER_ADMIN = "admin"


def tampilkan_alat():
    """Tampilkan_Alat: mengembalikan False bila data kosong."""
    if len(database.db["inventaris_alat"]) == 0:
        print("\nData belum tersedia")
        return False

    baris = [
        (nomor, kode, data["nama"], data["kategori"], data["jumlah"], data["kondisi"],
         data["tgl_pembelian"], data["lokasi"])
        for nomor, (kode, data) in enumerate(database.db["inventaris_alat"].items(), 1)
    ]

    tampilkan_tabel(
        "INVENTARIS ALAT",
        ("No", "ID", "Nama Alat", "Kategori", "Stok", "Kondisi", "Tgl Pembelian", "Lokasi Simpan"),
        baris,
        kiri=("Nama Alat", "Kategori", "Lokasi Simpan")
    )
    return True


def pilih_kondisi():
    daftar = list(database.KONDISI_ALAT)
    return daftar[pilih_menu("Pilih kondisi alat", daftar) - 1]


def tambah_alat():
    nama = input("Nama alat: ").strip()
    kategori = input("Kategori: ").strip()
    stok = ke_angka(input("Stok: "))
    kondisi = pilih_kondisi()
    tgl = input("Tanggal pembelian (YYYY-MM-DD): ").strip()
    lokasi = input("Lokasi simpan: ").strip()

    if nama == "" or kategori == "" or stok is None or lokasi == "" or parse_tanggal(tgl) is None:
        print("Data kosong atau tidak valid")
        return

    if nama.lower() in {data["nama"].lower() for data in database.db["inventaris_alat"].values()}:
        print("Nama alat sudah terdaftar")
        return

    kode = id_berikutnya(database.db["inventaris_alat"])
    database.db["inventaris_alat"][kode] = {
        "nama": nama, "kategori": kategori, "jumlah": stok, "kondisi": kondisi,
        "tgl_pembelian": tgl, "lokasi": lokasi
    }
    catat_log_inventaris(database.db, "alat", kode, nama, "TAMBAH",
                         "Stok awal " + str(stok) + ", kondisi " + kondisi, USER_ADMIN, stok)
    database.simpan(database.db, ["inventaris_alat", "log_riwayat"])
    print("Alat berhasil ditambah dengan ID", kode)


def ubah_alat():
    if not tampilkan_alat():
        return

    kode = pilih_kunci(database.db["inventaris_alat"], "Nomor alat yang ingin diubah: ")

    if kode is None:
        return

    nama = input("Nama baru: ").strip()
    kategori = input("Kategori baru: ").strip()

    if nama == "" or kategori == "":
        print("Data kosong atau tidak valid")
        return

    nama_lain = {
        isi["nama"].lower() for kode_lain, isi in database.db["inventaris_alat"].items() if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama alat sudah terdaftar")
        return

    data = database.db["inventaris_alat"][kode]
    lama = data["nama"] + " / " + data["kategori"]
    data["nama"] = nama
    data["kategori"] = kategori
    catat_log_inventaris(database.db, "alat", kode, nama, "UBAH", lama + " -> " + nama + " / " + kategori, USER_ADMIN)
    database.simpan(database.db, ["inventaris_alat", "log_riwayat"])
    print("Data alat berhasil diubah")


def ubah_stok_alat():
    if not tampilkan_alat():
        return

    kode = pilih_kunci(database.db["inventaris_alat"], "Nomor alat: ")

    if kode is None:
        return

    aksi = pilih_menu("Ubah stok", ["Tambah", "Kurangi"])
    jumlah = ke_angka(input("Jumlah: "))
    data = database.db["inventaris_alat"][kode]

    if jumlah is None or jumlah < 1 or (aksi == 2 and jumlah > data["jumlah"]):
        print("Jumlah tidak valid atau melebihi stok")
        return

    lama = data["jumlah"]
    data["jumlah"] = lama + jumlah if aksi == 1 else lama - jumlah
    tanda = "+" if aksi == 1 else "-"
    catat_log_inventaris(database.db, "alat", kode, data["nama"], "STOK",
                         tanda + str(jumlah) + " (" + str(lama) + " -> " + str(data["jumlah"]) + ")",
                         USER_ADMIN, jumlah if aksi == 1 else -jumlah)
    database.simpan(database.db, ["inventaris_alat", "log_riwayat"])
    print("Stok alat berhasil diperbarui")


def ubah_kondisi_alat():
    if not tampilkan_alat():
        return

    kode = pilih_kunci(database.db["inventaris_alat"], "Nomor alat: ")

    if kode is None:
        return

    kondisi = pilih_kondisi()

    if kondisi not in database.KONDISI_ALAT:
        print("Kondisi tidak valid")
        return

    data = database.db["inventaris_alat"][kode]
    lama = data["kondisi"]
    data["kondisi"] = kondisi
    catat_log_inventaris(database.db, "alat", kode, data["nama"], "KONDISI", lama + " -> " + kondisi, USER_ADMIN)
    database.simpan(database.db, ["inventaris_alat", "log_riwayat"])
    print("Kondisi alat berhasil diubah")


def hapus_alat():
    if not tampilkan_alat():
        return

    kode = pilih_kunci(database.db["inventaris_alat"], "Nomor alat yang ingin dihapus: ")

    if kode is None:
        return

    data = database.db["inventaris_alat"][kode]

    if konfirmasi("Hapus " + data["nama"]):
        del database.db["inventaris_alat"][kode]
        catat_log_inventaris(database.db, "alat", kode, data["nama"], "HAPUS", "Data alat dihapus", USER_ADMIN)
        database.simpan(database.db, ["inventaris_alat", "log_riwayat"])
        print("Data alat berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def riwayat_alat():
    log = log_jenis(database.db, "alat")

    if len(log) == 0:
        print("\nRiwayat belum tersedia")
        return

    tampilkan_tabel(
        "RIWAYAT PERUBAHAN STOK DAN KONDISI ALAT",
        ("Waktu", "Alat", "Aksi", "Detail", "Oleh"),
        [(isi["waktu"], isi["nama"], isi["aksi"], isi["detail"], isi["oleh"]) for isi in log],
        kiri=("Alat", "Detail", "Oleh")
    )


def menu_alat():
    daftar_menu = [
        "Tambah Data Alat",
        "Tampilkan Data Alat",
        "Ubah Nama dan Kategori Alat",
        "Ubah Stok Alat",
        "Ubah Kondisi Alat",
        "Hapus Data Alat",
        "Riwayat Alat",
        "Kembali ke Menu Admin"
    ]

    while True:
        bersihkan_layar()
        pilihan = pilih_menu("MENU KELOLA ALAT", daftar_menu)

        if pilihan == 8:
            return

        if pilihan == 1:
            tambah_alat()
        elif pilihan == 2:
            tampilkan_alat()
        elif pilihan == 3:
            ubah_alat()
        elif pilihan == 4:
            ubah_stok_alat()
        elif pilihan == 5:
            ubah_kondisi_alat()
        elif pilihan == 6:
            hapus_alat()
        elif pilihan == 7:
            riwayat_alat()

        jeda()
