import pandas as pd

from modules import database
from modules.inventaris import BATAS_STOK_OBAT
from modules.utils import bersihkan_layar, format_rupiah, jeda, pilih_menu
from admin.akun import menu_akun
from admin.alat import menu_alat
from admin.dokter import menu_dokter
from admin.jadwal import menu_jadwal
from admin.laporan import laporan_obat, laporan_pembayaran, lihat_pasien_reservasi
from admin.layanan import menu_layanan
from admin.obat import menu_obat


def tampilkan_ringkasan():
    """Ringkasan data klinik memakai Pandas (DataFrame, Series, dan filter)."""
    db = database.db

    # Series dengan index custom: jumlah data tiap tabel
    jumlah = pd.Series(
        [len(db["dokter"]), len(db["pasien"]), len(db["jadwal"]), len(db["reservasi"]), len(db["obat"])],
        index=["Dokter", "Pasien", "Jadwal", "Reservasi", "Obat"]
    )
    print("\n===== DASHBOARD ADMIN =====")
    print(jumlah)

    # DataFrame reservasi, lalu hitung jumlah per status
    if len(db["reservasi"]) > 0:
        df_reservasi = pd.DataFrame({
            "Dokter": [db["dokter"].get(isi["id_dokter"], {"nama": "-"})["nama"] for isi in db["reservasi"].values()],
            "Status": [isi["status"] for isi in db["reservasi"].values()]
        })
        print("\nReservasi per status")
        print(df_reservasi["Status"].value_counts())
        print("\nReservasi per dokter")
        print(df_reservasi["Dokter"].value_counts())

    # DataFrame obat, filter stok di bawah batas
    if len(db["obat"]) > 0:
        df_obat = pd.DataFrame({
            "Nama": [isi["nama"] for isi in db["obat"].values()],
            "Stok": [isi["stok"] for isi in db["obat"].values()]
        })
        menipis = df_obat[df_obat["Stok"] < BATAS_STOK_OBAT]
        print("\nObat dengan stok di bawah", BATAS_STOK_OBAT)
        print(menipis if len(menipis) > 0 else "Tidak ada")

    # DataFrame transaksi, filter yang sudah Lunas
    if len(db["transaksi"]) > 0:
        df_transaksi = pd.DataFrame({
            "Total": [isi["total"] for isi in db["transaksi"].values()],
            "Status": [isi["status_bayar"] for isi in db["transaksi"].values()]
        })
        lunas = df_transaksi[df_transaksi["Status"] == "Lunas"]
        print("\nPendapatan (Lunas):", format_rupiah(int(lunas["Total"].sum())))


def menu_admin(username="admin"):
    daftar_menu = [
        "Kelola Dokter",
        "Kelola Layanan",
        "Kelola Jadwal Praktik",
        "Kelola Inventaris Alat",
        "Kelola Inventaris Obat",
        "Lihat Data Pasien dan Reservasi",
        "Laporan Pembayaran dan Transaksi",
        "Laporan Penggunaan dan Stok Obat",
        "Kelola Akun dan Hak Akses",
        "Logout"
    ]

    while True:
        database.muat_ulang()
        bersihkan_layar()
        tampilkan_ringkasan()
        pilihan = pilih_menu("MENU ADMIN", daftar_menu)

        if pilihan == 10:
            bersihkan_layar()
            print("Logout berhasil")
            return "logout"

        if pilihan == 1:
            menu_dokter()
        elif pilihan == 2:
            menu_layanan()
        elif pilihan == 3:
            menu_jadwal()
        elif pilihan == 4:
            menu_alat()
        elif pilihan == 5:
            menu_obat()
        elif pilihan == 6:
            lihat_pasien_reservasi()
            jeda()
        elif pilihan == 7:
            laporan_pembayaran()
            jeda()
        elif pilihan == 8:
            laporan_obat()
            jeda()
        elif pilihan == 9:
            menu_akun(username)
