from datetime import date

from modules import database
from modules.utils import bersihkan_layar, jeda, pilih_menu, tampilkan_tabel
from resepsionis import pasien, pembayaran, reservasi

TABEL_RESEPSIONIS = ["pasien", "dokter", "jadwal", "reservasi", "log_riwayat", "obat", "transaksi"]


def tampil_ringkasan(db, username):
    hari_ini = str(date.today())
    baris = (
        ("User", username),
        ("Tanggal", hari_ini),
        ("Total pasien terdaftar", len(db["pasien"])),
        ("Reservasi hari ini", sum(1 for v in db["reservasi"].values() if v["tanggal"] == hari_ini and v["status"] != "Dibatalkan")),
        ("Reservasi menunggu", sum(1 for v in db["reservasi"].values() if v["status"] == "Menunggu")),
        ("Tagihan belum lunas", sum(1 for v in db["transaksi"].values() if v["status_bayar"] in ("Belum Dibayar", "Menunggu Pembayaran"))),
    )
    tampilkan_tabel("DASHBOARD RESEPSIONIS", ("Keterangan", "Nilai"), baris, kiri=("Keterangan", "Nilai"))


def menu_resepsionis(username="resepsionis"):
    daftar_menu = [
        "Daftarkan Pasien Baru",
        "Lihat Data Pasien, Dokter, dan Harga",
        "Lihat Jadwal Praktik",
        "Buat Reservasi Manual",
        "Ubah atau Batalkan Reservasi",
        "Konfirmasi Kedatangan",
        "Kelola Status Reservasi",
        "Lihat Log Riwayat Jadwal",
        "Input Obat Resep",
        "Buat Tagihan",
        "Proses Pembayaran",
        "Cetak Struk",
        "Logout"
    ]

    while True:
        db = database.muat_database(TABEL_RESEPSIONIS)
        bersihkan_layar()
        tampil_ringkasan(db, username)
        pilihan = pilih_menu("MENU RESEPSIONIS", daftar_menu)

        if pilihan == 13:
            bersihkan_layar()
            print("Logout berhasil")
            return "logout"

        if pilihan == 1:
            pasien.daftar_pasien(db)
        elif pilihan == 2:
            pasien.lihat_data(db)
        elif pilihan == 3:
            reservasi.lihat_jadwal(db)
        elif pilihan == 4:
            reservasi.buat_reservasi_manual(db, username)
        elif pilihan == 5:
            reservasi.ubah_batal_reservasi(db, username)
        elif pilihan == 6:
            reservasi.konfirmasi_kedatangan(db, username)
        elif pilihan == 7:
            reservasi.status_reservasi(db, username)
        elif pilihan == 8:
            reservasi.log_jadwal(db)
        elif pilihan == 9:
            pembayaran.input_obat_resep(db, username)
        elif pilihan == 10:
            pembayaran.buat_tagihan(db, username)
        elif pilihan == 11:
            pembayaran.proses_pembayaran(db, username)
        elif pilihan == 12:
            pembayaran.cetak_struk(db)

        jeda()
