from modules import database
from modules.pembayaran import STATUS_BELUM_DITAGIH, total_pendapatan
from modules.reservasi import log_jenis, tampilkan_reservasi
from modules.utils import format_rupiah, nama_dari, tampilkan_tabel
from resepsionis.struk import nomor_transaksi


def lihat_pasien_reservasi():
    db = database.db

    if len(db["pasien"]) == 0 and len(db["reservasi"]) == 0:
        print("\nData belum tersedia")
        return

    tampilkan_tabel(
        "DATA PASIEN",
        ("ID", "Nama", "Tgl Lahir", "No. HP", "Alamat"),
        [
            (kode, isi["nama"], isi.get("tgl_lahir", "-"), isi["no_hp"], isi["alamat"])
            for kode, isi in db["pasien"].items()
        ],
        kiri=("Nama", "Alamat")
    )

    if len(db["reservasi"]) == 0:
        print("\nBelum ada data reservasi")
    else:
        tampilkan_reservasi(db, list(db["reservasi"]), "DATA RESERVASI")


def laporan_pembayaran():
    db = database.db
    daftar = {k: v for k, v in db["transaksi"].items() if v["status_bayar"] != STATUS_BELUM_DITAGIH}

    if len(daftar) == 0:
        print("\nData belum tersedia")
        return

    tampilkan_tabel(
        "LAPORAN PEMBAYARAN DAN TRANSAKSI",
        ("No. Transaksi", "Tanggal", "Pasien", "Dokter", "Jasa", "Obat", "Total", "Metode", "Status"),
        [
            (
                nomor_transaksi(kode), isi["tanggal"],
                nama_dari(db["pasien"], isi["id_pasien"]), nama_dari(db["dokter"], isi["id_dokter"]),
                format_rupiah(isi["biaya_jasa"]), format_rupiah(isi["total"] - isi["biaya_jasa"]),
                format_rupiah(isi["total"]), isi["metode"] or "-", isi["status_bayar"]
            )
            for kode, isi in daftar.items()
        ],
        kiri=("Pasien", "Dokter", "Status"),
        kanan=("Jasa", "Obat", "Total")
    )

    belum = sum(isi["total"] for isi in daftar.values() if isi["status_bayar"] != "Lunas")
    print("\nJumlah transaksi         :", len(daftar))
    print("Total pendapatan (Lunas) :", format_rupiah(total_pendapatan(daftar)))
    print("Belum lunas              :", format_rupiah(belum))


def laporan_obat():
    db = database.db
    pemakaian = {}

    for isi in log_jenis(db, "obat"):
        if isi["aksi"] == "PAKAI":
            pemakaian[isi["id_item"]] = pemakaian.get(isi["id_item"], 0) + isi["jumlah"]

    if len(pemakaian) == 0:
        print("\nData belum tersedia")
        return

    tampilkan_tabel(
        "LAPORAN PENGGUNAAN DAN STOK OBAT",
        ("ID", "Nama Obat", "Jumlah Terpakai", "Stok Saat Ini"),
        [
            (
                kode,
                db["obat"][kode]["nama"] if kode in db["obat"] else "(data dihapus)",
                jumlah,
                db["obat"][kode]["stok"] if kode in db["obat"] else "-"
            )
            for kode, jumlah in pemakaian.items()
        ],
        kiri=("Nama Obat",)
    )
