from datetime import date, timedelta

from modules.reservasi import HARI, sisa_kuota
from modules.utils import nama_dari, tampilkan_tabel


def lihat_jadwal_slot(db):
    """Lihat_Jadwal_Slot: jadwal praktik + sisa slot pada tanggal terdekat tiap jadwal."""
    if len(db["jadwal"]) == 0:
        print("\nData belum tersedia")
        return

    baris = []
    for kode, data in db["jadwal"].items():
        tanggal = date.today()
        while HARI[tanggal.weekday()] != data["hari"]:
            tanggal += timedelta(days=1)

        dokter = db["dokter"].get(data["id_dokter"])
        
        baris.append((
        kode,
        data["id_dokter"],
        nama_dari(db["dokter"], data["id_dokter"]),
        dokter["spesialisasi"] if dokter else "-",
        data["hari"],
        data["jam_mulai"] + " - " + data["jam_selesai"],
        str(tanggal),
        sisa_kuota(db, data["id_dokter"], tanggal)
    ))

    tampilkan_tabel(
        "JADWAL PRAKTIK DAN SLOT TERSEDIA",
        ("ID Jadwal", "ID Dokter", "Dokter", "Spesialisasi",
         "Hari", "Jam Praktik", "Tanggal Terdekat", "Sisa Slot"),
        baris,
        kiri=("Dokter", "Spesialisasi")
    )