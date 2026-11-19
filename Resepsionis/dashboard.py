
from datetime import date
from modules import database
from modules.utils import bersihkan_layar, jeda, buat_tabel, judul
from resepsionis import pasien, reservasi, pembayaran

# [JSON] tabel (file di data/) yang dibaca & diubah oleh resepsionis
TABEL_RESEPSIONIS = ["pasien", "dokter", "jadwal", "reservasi", "log_riwayat", "obat", "transaksi"]


def tampil_ringkasan(db, username):
    hari_ini = str(date.today())
    reservasi_hari_ini = 0
    menunggu_konfirmasi = 0
    tagihan_belum_lunas = 0

    for id_res in db["reservasi"]:
        data = db["reservasi"][id_res]
        if data["tanggal"] == hari_ini and data["status"] != "Dibatalkan":
            reservasi_hari_ini = reservasi_hari_ini + 1
        if data["status"] == "Menunggu":
            menunggu_konfirmasi = menunggu_konfirmasi + 1

    for id_trx in db["transaksi"]:
        if db["transaksi"][id_trx]["status_bayar"] != "Lunas":
            tagihan_belum_lunas = tagihan_belum_lunas + 1

    judul("DASHBOARD RESEPSIONIS")
    print("  User    : " + username)
    print("  Tanggal : " + hari_ini)
    tabel = buat_tabel(["Ringkasan", "Jumlah"], ["Ringkasan"])
    tabel.add_row(["Total pasien terdaftar", len(db["pasien"])])
    tabel.add_row(["Reservasi hari ini", reservasi_hari_ini])
    tabel.add_row(["Reservasi menunggu konfirmasi", menunggu_konfirmasi])
    tabel.add_row(["Tagihan belum lunas", tagihan_belum_lunas])
    print(tabel)


def menu_resepsionis(username="resepsionis"):
    """Menu utama resepsionis. Dipanggil dari main.py setelah login."""
    db = database.muat_database(TABEL_RESEPSIONIS)        # [JSON] ambil data
    sesi_jalan = True
    while sesi_jalan:
        bersihkan_layar()
        tampil_ringkasan(db, username)
        tabel = buat_tabel(["No", "Menu"], ["Menu"])
        tabel.add_row([1, "Kelola Pasien (daftar, ubah, lihat pasien & dokter)"])
        tabel.add_row([2, "Kelola Reservasi (jadwal, reservasi, status, log)"])
        tabel.add_row([3, "Kelola Pembayaran (obat resep, tagihan, bayar, struk)"])
        tabel.add_row([0, "Logout"])
        print(tabel)
        pilihan = input("Pilih menu [0-3] : ").strip()

        if pilihan == "1":
            pasien.menu_pasien(db, username)
        elif pilihan == "2":
            reservasi.menu_reservasi(db, username)
        elif pilihan == "3":
            pembayaran.menu_pembayaran(db, username)
        elif pilihan == "0":
            print("\n[*] Logout berhasil, kembali ke menu utama.")
            sesi_jalan = False
        else:
            print("\n[!] Pilihan tidak tersedia, pilih 0 sampai 3.")
            jeda("Tekan Enter untuk melanjutkan...")


if __name__ == "__main__":
    try:
        menu_resepsionis("resepsionis")
    except (KeyboardInterrupt, EOFError):
        print("\n\n[!] Program dihentikan oleh pengguna.")