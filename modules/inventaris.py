"""Fungsi inventaris (alat & obat) yang dipakai bersama oleh admin/ dan resepsionis/.
Data tetap dipisah: alat di inventaris_alat.json, obat di obat.json."""
from datetime import date

BATAS_STOK_OBAT = 20


def obat_kedaluwarsa(obat):
    return obat["kedaluwarsa"] < str(date.today())


def stok_menipis(obat):
    return obat["stok"] < BATAS_STOK_OBAT


def jumlah_obat_menipis(daftar_obat):
    return sum(1 for isi in daftar_obat.values() if stok_menipis(isi))


def jumlah_alat_bermasalah(daftar_alat):
    return sum(isi["jumlah"] for isi in daftar_alat.values() if isi["kondisi"] != "Baik")
