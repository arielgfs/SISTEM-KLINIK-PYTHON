import os

import inquirer
from prettytable import PrettyTable


def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def jeda():
    input("\nTekan Enter untuk melanjutkan...")


def format_rupiah(angka):
    return "Rp. " + format(angka, ",").replace(",", ".")


def buat_id(awalan, kumpulan):
    urutan = [int(kode[len(awalan):]) for kode in kumpulan]
    return f"{awalan}{max(urutan, default=0) + 1:02d}"


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


def pilih_menu(judul, daftar_menu):
    pertanyaan = [
        inquirer.List(
            "menu",
            message=judul,
            choices=daftar_menu
        )
    ]

    jawaban = inquirer.prompt(pertanyaan)

    if jawaban is None:
        return len(daftar_menu)

    return daftar_menu.index(jawaban["menu"]) + 1


def pilih_kunci(kumpulan, pesan):
    if len(kumpulan) == 0:
        print("Data masih kosong")
        return None

    nomor = input_angka(pesan, 1)
    daftar_kunci = list(kumpulan)

    if nomor > len(daftar_kunci):
        print("Nomor tidak valid")
        return None

    return daftar_kunci[nomor - 1]


def tampilkan_tabel(judul, kolom, baris, kiri=(), kanan=()):
    tabel = PrettyTable()
    tabel.title = judul
    tabel.field_names = list(kolom)

    for nama_kolom in kiri:
        tabel.align[nama_kolom] = "l"

    for nama_kolom in kanan:
        tabel.align[nama_kolom] = "r"

    for isi in baris:
        tabel.add_row(list(isi))

    print()
    print(tabel)

def cari(nama_tabel, id_cari):
    for item in db[nama_tabel]:
        if item["id"] == id_cari:
            return item
    return {}