from modules.pembayaran import transaksi_milik_pasien
from modules.reservasi import log_jenis, tampilkan_reservasi
from modules.utils import format_rupiah, konfirmasi, pilih_id, tampilkan_tabel
from pasien.reservasi import reservasi_pasien
from resepsionis import struk


def lihat_riwayat_reservasi(db, user):
    """Lihat_Riwayat_Reservasi: status dan riwayat reservasi pribadi."""
    daftar = reservasi_pasien(db, user["id_pasien"])

    if len(daftar) == 0:
        print("\nData belum tersedia")
        return

    tampilkan_reservasi(db, daftar, "STATUS DAN RIWAYAT RESERVASI")

    log = [isi for isi in log_jenis(db, "reservasi") if isi["id_pasien"] == user["id_pasien"]]

    if len(log) > 0:
        tampilkan_tabel(
            "LOG PERUBAHAN RESERVASI",
            ("Waktu", "ID Res", "Aksi", "Detail"),
            [(isi["waktu"], isi["id_reservasi"], isi["aksi"], isi["detail"]) for isi in log],
            kiri=("Detail",)
        )


def tabel_transaksi(db, daftar, judul_tabel):
    tampilkan_tabel(
        judul_tabel,
        ("ID", "No. Transaksi", "Tanggal", "Total", "Metode", "Status"),
        [
            (kode, struk.nomor_transaksi(kode), db["transaksi"][kode]["tanggal"],
             format_rupiah(db["transaksi"][kode]["total"]), db["transaksi"][kode]["metode"] or "-",
             db["transaksi"][kode]["status_bayar"])
            for kode in daftar
        ],
        kiri=("Status",),
        kanan=("Total",)
    )


def lihat_tagihan(db, user):
    """Lihat_Tagihan: rincian tagihan, biaya jasa, dan obat."""
    daftar = transaksi_milik_pasien(db, user["id_pasien"])

    if len(daftar) == 0:
        print("\nData belum tersedia")
        return

    tabel_transaksi(db, daftar, "TAGIHAN ANDA")
    id_trx = pilih_id(daftar, "ID transaksi untuk melihat rincian (Enter = kembali): ")

    if id_trx is not None:
        print()
        struk.tampil_rincian(db, id_trx)


def riwayat_pembayaran(db, user):
    """Riwayat_Pembayaran: transaksi yang sudah diproses pembayarannya."""
    daftar = [
        kode for kode in transaksi_milik_pasien(db, user["id_pasien"])
        if db["transaksi"][kode]["status_bayar"] != "Belum Dibayar"
    ]

    if len(daftar) == 0:
        print("\nData belum tersedia")
        return

    tabel_transaksi(db, daftar, "RIWAYAT PEMBAYARAN")


def unduh_struk(db, user):
    """Unduh_Struk: hanya transaksi milik sendiri yang Lunas."""
    milik = transaksi_milik_pasien(db, user["id_pasien"])

    if len(milik) > 0:
        tabel_transaksi(db, milik, "TRANSAKSI ANDA")

    id_trx = input("Nomor transaksi: ").strip()

    if id_trx not in milik or db["transaksi"][id_trx]["status_bayar"] != "Lunas":
        print("Transaksi tidak ada atau belum lunas")
        return

    print()
    print(struk.buat_teks_struk(db, id_trx))

    if konfirmasi("\nSimpan struk ke file .txt"):
        print("Struk disimpan di:", struk.simpan_struk(db, id_trx))
