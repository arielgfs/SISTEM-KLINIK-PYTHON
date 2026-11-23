from datetime import date, timedelta
from modules import database
from modules.utils import (bersihkan_layar, jeda, judul, buat_tabel, id_berikutnya, sekarang, parse_tanggal, nama_dari)
from resepsionis import pasien
from resepsionis.pasien import pilih_menu, pilih_data, konfirmasi

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]   
STATUS_RESERVASI = ["Menunggu", "Dikonfirmasi", "Selesai", "Dibatalkan"]
HARI_CARI = 14            



def catat_log(db, id_res, id_pasien, aksi, detail, user):
    id_log = id_berikutnya(db["log_riwayat"])             
    db["log_riwayat"][id_log] = {
        "id_reservasi": id_res,
        "id_pasien": id_pasien,
        "aksi": aksi,
        "detail": detail,
        "oleh": user,
        "waktu": sekarang()
    }


def slot_tersedia(db, id_dokter, tanggal, kecuali_id=None):
    hari = HARI[tanggal.weekday()]
    semua_jam = []
    for id_jadwal in db["jadwal"]:                        
        jadwal = db["jadwal"][id_jadwal]
        if jadwal["id_dokter"] == id_dokter and jadwal["hari"] == hari:
            for jam in jadwal["jam"]:
                if jam not in semua_jam:
                    semua_jam.append(jam)

    jam_terisi = []
    for id_res in db["reservasi"]:                       
        data = db["reservasi"][id_res]
        if (data["id_dokter"] == id_dokter and data["tanggal"] == str(tanggal)
                and data["status"] != "Dibatalkan" and id_res != kecuali_id):
            jam_terisi.append(data["jam"])

    tersedia = []
    for jam in semua_jam:
        if jam not in jam_terisi:
            tersedia.append(jam)
    tersedia.sort()
    return tersedia, hari



def pilihan_reservasi(db, status_boleh):
    pilihan = []
    for id_res in db["reservasi"]:                        
        data = db["reservasi"][id_res]
        if data["status"] in status_boleh:
            pilihan.append((id_res + " | " + nama_dari(db["pasien"], data["id_pasien"])
                            + " | " + nama_dari(db["dokter"], data["id_dokter"])
                            + " | " + data["tanggal"] + " " + data["jam"] + " | " + data["status"], id_res))
    return pilihan


def pilih_tanggal_dan_jam(db, id_dokter, kecuali_id=None):
    pilihan_tanggal = []
    for selisih in range(0, HARI_CARI):
        tanggal = date.today() + timedelta(days=selisih)
        tersedia, hari = slot_tersedia(db, id_dokter, tanggal, kecuali_id)
        if len(tersedia) > 0:
            pilihan_tanggal.append((hari + ", " + str(tanggal) + " (" + str(len(tersedia)) + " slot)", tanggal))
    if len(pilihan_tanggal) == 0:
        print("\n[!] Tidak ada slot tersedia untuk dokter ini dalam " + str(HARI_CARI) + " hari ke depan.")
        return None, None

    tanggal = pilih_data("Pilih tanggal", pilihan_tanggal)
    if tanggal == None:
        return None, None

    tersedia, hari = slot_tersedia(db, id_dokter, tanggal, kecuali_id)
    pilihan_jam = []
    for jam in tersedia:
        pilihan_jam.append((jam, jam))
    jam = pilih_data("Pilih jam", pilihan_jam)
    if jam == None:
        return None, None
    return tanggal, jam



def lihat_jadwal_dokter(db):
    bersihkan_layar()
    judul("JADWAL PRAKTIK DOKTER")
    if len(db["jadwal"]) == 0:
        print(" Belum ada jadwal praktik.")
        jeda()
        return

    tabel = buat_tabel(["Dokter", "Spesialisasi", "Hari", "Jam Praktik"], ["Dokter", "Spesialisasi", "Jam Praktik"])
    for id_jadwal in db["jadwal"]:                        
        jadwal = db["jadwal"][id_jadwal]
        spesialisasi = "-"
        if jadwal["id_dokter"] in db["dokter"]:
            spesialisasi = db["dokter"][jadwal["id_dokter"]]["spesialisasi"]
        tabel.add_row([nama_dari(db["dokter"], jadwal["id_dokter"]), spesialisasi, jadwal["hari"], ", ".join(jadwal["jam"])])
    print(tabel)
    jeda()


