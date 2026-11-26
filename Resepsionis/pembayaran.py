from datetime import date

from modules import database
from modules.inventaris import obat_kedaluwarsa, stok_menipis
from modules.pembayaran import STATUS_BELUM_DITAGIH, hitung_total, transaksi_reservasi
from modules.reservasi import catat_log_inventaris, tampilkan_reservasi
from modules.utils import (
    format_rupiah, id_berikutnya, ke_angka, konfirmasi, nama_dari, pilih_id, sekarang, tampilkan_tabel
)
from resepsionis import struk
from resepsionis.pasien import tampil_tabel_obat

METODE_BAYAR = ("Tunai", "Transfer")


def input_obat_resep(db, user):
    """Input_Obat_Resep: simpan obat ke detail transaksi, kurangi stok, catat log obat."""
    if len(db["reservasi"]) > 0:
        tampilkan_reservasi(db, list(db["reservasi"]), "DAFTAR RESERVASI")

    id_res = pilih_id(db["reservasi"], "ID reservasi: ")

    if id_res is None or db["reservasi"][id_res]["status"] == "Dibatalkan":
        print("Reservasi tidak ditemukan")
        return

    id_trx = transaksi_reservasi(db, id_res)

    if id_trx is not None and db["transaksi"][id_trx]["status_bayar"] != STATUS_BELUM_DITAGIH:
        print("Tagihan reservasi ini sudah dibuat, obat tidak dapat ditambahkan")
        return

    if len(db["obat"]) == 0:
        print("Data obat belum tersedia")
        return

    tampil_tabel_obat(db)
    id_obat = pilih_id(db["obat"], "Nomor (ID) obat: ")
    jumlah = ke_angka(input("Jumlah: "))

    if id_obat is None or jumlah is None or jumlah <= 0:
        print("Obat tidak ada, jumlah <= 0, atau stok kurang")
        return

    obat = db["obat"][id_obat]

    if jumlah > obat["stok"] or obat_kedaluwarsa(obat):
        print("Obat tidak ada, jumlah <= 0, atau stok kurang (atau obat sudah kedaluwarsa)")
        return

    res = db["reservasi"][id_res]

    if id_trx is None:
        id_trx = id_berikutnya(db["transaksi"])
        db["transaksi"][id_trx] = {
            "id_reservasi": id_res, "id_pasien": res["id_pasien"], "id_dokter": res["id_dokter"],
            "biaya_jasa": 0, "obat": [], "total": 0,
            "status_bayar": STATUS_BELUM_DITAGIH, "metode": "", "tanggal": str(date.today()),
            "waktu_bayar": "", "dibuat_oleh": user, "diproses_oleh": ""
        }

    transaksi = db["transaksi"][id_trx]
    item = next((b for b in transaksi["obat"] if b["id_obat"] == id_obat), None)

    if item is None:
        item = {"id_obat": id_obat, "nama": obat["nama"], "satuan": obat["satuan"],
                "jumlah": 0, "harga_satuan": obat["harga"], "subtotal": 0}
        transaksi["obat"].append(item)

    item["jumlah"] += jumlah
    item["subtotal"] = item["jumlah"] * item["harga_satuan"]
    hitung_total(transaksi)

    obat["stok"] -= jumlah
    catat_log_inventaris(db, "obat", id_obat, obat["nama"], "PAKAI",
                         str(jumlah) + " " + obat["satuan"] + " untuk reservasi " + id_res, user, jumlah)
    database.simpan(db, ["transaksi", "obat", "log_riwayat"])

    print("Obat berhasil dicatat: " + obat["nama"] + " x" + str(jumlah))
    if stok_menipis(obat):
        print("[!] PERINGATAN: stok " + obat["nama"] + " menipis (sisa " + str(obat["stok"]) + ")")


