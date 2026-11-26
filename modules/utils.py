import os
import sys
from datetime import datetime

from prettytable import PrettyTable

try:
    import inquirer
except ImportError:
    inquirer = None


def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def jeda(pesan="Tekan Enter untuk melanjutkan..."):
    input("\n" + pesan)


def judul(teks):
    print("\n" + "=" * 60)
    print(" " + teks)
    print("=" * 60)


def buat_tabel(kolom, kiri=()):
    """Membuat tabel kosong; kolom yang disebut di 'kiri' rata kiri."""
    tabel = PrettyTable()
    tabel.field_names = list(kolom)

    for nama_kolom in kiri:
        tabel.align[nama_kolom] = "l"

    return tabel


def tampilkan_tabel(judul_tabel, kolom, baris, kiri=(), kanan=()):
    tabel = buat_tabel(kolom, kiri)
    tabel.title = judul_tabel

    for nama_kolom in kanan:
        tabel.align[nama_kolom] = "r"

    for isi in baris:
        tabel.add_row(list(isi))

    print()
    print(tabel)


def format_rupiah(angka):
    return "Rp. " + format(angka, ",").replace(",", ".")


def id_berikutnya(kumpulan):
    """ID numerik berikutnya sebagai teks: {"1":..,"2":..} -> "3"."""
    urutan = [int(kode) for kode in kumpulan if str(kode).isdigit()]
    return str(max(urutan, default=0) + 1)


def sekarang():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_tanggal(teks):
    """'2026-11-12' -> date, atau None bila formatnya salah."""
    try:
        return datetime.strptime(teks, "%Y-%m-%d").date()
    except ValueError:
        return None


def nama_dari(tabel, kode):
    """Nama dari tabel data (dokter/pasien) berdasarkan ID; aman bila data sudah dihapus."""
    if kode in tabel:
        return tabel[kode]["nama"]
    return "(data dihapus)"


def ke_angka(teks):
    """Mengubah teks menjadi bilangan bulat, None bila bukan angka."""
    teks = teks.strip()

    if teks.isdigit():
        return int(teks)

    return None


def input_teks(pesan, lama=None):
    while True:
        nilai = input(pesan).strip()

        if nilai != "":
            return nilai

        if lama is not None:
            return lama

        print("Input tidak boleh kosong")


def input_angka(pesan, minimum=0, lama=None):
    while True:
        nilai = input(pesan).strip()

        if nilai == "" and lama is not None:
            return lama

        try:
            angka = int(nilai)
        except ValueError:
            print("Input harus berupa angka bulat")
            continue

        if angka >= minimum:
            return angka

        print("Nilai minimal adalah", minimum)


def konfirmasi(pesan):
    jawaban = input(pesan + " (y/n): ").strip().lower()
    return jawaban in {"y", "ya"}


def pilih_id(kumpulan, pesan):
    """Meminta ID/nomor; mengembalikan kunci bila ada di kumpulan, selain itu None."""
    kode = input(pesan).strip()

    if kode in kumpulan:
        return kode

    return None


def jam_ke_menit(teks):
    """'08:30' -> 510, atau None bila formatnya salah."""
    try:
        waktu = datetime.strptime(teks.strip(), "%H:%M")
    except ValueError:
        return None

    return waktu.hour * 60 + waktu.minute


def menit_ke_jam(menit):
    return f"{menit // 60:02d}:{menit % 60:02d}"


def pilih_menu(judul_menu, daftar_menu):
    """Menu pilihan; mengembalikan nomor pilihan (mulai dari 1).

    Memakai panah atas/bawah (inquirer) bila tersedia di terminal interaktif,
    selain itu memakai pilihan nomor biasa.
    """
    if inquirer is not None and sys.stdin.isatty():
        jawaban = inquirer.prompt([
            inquirer.List("menu", message=judul_menu, choices=daftar_menu)
        ])

        if jawaban is None:
            return len(daftar_menu)

        return daftar_menu.index(jawaban["menu"]) + 1

    print("\n" + judul_menu)
    for nomor, nama in enumerate(daftar_menu, 1):
        print(f"  {nomor}. {nama}")

    while True:
        nomor = ke_angka(input("Pilih nomor: "))

        if nomor is not None and 1 <= nomor <= len(daftar_menu):
            return nomor

        print("Pilihan tidak valid")


def pilih_kunci(kumpulan, pesan):
    """Meminta nomor urut (mulai 1) dari daftar yang sedang ditampilkan; mengembalikan kunci, atau None bila tidak valid."""
    if len(kumpulan) == 0:
        print("Data belum tersedia")
        return None

    nomor = ke_angka(input(pesan))

    if nomor is None or nomor < 1 or nomor > len(kumpulan):
        print("Nomor tidak valid")
        return None

    return list(kumpulan)[nomor - 1]
