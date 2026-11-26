from modules import database
from modules.utils import bersihkan_layar, jeda, pilih_menu
from pasien.dokter import lihat_dokter, lihat_layanan
from pasien.jadwal import lihat_jadwal_slot
from pasien.reservasi import reservasi_konsultasi, ubah_batal_reservasi
from pasien.riwayat import lihat_riwayat_reservasi, lihat_tagihan, riwayat_pembayaran, unduh_struk

TABEL_PASIEN = ["pasien", "dokter", "layanan", "jadwal", "reservasi", "log_riwayat", "transaksi"]


def menu_pasien(user):
    if user.get("id_pasien") not in database.muat_tabel("pasien"):
        print("Akun ini belum terhubung dengan data pasien. Hubungi resepsionis.")
        jeda()
        return "logout"

    daftar_menu = [
        "Lihat Dokter dan Biaya Jasa",
        "Lihat Jenis Layanan",
        "Lihat Jadwal dan Slot Tersedia",
        "Reservasi Konsultasi",
        "Ubah atau Batalkan Reservasi",
        "Lihat Status dan Riwayat Reservasi",
        "Lihat Tagihan",
        "Lihat Riwayat Pembayaran",
        "Lihat dan Unduh Struk",
        "Logout"
    ]

    while True:
        db = database.muat_database(TABEL_PASIEN)
        bersihkan_layar()
        print("Selamat datang di klinik kami,", db["pasien"][user["id_pasien"]]["nama"])
        pilihan = pilih_menu("MENU USER", daftar_menu)

        if pilihan == 10:
            bersihkan_layar()
            print("Logout berhasil")
            return "logout"

        if pilihan == 1:
            lihat_dokter(db)
        elif pilihan == 2:
            lihat_layanan(db)
        elif pilihan == 3:
            lihat_jadwal_slot(db)
        elif pilihan == 4:
            reservasi_konsultasi(db, user)
        elif pilihan == 5:
            ubah_batal_reservasi(db, user)
        elif pilihan == 6:
            lihat_riwayat_reservasi(db, user)
        elif pilihan == 7:
            lihat_tagihan(db, user)
        elif pilihan == 8:
            riwayat_pembayaran(db, user)
        elif pilihan == 9:
            unduh_struk(db, user)

        jeda()
