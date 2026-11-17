"""
=====================================================================
resepsionis/pembayaran.py
Tabel JSON : transaksi.json, reservasi.json, obat.json, pasien.json, dokter.json
=====================================================================
"""
from datetime import date
from modules import database
from modules.utils import (bersihkan_layar, jeda, ke_angka, buat_tabel, judul, format_rupiah,
                           id_berikutnya, sekarang, nama_dari)
from resepsionis import reservasi, struk

STATUS_BAYAR = {"1": "Belum Dibayar", "2": "Menunggu Pembayaran", "3": "Lunas"}
METODE_BAYAR = {"1": "Tunai", "2": "Transfer"}
STOK_MINIMUM = 5          



def hitung_total(transaksi):
    """Total = biaya jasa dokter + jumlah semua subtotal obat. Hasil juga disimpan di transaksi."""
    total = transaksi["biaya_jasa"]
    for item in transaksi["obat"]:
        total = total + item["subtotal"]
    transaksi["total"] = total
    return total



def reservasi_siap_tagih(db):
    """ID reservasi berstatus Dikonfirmasi / Selesai yang belum punya tagihan."""
    sudah = []
    for id_trx in db["transaksi"]:                        
        sudah.append(db["transaksi"][id_trx]["id_reservasi"])
    daftar = []
    for id_res in db["reservasi"]:                        
        if db["reservasi"][id_res]["status"] in ("Dikonfirmasi", "Selesai") and id_res not in sudah:
            daftar.append(id_res)
    return daftar


def buat_transaksi(db, id_res, user):
    """Membuat tagihan baru. Mengembalikan (id_transaksi atau None, pesan)."""
    res = db["reservasi"][id_res]
    if res["id_dokter"] not in db["dokter"]:
        return None, "Data dokter reservasi ini sudah tidak ada, tagihan tidak dapat dibuat."
    biaya_jasa = db["dokter"][res["id_dokter"]]["biaya_jasa"]     
    id_trx = id_berikutnya(db["transaksi"])
    db["transaksi"][id_trx] = {
        "id_reservasi": id_res, "id_pasien": res["id_pasien"], "id_dokter": res["id_dokter"],
        "biaya_jasa": biaya_jasa, "obat": [], "total": biaya_jasa,
        "status_bayar": "Belum Dibayar", "metode": "", "tanggal": str(date.today()),
        "waktu_bayar": "", "dibuat_oleh": user, "diproses_oleh": ""
    }
    database.simpan(db, ["transaksi"])                    
    return id_trx, "Tagihan " + struk.nomor_transaksi(id_trx) + " dibuat (jasa dokter " + format_rupiah(biaya_jasa) + ")."


def obat_kedaluwarsa(obat):
    return obat["kedaluwarsa"] < str(date.today())


def tambah_obat(db, id_trx, id_obat, jumlah, user):
    """Menambah obat resep ke tagihan. Stok obat berkurang otomatis.
    Mengembalikan (berhasil, pesan)."""
    transaksi = db["transaksi"][id_trx]
    if transaksi["status_bayar"] == "Lunas":
        return False, "Transaksi sudah Lunas, obat tidak dapat ditambahkan."
    if id_obat not in db["obat"]:                         
        return False, "Obat dengan ID " + id_obat + " tidak ditemukan."
    obat = db["obat"][id_obat]
    if obat_kedaluwarsa(obat):
        return False, "Obat '" + obat["nama"] + "' sudah kedaluwarsa, tidak boleh diberikan."
    if jumlah < 1:
        return False, "Jumlah harus lebih dari 0."
    if jumlah > obat["stok"]:
        return False, "Stok tidak cukup. Stok tersedia : " + str(obat["stok"])


    item = None
    for baris in transaksi["obat"]:
        if baris["id_obat"] == id_obat:
            item = baris
    if item == None:
        item = {"id_obat": id_obat, "nama": obat["nama"], "satuan": obat["satuan"],
                "jumlah": 0, "harga_satuan": obat["harga"], "subtotal": 0}
        transaksi["obat"].append(item)
    item["jumlah"] = item["jumlah"] + jumlah
    item["subtotal"] = item["jumlah"] * item["harga_satuan"]

    obat["stok"] = obat["stok"] - jumlah                  
    hitung_total(transaksi)
    database.simpan(db, ["transaksi", "obat"])           
    pesan = obat["nama"] + " x" + str(jumlah) + " ditambahkan ke tagihan."
    if obat["stok"] <= STOK_MINIMUM:
        pesan = pesan + "\n[!] PERINGATAN: stok " + obat["nama"] + " menipis (sisa " + str(obat["stok"]) + ")."
    return True, pesan



