from modules import database
from modules.utils import (
    bersihkan_layar, jeda, konfirmasi, pilih_kunci, pilih_menu, tampilkan_tabel
)

ROLE = ("admin", "resepsionis", "pasien")


def tampilkan_akun():
    """Tampilkan_Akun: mengembalikan False bila data kosong."""
    if len(database.db["users"]) == 0:
        print("\nData belum tersedia")
        return False

    tampilkan_tabel(
        "DAFTAR AKUN",
        ("No", "Username", "Nama", "Role"),
        [
            (nomor, kode, data.get("nama", "-"), data["role"])
            for nomor, (kode, data) in enumerate(database.db["users"].items(), 1)
        ],
        kiri=("Username", "Nama")
    )
    return True


def pilih_role():
    return ROLE[pilih_menu("Pilih role / hak akses", list(ROLE)) - 1]


def tambah_akun():
    username = input("Username: ").strip().lower()
    password = input("Password (minimal 6 karakter): ").strip()
    role = pilih_role()

    if username == "" or password == "" or " " in username or len(password) < 6:
        print("Data kosong atau tidak valid")
        return

    if username in database.db["users"]:
        print("Username sudah dipakai")
        return

    akun = {"password": password, "role": role, "nama": username}

    if role == "pasien":
        id_pasien = input("ID data pasien untuk akun ini: ").strip()
        terpakai = {isi.get("id_pasien") for isi in database.db["users"].values()}

        if id_pasien not in database.db["pasien"] or id_pasien in terpakai:
            print("Data tidak valid: ID pasien tidak ada atau sudah punya akun")
            return

        akun["id_pasien"] = id_pasien
        akun["nama"] = database.db["pasien"][id_pasien]["nama"]

    database.db["users"][username] = akun
    database.simpan(database.db, ["users"])
    print("Akun berhasil ditambah")


def ubah_akun():
    if not tampilkan_akun():
        return

    kode = pilih_kunci(database.db["users"], "Nomor akun yang ingin diubah: ")

    if kode is None:
        return

    akun = database.db["users"][kode]
    role = pilih_role()

    if role == "pasien" and "id_pasien" not in akun:
        print("Data tidak valid: akun ini tidak terhubung dengan data pasien")
        return

    if akun["role"] == "admin" and role != "admin" and jumlah_admin() == 1:
        print("Data tidak valid: harus ada minimal satu admin")
        return

    akun["role"] = role
    database.simpan(database.db, ["users"])
    print("Data akun berhasil diubah")


def jumlah_admin():
    return sum(1 for isi in database.db["users"].values() if isi["role"] == "admin")


def hapus_akun(username_aktif):
    if not tampilkan_akun():
        return

    kode = pilih_kunci(database.db["users"], "Nomor akun yang ingin dihapus: ")

    if kode is None:
        return

    if kode == username_aktif:
        print("Akun yang sedang dipakai tidak bisa dihapus")
        return

    if database.db["users"][kode]["role"] == "admin" and jumlah_admin() == 1:
        print("Admin terakhir tidak bisa dihapus")
        return

    if konfirmasi("Hapus akun " + kode):
        del database.db["users"][kode]
        database.simpan(database.db, ["users"])
        print("Data akun berhasil dihapus")
    else:
        print("Penghapusan dibatalkan")


def menu_akun(username_aktif):
    daftar_menu = [
        "Tambah Akun",
        "Tampilkan Akun",
        "Ubah Role Akun",
        "Hapus Akun",
        "Kembali ke Menu Admin"
    ]

    while True:
        bersihkan_layar()
        pilihan = pilih_menu("MENU KELOLA AKUN", daftar_menu)

        if pilihan == 5:
            return

        if pilihan == 1:
            tambah_akun()
        elif pilihan == 2:
            tampilkan_akun()
        elif pilihan == 3:
            ubah_akun()
        elif pilihan == 4:
            hapus_akun(username_aktif)

        jeda()
