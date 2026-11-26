from modules import database
from modules.inventaris import (
    BATAS_HARI_KEDALUWARSA, BATAS_STOK_OBAT, mendekati_kedaluwarsa, obat_kedaluwarsa, stok_menipis
)
from modules.reservasi import catat_log_inventaris, log_jenis
from modules.utils import (
    bersihkan_layar, jeda, format_rupiah, id_berikutnya, ke_angka, konfirmasi,
    parse_tanggal, pilih_kunci, pilih_menu, tampilkan_tabel
)

USER_ADMIN = "admin"


def status_obat(obat):
    if obat_kedaluwarsa(obat):
        return "Kedaluwarsa"
    if stok_menipis(obat):
        return "Menipis"
    if mendekati_kedaluwarsa(obat):
        return "Hampir kedaluwarsa"
    return "Aman"


def tampilkan_obat():
    """Tampilkan_Obat: mengembalikan False bila data kosong."""
    if len(database.db["obat"]) == 0:
        print("\nData belum tersedia")
        return False

    baris = [
        (nomor, kode, data["nama"], data["kategori"], format_rupiah(data["harga"]), data["stok"],
         data["kedaluwarsa"], status_obat(data))
        for nomor, (kode, data) in enumerate(database.db["obat"].items(), 1)
    ]

    tampilkan_tabel(
        "INVENTARIS OBAT",
        ("No", "ID", "Nama Obat", "Kategori", "Harga Jual", "Stok", "Kedaluwarsa", "Status"),
        baris,
        kiri=("Nama Obat", "Kategori"),
        kanan=("Harga Jual",)
    )
    return True


def tambah_obat():
    nama = input("Nama obat: ").strip()
    kategori = input("Kategori: ").strip()
    harga = ke_angka(input("Harga jual: "))
    stok = ke_angka(input("Stok: "))
    tgl = input("Tanggal kedaluwarsa (YYYY-MM-DD): ").strip()

    if nama == "" or kategori == "" or harga is None or stok is None or parse_tanggal(tgl) is None:
        print("Data kosong atau tidak valid")
        return

    if nama.lower() in {data["nama"].lower() for data in database.db["obat"].values()}:
        print("Nama obat sudah terdaftar")
        return

    kode = id_berikutnya(database.db["obat"])
    database.db["obat"][kode] = {
        "nama": nama, "kategori": kategori, "satuan": "unit",
        "harga": harga, "stok": stok, "kedaluwarsa": tgl
    }
    catat_log_inventaris(database.db, "obat", kode, nama, "TAMBAH", "Stok awal " + str(stok), USER_ADMIN, stok)
    database.simpan(database.db, ["obat", "log_riwayat"])
    print("Obat berhasil ditambah dengan ID", kode)


