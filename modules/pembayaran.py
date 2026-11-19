"""
Fungsi pembayaran yang dipakai bersama oleh admin/, resepsionis/, dan pasien/.
"""


def hitung_total(transaksi):
    """Total = biaya jasa dokter + jumlah semua subtotal obat. Hasil juga disimpan di transaksi."""
    total = transaksi["biaya_jasa"]
    for item in transaksi["obat"]:
        total = total + item["subtotal"]
    transaksi["total"] = total
    return total


def total_pendapatan(daftar_transaksi):
    """Jumlah transaksi yang sudah Lunas."""
    return sum(isi["total"] for isi in daftar_transaksi.values() if isi["status_bayar"] == "Lunas")


def transaksi_milik_pasien(db, id_pasien):
    """ID transaksi milik satu pasien."""
    return [
        id_trx for id_trx, isi in db["transaksi"].items()
        if isi["id_pasien"] == id_pasien
    ]