def set_status_bayar(db, id_trx, status, metode, user):
    """Memperbarui status pembayaran (dipakai proses bayar & ubah status)."""
    transaksi = db["transaksi"][id_trx]
    transaksi["status_bayar"] = status
    transaksi["metode"] = metode
    transaksi["diproses_oleh"] = user
    if status == "Lunas":
        transaksi["waktu_bayar"] = sekarang()
    database.simpan(db, ["transaksi"])                    



def tampil_tabel_dokter_harga(db):
    tabel = buat_tabel(["ID", "Nama Dokter", "Spesialisasi", "Biaya Jasa"], ["Nama Dokter", "Spesialisasi"])
    for id_dokter in db["dokter"]:                        
        data = db["dokter"][id_dokter]
        tabel.add_row([id_dokter, data["nama"], data["spesialisasi"], format_rupiah(data["biaya_jasa"])])
    print(tabel)


def tampil_tabel_obat(db):
    tabel = buat_tabel(["ID", "Nama Obat", "Kategori", "Harga", "Stok", "Kedaluwarsa"], ["Nama Obat", "Kategori"])
    for id_obat in db["obat"]:                            
        data = db["obat"][id_obat]
        tabel.add_row([id_obat, data["nama"], data["kategori"], format_rupiah(data["harga"]) + "/" + data["satuan"],
                       data["stok"], data["kedaluwarsa"]])
    print(tabel)


def daftar_transaksi(db, hanya_belum_lunas=False):
    daftar = []
    for id_trx in db["transaksi"]:
        if hanya_belum_lunas == False or db["transaksi"][id_trx]["status_bayar"] != "Lunas":
            daftar.append(id_trx)
    return daftar


def tampil_tabel_transaksi(db, daftar):
    tabel = buat_tabel(["ID", "No. Transaksi", "Pasien", "Dokter", "Tanggal", "Total", "Status"],
                       ["Pasien", "Dokter", "Status"])
    for id_trx in daftar:
        data = db["transaksi"][id_trx]
        tabel.add_row([id_trx, struk.nomor_transaksi(id_trx), nama_dari(db["pasien"], data["id_pasien"]),
                       nama_dari(db["dokter"], data["id_dokter"]), data["tanggal"],
                       format_rupiah(data["total"]), data["status_bayar"]])
    print(tabel)


def tampil_rincian(db, id_trx):
    """Rincian tagihan: jasa dokter + obat + total."""
    data = db["transaksi"][id_trx]
    print(" No. Transaksi : " + struk.nomor_transaksi(id_trx))
    print(" Pasien        : " + nama_dari(db["pasien"], data["id_pasien"]))
    print(" Dokter        : " + nama_dari(db["dokter"], data["id_dokter"]))
    tabel = buat_tabel(["No", "Keterangan", "Jumlah", "Harga Satuan", "Subtotal"], ["Keterangan"])
    tabel.add_row([1, "Jasa konsultasi dokter", 1, format_rupiah(data["biaya_jasa"]), format_rupiah(data["biaya_jasa"])])
    nomor = 1
    for item in data["obat"]:
        nomor = nomor + 1
        tabel.add_row([nomor, item["nama"], str(item["jumlah"]) + " " + item["satuan"],
                       format_rupiah(item["harga_satuan"]), format_rupiah(item["subtotal"])])
    print(tabel)
    print(" TOTAL PEMBAYARAN : " + format_rupiah(data["total"]))
    print(" Status pembayaran: " + data["status_bayar"])



def lihat_harga(db):
    bersihkan_layar()
    judul("HARGA JASA DOKTER & HARGA OBAT")
    print(" Biaya jasa dokter :")
    if len(db["dokter"]) == 0:
        print(" (belum ada data dokter)")
    else:
        tampil_tabel_dokter_harga(db)
    print("\n Harga obat :")
    if len(db["obat"]) == 0:
        print(" (belum ada data obat)")
    else:
        tampil_tabel_obat(db)
    jeda()



