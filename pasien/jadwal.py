from modules.reservasi import slot_tersedia
from modules.utils import nama_dari, parse_tanggal, tampilkan_tabel
from pasien.dokter import lihat_dokter


def lihat_jadwal(db):
    baris = []

    for kode, data in db["jadwal"].items():
        dokter = db["dokter"].get(data["id_dokter"])
        baris.append((
            kode,
            nama_dari(db["dokter"], data["id_dokter"]),
            dokter["spesialisasi"] if dokter else "-",
            data["hari"],
            ", ".join(data["jam"])
        ))

    if len(baris) == 0:
        print("\nBelum ada jadwal praktik")
        return

    tampilkan_tabel(
        "JADWAL PRAKTIK DOKTER",
        ("ID", "Dokter", "Spesialisasi", "Hari", "Jam Praktik"),
        baris,
        kiri=("Dokter", "Spesialisasi", "Jam Praktik")
    )


def lihat_slot_tersedia(db):
    lihat_dokter(db)
    id_dokter = input("ID dokter: ").strip()

    if id_dokter not in db["dokter"]:
        print("Dokter dengan ID", id_dokter, "tidak ditemukan")
        return

    tanggal = parse_tanggal(input("Tanggal (YYYY-MM-DD): ").strip())

    if tanggal is None:
        print("Format tanggal salah. Contoh: 2026-11-12")
        return

    tersedia, hari = slot_tersedia(db, id_dokter, tanggal)
    print("\n" + nama_dari(db["dokter"], id_dokter) + " - " + hari + ", " + str(tanggal))

    if len(tersedia) == 0:
        print("Tidak ada slot tersedia (dokter tidak praktik / jadwal penuh)")
        return

    tampilkan_tabel(
        "SLOT TERSEDIA",
        ("No", "Jam"),
        [(nomor, jam) for nomor, jam in enumerate(tersedia, 1)]
    )
