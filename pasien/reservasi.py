from modules.reservasi import (
    batalkan_reservasi, buat_reservasi, pilih_slot, tampilkan_reservasi, ubah_jadwal
)
from modules.utils import konfirmasi, pilih_id, pilih_menu
from pasien.dokter import lihat_dokter
from pasien.jadwal import lihat_jadwal_slot


def reservasi_pasien(db, id_pasien, status_boleh=None):
    """ID reservasi milik pasien (dan berstatus tertentu bila status_boleh diisi)."""
    return [
        kode for kode, isi in db["reservasi"].items()
        if isi["id_pasien"] == id_pasien and (status_boleh is None or isi["status"] in status_boleh)
    ]


def reservasi_konsultasi(db, user):
    """Reservasi_Konsultasi: lihat jadwal/slot, pilih dokter, tanggal, jam."""
    lihat_jadwal_slot(db)

    if len(db["dokter"]) == 0:
        return

    id_dokter = pilih_id(db["dokter"], "Masukkan ID Dokter: ")

    if id_dokter is None:
        print("Jadwal tidak valid: dokter tidak ditemukan")
        return

    hasil = pilih_slot(db, id_dokter)

    if hasil is None:
        return

    tanggal, jam = hasil
    id_baru = buat_reservasi(db, user["id_pasien"], id_dokter, tanggal, jam, user["username"])
    print("\nReservasi berhasil dibuat dengan ID", id_baru, "(status: Menunggu)")


def ubah_batal_reservasi(db, user):
    """Ubah_Batal_Reservasi: hanya reservasi milik sendiri yang masih Menunggu."""
    from pasien.riwayat import lihat_riwayat_reservasi

    lihat_riwayat_reservasi(db, user)
    id_res = pilih_id(db["reservasi"], "Nomor reservasi: ")

    if id_res is None or db["reservasi"][id_res]["id_pasien"] != user["id_pasien"]:
        print("Bukan reservasi milik anda")
        return

    data = db["reservasi"][id_res]

    if data["status"] != "Menunggu":
        print("Reservasi berstatus", data["status"], "tidak dapat diubah atau dibatalkan")
        return

    aksi = pilih_menu("Pilih tindakan", ["Ubah jadwal", "Batalkan reservasi"])

    if aksi == 2:
        if konfirmasi("Yakin membatalkan reservasi " + id_res):
            batalkan_reservasi(db, id_res, user["username"])
            print("Reservasi berhasil diperbarui (status Dibatalkan)")
        else:
            print("Pembatalan dibatalkan")
        return

    hasil = pilih_slot(db, data["id_dokter"], id_res, data["tanggal"])

    if hasil is None:
        return

    tanggal, jam = hasil
    ubah_jadwal(db, id_res, tanggal, jam, user["username"])
    print("Reservasi berhasil diperbarui")
