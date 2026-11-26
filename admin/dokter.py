from modules import database
from modules.utils import (
    bersihkan_layar, jeda, format_rupiah, id_berikutnya, ke_angka,
    konfirmasi, pilih_menu, pilih_kunci, tampilkan_tabel
)


def tampilkan_dokter():
    """Tampilkan_Dokter: mengembalikan False bila data kosong."""
    if len(database.db["dokter"]) == 0:
        print("\nData belum tersedia")
        return False

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
    return True


def tambah_dokter():
    nama = input("Nama dokter: ").strip()
    spesialis = input("Spesialisasi: ").strip()
    biaya = ke_angka(input("Biaya jasa: "))

    if nama == "" or spesialis == "" or biaya is None:
        print("Data kosong atau tidak valid")
        return

    if nama.lower() in {data["nama"].lower() for data in database.db["dokter"].values()}:
        print("Nama dokter sudah terdaftar")
        return

    kode = id_berikutnya(database.db["dokter"])
    database.db["dokter"][kode] = {"nama": nama, "spesialisasi": spesialis, "biaya_jasa": biaya}
    database.simpan(database.db, ["dokter"])
    print("Dokter berhasil ditambah dengan ID", kode)


def ubah_dokter():
    if not tampilkan_dokter():
        return

    kode = pilih_kunci(database.db["dokter"], "Nomor dokter yang ingin diubah: ")

    if kode is None:
        return

    nama = input("Nama baru: ").strip()
    spesialis = input("Spesialisasi baru: ").strip()
    biaya = ke_angka(input("Biaya jasa baru: "))

    if nama == "" or spesialis == "" or biaya is None:
        print("Data kosong atau tidak valid")
        return

    nama_lain = {
        isi["nama"].lower() for kode_lain, isi in database.db["dokter"].items() if kode_lain != kode
    }

    if nama.lower() in nama_lain:
        print("Nama dokter sudah terdaftar")
        return

    database.db["dokter"][kode] = {"nama": nama, "spesialisasi": spesialis, "biaya_jasa": biaya}
    database.simpan(database.db, ["dokter"])
    print("Data dokter berhasil diubah")


def hapus_dokter():
    if not tampilkan_dokter():
        return

    kode = pilih_kunci(database.db["dokter"], "Nomor dokter yang ingin dihapus: ")

    if kode is None:
        return

    if any(isi["id_dokter"] == kode for isi in database.db["jadwal"].values()):
        print("Dokter tidak bisa dihapus karena masih memiliki jadwal")
        return

    if any(isi["id_dokter"] == kode for isi in database.db["reservasi"].values()):
        print("Dokter tidak bisa dihapus karena sudah memiliki data reservasi")
        return

    if konfirmasi("Hapus " + database.db["dokter"][kode]["nama"]):
        del database.db["dokter"][kode]
        database.simpan(database.db, ["dokter"])
        print("Data dokter berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_dokter():
    daftar_menu = [
        "Tambah Data Dokter",
        "Tampilkan Data Dokter",
        "Ubah Data Dokter",
        "Hapus Data Dokter",
        "Kembali ke Menu Admin"
    ]

    while True:
        bersihkan_layar()
        pilihan = pilih_menu("MENU KELOLA DOKTER", daftar_menu)

        if pilihan == 5:
            return

        if pilihan == 1:
            tambah_dokter()
        elif pilihan == 2:
            tampilkan_dokter()
        elif pilihan == 3:
            ubah_dokter()
        elif pilihan == 4:
            hapus_dokter()

        jeda()
