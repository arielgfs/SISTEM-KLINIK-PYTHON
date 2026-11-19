"""
=====================================================================
resepsionis/reservasi.py         
Tabel JSON : reservasi.json, jadwal.json, log_riwayat.json, pasien.json, dokter.json
Catatan    : fungsi slot_tersedia() dan catat_log() bisa dipakai ulang untuk bagian
             Pasien bila ingin memindahkannya ke modules/reservasi.py.
=====================================================================
"""
from datetime import date, datetime
from modules import database
from modules.utils import (bersihkan_layar, jeda, ke_angka, buat_tabel, judul,
                           parse_tanggal, nama_dari)
# Fungsi inti reservasi dipakai bersama dengan bagian pasien -> ada di modules/reservasi.py
from modules.reservasi import (catat_log, slot_tersedia, buat_reservasi,
                               ubah_jadwal, batalkan_reservasi)

STATUS_RESERVASI = {"1": "Menunggu", "2": "Dikonfirmasi", "3": "Selesai", "4": "Dibatalkan"}


def set_konfirmasi(db, id_res, user):
    data = db["reservasi"][id_res]
    data["status"] = "Dikonfirmasi"
    catat_log(db, id_res, data["id_pasien"], "KONFIRMASI", "Pasien hadir, status -> Dikonfirmasi", user)
    database.simpan(db, ["reservasi", "log_riwayat"])     


def ubah_status(db, id_res, status_baru, user):
    """Mengembalikan (berhasil, pesan)."""
    data = db["reservasi"][id_res]
    if status_baru == data["status"]:
        return False, "Status tidak berubah."
    if data["status"] == "Dibatalkan":
        tanggal = datetime.strptime(data["tanggal"], "%Y-%m-%d").date()
        tersedia, hari = slot_tersedia(db, data["id_dokter"], tanggal, id_res)
        if data["jam"] not in tersedia:
            return False, "Slot " + data["tanggal"] + " " + data["jam"] + " sudah terisi / tidak tersedia."
    lama = data["status"]
    data["status"] = status_baru
    catat_log(db, id_res, data["id_pasien"], "STATUS", lama + " -> " + status_baru, user)
    database.simpan(db, ["reservasi", "log_riwayat"])     # [JSON] simpan perubahan
    return True, "Status reservasi diubah: " + lama + " -> " + status_baru



def daftar_reservasi(db, status_boleh=None):
    """List ID reservasi (status_boleh = list status yang diambil, None = semua)."""
    daftar = []
    for id_res in db["reservasi"]:                        # [JSON] reservasi.json
        if status_boleh == None or db["reservasi"][id_res]["status"] in status_boleh:
            daftar.append(id_res)
    return daftar


def tampil_tabel_reservasi(db, daftar):
    tabel = buat_tabel(["ID", "Pasien", "Dokter", "Tanggal", "Jam", "Status"], ["Pasien", "Dokter", "Status"])
    for id_res in daftar:
        data = db["reservasi"][id_res]
        tabel.add_row([id_res, nama_dari(db["pasien"], data["id_pasien"]),
                       nama_dari(db["dokter"], data["id_dokter"]),
                       data["tanggal"], data["jam"], data["status"]])
    print(tabel)


def tampil_tabel_jadwal(db):
    tabel = buat_tabel(["Dokter", "Spesialisasi", "Hari", "Jam Praktik"], ["Dokter", "Spesialisasi", "Jam Praktik"])
    for id_jadwal in db["jadwal"]:                        # [JSON] jadwal.json
        jadwal = db["jadwal"][id_jadwal]
        spesialisasi = "-"
        if jadwal["id_dokter"] in db["dokter"]:
            spesialisasi = db["dokter"][jadwal["id_dokter"]]["spesialisasi"]
        tabel.add_row([nama_dari(db["dokter"], jadwal["id_dokter"]), spesialisasi, jadwal["hari"], ", ".join(jadwal["jam"])])
    print(tabel)


