from datetime import date
from modules import database
from modules.utils import (bersihkan_layar, jeda, judul, buat_tabel, ke_angka, format_rupiah, id_berikutnya, sekarang, nama_dari)
from modules.pembayaran import hitung_total
from modules.inventaris import stok_menipis
from resepsionis import pasien, struk
from resepsionis.pasien import pilih_menu, pilih_data, konfirmasi, tanya

STATUS_BAYAR = ["Belum Dibayar", "Menunggu Pembayaran", "Lunas"]
METODE_BAYAR = ["Tunai", "Transfer"]


def reservasi_siap_tagih(db):
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


def tambah_obat(db, id_trx, id_obat, jumlah, user):
    transaksi = db["transaksi"][id_trx]
    if transaksi["status_bayar"] == "Lunas":
        return False, "Transaksi sudah Lunas, obat tidak dapat ditambahkan."
    obat = db["obat"][id_obat]
    if obat["kedaluwarsa"] < str(date.today()):
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
    if stok_menipis(obat):
        pesan = pesan + "\n[!] PERINGATAN: stok " + obat["nama"] + " menipis (sisa " + str(obat["stok"]) + ")."
    return True, pesan


def set_status_bayar(db, id_trx, status, metode, user):
    transaksi = db["transaksi"][id_trx]
    transaksi["status_bayar"] = status
    transaksi["metode"] = metode
    transaksi["diproses_oleh"] = user
    if status == "Lunas":
        transaksi["waktu_bayar"] = sekarang()
    database.simpan(db, ["transaksi"])


def pilihan_transaksi(db, status_boleh):
    pilihan = []
    for id_trx in db["transaksi"]:
        data = db["transaksi"][id_trx]
        if data["status_bayar"] in status_boleh:
            pilihan.append((struk.nomor_transaksi(id_trx) + " | " + nama_dari(db["pasien"], data["id_pasien"])
                            + " | " + format_rupiah(data["total"]) + " | " + data["status_bayar"], id_trx))
    return pilihan


def tampil_tabel_obat(db):
    tabel = buat_tabel(["ID", "Nama Obat", "Kategori", "Harga", "Stok", "Kedaluwarsa"], ["Nama Obat", "Kategori"])
    for id_obat in db["obat"]:
        data = db["obat"][id_obat]
        tabel.add_row([id_obat, data["nama"], data["kategori"], format_rupiah(data["harga"]) + "/" + data["satuan"],
                       data["stok"], data["kedaluwarsa"]])
    print(tabel)


def tampil_rincian(db, id_trx):
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
        pasien.tampil_tabel_dokter(db)
    print("\n Harga obat :")
    if len(db["obat"]) == 0:
        print(" (belum ada data obat)")
    else:
        tampil_tabel_obat(db)
    jeda()


def input_obat_resep(db, id_trx, user):
    selesai = False
    while selesai == False:
        bersihkan_layar()
        judul("INPUT OBAT RESEP DOKTER")
        tampil_rincian(db, id_trx)

        pilihan = []
        for id_obat in db["obat"]:
            obat = db["obat"][id_obat]
            pilihan.append((obat["nama"] + " | " + format_rupiah(obat["harga"]) + "/" + obat["satuan"]
                            + " | stok " + str(obat["stok"]) + " | exp " + obat["kedaluwarsa"], id_obat))
        id_obat = pilih_data("Pilih obat resep", pilihan, "<< Selesai (tidak ada obat lagi)")

        if id_obat == None:
            selesai = True
        else:
            jumlah = ke_angka(tanya("Jumlah (" + db["obat"][id_obat]["satuan"] + ")"))
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
    pilihan = pilihan_transaksi(db, ["Belum Dibayar", "Menunggu Pembayaran"])
    if len(pilihan) == 0:
        print(" Tidak ada tagihan yang belum lunas.")
        jeda()
        return
    id_trx = pilih_data("Pilih tagihan", pilihan)
    if id_trx != None:
        input_obat_resep(db, id_trx, user)


