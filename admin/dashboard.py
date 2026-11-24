import pandas as pd

from modules import database
from modules.inventaris import BATAS_STOK_OBAT, jumlah_alat_bermasalah, jumlah_obat_menipis
from modules.pembayaran import total_pendapatan
from modules.utils import (
    bersihkan_layar, jeda, format_rupiah, pilih_menu, tampilkan_tabel
)
from admin.dokter import menu_dokter
from admin.jadwal import menu_jadwal
from admin.layanan import menu_layanan
from admin.inventaris import menu_inventaris


def tampilkan_ringkasan():
    db = database.db
    reservasi_aktif = sum(
        1 for isi in db["reservasi"].values() if isi["status"] in database.STATUS_AKTIF
    )

    baris = (
        ("Jumlah Dokter", len(db["dokter"])),
        ("Jumlah Jadwal", len(db["jadwal"])),
        ("Jumlah Layanan", len(db["layanan"])),
        ("Jumlah Pasien", len(db["pasien"])),
        ("Jenis Alat", len(db["inventaris_alat"])),
        ("Alat Perlu Perhatian", jumlah_alat_bermasalah(db["inventaris_alat"])),
        ("Jenis Obat", len(db["obat"])),
        ("Obat Stok Menipis", jumlah_obat_menipis(db["obat"])),
        ("Reservasi Aktif", reservasi_aktif),
        ("Total Pendapatan (Lunas)", format_rupiah(total_pendapatan(db["transaksi"])))
    )

    tampilkan_tabel("DASHBOARD ADMIN", ("Keterangan", "Nilai"), baris, kiri=("Keterangan",))


def tampil_reservasi_dokter():
    db = database.db
    if len(db["reservasi"]) == 0 or len(db["dokter"]) == 0:
        print("Data reservasi atau dokter masih kosong")
        return

    nama_dokter = []
    jumlah_reservasi = []

    for kode, dokter in db["dokter"].items():
        jumlah = 0
        for reservasi in db["reservasi"].values():
            if reservasi["id_dokter"] == kode:
                jumlah = jumlah + 1

        nama_dokter.append(dokter["nama"])
        jumlah_reservasi.append(jumlah)

    series = pd.Series(jumlah_reservasi, index=nama_dokter)

    print("\nJumlah reservasi per dokter")
    print(series)
    print("\nDokter dengan reservasi terbanyak:", series.idxmax(), "(" + str(series.max()) + ")")


def tampil_stok_obat():
    db = database.db
    if len(db["obat"]) == 0:
        print("Data obat masih kosong")
        return

    data = {
        "Nama": [isi["nama"] for isi in db["obat"].values()],
        "Kategori": [isi["kategori"] for isi in db["obat"].values()],
        "Stok": [isi["stok"] for isi in db["obat"].values()],
        "Harga": [isi["harga"] for isi in db["obat"].values()]
    }
    df = pd.DataFrame(data)

    print("\nData stok obat")
    print(df)

    print("\nObat dengan stok di bawah", BATAS_STOK_OBAT)
    menipis = df[df["Stok"] < BATAS_STOK_OBAT]

    if len(menipis) == 0:
        print("Tidak ada obat yang stoknya menipis")
    else:
        print(menipis)


def tampil_pendapatan_dokter():
    db = database.db
    data = {
        "Dokter": [],
        "Total": [],
        "Status": []
    }

    for isi in db["transaksi"].values():
        data["Dokter"].append(db["dokter"].get(isi["id_dokter"], {"nama": "Dokter Dihapus"})["nama"])
        data["Total"].append(isi["total"])
        data["Status"].append(isi["status_bayar"])

    if len(data["Dokter"]) == 0:
        print("Data transaksi masih kosong")
        return

    df = pd.DataFrame(data)

    print("\nSeluruh transaksi")
    print(df)

    lunas = df[df["Status"] == "Lunas"]

    print("\nTransaksi yang sudah Lunas")
    if len(lunas) == 0:
        print("Belum ada transaksi yang lunas")
        return

    print(lunas)

    pendapatan = pd.Series(
        [lunas[lunas["Dokter"] == nama]["Total"].sum() for nama in lunas["Dokter"].unique()],
        index=lunas["Dokter"].unique()
    )

    print("\nPendapatan per dokter (Lunas)")
    print(pendapatan)


def tampil_kondisi_alat():
    db = database.db
    if len(db["inventaris_alat"]) == 0:
        print("Data alat masih kosong")
        return

    data = {
        "Nama": [isi["nama"] for isi in db["inventaris_alat"].values()],
        "Jumlah": [isi["jumlah"] for isi in db["inventaris_alat"].values()],
        "Kondisi": [isi["kondisi"] for isi in db["inventaris_alat"].values()]
    }
    df = pd.DataFrame(data)

    print("\nData inventaris alat")
    print(df)

    print("\nAlat yang perlu perhatian (kondisi bukan Baik)")
    perlu = df[df["Kondisi"] != "Baik"]

    if len(perlu) == 0:
        print("Semua alat dalam kondisi baik")
    else:
        print(perlu)


def menu_visualisasi():
    daftar_menu = [
        "Reservasi per Dokter",
        "Stok Obat",
        "Pendapatan per Dokter",
        "Kondisi Alat",
        "Kembali"
    ]

    while True:
        bersihkan_layar()
        tampilkan_ringkasan()

        pilihan = pilih_menu("VISUALISASI DATA (PANDAS)", daftar_menu)

        if pilihan == 5:
            return

        if pilihan == 1:
            tampil_reservasi_dokter()
        elif pilihan == 2:
            tampil_stok_obat()
        elif pilihan == 3:
            tampil_pendapatan_dokter()
        elif pilihan == 4:
            tampil_kondisi_alat()

        jeda()


def menu_admin():
    daftar_menu = [
        "Kelola Dokter",
        "Kelola Jadwal Dokter",
        "Kelola Layanan",
        "Kelola Inventaris",
        "Visualisasi Data",
        "Logout",
        "Keluar dari Program"
    ]

    database.muat_ulang()

    while True:
        bersihkan_layar()
        tampilkan_ringkasan()

        pilihan = pilih_menu("MENU ADMIN", daftar_menu)

        if pilihan == 1:
            menu_dokter()
        elif pilihan == 2:
            menu_jadwal()
        elif pilihan == 3:
            menu_layanan()
        elif pilihan == 4:
            menu_inventaris()
        elif pilihan == 5:
            menu_visualisasi()
        elif pilihan == 6:
            bersihkan_layar()
            print("Logout berhasil")
            return "logout"
        elif pilihan == 7:
            bersihkan_layar()
            print("Program selesai. Terima kasih!")
            return "keluar"
