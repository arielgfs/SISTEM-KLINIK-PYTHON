from modules.utils import bersihkan_layar, jeda, pilih_menu
from auth.login import proses_login
from auth.register import proses_register
from admin.dashboard import menu_admin
from resepsionis.dashboard import menu_resepsionis
from pasien.dashboard import menu_pasien


def jalankan_menu_role(user):
    role = user["role"]

    if role == "admin":
        return menu_admin(user["username"])

    if role == "resepsionis":
        return menu_resepsionis(user["username"])

    if role == "pasien":
        return menu_pasien(user)

    print("Role", role, "tidak dikenali")
    jeda()
    return "logout"


def main():
    daftar_menu = [
        "Register Pasien",
        "Login",
        "Keluar Program"
    ]

    while True:
        bersihkan_layar()
        pilihan = pilih_menu("MENU AWAL", daftar_menu)

        if pilihan == 1:
            proses_register()

        elif pilihan == 2:
            user = proses_login()

            if user is None:
                print("\nAkses ditolak. Kesempatan login habis")
                jeda("Tekan Enter untuk kembali...")
                continue

            jalankan_menu_role(user)

        elif pilihan == 3:
            bersihkan_layar()
            print("Program selesai. Terima kasih!")
            return


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan oleh pengguna.")
