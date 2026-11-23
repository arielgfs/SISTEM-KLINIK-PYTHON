from modules import database
from modules.utils import id_berikutnya, jeda
from resepsionis.pasien import valid_no_hp


def proses_register():
    """Registrasi akun pasien baru: membuat data pasien (pasien.json) sekaligus akun login (users.json)."""
    print("\n========== REGISTRASI PASIEN ==========")
    db = database.muat_database(["users", "pasien"])

    nama = input("Nama lengkap: ").strip()
    if nama == "":
        print("Nama tidak boleh kosong")
        jeda()
        return

    no_hp = input("No. HP (10-13 angka): ").strip()
    if not valid_no_hp(no_hp):
        print("No. HP harus 10-13 digit angka")
        jeda()
        return

    if any(isi["no_hp"] == no_hp for isi in db["pasien"].values()):
        print("No. HP sudah terdaftar. Jika sudah pernah berobat, minta resepsionis membuatkan akun Anda")
        jeda()
        return

    alamat = input("Alamat: ").strip()
    if alamat == "":
        print("Alamat tidak boleh kosong")
        jeda()
        return

    username = input("Username: ").strip().lower()
    if username == "" or " " in username:
        print("Username tidak boleh kosong atau mengandung spasi")
        jeda()
        return

    if username in db["users"]:
        print("Username sudah dipakai")
        jeda()
        return

    password = input("Password (minimal 6 karakter): ").strip()
    if len(password) < 6:
        print("Password minimal 6 karakter")
        jeda()
        return

    id_pasien = id_berikutnya(db["pasien"])
    db["pasien"][id_pasien] = {"nama": nama, "no_hp": no_hp, "alamat": alamat}
    db["users"][username] = {
        "password": password,
        "role": "pasien",
        "nama": nama,
        "id_pasien": id_pasien
    }
    database.simpan(db, ["pasien", "users"])

    print("\nRegistrasi berhasil. Silakan login dengan username", username)
    jeda()