def buat_tagihan(db, user):
    bersihkan_layar()
    judul("BUAT TAGIHAN")
    daftar = reservasi_siap_tagih(db)
    if len(daftar) == 0:
        print(" Tidak ada reservasi (Dikonfirmasi / Selesai) yang belum ditagih.")
        jeda()
        return

    pilihan = []
    for id_res in daftar:
        data = db["reservasi"][id_res]
        pilihan.append((id_res + " | " + nama_dari(db["pasien"], data["id_pasien"])
                        + " | " + nama_dari(db["dokter"], data["id_dokter"])
                        + " | " + data["tanggal"] + " " + data["jam"] + " | " + data["status"], id_res))
    id_res = pilih_data("Pilih reservasi yang ditagih", pilihan)
    if id_res == None:
        return

    res = db["reservasi"][id_res]
    if res["id_dokter"] not in db["dokter"]:
        print("\n[!] Data dokter reservasi ini sudah tidak ada, tagihan tidak dapat dibuat.")
        jeda()
        return

    biaya_jasa = db["dokter"][res["id_dokter"]]["biaya_jasa"]
    id_trx = id_berikutnya(db["transaksi"])
    db["transaksi"][id_trx] = {
        "id_reservasi": id_res, "id_pasien": res["id_pasien"], "id_dokter": res["id_dokter"],
        "biaya_jasa": biaya_jasa, "obat": [], "total": biaya_jasa,
        "status_bayar": "Belum Dibayar", "metode": "", "tanggal": str(date.today()),
        "waktu_bayar": "", "dibuat_oleh": user, "diproses_oleh": ""
    }
    database.simpan(db, ["transaksi"])
    print("\n[+] Tagihan " + struk.nomor_transaksi(id_trx) + " dibuat (jasa dokter " + format_rupiah(biaya_jasa) + ").")

    if konfirmasi("Dokter memberikan resep obat?"):
        input_obat_resep(db, id_trx, user)

    hitung_total(db["transaksi"][id_trx])
    database.simpan(db, ["transaksi"])
    bersihkan_layar()
    judul("TAGIHAN BERHASIL DIBUAT")
    tampil_rincian(db, id_trx)
    jeda()


def lihat_daftar_tagihan(db):
    bersihkan_layar()
    judul("DAFTAR TAGIHAN & RIWAYAT TRANSAKSI")
    pilihan = pilihan_transaksi(db, STATUS_BAYAR)
    if len(pilihan) == 0:
        print(" Belum ada tagihan.")
        jeda()
        return

    tabel = buat_tabel(["ID", "No. Transaksi", "Pasien", "Dokter", "Tanggal", "Total", "Status"], ["Pasien", "Dokter", "Status"])
    for id_trx in db["transaksi"]:
        data = db["transaksi"][id_trx]
        tabel.add_row([id_trx, struk.nomor_transaksi(id_trx), nama_dari(db["pasien"], data["id_pasien"]),
                       nama_dari(db["dokter"], data["id_dokter"]), data["tanggal"],
                       format_rupiah(data["total"]), data["status_bayar"]])
    print(tabel)

    id_trx = pilih_data("Pilih tagihan untuk melihat rincian", pilihan, "<< Kembali")
    if id_trx != None:
        print("")
        tampil_rincian(db, id_trx)
        jeda()


