import inquirer
from modules import database
from modules.utils import (bersihkan_layar, jeda, judul, buat_tabel, format_rupiah, id_berikutnya)


def pilih_menu(pesan, daftar_menu):
    jawaban = inquirer.prompt([inquirer.List("menu", message=pesan, choices=daftar_menu)])
    if jawaban == None:
        return daftar_menu[-1]
    return jawaban["menu"]


def pilih_data(pesan, pilihan, label_batal="<< Batal"):
    daftar = list(pilihan)
    daftar.append((label_batal, None))
    jawaban = inquirer.prompt([inquirer.List("data", message=pesan, choices=daftar)])
    if jawaban == None:
        return None
    return jawaban["data"]


def konfirmasi(pesan):
    jawaban = inquirer.prompt([inquirer.Confirm("ya", message=pesan, default=False)])
    if jawaban == None:
        return False
    return jawaban["ya"]


def tanya(pesan, awal=""):
    if awal == "":
        pertanyaan = inquirer.Text("isi", message=pesan)
    else:
        pertanyaan = inquirer.Text("isi", message=pesan, default=awal)
    jawaban = inquirer.prompt([pertanyaan])
    if jawaban == None:
        return ""
    return jawaban["isi"].strip()


def valid_no_hp(teks):
    return teks.isdigit() and 10 <= len(teks) <= 13


def no_hp_terpakai(db, no_hp, kecuali_id=None):
    for id_pasien in db["pasien"]:
        if id_pasien != kecuali_id and db["pasien"][id_pasien]["no_hp"] == no_hp:
            return True
    return False


def pilihan_pasien(db):
    pilihan = []
    for id_pasien in db["pasien"]:
        data = db["pasien"][id_pasien]
        pilihan.append((id_pasien + " | " + data["nama"] + " | " + data["no_hp"], id_pasien))
    return pilihan


def pilihan_dokter(db):
    pilihan = []
    for id_dokter in db["dokter"]:
        data = db["dokter"][id_dokter]
        pilihan.append((id_dokter + " | " + data["nama"] + " | " + data["spesialisasi"]
                        + " | " + format_rupiah(data["biaya_jasa"]), id_dokter))
    return pilihan


def tampil_tabel_pasien(db):
    tabel = buat_tabel(["ID", "Nama", "No. HP", "Alamat"], ["Nama", "Alamat"])
    for id_pasien in db["pasien"]:
        data = db["pasien"][id_pasien]
        tabel.add_row([id_pasien, data["nama"], data["no_hp"], data["alamat"]])
    print(tabel)


def tampil_tabel_dokter(db):
    tabel = buat_tabel(["ID", "Nama Dokter", "Spesialisasi", "Biaya Jasa"], ["Nama Dokter", "Spesialisasi"])
    for id_dokter in db["dokter"]:
        data = db["dokter"][id_dokter]
        tabel.add_row([id_dokter, data["nama"], data["spesialisasi"], format_rupiah(data["biaya_jasa"])])
    print(tabel)


def tambah_pasien(db, user):
    bersihkan_layar()
    judul("DAFTAR PASIEN BARU")
    nama = tanya("Nama lengkap")
    if nama == "":
        print("\n[!] Nama tidak boleh kosong, data batal disimpan.")
        jeda()
        return

    no_hp = tanya("No. HP (10-13 angka)")
    if valid_no_hp(no_hp) == False:
        print("\n[!] No. HP harus 10-13 digit angka, data batal disimpan.")
        jeda()
        return
    if no_hp_terpakai(db, no_hp):
        print("\n[!] No. HP sudah terdaftar atas pasien lain.")
        jeda()
        return

    alamat = tanya("Alamat")
    if alamat == "":
        print("\n[!] Alamat tidak boleh kosong, data batal disimpan.")
        jeda()
        return

    id_baru = id_berikutnya(db["pasien"])
    db["pasien"][id_baru] = {"nama": nama, "no_hp": no_hp, "alamat": alamat}
    database.simpan(db, ["pasien"])
    print("\n[+] Pasien '" + nama + "' berhasil didaftarkan dengan ID " + id_baru + ".")
    jeda()


def ubah_pasien(db, user):
    bersihkan_layar()
    judul("UBAH DATA PASIEN")
    if len(db["pasien"]) == 0:
        print(" Belum ada data pasien.")
        jeda()
        return

    id_pasien = pilih_data("Pilih pasien yang diubah", pilihan_pasien(db))
    if id_pasien == None:
        return

    data = db["pasien"][id_pasien]
    print("(tekan Enter bila tidak ingin mengubah isian)")
    nama_baru = tanya("Nama", data["nama"])
    no_hp_baru = tanya("No. HP", data["no_hp"])
    alamat_baru = tanya("Alamat", data["alamat"])

    if nama_baru == "" or alamat_baru == "":
        print("\n[!] Nama dan alamat tidak boleh kosong, perubahan dibatalkan.")
    elif valid_no_hp(no_hp_baru) == False:
        print("\n[!] No. HP harus 10-13 digit angka, perubahan dibatalkan.")
    elif no_hp_terpakai(db, no_hp_baru, id_pasien):
        print("\n[!] No. HP sudah terdaftar atas pasien lain, perubahan dibatalkan.")
    else:
        data["nama"] = nama_baru
        data["no_hp"] = no_hp_baru
        data["alamat"] = alamat_baru
        database.simpan(db, ["pasien"])
        print("\n[+] Data pasien berhasil diubah.")
    jeda()


def lihat_pasien(db):
    bersihkan_layar()
    judul("DATA PASIEN")
    if len(db["pasien"]) == 0:
        print(" Belum ada data pasien.")
    else:
        tampil_tabel_pasien(db)
        print(" Total pasien : " + str(len(db["pasien"])))
    jeda()


def lihat_dokter(db):
    bersihkan_layar()
    judul("DATA DOKTER")
    if len(db["dokter"]) == 0:
        print(" Belum ada data dokter.")
    else:
        tampil_tabel_dokter(db)
        print(" Total dokter : " + str(len(db["dokter"])))
    jeda()


def menu_pasien(db, user):
    daftar_menu = [
        "Daftarkan Pasien Baru",
        "Ubah Data Pasien",
        "Lihat Data Pasien",
        "Lihat Data Dokter",
        "Kembali ke Dashboard"
    ]
    jalan = True
    while jalan:
        bersihkan_layar()
        judul("KELOLA PASIEN")
        pilihan = pilih_menu("Pilih menu (panah atas/bawah, Enter untuk memilih)", daftar_menu)

        if pilihan == "Daftarkan Pasien Baru":
            tambah_pasien(db, user)
        elif pilihan == "Ubah Data Pasien":
            ubah_pasien(db, user)
        elif pilihan == "Lihat Data Pasien":
            lihat_pasien(db)
        elif pilihan == "Lihat Data Dokter":
            lihat_dokter(db)
        elif pilihan == "Kembali ke Dashboard":
            jalan = False