def tampil_slot(tersedia):
    tabel = buat_tabel(["No", "Jam Tersedia"], [])
    nomor = 0
    for jam in tersedia:
        nomor = nomor + 1
        tabel.add_row([nomor, jam])
    print(tabel)



def tampil_pasien_ringkas(db):
    tabel = buat_tabel(["ID", "Nama Pasien", "No. HP"], ["Nama Pasien"])
    for id_pasien in db["pasien"]:                        
        tabel.add_row([id_pasien, db["pasien"][id_pasien]["nama"], db["pasien"][id_pasien]["no_hp"]])
    print(tabel)


def tampil_dokter_ringkas(db):
    tabel = buat_tabel(["ID", "Nama Dokter", "Spesialisasi"], ["Nama Dokter", "Spesialisasi"])
    for id_dokter in db["dokter"]:                       
        tabel.add_row([id_dokter, db["dokter"][id_dokter]["nama"], db["dokter"][id_dokter]["spesialisasi"]])
    print(tabel)


def pilih_slot(tersedia, hari, tanggal):
    """Menampilkan slot & meminta pilihan. Mengembalikan jam terpilih atau None."""
    print("\nSlot tersedia - " + hari + ", " + str(tanggal) + " :")
    tampil_slot(tersedia)
    pilih = ke_angka(input("Pilih nomor slot : ").strip())
    if pilih == None or pilih < 1 or pilih > len(tersedia):
        return None
    return tersedia[pilih - 1]



def lihat_jadwal_dokter(db):
    bersihkan_layar()
    judul("JADWAL PRAKTIK DOKTER")
    if len(db["jadwal"]) == 0:
        print(" Belum ada jadwal praktik.")
    else:
        tampil_tabel_jadwal(db)
    jeda()


def cek_slot_tersedia(db):
    bersihkan_layar()
    judul("CEK SLOT TERSEDIA")
    tampil_dokter_ringkas(db)
    id_dokter = input("ID dokter : ").strip()
    if id_dokter not in db["dokter"]:
        print("\n[!] Dokter dengan ID " + id_dokter + " tidak ditemukan.")
        jeda()
        return
    tanggal = parse_tanggal(input("Tanggal (YYYY-MM-DD) : ").strip())
    if tanggal == None:
        print("\n[!] Format tanggal salah. Contoh: 2026-11-12")
        jeda()
        return

    tersedia, hari = slot_tersedia(db, id_dokter, tanggal)
    print("\n" + db["dokter"][id_dokter]["nama"] + " - " + hari + ", " + str(tanggal))
    if len(tersedia) == 0:
        print("[!] Tidak ada slot tersedia (dokter tidak praktik / jadwal penuh).")
    else:
        tampil_slot(tersedia)
    jeda()



def buat_reservasi_manual(db, user):
    bersihkan_layar()
    judul("BUAT RESERVASI MANUAL")
    if len(db["pasien"]) == 0 or len(db["dokter"]) == 0:
        print(" Data pasien / dokter masih kosong.")
        jeda()
        return

    tampil_pasien_ringkas(db)
    id_pasien = input("ID pasien : ").strip()
    if id_pasien not in db["pasien"]:
        print("\n[!] Pasien dengan ID " + id_pasien + " tidak ditemukan.")
        jeda()
        return

    tampil_dokter_ringkas(db)
    id_dokter = input("ID dokter : ").strip()
    if id_dokter not in db["dokter"]:
        print("\n[!] Dokter dengan ID " + id_dokter + " tidak ditemukan.")
        jeda()
        return

    tanggal = parse_tanggal(input("Tanggal konsultasi (YYYY-MM-DD) : ").strip())
    if tanggal == None:
        print("\n[!] Format tanggal salah. Contoh: 2026-11-12")
        jeda()
        return
    if tanggal < date.today():
        print("\n[!] Tanggal sudah lewat, pilih hari ini atau setelahnya.")
        jeda()
        return

    tersedia, hari = slot_tersedia(db, id_dokter, tanggal)
    if len(tersedia) == 0:
        print("\n[!] Tidak ada slot tersedia pada hari " + hari + " (dokter tidak praktik / jadwal penuh).")
        jeda()
        return

    jam = pilih_slot(tersedia, hari, tanggal)
    if jam == None:
        print("\n[!] Pilihan slot tidak valid, reservasi dibatalkan.")
        jeda()
        return

    id_baru = buat_reservasi(db, id_pasien, id_dokter, tanggal, jam, user)
    print("\n[+] Reservasi berhasil dibuat. Nomor reservasi : " + id_baru)
    jeda()



