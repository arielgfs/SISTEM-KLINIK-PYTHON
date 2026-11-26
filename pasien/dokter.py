from modules.utils import format_rupiah, tampilkan_tabel


def lihat_dokter(db):
    """Lihat_Dokter: dokter, spesialisasi, dan biaya jasa."""
    if len(db["dokter"]) == 0:
        print("\nData belum tersedia")
        return False

    tampilkan_tabel(
        "DAFTAR DOKTER",
        ("No", "ID", "Nama Dokter", "Spesialisasi", "Biaya Jasa"),
        [
            (nomor, kode, data["nama"], data["spesialisasi"], format_rupiah(data["biaya_jasa"]))
            for nomor, (kode, data) in enumerate(db["dokter"].items(), 1)
        ],
        kiri=("Nama Dokter", "Spesialisasi"),
        kanan=("Biaya Jasa",)
    )
    return True


def lihat_layanan(db):
    """Lihat_Layanan: jenis layanan klinik."""
    if len(db["layanan"]) == 0:
        print("\nData belum tersedia")
        return

    tampilkan_tabel(
        "JENIS LAYANAN KLINIK",
        ("No", "Layanan", "Deskripsi"),
        [(nomor, data["nama"], data["keterangan"]) for nomor, data in enumerate(db["layanan"].values(), 1)],
        kiri=("Layanan", "Deskripsi")
    )