def input_obat_resep(db, id_trx, user):
    """Loop input obat sesuai resep dokter. Stok berkurang otomatis."""
    selesai = False
    while selesai == False:
        bersihkan_layar()
        judul("INPUT OBAT RESEP DOKTER")
        tampil_rincian(db, id_trx)
        print("\n Daftar obat :")
        tampil_tabel_obat(db)
        id_obat = input("ID obat (0 = selesai) : ").strip()

        if id_obat == "0":
            selesai = True
        elif id_obat not in db["obat"]:
            print("\n[!] Obat dengan ID " + id_obat + " tidak ditemukan.")
            jeda("Tekan Enter...")
        else:
            jumlah = ke_angka(input("Jumlah (" + db["obat"][id_obat]["satuan"] + ") : ").strip())
            if jumlah == None:
                print("\n[!] Jumlah harus berupa angka.")
            else:
                berhasil, pesan = tambah_obat(db, id_trx, id_obat, jumlah, user)
                if berhasil:
                    print("\n[+] " + pesan)
                else:
                    print("\n[!] " + pesan)
            jeda("Tekan Enter...")


def tambah_obat_ke_tagihan(db, user):
    bersihkan_layar()
    judul("TAMBAH OBAT RESEP KE TAGIHAN")
    daftar = daftar_transaksi(db, True)
    if len(daftar) == 0:
        print(" Tidak ada tagihan yang belum lunas.")
        jeda()
        return
    tampil_tabel_transaksi(db, daftar)
    id_trx = input("ID transaksi : ").strip()
    if id_trx not in daftar:
        print("\n[!] ID tidak ada dalam daftar tagihan belum lunas.")
        jeda()
        return
    input_obat_resep(db, id_trx, user)



def buat_tagihan(db, user):
    bersihkan_layar()
    judul("BUAT TAGIHAN")
    daftar = reservasi_siap_tagih(db)
    if len(daftar) == 0:
        print(" Tidak ada reservasi (Dikonfirmasi / Selesai) yang belum ditagih.")
        jeda()
        return

    reservasi.tampil_tabel_reservasi(db, daftar)
    id_res = input("ID reservasi yang ditagih : ").strip()
    if id_res not in daftar:
        print("\n[!] ID tidak ada dalam daftar reservasi yang siap ditagih.")
        jeda()
        return

    id_trx, pesan = buat_transaksi(db, id_res, user)
    if id_trx == None:
        print("\n[!] " + pesan)
        jeda()
        return
    print("\n[+] " + pesan)

    ada_resep = input("Dokter memberikan resep obat? [y/n] : ").strip()
    if ada_resep == "y" or ada_resep == "Y":
        input_obat_resep(db, id_trx, user)

    bersihkan_layar()
    judul("TAGIHAN BERHASIL DIBUAT")
    tampil_rincian(db, id_trx)
    jeda()


def lihat_daftar_tagihan(db):
    bersihkan_layar()
    judul("DAFTAR TAGIHAN & RIWAYAT TRANSAKSI")
    daftar = daftar_transaksi(db)
    if len(daftar) == 0:
        print(" Belum ada tagihan.")
        jeda()
        return
    tampil_tabel_transaksi(db, daftar)
    id_trx = input("\nID transaksi untuk lihat rincian (Enter = kembali) : ").strip()
    if id_trx != "":
        if id_trx in db["transaksi"]:
            print("")
            tampil_rincian(db, id_trx)
        else:
            print("\n[!] ID transaksi tidak ditemukan.")
        jeda()



def pilih_metode():
    tabel = buat_tabel(["No", "Metode Pembayaran"], ["Metode Pembayaran"])
    for kunci in METODE_BAYAR:
        tabel.add_row([kunci, METODE_BAYAR[kunci]])
    print(tabel)
    pilih = input("Metode [1/2] : ").strip()
    if pilih in METODE_BAYAR:
        return METODE_BAYAR[pilih]
    return None