def ubah_reservasi_pasien(db, user):
    bersihkan_layar()
    judul("UBAH RESERVASI")
    daftar = daftar_reservasi(db, ["Menunggu", "Dikonfirmasi"])
    if len(daftar) == 0:
        print(" Tidak ada reservasi yang dapat diubah.")
        jeda()
        return

    tampil_tabel_reservasi(db, daftar)
    id_res = input("ID reservasi yang diubah : ").strip()
    if id_res not in daftar:
        print("\n[!] ID tidak ada dalam daftar reservasi yang dapat diubah.")
        jeda()
        return

    data = db["reservasi"][id_res]
    tanggal_teks = input("Tanggal baru (YYYY-MM-DD, Enter = tetap " + data["tanggal"] + ") : ").strip()
    if tanggal_teks == "":
        tanggal = parse_tanggal(data["tanggal"])
    else:
        tanggal = parse_tanggal(tanggal_teks)
    if tanggal == None:
        print("\n[!] Format tanggal salah. Contoh: 2026-11-12")
        jeda()
        return
    if tanggal < date.today():
        print("\n[!] Tanggal sudah lewat, pilih hari ini atau setelahnya.")
        jeda()
        return

    tersedia, hari = slot_tersedia(db, data["id_dokter"], tanggal, id_res)
    if len(tersedia) == 0:
        print("\n[!] Tidak ada slot tersedia pada hari " + hari + ".")
        jeda()
        return

    jam = pilih_slot(tersedia, hari, tanggal)
    if jam == None:
        print("\n[!] Pilihan slot tidak valid, perubahan dibatalkan.")
        jeda()
        return

    ubah_jadwal(db, id_res, tanggal, jam, user)
    print("\n[+] Reservasi berhasil diubah.")
    jeda()


def batalkan_reservasi_pasien(db, user):
    bersihkan_layar()
    judul("BATALKAN RESERVASI")
    daftar = daftar_reservasi(db, ["Menunggu", "Dikonfirmasi"])
    if len(daftar) == 0:
        print(" Tidak ada reservasi yang dapat dibatalkan.")
        jeda()
        return

    tampil_tabel_reservasi(db, daftar)
    id_res = input("ID reservasi yang dibatalkan : ").strip()
    if id_res not in daftar:
        print("\n[!] ID tidak ada dalam daftar reservasi yang dapat dibatalkan.")
        jeda()
        return

    yakin = input("Yakin membatalkan reservasi " + id_res + " ? [y/n] : ").strip()
    if yakin == "y" or yakin == "Y":
        batalkan_reservasi(db, id_res, user)
        print("\n[+] Reservasi berhasil dibatalkan (slot kembali tersedia).")
    else:
        print("\n[*] Pembatalan dibatalkan.")
    jeda()



def konfirmasi_kedatangan(db, user):
    bersihkan_layar()
    judul("KONFIRMASI KEDATANGAN PASIEN")
    daftar = daftar_reservasi(db, ["Menunggu"])
    if len(daftar) == 0:
        print(" Tidak ada reservasi berstatus Menunggu.")
        jeda()
        return

    tampil_tabel_reservasi(db, daftar)
    id_res = input("ID reservasi pasien yang datang : ").strip()
    if id_res not in daftar:
        print("\n[!] ID tidak ada dalam daftar reservasi Menunggu.")
        jeda()
        return

    data = db["reservasi"][id_res]
    if data["tanggal"] != str(date.today()):
        print("\n[!] Tanggal reservasi (" + data["tanggal"] + ") bukan hari ini.")
        lanjut = input("Tetap konfirmasi kedatangan? [y/n] : ").strip()
        if lanjut != "y" and lanjut != "Y":
            print("\n[*] Konfirmasi dibatalkan.")
            jeda()
            return

    set_konfirmasi(db, id_res, user)
    print("\n[+] Kedatangan pasien dikonfirmasi.")
    jeda()