def ubah_obat():
    if not tampilkan_obat():
        return

    kode = pilih_kunci(database.db["obat"], "Nomor obat yang ingin diubah: ")

    if kode is None:
        return

    nama = input("Nama baru: ").strip()
    kategori = input("Kategori baru: ").strip()
    harga = ke_angka(input("Harga jual baru: "))
    tgl = input("Tanggal kedaluwarsa baru (YYYY-MM-DD): ").strip()

    if nama == "" or kategori == "" or harga is None or parse_tanggal(tgl) is None:
        print("Data kosong atau tidak valid")
        return

    nama_lain = {
        isi["nama"].lower() for kode_lain, isi in database.db["obat"].items() if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama obat sudah terdaftar")
        return

    data = database.db["obat"][kode]
    data["nama"] = nama
    data["kategori"] = kategori
    data["harga"] = harga
    data["kedaluwarsa"] = tgl
    database.simpan(database.db, ["obat"])
    print("Data obat berhasil diubah")


def ubah_stok_obat():
    if not tampilkan_obat():
        return

    kode = pilih_kunci(database.db["obat"], "Nomor obat: ")

    if kode is None:
        return

    aksi = pilih_menu("Ubah stok", ["Tambah", "Kurangi"])
    jumlah = ke_angka(input("Jumlah: "))
    data = database.db["obat"][kode]

    if jumlah is None or jumlah < 1 or (aksi == 2 and jumlah > data["stok"]):
        print("Jumlah tidak valid atau melebihi stok")
        return

    lama = data["stok"]
    data["stok"] = lama + jumlah if aksi == 1 else lama - jumlah
    tanda = "+" if aksi == 1 else "-"
    catat_log_inventaris(database.db, "obat", kode, data["nama"], "STOK",
                         tanda + str(jumlah) + " (" + str(lama) + " -> " + str(data["stok"]) + ")",
                         USER_ADMIN, jumlah if aksi == 1 else -jumlah)
    database.simpan(database.db, ["obat", "log_riwayat"])
    print("Stok obat berhasil diperbarui")


def hapus_obat():
    if not tampilkan_obat():
        return

    kode = pilih_kunci(database.db["obat"], "Nomor obat yang ingin dihapus: ")

    if kode is None:
        return

    data = database.db["obat"][kode]

    if konfirmasi("Hapus " + data["nama"]):
        del database.db["obat"][kode]
        catat_log_inventaris(database.db, "obat", kode, data["nama"], "HAPUS", "Data obat dihapus", USER_ADMIN)
        database.simpan(database.db, ["obat", "log_riwayat"])
        print("Data obat berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def peringatan_obat():
    obat = database.db["obat"]
    menipis = [(k, d) for k, d in obat.items() if stok_menipis(d)]
    mendekati = [(k, d) for k, d in obat.items() if obat_kedaluwarsa(d) or mendekati_kedaluwarsa(d)]

    if len(menipis) == 0:
        print("\nTidak ada obat dengan stok menipis")
    else:
        tampilkan_tabel(
            "OBAT STOK MENIPIS (< " + str(BATAS_STOK_OBAT) + ")",
            ("ID", "Nama Obat", "Stok"),
            [(k, d["nama"], d["stok"]) for k, d in menipis],
            kiri=("Nama Obat",)
        )

    if len(mendekati) == 0:
        print("\nTidak ada obat yang mendekati kedaluwarsa")
    else:
        tampilkan_tabel(
            "OBAT KEDALUWARSA / MENDEKATI KEDALUWARSA (<= " + str(BATAS_HARI_KEDALUWARSA) + " hari)",
            ("ID", "Nama Obat", "Kedaluwarsa", "Status"),
            [(k, d["nama"], d["kedaluwarsa"], "Kedaluwarsa" if obat_kedaluwarsa(d) else "Mendekati") for k, d in mendekati],
            kiri=("Nama Obat",)
        )


def riwayat_obat():
    log = log_jenis(database.db, "obat")

    if len(log) == 0:
        print("\nRiwayat belum tersedia")
        return

    tampilkan_tabel(
        "RIWAYAT PENGGUNAAN DAN PERUBAHAN STOK OBAT",
        ("Waktu", "Obat", "Aksi", "Detail", "Oleh"),
        [(isi["waktu"], isi["nama"], isi["aksi"], isi["detail"], isi["oleh"]) for isi in log],
        kiri=("Obat", "Detail", "Oleh")
    )


def menu_obat():
    daftar_menu = [
        "Tambah Data Obat",
        "Tampilkan Data Obat",
        "Ubah Data Obat",
        "Ubah Stok Obat",
        "Hapus Data Obat",
        "Peringatan Obat",
        "Riwayat Obat",
        "Kembali ke Menu Admin"
    ]

    while True:
        bersihkan_layar()
        pilihan = pilih_menu("MENU KELOLA OBAT", daftar_menu)

        if pilihan == 8:
            return

        if pilihan == 1:
            tambah_obat()
        elif pilihan == 2:
            tampilkan_obat()
        elif pilihan == 3:
            ubah_obat()
        elif pilihan == 4:
            ubah_stok_obat()
        elif pilihan == 5:
            hapus_obat()
        elif pilihan == 6:
            peringatan_obat()
        elif pilihan == 7:
            riwayat_obat()

        jeda()
