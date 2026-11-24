"""Fungsi reservasi yang dipakai bersama oleh resepsionis/ dan pasien/.
Semua fungsi menerima `db` (dict hasil database.muat_database) dan langsung menyimpan perubahan ke JSON."""
from modules import database
from modules.utils import id_berikutnya, nama_dari, sekarang

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
TABEL_RESERVASI = ["pasien", "dokter", "jadwal", "reservasi", "log_riwayat"]


def catat_log(db, id_reservasi, id_pasien, aksi, detail, user):
    id_log = id_berikutnya(db["log_riwayat"])
    db["log_riwayat"][id_log] = {
        "id_reservasi": id_reservasi,
        "id_pasien": id_pasien,
        "aksi": aksi,
        "detail": detail,
        "oleh": user,
        "waktu": sekarang()
    }


def slot_tersedia(db, id_dokter, tanggal, kecuali_id=None):
    """Mengembalikan (daftar jam yang masih kosong, nama hari).
    Jam yang sudah dipesan (status bukan Dibatalkan) tidak ikut -> mencegah jadwal penuh/bentrok.
    """
    hari = HARI[tanggal.weekday()]
    semua_jam = []
    for id_jadwal in db["jadwal"]:
        jadwal = db["jadwal"][id_jadwal]
        if jadwal["id_dokter"] == id_dokter and jadwal["hari"] == hari:
            for jam in jadwal["jam"]:
                if jam not in semua_jam:
                    semua_jam.append(jam)

    terisi = []
    for id_res in db["reservasi"]:
        data = db["reservasi"][id_res]
        if (data["id_dokter"] == id_dokter and data["tanggal"] == str(tanggal)
                and data["status"] != "Dibatalkan" and id_res != kecuali_id):
            terisi.append(data["jam"])

    tersedia = []
    for jam in semua_jam:
        if jam not in terisi:
            tersedia.append(jam)
    tersedia.sort()
    return tersedia, hari


def buat_reservasi(db, id_pasien, id_dokter, tanggal, jam, user):
    """Membuat reservasi baru (status Menunggu). Mengembalikan ID reservasi."""
    id_baru = id_berikutnya(db["reservasi"])
    db["reservasi"][id_baru] = {
        "id_pasien": id_pasien,
        "id_dokter": id_dokter,
        "tanggal": str(tanggal),
        "jam": jam,
        "status": "Menunggu",
        "dibuat_oleh": user
    }
    catat_log(db, id_baru, id_pasien, "BUAT",
              str(tanggal) + " " + jam + " dengan " + nama_dari(db["dokter"], id_dokter), user)
    database.simpan(db, ["reservasi", "log_riwayat"])
    return id_baru


def ubah_jadwal(db, id_res, tanggal, jam, user):
    data = db["reservasi"][id_res]
    lama = data["tanggal"] + " " + data["jam"]
    data["tanggal"] = str(tanggal)
    data["jam"] = jam
    catat_log(db, id_res, data["id_pasien"], "UBAH", lama + " -> " + data["tanggal"] + " " + data["jam"], user)
    database.simpan(db, ["reservasi", "log_riwayat"])


def batalkan_reservasi(db, id_res, user):
    data = db["reservasi"][id_res]
    data["status"] = "Dibatalkan"
    catat_log(db, id_res, data["id_pasien"], "BATAL", data["tanggal"] + " " + data["jam"], user)
    database.simpan(db, ["reservasi", "log_riwayat"])
