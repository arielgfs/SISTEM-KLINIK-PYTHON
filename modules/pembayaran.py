"""Fungsi pembayaran yang dipakai bersama oleh admin/, resepsionis/, dan pasien/."""

STATUS_BELUM_DITAGIH = "Belum Ditagih" # transaksi yang berisi obat tapi belum ditagihkan.


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
    """ID transaksi (yang sudah ditagihkan) milik satu pasien."""
    return [
        id_trx for id_trx, isi in db["transaksi"].items()
        if isi["id_pasien"] == id_pasien and isi["status_bayar"] != STATUS_BELUM_DITAGIH
    ]


def transaksi_reservasi(db, id_reservasi):
    """ID transaksi milik satu reservasi, atau None."""
    for id_trx, isi in db["transaksi"].items():
        if isi["id_reservasi"] == id_reservasi:
            return id_trx
    return None
