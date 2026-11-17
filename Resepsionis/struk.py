"""
=====================================================================
resepsionis/struk.py                  
Isi struk dibuat langsung dari data transaksi (transaksi.json).
File eksternal yang dihasilkan : struk/ID-xxx.txt
Tabel JSON : transaksi.json, pasien.json, dokter.json
=====================================================================
"""
import os
from modules.utils import bersihkan_layar, jeda, buat_tabel, judul, format_rupiah, nama_dari

NAMA_KLINIK = "KLINIK SEHAT"      # [UBAH] nama klinik pada struk
# [FILE EKSTERNAL] folder hasil simpan struk (.txt) -> di folder utama proyek
FOLDER_STRUK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "struk")
LEBAR = 46
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def nomor_transaksi(id_trx):
    """'1' -> 'ID-001'  (juga dipakai pembayaran.py)"""
    return "ID-" + str(id_trx).zfill(3)


# ---------------------------------------------------------------------
# ISI STRUK (dibuat langsung dari data transaksi yang tersimpan)
# ---------------------------------------------------------------------
def tanggal_indonesia(teks):
    """'2026-11-10' -> '10 November 2026'"""
    try:
        tahun, bulan, hari = teks.split("-")
        return str(int(hari)) + " " + BULAN[int(bulan) - 1] + " " + tahun
    except (ValueError, IndexError):
        return teks


def baris(kiri, kanan):
    """Satu baris struk: teks kiri rata kiri, teks kanan rata kanan."""
    spasi = LEBAR - len(kiri) - len(kanan)
    if spasi < 1:
        spasi = 1
    return kiri + " " * spasi + kanan


def buat_teks_struk(db, id_trx):
    """Menyusun isi struk (sesuai contoh format struk di dokumen proyek)."""
    transaksi = db["transaksi"][id_trx]                   
    metode = transaksi["metode"]
    if metode == "":
        metode = "-"
    garis = "=" * LEBAR
    putus = "-" * LEBAR
    teks = []
    teks.append(garis)
    teks.append(NAMA_KLINIK.center(LEBAR))
    teks.append(garis)
    teks.append("Nomor Transaksi : " + nomor_transaksi(id_trx))
    teks.append("Tanggal         : " + tanggal_indonesia(transaksi["tanggal"]))
    teks.append("Nama Pasien     : " + nama_dari(db["pasien"], transaksi["id_pasien"]))
    teks.append("Nama Dokter     : " + nama_dari(db["dokter"], transaksi["id_dokter"]))
    teks.append(putus)
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

    teks.append(putus)
    teks.append(baris("Subtotal obat", format_rupiah(subtotal_obat)))
    teks.append(baris("Total Pembayaran", format_rupiah(transaksi["total"])))
    teks.append(putus)
    teks.append("Metode Pembayaran: " + metode)
    teks.append("Status Pembayaran: " + transaksi["status_bayar"].upper())
    teks.append("")
    teks.append("Terima kasih telah mempercayai layanan kami.".center(LEBAR))
    teks.append(garis)
    return "\n".join(teks)


def simpan_struk_file(db, id_trx):
    """[FILE EKSTERNAL] menulis struk ke struk/ID-xxx.txt, mengembalikan lokasi file."""
    os.makedirs(FOLDER_STRUK, exist_ok=True)
    jalur = os.path.join(FOLDER_STRUK, nomor_transaksi(id_trx) + ".txt")
    with open(jalur, "w", encoding="utf-8") as berkas:
        berkas.write(buat_teks_struk(db, id_trx) + "\n")
    return jalur



def tampil_dan_simpan(db, id_trx):
    """Menampilkan struk lalu simpan ke file .txt (juga dipanggil dari pembayaran.py)."""
    bersihkan_layar()
    print(buat_teks_struk(db, id_trx))
    simpan = input("\nSimpan struk ke file .txt? [y/n] : ").strip()
    if simpan == "y" or simpan == "Y":
        jalur = simpan_struk_file(db, id_trx)
        print("[+] Struk disimpan di : " + jalur)
    jeda()


def menu_struk(db, user):
    bersihkan_layar()
    judul("CETAK STRUK PEMBAYARAN")
    if len(db["transaksi"]) == 0:
        print(" Belum ada transaksi.")
        jeda()
        return

    tabel = buat_tabel(["ID", "No. Transaksi", "Pasien", "Total", "Status"], ["Pasien", "Status"])
    for id_trx in db["transaksi"]:                        
        data = db["transaksi"][id_trx]
        tabel.add_row([id_trx, nomor_transaksi(id_trx), nama_dari(db["pasien"], data["id_pasien"]),
                       format_rupiah(data["total"]), data["status_bayar"]])
    print(tabel)

    id_trx = input("ID transaksi yang dicetak struknya : ").strip()
    if id_trx not in db["transaksi"]:
        print("\n[!] Transaksi dengan ID " + id_trx + " tidak ditemukan.")
        jeda()
        return
    if db["transaksi"][id_trx]["status_bayar"] != "Lunas":
        print("\n[!] Struk hanya dapat dicetak untuk transaksi berstatus Lunas.")
        jeda()
        return

    tampil_dan_simpan(db, id_trx)