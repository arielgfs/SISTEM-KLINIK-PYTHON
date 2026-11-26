from datetime import date

from modules import database
from modules.reservasi import (
    batalkan_reservasi, buat_reservasi, catat_log, log_jenis, pilih_slot,
    slot_tersedia, tampilkan_jadwal, tampilkan_reservasi, ubah_jadwal
)
from modules.utils import nama_dari, parse_tanggal, pilih_id, pilih_menu, konfirmasi, tampilkan_tabel
from resepsionis.pasien import tampil_tabel_pasien


def lihat_jadwal(db):
    """Lihat_Jadwal."""
    tampilkan_jadwal(db)


def buat_reservasi_manual(db, user):
    """Buat_Reservasi: pasien dicari lewat ID, lalu pilih dokter, tanggal, jam."""
    if len(db["pasien"]) > 0:
        tampil_tabel_pasien(db)

    id_pasien = pilih_id(db["pasien"], "ID pasien: ")

    if id_pasien is None:
        print("Pasien tidak ditemukan")
        return

    if not tampilkan_jadwal(db):
        return

    id_dokter = pilih_id(db["dokter"], "ID dokter: ")

    if id_dokter is None:
        print("Reservasi ditolak: dokter tidak ditemukan")
        return

    hasil = pilih_slot(db, id_dokter)

    if hasil is None:
        return

    tanggal, jam = hasil
    id_baru = buat_reservasi(db, id_pasien, id_dokter, tanggal, jam, user)
    print("\nReservasi berhasil dibuat dengan ID", id_baru, "(status: Menunggu)")


def ubah_batal_reservasi(db, user):
    """Ubah_Batal_Reservasi: ubah jadwal atau batalkan."""
    daftar = [k for k, v in db["reservasi"].items() if v["status"] in database.STATUS_AKTIF]
    if len(daftar) > 0:
        tampilkan_reservasi(db, daftar, "RESERVASI AKTIF")

    id_res = pilih_id(db["reservasi"], "Nomor reservasi: ")

    if id_res is None or db["reservasi"][id_res]["status"] in ("Selesai", "Dibatalkan"):
        print("Reservasi tidak ada atau sudah selesai")
        return

    data = db["reservasi"][id_res]
    aksi = pilih_menu("Pilih tindakan", ["Ubah jadwal", "Batalkan reservasi"])

    if aksi == 2:
        if konfirmasi("Batalkan reservasi " + id_res):
            batalkan_reservasi(db, id_res, user)
            print("Reservasi berhasil diperbarui (status Dibatalkan)")
        else:
            print("Pembatalan dibatalkan")
        return

    hasil = pilih_slot(db, data["id_dokter"], id_res, data["tanggal"])

    if hasil is None:
        return

    tanggal, jam = hasil
    ubah_jadwal(db, id_res, tanggal, jam, user)
    print("Reservasi berhasil diperbarui")


def konfirmasi_kedatangan(db, user):
    """Konfirmasi_Kedatangan: reservasi Menunggu pada hari ini -> status Hadir."""
    id_res = pilih_id(db["reservasi"], "Nomor reservasi: ")

    if (id_res is None or db["reservasi"][id_res]["status"] != "Menunggu"
            or db["reservasi"][id_res]["tanggal"] != str(date.today())):
        print("Reservasi tidak valid atau bukan hari ini")
        return

    data = db["reservasi"][id_res]
    data["status"] = "Hadir"
    catat_log(db, id_res, data["id_pasien"], "HADIR", "Status Menunggu -> Hadir", user)
    database.simpan(db, ["reservasi", "log_riwayat"])
    print("Kedatangan pasien dikonfirmasi")


def status_reservasi(db, user):
    """Status_Reservasi: ubah status (Menunggu/Hadir/Selesai/Dibatalkan)."""
    if len(db["reservasi"]) == 0:
        print("Data belum tersedia")
        return

    tampilkan_reservasi(db, list(db["reservasi"]), "SEMUA RESERVASI")
    id_res = pilih_id(db["reservasi"], "Nomor reservasi: ")

    if id_res is None:
        print("Nomor tidak valid")
        return

    data = db["reservasi"][id_res]
    print("Status saat ini:", data["status"])
    baru = input("Status baru (" + "/".join(database.STATUS_RESERVASI) + "): ").strip().capitalize()

    if baru not in database.STATUS_RESERVASI:
        print("Status tidak valid")
        return

    if baru == data["status"]:
        print("Status tidak berubah")
        return

    if data["status"] == "Dibatalkan":
        tersedia, hari = slot_tersedia(db, data["id_dokter"], parse_tanggal(data["tanggal"]), id_res)
        if data["jam"] not in tersedia:
            print("Status tidak bisa diubah: slot " + data["tanggal"] + " " + data["jam"] + " sudah terisi")
            return

    lama = data["status"]
    data["status"] = baru
    catat_log(db, id_res, data["id_pasien"], "STATUS", lama + " -> " + baru, user)
    database.simpan(db, ["reservasi", "log_riwayat"])
    print("Status berhasil diubah: " + lama + " -> " + baru)


def log_jadwal(db):
    """Log_Jadwal: riwayat perubahan jadwal reservasi."""
    log = log_jenis(db, "reservasi")

    if len(log) == 0:
        print("\nData belum tersedia")
        return

    tampilkan_tabel(
        "LOG RIWAYAT JADWAL PASIEN",
        ("Waktu", "ID Res", "Pasien", "Aksi", "Detail", "Oleh"),
        [
            (isi["waktu"], isi["id_reservasi"], nama_dari(db["pasien"], isi["id_pasien"]),
             isi["aksi"], isi["detail"], isi["oleh"])
            for isi in log
        ],
        kiri=("Pasien", "Detail", "Oleh")
    )