def proses_pembayaran(db, user):
    bersihkan_layar()
    judul("PROSES PEMBAYARAN")
    pilihan = pilihan_transaksi(db, ["Belum Dibayar", "Menunggu Pembayaran"])
    if len(pilihan) == 0:
        print(" Tidak ada tagihan yang belum lunas.")
        jeda()
        return

    id_trx = pilih_data("Pilih tagihan yang dibayar", pilihan)
    if id_trx == None:
        return

    print("")
    tampil_rincian(db, id_trx)
    total = db["transaksi"][id_trx]["total"]
    pilihan_metode = []
    for metode in METODE_BAYAR:
        pilihan_metode.append((metode, metode))
    metode = pilih_data("Pilih metode pembayaran", pilihan_metode)
    if metode == None:
        return

    status = "Lunas"
    kembalian = 0
    if metode == "Tunai":
        uang = ke_angka(tanya("Uang diterima (Rp, angka saja)"))
        if uang == None or uang < total:
            print("\n[!] Uang kurang / tidak valid. Pembayaran belum diproses.")
            jeda()
            return
        kembalian = uang - total
    else:
        if konfirmasi("Bukti transfer sudah diterima?") == False:
            status = "Menunggu Pembayaran"

    set_status_bayar(db, id_trx, status, metode, user)
    if status == "Lunas":
        print("\n[+] Pembayaran LUNAS (" + metode + ").")
        if kembalian > 0:
            print("    Kembalian : " + format_rupiah(kembalian))
        if konfirmasi("Cetak struk sekarang?"):
            struk.tampil_dan_simpan(db, id_trx)
            return
    else:
        print("\n[*] Status pembayaran: Menunggu Pembayaran (menunggu bukti transfer).")
    jeda()


def ubah_status_pembayaran(db, user):
    bersihkan_layar()
    judul("UBAH STATUS PEMBAYARAN")
    print(" (transaksi yang sudah Lunas tidak dapat diubah lagi)")
    pilihan = pilihan_transaksi(db, ["Belum Dibayar", "Menunggu Pembayaran"])
    if len(pilihan) == 0:
        print(" Tidak ada tagihan yang belum lunas.")
        jeda()
        return

    id_trx = pilih_data("Pilih tagihan", pilihan)
    if id_trx == None:
        return

    pilihan_status = []
    for status in STATUS_BAYAR:
        pilihan_status.append((status, status))
    status_baru = pilih_data("Pilih status baru (saat ini: " + db["transaksi"][id_trx]["status_bayar"] + ")", pilihan_status)
    if status_baru == None:
        return
    if status_baru == db["transaksi"][id_trx]["status_bayar"]:
        print("\n[*] Status tidak berubah.")
        jeda()
        return

    metode = ""
    if status_baru != "Belum Dibayar":
        pilihan_metode = []
        for nama_metode in METODE_BAYAR:
            pilihan_metode.append((nama_metode, nama_metode))
        metode = pilih_data("Pilih metode pembayaran", pilihan_metode)
        if metode == None:
            return

    set_status_bayar(db, id_trx, status_baru, metode, user)
    print("\n[+] Status pembayaran diubah menjadi: " + status_baru)
    jeda()


def menu_pembayaran(db, user):
    daftar_menu = [
        "Lihat Harga Jasa Dokter & Obat",
        "Buat Tagihan (Jasa + Obat Resep)",
        "Tambah Obat Resep ke Tagihan",
        "Lihat Daftar Tagihan",
        "Proses Pembayaran",
        "Ubah Status Pembayaran",
        "Cetak Struk Pembayaran",
        "Kembali ke Dashboard"
    ]
    jalan = True
    while jalan:
        bersihkan_layar()
        judul("KELOLA PEMBAYARAN")
        pilihan = pilih_menu("Pilih menu (panah atas/bawah, Enter untuk memilih)", daftar_menu)

        if pilihan == "Lihat Harga Jasa Dokter & Obat":
            lihat_harga(db)
        elif pilihan == "Buat Tagihan (Jasa + Obat Resep)":
            buat_tagihan(db, user)
        elif pilihan == "Tambah Obat Resep ke Tagihan":
            tambah_obat_ke_tagihan(db, user)
        elif pilihan == "Lihat Daftar Tagihan":
            lihat_daftar_tagihan(db)
        elif pilihan == "Proses Pembayaran":
            proses_pembayaran(db, user)
        elif pilihan == "Ubah Status Pembayaran":
            ubah_status_pembayaran(db, user)
        elif pilihan == "Cetak Struk Pembayaran":
            struk.menu_struk(db, user)
        elif pilihan == "Kembali ke Dashboard":
            jalan = False
