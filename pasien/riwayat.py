import os

from modules.pembayaran import transaksi_milik_pasien
from modules.utils import format_rupiah, konfirmasi, nama_dari, tampilkan_tabel
from pasien.reservasi import reservasi_pasien, tampilkan_reservasi
from resepsionis import struk


def lihat_riwayat(db, user):
    daftar = reservasi_pasien(db, user["id_pasien"])

    if len(daftar) == 0:
        print("\nAnda belum memiliki reservasi")
        return

    tampilkan_reservasi(db, daftar, "STATUS & RIWAYAT RESERVASI")

    log = sorted(
        (isi for isi in db["log_riwayat"].values() if isi["id_pasien"] == user["id_pasien"]),
        key=lambda isi: isi["waktu"]
    )

    if len(log) > 0:
        tampilkan_tabel(
            "LOG PERUBAHAN RESERVASI",
            ("Waktu", "ID Res", "Aksi", "Detail"),
            [(isi["waktu"], isi["id_reservasi"], isi["aksi"], isi["detail"]) for isi in log],
            kiri=("Detail",)
        )


def lihat_tagihan(db, user):
    daftar = transaksi_milik_pasien(db, user["id_pasien"])

    if len(daftar) == 0:
        print("\nAnda belum memiliki tagihan")
        return

    tampilkan_tabel(
        "TAGIHAN & RIWAYAT PEMBAYARAN",
        ("ID", "No. Transaksi", "Dokter", "Tanggal", "Total", "Status"),
        [
            (
                kode,
                struk.nomor_transaksi(kode),
                nama_dari(db["dokter"], db["transaksi"][kode]["id_dokter"]),
                db["transaksi"][kode]["tanggal"],
                format_rupiah(db["transaksi"][kode]["total"]),
                db["transaksi"][kode]["status_bayar"]
            )
            for kode in daftar
        ],
        kiri=("Dokter", "Status"),
        kanan=("Total",)
    )

    id_trx = input("ID transaksi untuk melihat struk (Enter = kembali): ").strip()

    if id_trx == "":
        return

    if id_trx not in daftar:
        print("ID transaksi tidak ditemukan")
        return

    if db["transaksi"][id_trx]["status_bayar"] != "Lunas":
        print("Struk hanya tersedia untuk transaksi berstatus Lunas")
        return

    print()
    print(struk.buat_teks_struk(db, id_trx))

    if konfirmasi("\nUnduh struk ke file .txt"):
        os.makedirs(struk.FOLDER_STRUK, exist_ok=True)
        jalur = os.path.join(struk.FOLDER_STRUK, struk.nomor_transaksi(id_trx) + ".txt")
        with open(jalur, "w", encoding="utf-8") as berkas:
            berkas.write(struk.buat_teks_struk(db, id_trx) + "\n")
        print("Struk disimpan di:", jalur)
