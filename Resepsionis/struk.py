import os
from modules.utils import bersihkan_layar, jeda, judul, format_rupiah, nama_dari
from resepsionis.pasien import pilih_data, konfirmasi

NAMA_KLINIK = "KLINIK SEHAT"     
FOLDER_STRUK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "struk")
LEBAR = 46
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def nomor_transaksi(id_trx):
    return "ID-" + str(id_trx).zfill(3)


def tanggal_indonesia(teks):
    try:
        tahun, bulan, hari = teks.split("-")
        return str(int(hari)) + " " + BULAN[int(bulan) - 1] + " " + tahun
    except (ValueError, IndexError):
        return teks


def baris(kiri, kanan):
    spasi = LEBAR - len(kiri) - len(kanan)
    if spasi < 1:
        spasi = 1
    return kiri + " " * spasi + kanan


def buat_teks_struk(db, id_trx):
    transaksi = db["transaksi"][id_trx]                  
    metode = transaksi["metode"]
    if metode == "":
        metode = "-"

    teks = []
    teks.append("=" * LEBAR)
    teks.append(NAMA_KLINIK.center(LEBAR))
    teks.append("=" * LEBAR)
    teks.append("Nomor Transaksi : " + nomor_transaksi(id_trx))
    teks.append("Tanggal         : " + tanggal_indonesia(transaksi["tanggal"]))
    teks.append("Nama Pasien     : " + nama_dari(db["pasien"], transaksi["id_pasien"]))
    teks.append("Nama Dokter     : " + nama_dari(db["dokter"], transaksi["id_dokter"]))
    teks.append("-" * LEBAR)
    teks.append("Rincian Pembayaran:")
    teks.append(baris("1. Jasa konsultasi dokter", format_rupiah(transaksi["biaya_jasa"])))

    nomor = 1
    subtotal_obat = 0
    for item in transaksi["obat"]:
        nomor = nomor + 1
        subtotal_obat = subtotal_obat + item["subtotal"]
        teks.append(baris(str(nomor) + ". " + item["nama"] + " (" + str(item["jumlah"]) + " " + item["satuan"] + ")",
                          format_rupiah(item["subtotal"])))
        teks.append("     @ " + format_rupiah(item["harga_satuan"]) + " / " + item["satuan"])

    teks.append("-" * LEBAR)
    teks.append(baris("Subtotal obat", format_rupiah(subtotal_obat)))
    teks.append(baris("Total Pembayaran", format_rupiah(transaksi["total"])))
    teks.append("-" * LEBAR)
    teks.append("Metode Pembayaran: " + metode)
    teks.append("Status Pembayaran: " + transaksi["status_bayar"].upper())
    teks.append("")
    teks.append("Terima kasih telah mempercayai layanan kami.".center(LEBAR))
    teks.append("=" * LEBAR)
    return "\n".join(teks)


def tampil_dan_simpan(db, id_trx):
    bersihkan_layar()
    teks = buat_teks_struk(db, id_trx)
    print(teks)
    if konfirmasi("Simpan struk ke file .txt?"):
        os.makedirs(FOLDER_STRUK, exist_ok=True)
        jalur = os.path.join(FOLDER_STRUK, nomor_transaksi(id_trx) + ".txt")
        with open(jalur, "w", encoding="utf-8") as berkas:
            berkas.write(teks + "\n")
        print("[+] Struk disimpan di : " + jalur)
    jeda()


def menu_struk(db, user):
    bersihkan_layar()
    judul("CETAK STRUK PEMBAYARAN")

    pilihan = []
    for id_trx in db["transaksi"]:                        
        data = db["transaksi"][id_trx]
        if data["status_bayar"] == "Lunas":              
            pilihan.append((nomor_transaksi(id_trx) + " | " + nama_dari(db["pasien"], data["id_pasien"])
                            + " | " + format_rupiah(data["total"]), id_trx))
    if len(pilihan) == 0:
        print(" Belum ada transaksi berstatus Lunas.")
        jeda()
        return

    id_trx = pilih_data("Pilih transaksi yang dicetak struknya", pilihan)
    if id_trx != None:
        tampil_dan_simpan(db, id_trx)