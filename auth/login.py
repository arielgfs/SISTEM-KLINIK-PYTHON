from modules import database
from modules.utils import jeda, tampilkan_tabel


def proses_login():
    """Meminta username & password. Mengembalikan data user (dict) atau None bila kesempatan habis.

    Data user: {"username", "role", "nama", "id_pasien" (khusus pasien)}
    """
    users = database.muat_tabel("users")
    sisa_kesempatan = database.BATAS_LOGIN

    while sisa_kesempatan > 0:
        print("\n========== LOGIN ==========")
        username = input("Masukkan username: ").strip()
        password = input("Masukkan password: ").strip()

        sisa_kesempatan -= 1

        if username in users and users[username]["password"] == password:
            user = dict(users[username])
            user.pop("password")
            user["username"] = username

            tampilkan_tabel(
                "LOGIN BERHASIL",
                ("Keterangan", "Nilai"),
                (("Selamat datang", user.get("nama", username)), ("Role anda", user["role"])),
                kiri=("Keterangan", "Nilai")
            )
            jeda()
            return user

        print("Username atau password salah")
        if sisa_kesempatan > 0:
            print("Login tersisa:", sisa_kesempatan, "kali")

    return None
