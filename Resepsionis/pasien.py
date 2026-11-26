from modules import database
from modules.utils import format_rupiah, id_berikutnya, parse_tanggal, tampilkan_tabel


def valid_no_hp(teks):
    return teks.isdigit() and 10 <= len(teks) <= 13


def no_hp_terpakai(db, no_hp):
    return any(isi["no_hp"] == no_hp for isi in db["pasien"].values())


def tampil_tabel_pasien(db):
    tampilkan_tabel(
        "DATA PASIEN",
        ("ID", "Nama", "Tgl Lahir", "No. HP", "Alamat"),
        [
            (kode, isi["nama"], isi.get("tgl_lahir", "-"), isi["no_hp"], isi["alamat"])
            for kode, isi in db["pasien"].items()
        ],
        kiri=("Nama", "Alamat")
    )


def tampil_tabel_dokter(db):
    tampilkan_tabel(
        "DATA DOKTER DAN BIAYA JASA",
        ("ID", "Nama Dokter", "Spesialisasi", "Biaya Jasa"),
        [
            (kode, isi["nama"], isi["spesialisasi"], format_rupiah(isi["biaya_jasa"]))
            for kode, isi in db["dokter"].items()
        ],
        kiri=("Nama Dokter", "Spesialisasi"),
        kanan=("Biaya Jasa",)
    )


def tampil_tabel_obat(db):
    tampilkan_tabel(
        "HARGA OBAT",
        ("ID", "Nama Obat", "Kategori", "Harga", "Stok", "Kedaluwarsa"),
        [
            (kode, isi["nama"], isi["kategori"], format_rupiah(isi["harga"]) + "/" + isi["satuan"],
             isi["stok"], isi["kedaluwarsa"])
            for kode, isi in db["obat"].items()
        ],
        kiri=("Nama Obat", "Kategori"),
        kanan=("Harga",)
    )


def daftar_pasien(db):
    """Daftar_Pasien: resepsionis mendaftarkan pasien baru (tanpa akun login)."""
    print("\n========== DAFTAR PASIEN BARU ==========")
    nama = input("Nama lengkap: ").strip()
    tgl_lahir = input("Tanggal lahir (YYYY-MM-DD): ").strip()
    no_hp = input("No. HP (10-13 angka): ").strip()
    alamat = input("Alamat: ").strip()

    if nama == "" or alamat == "" or parse_tanggal(tgl_lahir) is None or not valid_no_hp(no_hp):
        print("Data kosong atau tidak valid (tanggal lahir YYYY-MM-DD, No. HP 10-13 digit)")
        return

    if no_hp_terpakai(db, no_hp):
        print("No. HP sudah terdaftar atas pasien lain")
        return

    id_baru = id_berikutnya(db["pasien"])
    db["pasien"][id_baru] = {"nama": nama, "tgl_lahir": tgl_lahir, "no_hp": no_hp, "alamat": alamat}
    database.simpan(db, ["pasien"])
    print("Pasien '" + nama + "' berhasil ditambah dengan ID " + id_baru)


def lihat_data(db):
    """Lihat_Data: data pasien, dokter + biaya jasa, dan harga obat."""
    if len(db["pasien"]) == 0 and len(db["dokter"]) == 0 and len(db["obat"]) == 0:
        print("\nData belum tersedia")
        return

    for kunci, tampil, nama in (("pasien", tampil_tabel_pasien, "pasien"),
                                ("dokter", tampil_tabel_dokter, "dokter"),
                                ("obat", tampil_tabel_obat, "obat")):
        if len(db[kunci]) == 0:
            print("\nBelum ada data " + nama)
        else:
            tampil(db)
