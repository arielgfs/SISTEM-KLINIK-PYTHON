from modules import input_teks, buat_id, waktu_sekarang, cari, input_angka
from admin import tampilkan_jadwal

db = {}


def buat_reservasi(id_pasien, pengguna):
    hasil_pilihan = pilih_jadwal_dan_tanggal()

    if not hasil_pilihan:
        return

    for reservasi_lama in db["reservasi"]:
        if (reservasi_lama["id_pasien"] == id_pasien
            and reservasi_lama["id_jadwal"] == hasil_pilihan[0]):

            if (reservasi_lama["tanggal"] == hasil_pilihan[1]
                and reservasi_lama["status"] != "dibatalkan"):

                print("Pasien sudah memiliki reservasi pada jadwal tersebut!")
                return

    keluhan = input_teks("Keluhan singkat: ")

    data_reservasi = {
        "id": buat_id(
            "RS",
            [r["id"] for r in db["reservasi"]]
        ),
        "id_pasien": id_pasien,
        "id_jadwal": hasil_pilihan[0],
        "tanggal": hasil_pilihan[1],
        "keluhan": keluhan,
        "status": "menunggu",
        "dibuat_pada": waktu_sekarang()
    }

    db["reservasi"].append(data_reservasi)

    catat_log_jadwal(
        data_reservasi["id"],
        "dibuat",
        f"Reservasi dibuat untuk {hasil_pilihan[1]} (jadwal {hasil_pilihan[0]})",
        pengguna
    )

    simpan_data()

    print(
        f"Reservasi berhasil dibuat dengan ID {data_reservasi['id']}. "
        "Status: menunggu."
    )


def pilih_jadwal_dan_tanggal(id_abaikan=0):
    tampilkan_jadwal()
    jadwal = cari("jadwal_dokter", input_angka("ID jadwal praktik: ", 1))
    if not jadwal:
        print("Jadwal tidak ditemukan!")
        return []
    tanggal = input_tanggal("Tanggal konsultasi (YYYY-MM-DD): ")
    if tanggal < hari_ini():
        print("Tanggal sudah lewat!")
        return []
    if nama_hari(tanggal) != jadwal["hari"]:
        print(f"Dokter hanya praktik hari {jadwal['hari']}, sedangkan {tanggal} adalah hari {nama_hari(tanggal)}!")
        return []
    if sisa_kuota(jadwal, tanggal, id_abaikan) <= 0:
        print("Jadwal tersebut sudah penuh, pilih jadwal/tanggal lain!")
        return []
    return [jadwal["id"], tanggal]
