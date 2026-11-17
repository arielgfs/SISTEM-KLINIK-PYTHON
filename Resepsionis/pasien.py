"""
=====================================================================
resepsionis/pasien.py
Fitur  : 1. Mendaftarkan pasien baru
         2. Melihat data pasien dan dokter
         + mengubah data pasien (CRUD Resepsionis)
Tabel JSON yang dipakai : pasien.json, dokter.json
=====================================================================
"""
from modules import database
from modules.utils import (bersihkan_layar, jeda, buat_tabel, judul,
                           format_rupiah, id_berikutnya)


def valid_no_hp(teks):
    return teks.isdigit() and 10 <= len(teks) <= 13


def no_hp_terpakai(db, no_hp, kecuali_id=None):
    for id_pasien in db["pasien"]:                        # [JSON] pasien.json
        if id_pasien != kecuali_id and db["pasien"][id_pasien]["no_hp"] == no_hp:
            return True
    return False


def tampil_tabel_pasien(db):
    tabel = buat_tabel(["ID", "Nama", "No. HP", "Alamat"], ["Nama", "Alamat"])
    for id_pasien in db["pasien"]:                        # [JSON] pasien.json
        data = db["pasien"][id_pasien]
        tabel.add_row([id_pasien, data["nama"], data["no_hp"], data["alamat"]])
    print(tabel)


def tampil_tabel_dokter(db):
    tabel = buat_tabel(["ID", "Nama Dokter", "Spesialisasi", "Biaya Jasa"], ["Nama Dokter", "Spesialisasi"])
    for id_dokter in db["dokter"]:                        # [JSON] dokter.json
        data = db["dokter"][id_dokter]
        tabel.add_row([id_dokter, data["nama"], data["spesialisasi"], format_rupiah(data["biaya_jasa"])])
    print(tabel)


def tambah_pasien(db, user):
    bersihkan_layar()
    judul("DAFTAR PASIEN BARU")
    nama = input("Nama lengkap : ").strip()
    if nama == "":
        print("\n[!] Nama tidak boleh kosong, data batal disimpan.")
        jeda()
        return

    no_hp = input("No. HP (10-13 angka) : ").strip()
    if valid_no_hp(no_hp) == False:
        print("\n[!] No. HP harus 10-13 digit angka, data batal disimpan.")
        jeda()
        return
    if no_hp_terpakai(db, no_hp):
        print("\n[!] No. HP sudah terdaftar atas pasien lain.")
        jeda()
        return

    alamat = input("Alamat : ").strip()
    if alamat == "":
        print("\n[!] Alamat tidak boleh kosong, data batal disimpan.")
        jeda()
        return

    id_baru = id_berikutnya(db["pasien"])
    db["pasien"][id_baru] = {"nama": nama, "no_hp": no_hp, "alamat": alamat}
    database.simpan(db, ["pasien"])                       # [JSON] simpan ke pasien.json
    print("\n[+] Pasien '" + nama + "' berhasil didaftarkan dengan ID " + id_baru + ".")
    jeda()


def ubah_pasien(db, user):
    bersihkan_layar()
    judul("UBAH DATA PASIEN")
    if len(db["pasien"]) == 0:
        print(" Belum ada data pasien.")
        jeda()
        return

    tampil_tabel_pasien(db)
    id_pasien = input("Masukkan ID pasien yang diubah : ").strip()
    if id_pasien not in db["pasien"]:
        print("\n[!] Pasien dengan ID " + id_pasien + " tidak ditemukan.")
        jeda()
        return

    data = db["pasien"][id_pasien]
    print("\n(kosongkan lalu Enter bila tidak ingin mengubah)")
    nama_baru = input("Nama [" + data["nama"] + "] : ").strip()
    no_hp_baru = input("No. HP [" + data["no_hp"] + "] : ").strip()
    alamat_baru = input("Alamat [" + data["alamat"] + "] : ").strip()

    if no_hp_baru != "":
        if valid_no_hp(no_hp_baru) == False:
            print("\n[!] No. HP harus 10-13 digit angka, perubahan dibatalkan.")
            jeda()
            return
        if no_hp_terpakai(db, no_hp_baru, id_pasien):
            print("\n[!] No. HP sudah terdaftar atas pasien lain, perubahan dibatalkan.")
            jeda()
            return
        data["no_hp"] = no_hp_baru
    if nama_baru != "":
        data["nama"] = nama_baru
    if alamat_baru != "":
        data["alamat"] = alamat_baru

    database.simpan(db, ["pasien"])                       # [JSON] simpan ke pasien.json
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
    jalan = True
    while jalan:
        bersihkan_layar()
        judul("KELOLA PASIEN")
        tabel = buat_tabel(["No", "Menu"], ["Menu"])
        tabel.add_row([1, "Daftarkan pasien baru"])
        tabel.add_row([2, "Ubah data pasien"])
        tabel.add_row([3, "Lihat data pasien"])
        tabel.add_row([4, "Lihat data dokter"])
        tabel.add_row([0, "Kembali ke dashboard"])
        print(tabel)
        pilihan = input("Pilih menu [0-4] : ").strip()

        if pilihan == "1":
            tambah_pasien(db, user)
        elif pilihan == "2":
            ubah_pasien(db, user)
        elif pilihan == "3":
            lihat_pasien(db)
        elif pilihan == "4":
            lihat_dokter(db)
        elif pilihan == "0":
            jalan = False
        else:
            print("\n[!] Pilihan tidak tersedia, pilih 0 sampai 4.")
            jeda()