def cek_slot_tersedia(db):
    bersihkan_layar()
    judul("CEK SLOT TERSEDIA")
    id_dokter = pilih_data("Pilih dokter", pasien.pilihan_dokter(db))
    if id_dokter == None:
        return

    tabel = buat_tabel(["Tanggal", "Hari", "Jam Tersedia"], ["Jam Tersedia"])
    jumlah_hari = 0
    for selisih in range(0, HARI_CARI):
        tanggal = date.today() + timedelta(days=selisih)
        tersedia, hari = slot_tersedia(db, id_dokter, tanggal)
        if len(tersedia) > 0:
            jumlah_hari = jumlah_hari + 1
            tabel.add_row([str(tanggal), hari, ", ".join(tersedia)])

    print("\n" + nama_dari(db["dokter"], id_dokter) + " - " + str(HARI_CARI) + " hari ke depan")
    if jumlah_hari == 0:
        print("[!] Tidak ada slot tersedia.")
    else:
        print(tabel)
    jeda()



def buat_reservasi_manual(db, user):
    bersihkan_layar()
    judul("BUAT RESERVASI MANUAL")
    if len(db["pasien"]) == 0 or len(db["dokter"]) == 0:
        print(" Data pasien / dokter masih kosong.")
        jeda()
        return

    id_pasien = pilih_data("Pilih pasien", pasien.pilihan_pasien(db))
    if id_pasien == None:
        return
    id_dokter = pilih_data("Pilih dokter", pasien.pilihan_dokter(db))
    if id_dokter == None:
        return

    tanggal, jam = pilih_tanggal_dan_jam(db, id_dokter)
    if tanggal == None:
        jeda()
        return

    print("\nRingkasan reservasi")
    print(" Pasien  : " + nama_dari(db["pasien"], id_pasien))
    print(" Dokter  : " + nama_dari(db["dokter"], id_dokter))
    print(" Jadwal  : " + str(tanggal) + " pukul " + jam)
    if konfirmasi("Simpan reservasi ini?") == False:
        print("\n[*] Reservasi dibatalkan.")
        jeda()
        return

    id_baru = id_berikutnya(db["reservasi"])
    db["reservasi"][id_baru] = {
        "id_pasien": id_pasien, "id_dokter": id_dokter,
        "tanggal": str(tanggal), "jam": jam,
        "status": "Menunggu", "dibuat_oleh": user
    }
    catat_log(db, id_baru, id_pasien, "BUAT",
              str(tanggal) + " " + jam + " dengan " + nama_dari(db["dokter"], id_dokter), user)
    database.simpan(db, ["reservasi", "log_riwayat"])     
    print("\n[+] Reservasi berhasil dibuat. Nomor reservasi : " + id_baru)
    jeda()



def ubah_reservasi_pasien(db, user):
    bersihkan_layar()
    judul("UBAH RESERVASI")
    pilihan = pilihan_reservasi(db, ["Menunggu", "Dikonfirmasi"])
    if len(pilihan) == 0:
        print(" Tidak ada reservasi yang dapat diubah.")
        jeda()
        return

    id_res = pilih_data("Pilih reservasi yang diubah", pilihan)
    if id_res == None:
        return

    data = db["reservasi"][id_res]
    tanggal, jam = pilih_tanggal_dan_jam(db, data["id_dokter"], id_res)
    if tanggal == None:
        jeda()
        return

    lama = data["tanggal"] + " " + data["jam"]
    data["tanggal"] = str(tanggal)
    data["jam"] = jam
    catat_log(db, id_res, data["id_pasien"], "UBAH", lama + " -> " + data["tanggal"] + " " + data["jam"], user)
    database.simpan(db, ["reservasi", "log_riwayat"])     
    print("\n[+] Reservasi berhasil diubah.")
    jeda()


def batalkan_reservasi_pasien(db, user):
    bersihkan_layar()
    judul("BATALKAN RESERVASI")
    pilihan = pilihan_reservasi(db, ["Menunggu", "Dikonfirmasi"])
    if len(pilihan) == 0:
        print(" Tidak ada reservasi yang dapat dibatalkan.")
        jeda()
        return

    id_res = pilih_data("Pilih reservasi yang dibatalkan", pilihan)
    if id_res == None:
        return

    if konfirmasi("Yakin membatalkan reservasi " + id_res + "?"):
        data = db["reservasi"][id_res]
        data["status"] = "Dibatalkan"
        catat_log(db, id_res, data["id_pasien"], "BATAL", data["tanggal"] + " " + data["jam"], user)
        database.simpan(db, ["reservasi", "log_riwayat"])  
        print("\n[+] Reservasi berhasil dibatalkan (slot kembali tersedia).")
    else:
        print("\n[*] Pembatalan dibatalkan.")
    jeda()



def konfirmasi_kedatangan(db, user):
    bersihkan_layar()
    judul("KONFIRMASI KEDATANGAN PASIEN")
    pilihan = pilihan_reservasi(db, ["Menunggu"])
    if len(pilihan) == 0:
        print(" Tidak ada reservasi berstatus Menunggu.")
        jeda()
        return

    id_res = pilih_data("Pilih reservasi pasien yang datang", pilihan)
    if id_res == None:
        return

    data = db["reservasi"][id_res]
    if data["tanggal"] != str(date.today()):
        print("\n[!] Tanggal reservasi (" + data["tanggal"] + ") bukan hari ini.")
        if konfirmasi("Tetap konfirmasi kedatangan?") == False:
            print("\n[*] Konfirmasi dibatalkan.")
            jeda()
            return

    data["status"] = "Dikonfirmasi"
    catat_log(db, id_res, data["id_pasien"], "KONFIRMASI", "Pasien hadir, status -> Dikonfirmasi", user)
    database.simpan(db, ["reservasi", "log_riwayat"])     
    print("\n[+] Kedatangan pasien dikonfirmasi.")
    jeda()



