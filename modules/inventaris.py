"""Fungsi inventaris (alat & obat) yang dipakai bersama oleh admin/ dan resepsionis/.
Data tetap dipisah: alat di inventaris_alat.json, obat di obat.json."""
from datetime import date, timedelta

BATAS_STOK_OBAT = 20
BATAS_HARI_KEDALUWARSA = 30


def obat_kedaluwarsa(obat):
    return obat["kedaluwarsa"] < str(date.today())


def mendekati_kedaluwarsa(obat):
    """Belum kedaluwarsa, tetapi habis dalam BATAS_HARI_KEDALUWARSA hari."""
    batas = str(date.today() + timedelta(days=BATAS_HARI_KEDALUWARSA))
    return not obat_kedaluwarsa(obat) and obat["kedaluwarsa"] <= batas


def stok_menipis(obat):
    return obat["stok"] < BATAS_STOK_OBAT


def jumlah_obat_menipis(daftar_obat):
    return sum(1 for isi in daftar_obat.values() if stok_menipis(isi))


def jumlah_alat_bermasalah(daftar_alat):
    return sum(isi["jumlah"] for isi in daftar_alat.values() if isi["kondisi"] != "Baik")
