from modules.utils import format_rupiah, tampilkan_tabel


def lihat_dokter(db):
    baris = [
        (nomor, kode, data["nama"], data["spesialisasi"], format_rupiah(data["biaya_jasa"]))
        for nomor, (kode, data) in enumerate(db["dokter"].items(), 1)
    ]

    if len(baris) == 0:
        print("\nBelum ada data dokter")
        return

    tampilkan_tabel(
        "DAFTAR DOKTER",
        ("No", "ID", "Nama Dokter", "Spesialisasi", "Biaya Jasa"),
        baris,
        kiri=("Nama Dokter", "Spesialisasi"),
        kanan=("Biaya Jasa",)
    )


def lihat_layanan(db):
    baris = [
        (nomor, data["nama"], format_rupiah(data["harga"]), data["keterangan"])
        for nomor, data in enumerate(db["layanan"].values(), 1)
    ]

    if len(baris) == 0:
        print("\nBelum ada data layanan")
        return

    tampilkan_tabel(
        "JENIS LAYANAN KLINIK",
        ("No", "Layanan", "Harga", "Keterangan"),
        baris,
        kiri=("Layanan", "Keterangan"),
        kanan=("Harga",)
    )