def kelola_status_reservasi(db, user):
    bersihkan_layar()
    judul("KELOLA STATUS RESERVASI")
    pilihan = pilihan_reservasi(db, STATUS_RESERVASI)
    if len(pilihan) == 0:
        print(" Belum ada data reservasi.")
        jeda()
        return

    id_res = pilih_data("Pilih reservasi", pilihan)
    if id_res == None:
        return

    data = db["reservasi"][id_res]
    print("\nStatus saat ini : " + data["status"])
    pilihan_status = []
    for status in STATUS_RESERVASI:
        pilihan_status.append((status, status))
    status_baru = pilih_data("Pilih status baru", pilihan_status)
    if status_baru == None:
        return
    if status_baru == data["status"]:
        print("\n[*] Status tidak berubah.")
        jeda()
        return

    if data["status"] == "Dibatalkan":
        tersedia, hari = slot_tersedia(db, data["id_dokter"], parse_tanggal(data["tanggal"]), id_res)
        if data["jam"] not in tersedia:
            print("\n[!] Slot " + data["tanggal"] + " " + data["jam"] + " sudah terisi / tidak tersedia.")
            jeda()
            return

    lama = data["status"]
    data["status"] = status_baru
    catat_log(db, id_res, data["id_pasien"], "STATUS", lama + " -> " + status_baru, user)
    database.simpan(db, ["reservasi", "log_riwayat"])     
    print("\n[+] Status reservasi diubah: " + lama + " -> " + status_baru)
    jeda()



def ambil_waktu(item):
    return item[1]["waktu"]


def lihat_log_riwayat(db):
    bersihkan_layar()
    judul("LOG RIWAYAT JADWAL PASIEN")
    if len(db["log_riwayat"]) == 0:
        print(" Belum ada log riwayat.")
        jeda()
        return

    pilihan = [("Semua pasien", "")]
    for item in pasien.pilihan_pasien(db):
        pilihan.append(item)
    filter_id = pilih_data("Lihat log milik", pilihan)
    if filter_id == None:
        return

    urut = sorted(db["log_riwayat"].items(), key=ambil_waktu)       
    tabel = buat_tabel(["No", "Waktu", "ID Res", "Pasien", "Aksi", "Detail", "Oleh"], ["Pasien", "Detail", "Oleh"])
    nomor = 0
    for id_log, log in urut:                             
        if filter_id == "" or log["id_pasien"] == filter_id:
            nomor = nomor + 1
            tabel.add_row([nomor, log["waktu"], log["id_reservasi"],
                           nama_dari(db["pasien"], log["id_pasien"]), log["aksi"], log["detail"], log["oleh"]])
    if nomor == 0:
        print("\n Tidak ada log untuk pasien tersebut.")
    else:
        print(tabel)
    jeda()



def menu_reservasi(db, user):
    daftar_menu = [
        "Lihat Jadwal Praktik Dokter",
        "Cek Slot Tersedia",
        "Buat Reservasi Manual",
        "Ubah Reservasi",
        "Batalkan Reservasi",
        "Konfirmasi Kedatangan Pasien",
        "Kelola Status Reservasi",
        "Lihat Log Riwayat Jadwal",
        "Kembali ke Dashboard"
    ]
    jalan = True
    while jalan:
        bersihkan_layar()
        judul("KELOLA RESERVASI")
        pilihan = pilih_menu("Pilih menu (panah atas/bawah, Enter untuk memilih)", daftar_menu)

        if pilihan == "Lihat Jadwal Praktik Dokter":
            lihat_jadwal_dokter(db)
        elif pilihan == "Cek Slot Tersedia":
            cek_slot_tersedia(db)
        elif pilihan == "Buat Reservasi Manual":
            buat_reservasi_manual(db, user)
        elif pilihan == "Ubah Reservasi":
            ubah_reservasi_pasien(db, user)
        elif pilihan == "Batalkan Reservasi":
            batalkan_reservasi_pasien(db, user)
        elif pilihan == "Konfirmasi Kedatangan Pasien":
            konfirmasi_kedatangan(db, user)
        elif pilihan == "Kelola Status Reservasi":
            kelola_status_reservasi(db, user)
        elif pilihan == "Lihat Log Riwayat Jadwal":
            lihat_log_riwayat(db)
        elif pilihan == "Kembali ke Dashboard":
            jalan = False