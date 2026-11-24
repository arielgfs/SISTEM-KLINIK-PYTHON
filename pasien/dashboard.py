from modules import database
from modules.utils import bersihkan_layar, jeda, pilih_menu
from pasien.dokter import lihat_dokter, lihat_layanan
from pasien.jadwal import lihat_jadwal, lihat_slot_tersedia
from pasien.reservasi import batalkan_reservasi_pasien, reservasi_konsultasi, ubah_reservasi
from pasien.riwayat import lihat_riwayat, lihat_tagihan

TABEL_PASIEN = ["pasien", "dokter", "layanan", "jadwal", "reservasi", "log_riwayat", "transaksi"]


def menu_pasien(user):
    if user.get("id_pasien") not in database.muat_tabel("pasien"):
        print("Akun ini belum terhubung dengan data pasien. Hubungi resepsionis.")
        jeda()
        return "logout"

    db = database.muat_database(TABEL_PASIEN)
    daftar_menu = [
        "Lihat Dokter dan Biaya Jasa",
        "Lihat Jenis Layanan",
        "Lihat Jadwal Dokter",
        "Cek Slot Tersedia",
        "Buat Reservasi Konsultasi",
        "Ubah Reservasi",
        "Batalkan Reservasi",
        "Lihat Status dan Riwayat Reservasi",
        "Lihat Tagihan dan Struk",
        "Logout"
    ]

    while True:
        bersihkan_layar()
        print("Selamat datang di klinik kami,", db["pasien"][user["id_pasien"]]["nama"])
        pilihan = pilih_menu("MENU PASIEN", daftar_menu)

        if pilihan == 10:
            bersihkan_layar()
            print("Logout berhasil")
            return "logout"

        if pilihan == 1:
            lihat_dokter(db)
        elif pilihan == 2:
            lihat_layanan(db)
        elif pilihan == 3:
            lihat_jadwal(db)
        elif pilihan == 4:
            lihat_slot_tersedia(db)
        elif pilihan == 5:
            reservasi_konsultasi(db, user)
        elif pilihan == 6:
            ubah_reservasi(db, user)
        elif pilihan == 7:
            batalkan_reservasi_pasien(db, user)
        elif pilihan == 8:
            lihat_riwayat(db, user)
        elif pilihan == 9:
            lihat_tagihan(db, user)

        jeda()
