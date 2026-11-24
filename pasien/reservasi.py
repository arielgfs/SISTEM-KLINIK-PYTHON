from datetime import date

from modules.reservasi import batalkan_reservasi, buat_reservasi, slot_tersedia, ubah_jadwal
from modules.utils import konfirmasi, ke_angka, nama_dari, parse_tanggal, tampilkan_tabel
from pasien.dokter import lihat_dokter


def reservasi_pasien(db, id_pasien, status_boleh=None):
    """ID reservasi milik pasien (dan berstatus tertentu bila status_boleh diisi)."""
    return [
        kode for kode, isi in db["reservasi"].items()
        if isi["id_pasien"] == id_pasien and (status_boleh is None or isi["status"] in status_boleh)
    ]


def tampilkan_reservasi(db, daftar, judul_tabel="RESERVASI ANDA"):
    baris = [
        (
            kode,
            nama_dari(db["dokter"], db["reservasi"][kode]["id_dokter"]),
            db["reservasi"][kode]["tanggal"],
            db["reservasi"][kode]["jam"],
            db["reservasi"][kode]["status"]
        )
        for kode in daftar
    ]

    tampilkan_tabel(
        judul_tabel,
        ("ID", "Dokter", "Tanggal", "Jam", "Status"),
        baris,
        kiri=("Dokter", "Status")
    )


def pilih_slot(db, id_dokter, abaikan=None, tanggal_lama=None):
    """Meminta tanggal lalu jam. Mengembalikan (tanggal, jam) atau None bila dibatalkan."""
    petunjuk = "Tanggal (YYYY-MM-DD)"
    if tanggal_lama:
        petunjuk += ", Enter = tetap " + tanggal_lama

    teks = input(petunjuk + ": ").strip()
    if teks == "" and tanggal_lama:
        teks = tanggal_lama

    tanggal = parse_tanggal(teks)

    if tanggal is None:
        print("Format tanggal salah. Contoh: 2026-11-12")
        return None

    if tanggal < date.today():
        print("Tanggal sudah lewat, pilih hari ini atau setelahnya")
        return None

    tersedia, hari = slot_tersedia(db, id_dokter, tanggal, abaikan)

    if len(tersedia) == 0:
        print("Tidak ada slot tersedia pada hari", hari, "(dokter tidak praktik / jadwal penuh)")
        return None

    tampilkan_tabel(
        "SLOT TERSEDIA - " + hari + ", " + str(tanggal),
        ("No", "Jam"),
        [(nomor, jam) for nomor, jam in enumerate(tersedia, 1)]
    )
    nomor = ke_angka(input("Pilih nomor slot: "))

    if nomor is None or nomor < 1 or nomor > len(tersedia):
        print("Pilihan slot tidak valid")
        return None

    return tanggal, tersedia[nomor - 1]


def reservasi_konsultasi(db, user):
    lihat_dokter(db)

    if len(db["dokter"]) == 0:
        return

    id_dokter = input("ID dokter: ").strip()

    if id_dokter not in db["dokter"]:
        print("Dokter dengan ID", id_dokter, "tidak ditemukan")
        return

    hasil = pilih_slot(db, id_dokter)

    if hasil is None:
        return

    tanggal, jam = hasil
    id_baru = buat_reservasi(db, user["id_pasien"], id_dokter, tanggal, jam, user["username"])
    print("\nReservasi berhasil dibuat dengan ID", id_baru, "(status: Menunggu)")


def ubah_reservasi(db, user):
    daftar = reservasi_pasien(db, user["id_pasien"], ["Menunggu"])

    if len(daftar) == 0:
        print("Tidak ada reservasi (status Menunggu) yang dapat diubah")
        return

    tampilkan_reservasi(db, daftar, "RESERVASI YANG DAPAT DIUBAH")
    id_res = input("ID reservasi yang diubah: ").strip()

    if id_res not in daftar:
        print("ID tidak ada dalam daftar")
        return

    data = db["reservasi"][id_res]
    hasil = pilih_slot(db, data["id_dokter"], id_res, data["tanggal"])

    if hasil is None:
        return

    tanggal, jam = hasil
    ubah_jadwal(db, id_res, tanggal, jam, user["username"])
    print("\nReservasi berhasil diubah")


def batalkan_reservasi_pasien(db, user):
    daftar = reservasi_pasien(db, user["id_pasien"], ["Menunggu"])

    if len(daftar) == 0:
        print("Tidak ada reservasi (status Menunggu) yang dapat dibatalkan")
        return

    tampilkan_reservasi(db, daftar, "RESERVASI YANG DAPAT DIBATALKAN")
    id_res = input("ID reservasi yang dibatalkan: ").strip()

    if id_res not in daftar:
        print("ID tidak ada dalam daftar")
        return

    if konfirmasi("Yakin membatalkan reservasi " + id_res):
        batalkan_reservasi(db, id_res, user["username"])
        print("\nReservasi berhasil dibatalkan")
    else:
        print("Pembatalan dibatalkan")
