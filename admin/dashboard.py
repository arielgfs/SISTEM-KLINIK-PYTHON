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


def muat_pustaka_grafik():
    """pandas & matplotlib hanya dibutuhkan untuk visualisasi, jadi dimuat saat dipakai saja."""
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        print("Visualisasi membutuhkan pandas dan matplotlib: pip install pandas matplotlib")
        return None, None

    return plt, pd


def tampilkan_grafik(plt):
    plt.tight_layout()

    try:
        plt.show()
    except Exception:
        print("Grafik tidak dapat ditampilkan pada lingkungan ini")
    finally:
        plt.close("all")


def grafik_reservasi_dokter():
    plt, pd = muat_pustaka_grafik()
    if plt is None:
        return

    db = database.db
    if len(db["reservasi"]) == 0 or len(db["dokter"]) == 0:
        print("Data reservasi atau dokter masih kosong")
        return

    nama_dokter = pd.Series({kode: isi["nama"] for kode, isi in db["dokter"].items()})
    jumlah = pd.Series([isi["id_dokter"] for isi in db["reservasi"].values()]).value_counts()
    jumlah = jumlah.reindex(nama_dokter.index, fill_value=0)
    jumlah.index = nama_dokter[jumlah.index].values

    fig, sumbu = plt.subplots(figsize=(9, 5))
    jumlah.plot(kind="bar", ax=sumbu, color="steelblue")
    sumbu.set_title("Jumlah Reservasi per Dokter")
    sumbu.set_xlabel("Dokter")
    sumbu.set_ylabel("Jumlah Reservasi")
    sumbu.tick_params(axis="x", rotation=20)

    for posisi, nilai in enumerate(jumlah):
        sumbu.text(posisi, nilai, str(nilai), ha="center", va="bottom")

    tampilkan_grafik(plt)


def grafik_stok_obat():
    plt, pd = muat_pustaka_grafik()
    if plt is None:
        return

    db = database.db
    if len(db["obat"]) == 0:
        print("Data obat masih kosong")
        return

    df_obat = pd.DataFrame.from_dict(db["obat"], orient="index").sort_values("stok")
    warna = [
        "indianred" if stok < BATAS_STOK_OBAT else "seagreen"
        for stok in df_obat["stok"]
    ]

    fig, sumbu = plt.subplots(figsize=(9, 5))
    sumbu.barh(df_obat["nama"], df_obat["stok"], color=warna)
    sumbu.axvline(BATAS_STOK_OBAT, color="gray", linestyle="--", label="Batas stok menipis")
    sumbu.set_title("Stok Obat")
    sumbu.set_xlabel("Jumlah Stok")
    sumbu.legend()

    tampilkan_grafik(plt)


def grafik_pendapatan_dokter():
    plt, pd = muat_pustaka_grafik()
    if plt is None:
        return

    db = database.db
    lunas = [isi for isi in db["transaksi"].values() if isi["status_bayar"] == "Lunas"]
    if len(lunas) == 0:
        print("Belum ada transaksi yang lunas")
        return

    df_transaksi = pd.DataFrame(lunas)
    pendapatan = df_transaksi.groupby("id_dokter")["total"].sum()
    pendapatan.index = [
        db["dokter"].get(kode, {"nama": "Dokter Dihapus"})["nama"] for kode in pendapatan.index
    ]

    fig, sumbu = plt.subplots(figsize=(9, 5))
    pendapatan.plot(kind="bar", ax=sumbu, color="darkorange")
    sumbu.set_title("Pendapatan per Dokter (Transaksi Lunas)")
    sumbu.set_xlabel("Dokter")
    sumbu.set_ylabel("Pendapatan (Rp)")
    sumbu.tick_params(axis="x", rotation=20)

    tampilkan_grafik(plt)


def grafik_kondisi_alat():
    plt, pd = muat_pustaka_grafik()
    if plt is None:
        return

    db = database.db
    if len(db["inventaris_alat"]) == 0:
        print("Data alat masih kosong")
        return

    df_alat = pd.DataFrame.from_dict(db["inventaris_alat"], orient="index")
    jumlah = df_alat.groupby("kondisi")["jumlah"].sum()
    jumlah = jumlah[jumlah > 0]

    if jumlah.empty:
        print("Jumlah alat masih kosong")
        return

    fig, sumbu = plt.subplots(figsize=(6, 6))
    sumbu.pie(jumlah, labels=jumlah.index, autopct="%1.1f%%", startangle=90)
    sumbu.set_title("Kondisi Alat Klinik")

    tampilkan_grafik(plt)


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

        pilihan = pilih_menu("VISUALISASI DATA", daftar_menu)

        if pilihan == 5:
            return

        if pilihan == 1:
            grafik_reservasi_dokter()
        elif pilihan == 2:
            grafik_stok_obat()
        elif pilihan == 3:
            grafik_pendapatan_dokter()
        elif pilihan == 4:
            grafik_kondisi_alat()

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
