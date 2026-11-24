import inquirer
from datetime import date
from modules import database
from modules.utils import bersihkan_layar, buat_tabel, judul
from resepsionis import pasien, reservasi, pembayaran


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


def pilih_menu(daftar_menu):
    pertanyaan = [
        inquirer.List(
            "menu",
            message="Pilih menu (panah atas/bawah, Enter untuk memilih)",
            choices=daftar_menu
        )
    ]
    jawaban = inquirer.prompt(pertanyaan)
    if jawaban == None:
        return "Logout"
    return jawaban["menu"]


def menu_resepsionis(username="resepsionis"):
    db = database.muat_database(TABEL_RESEPSIONIS)
    daftar_menu = [
        "Kelola Pasien",
        "Kelola Reservasi",
        "Kelola Pembayaran",
        "Logout"
    ]

    sesi_jalan = True
    while sesi_jalan:
        bersihkan_layar()
        tampil_ringkasan(db, username)
        pilihan = pilih_menu(daftar_menu)

        if pilihan == "Kelola Pasien":
            pasien.menu_pasien(db, username)
        elif pilihan == "Kelola Reservasi":
            reservasi.menu_reservasi(db, username)
        elif pilihan == "Kelola Pembayaran":
            pembayaran.menu_pembayaran(db, username)
        elif pilihan == "Logout":
            print("\n[*] Logout berhasil, kembali ke menu utama.")
            sesi_jalan = False


if __name__ == "__main__":
    try:
        menu_resepsionis("resepsionis")
    except (KeyboardInterrupt, EOFError):
        print("\n\n[!] Program dihentikan oleh pengguna.")
