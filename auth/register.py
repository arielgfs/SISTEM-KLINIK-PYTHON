from modules import database
from modules.utils import id_berikutnya, jeda
from resepsionis.pasien import valid_no_hp


def proses_register():
    """Register_Pasien: membuat data pasien (pasien.json) sekaligus akun login (users.json, role pasien)."""
    print("\n========== REGISTRASI PASIEN ==========")
    db = database.muat_database(["users", "pasien"])

    nama = input("Nama lengkap: ").strip()
    username = input("Username: ").strip().lower()
    password = input("Password (minimal 6 karakter): ").strip()
    no_hp = input("No. HP (10-13 angka): ").strip()

    if nama == "" or username == "" or password == "" or no_hp == "":
        print("Data tidak boleh kosong")
    elif " " in username:
        print("Username tidak boleh mengandung spasi")
    elif username in db["users"]:
        print("Username sudah dipakai")
    elif len(password) < 6:
        print("Password minimal 6 karakter")
    elif not valid_no_hp(no_hp):
        print("No. HP harus 10-13 digit angka")
    elif any(isi["no_hp"] == no_hp for isi in db["pasien"].values()):
        print("No. HP sudah terdaftar. Jika sudah pernah berobat, minta resepsionis membuatkan akun Anda")
    else:
        id_pasien = id_berikutnya(db["pasien"])
        db["pasien"][id_pasien] = {"nama": nama, "tgl_lahir": "-", "no_hp": no_hp, "alamat": "-"}
        db["users"][username] = {
            "password": password,
            "role": "pasien",
            "nama": nama,
            "id_pasien": id_pasien
        }
        database.simpan(db, ["pasien", "users"])
        print("\nRegistrasi berhasil. Silakan login dengan username", username)

    jeda()