def proses_pembayaran(db, user):
    bersihkan_layar()
    judul("PROSES PEMBAYARAN")
    daftar = daftar_transaksi(db, True)
    if len(daftar) == 0:
        print(" Tidak ada tagihan yang belum lunas.")
        jeda()
        return

    tampil_tabel_transaksi(db, daftar)
    id_trx = input("ID transaksi yang dibayar : ").strip()
    if id_trx not in daftar:
        print("\n[!] ID tidak ada dalam daftar tagihan belum lunas.")
        jeda()
        return

    print("")
    tampil_rincian(db, id_trx)
    total = db["transaksi"][id_trx]["total"]
    metode = pilih_metode()
    if metode == None:
        print("\n[!] Metode pembayaran tidak tersedia.")
        jeda()
        return

    status = "Lunas"
    kembalian = 0
    if metode == "Tunai":
        uang = ke_angka(input("Uang diterima : Rp").strip())
        if uang == None or uang < total:
            print("\n[!] Uang kurang / tidak valid. Pembayaran belum diproses.")
            jeda()
            return
        kembalian = uang - total
    else:
        bukti = input("Bukti transfer sudah diterima? [y/n] : ").strip()
        if bukti != "y" and bukti != "Y":
            status = "Menunggu Pembayaran"

    set_status_bayar(db, id_trx, status, metode, user)

    if status == "Lunas":
        print("\n[+] Pembayaran LUNAS (" + metode + ").")
        if kembalian > 0:
            print("    Kembalian : " + format_rupiah(kembalian))
        cetak = input("\nCetak struk sekarang? [y/n] : ").strip()
        if cetak == "y" or cetak == "Y":
            struk.tampil_dan_simpan(db, id_trx)
            return
    else:
        print("\n[*] Status pembayaran: Menunggu Pembayaran (menunggu bukti transfer).")
    jeda()


def ubah_status_pembayaran(db, user):
    bersihkan_layar()
    judul("UBAH STATUS PEMBAYARAN")
    print(" (transaksi yang sudah Lunas tidak dapat diubah lagi)")
    daftar = daftar_transaksi(db, True)
    if len(daftar) == 0:
        print(" Tidak ada tagihan yang belum lunas.")
        jeda()
        return

    tampil_tabel_transaksi(db, daftar)
    id_trx = input("ID transaksi : ").strip()
    if id_trx not in daftar:
        print("\n[!] ID tidak ada dalam daftar tagihan belum lunas.")
        jeda()
        return

    print("\nStatus saat ini : " + db["transaksi"][id_trx]["status_bayar"])
    tabel = buat_tabel(["No", "Status Pembayaran"], ["Status Pembayaran"])
    for kunci in STATUS_BAYAR:
        tabel.add_row([kunci, STATUS_BAYAR[kunci]])
    print(tabel)
    pilih = input("Status baru [1-3] : ").strip()
    if pilih not in STATUS_BAYAR:
        print("\n[!] Pilihan status tidak tersedia.")
        jeda()
        return

    status_baru = STATUS_BAYAR[pilih]
    if status_baru == db["transaksi"][id_trx]["status_bayar"]:
        print("\n[*] Status tidak berubah.")
        jeda()
        return

    metode = ""
    if status_baru != "Belum Dibayar":                   
        metode = pilih_metode()
        if metode == None:
            print("\n[!] Metode pembayaran tidak tersedia, perubahan dibatalkan.")
            jeda()
            return

    set_status_bayar(db, id_trx, status_baru, metode, user)
    print("\n[+] Status pembayaran diubah menjadi: " + status_baru)
    jeda()


def menu_pembayaran(db, user):
    jalan = True
    while jalan:
        bersihkan_layar()
        judul("KELOLA PEMBAYARAN")
        tabel = buat_tabel(["No", "Menu"], ["Menu"])
        tabel.add_row([1, "Lihat harga jasa dokter & harga obat"])
        tabel.add_row([2, "Buat tagihan (jasa dokter + obat resep + total)"])
        tabel.add_row([3, "Tambah obat resep ke tagihan"])
        tabel.add_row([4, "Lihat daftar tagihan & riwayat transaksi"])
        tabel.add_row([5, "Proses pembayaran"])
        tabel.add_row([6, "Ubah status pembayaran"])
        tabel.add_row([7, "Cetak struk pembayaran"])
        tabel.add_row([0, "Kembali ke dashboard"])
        print(tabel)
        pilihan = input("Pilih menu [0-7] : ").strip()

        if pilihan == "1":
            lihat_harga(db)
        elif pilihan == "2":
            buat_tagihan(db, user)
        elif pilihan == "3":
            tambah_obat_ke_tagihan(db, user)
        elif pilihan == "4":
            lihat_daftar_tagihan(db)
        elif pilihan == "5":
            proses_pembayaran(db, user)
        elif pilihan == "6":
            ubah_status_pembayaran(db, user)
        elif pilihan == "7":
            struk.menu_struk(db, user)
        elif pilihan == "0":
            jalan = False
        else:
            print("\n[!] Pilihan tidak tersedia, pilih 0 sampai 7.")
            jeda()