def buat_tagihan(db, user):
    """Buat_Tagihan: total = biaya jasa dokter + biaya obat (jumlah x harga satuan)."""
    selesai = [k for k, v in db["reservasi"].items() if v["status"] == "Selesai"]
    if len(selesai) > 0:
        tampilkan_reservasi(db, selesai, "RESERVASI SELESAI")

    id_res = pilih_id(db["reservasi"], "ID reservasi: ")

    if id_res is None or db["reservasi"][id_res]["status"] != "Selesai":
        print("Reservasi belum selesai atau tagihan sudah ada")
        return

    id_trx = transaksi_reservasi(db, id_res)

    if id_trx is not None and db["transaksi"][id_trx]["status_bayar"] != STATUS_BELUM_DITAGIH:
        print("Reservasi belum selesai atau tagihan sudah ada")
        return

    res = db["reservasi"][id_res]

    if res["id_dokter"] not in db["dokter"]:
        print("Data dokter reservasi ini sudah tidak ada, tagihan tidak dapat dibuat")
        return

    if id_trx is None:
        id_trx = id_berikutnya(db["transaksi"])
        db["transaksi"][id_trx] = {
            "id_reservasi": id_res, "id_pasien": res["id_pasien"], "id_dokter": res["id_dokter"],
            "biaya_jasa": 0, "obat": [], "total": 0, "status_bayar": STATUS_BELUM_DITAGIH,
            "metode": "", "tanggal": str(date.today()), "waktu_bayar": "",
            "dibuat_oleh": user, "diproses_oleh": ""
        }

    transaksi = db["transaksi"][id_trx]
    transaksi["biaya_jasa"] = db["dokter"][res["id_dokter"]]["biaya_jasa"]
    for item in transaksi["obat"]:
        item["subtotal"] = item["jumlah"] * item["harga_satuan"]
    hitung_total(transaksi)
    transaksi["status_bayar"] = "Belum Dibayar"
    transaksi["tanggal"] = str(date.today())
    transaksi["dibuat_oleh"] = user
    database.simpan(db, ["transaksi"])

    print("\nTagihan berhasil dibuat")
    struk.tampil_rincian(db, id_trx)


def tampil_tagihan_belum_lunas(db):
    daftar = {k: v for k, v in db["transaksi"].items() if v["status_bayar"] in ("Belum Dibayar", "Menunggu Pembayaran")}
    if len(daftar) > 0:
        tampilkan_tabel(
            "TAGIHAN BELUM LUNAS",
            ("ID", "No. Transaksi", "Pasien", "Total", "Status"),
            [(k, struk.nomor_transaksi(k), nama_dari(db["pasien"], v["id_pasien"]),
              format_rupiah(v["total"]), v["status_bayar"]) for k, v in daftar.items()],
            kiri=("Pasien", "Status"),
            kanan=("Total",)
        )


def proses_pembayaran(db, user):
    """Proses_Pembayaran: Tunai -> Lunas bila uang cukup; Transfer -> Lunas bila bukti diterima, selain itu Menunggu Pembayaran."""
    tampil_tagihan_belum_lunas(db)
    id_trx = pilih_id(db["transaksi"], "ID transaksi: ")

    if id_trx is None or db["transaksi"][id_trx]["status_bayar"] in ("Lunas", STATUS_BELUM_DITAGIH):
        print("Transaksi tidak ada atau sudah lunas (atau tagihan belum dibuat)")
        return

    transaksi = db["transaksi"][id_trx]
    struk.tampil_rincian(db, id_trx)
    metode = input("Metode pembayaran (Tunai/Transfer): ").strip().capitalize()

    if metode not in METODE_BAYAR:
        print("Metode tidak valid")
        return

    status = "Lunas"

    if metode == "Tunai":
        uang = ke_angka(input("Uang diterima (angka saja): "))
        if uang is None or uang < transaksi["total"]:
            print("Uang kurang atau tidak valid. Pembayaran belum diproses")
            return
        if uang > transaksi["total"]:
            print("Kembalian:", format_rupiah(uang - transaksi["total"]))
    elif not konfirmasi("Bukti transfer sudah diterima"):
        status = "Menunggu Pembayaran"

    transaksi["metode"] = metode
    transaksi["status_bayar"] = status
    transaksi["diproses_oleh"] = user
    if status == "Lunas":
        transaksi["waktu_bayar"] = sekarang()
    database.simpan(db, ["transaksi"])

    print("Pembayaran berhasil diproses. Status:", status)


def cetak_struk(db):
    """Cetak_Struk: hanya transaksi Lunas."""
    lunas = {k: v for k, v in db["transaksi"].items() if v["status_bayar"] == "Lunas"}
    if len(lunas) > 0:
        tampilkan_tabel(
            "TRANSAKSI LUNAS",
            ("ID", "No. Transaksi", "Pasien", "Total"),
            [(k, struk.nomor_transaksi(k), nama_dari(db["pasien"], v["id_pasien"]), format_rupiah(v["total"]))
             for k, v in lunas.items()],
            kiri=("Pasien",),
            kanan=("Total",)
        )

    id_trx = struk.cetak_struk(db, input("ID transaksi: ").strip())

    if id_trx is not None:
        struk.tampil_dan_simpan(db, id_trx)