def kelola_status_reservasi(db, user):
    bersihkan_layar()
    judul("KELOLA STATUS RESERVASI")
    daftar = daftar_reservasi(db)
    if len(daftar) == 0:
        print(" Belum ada data reservasi.")
        jeda()
        return

    tampil_tabel_reservasi(db, daftar)
    id_res = input("ID reservasi : ").strip()
    if id_res not in daftar:
        print("\n[!] Reservasi dengan ID " + id_res + " tidak ditemukan.")
        jeda()
        return

    print("\nStatus saat ini : " + db["reservasi"][id_res]["status"])
    tabel = buat_tabel(["No", "Status"], ["Status"])
    for kunci in STATUS_RESERVASI:
        tabel.add_row([kunci, STATUS_RESERVASI[kunci]])
    print(tabel)
    pilih = input("Status baru [1-4] : ").strip()
    if pilih not in STATUS_RESERVASI:
        print("\n[!] Pilihan status tidak tersedia.")
        jeda()
        return

    berhasil, pesan = ubah_status(db, id_res, STATUS_RESERVASI[pilih], user)
    if berhasil:
        print("\n[+] " + pesan)
    else:
        print("\n[!] " + pesan)
    jeda()



def ambil_waktu(item):
    """Kunci pengurutan log: waktu perubahan."""
    return item[1]["waktu"]


def lihat_log_riwayat(db):
    bersihkan_layar()
    judul("LOG RIWAYAT JADWAL PASIEN")
    if len(db["log_riwayat"]) == 0:
        print(" Belum ada log riwayat.")
        jeda()
        return

    tampil_pasien_ringkas(db)
    filter_id = input("ID pasien (Enter = semua pasien) : ").strip()
    if filter_id != "" and filter_id not in db["pasien"]:
        print("\n[!] Pasien dengan ID " + filter_id + " tidak ditemukan.")
        jeda()
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
    jalan = True
    while jalan:
        bersihkan_layar()
        judul("KELOLA RESERVASI")
        tabel = buat_tabel(["No", "Menu"], ["Menu"])
        tabel.add_row([1, "Lihat jadwal praktik dokter"])
        tabel.add_row([2, "Cek slot tersedia (dokter & tanggal)"])
        tabel.add_row([3, "Buat reservasi manual"])
        tabel.add_row([4, "Ubah reservasi"])
        tabel.add_row([5, "Batalkan reservasi"])
        tabel.add_row([6, "Konfirmasi kedatangan pasien"])
        tabel.add_row([7, "Kelola status reservasi"])
        tabel.add_row([8, "Lihat log riwayat jadwal pasien"])
        tabel.add_row([0, "Kembali ke dashboard"])
        print(tabel)
        pilihan = input("Pilih menu [0-8] : ").strip()

        if pilihan == "1":
            lihat_jadwal_dokter(db)
        elif pilihan == "2":
            cek_slot_tersedia(db)
        elif pilihan == "3":
            buat_reservasi_manual(db, user)
        elif pilihan == "4":
            ubah_reservasi_pasien(db, user)
        elif pilihan == "5":
            batalkan_reservasi_pasien(db, user)
        elif pilihan == "6":
            konfirmasi_kedatangan(db, user)
        elif pilihan == "7":
            kelola_status_reservasi(db, user)
        elif pilihan == "8":
            lihat_log_riwayat(db)
        elif pilihan == "0":
            jalan = False
        else:
            print("\n[!] Pilihan tidak tersedia, pilih 0 sampai 8.")
            jeda()