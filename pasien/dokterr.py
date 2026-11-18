from modules import format_rupiah, tampilkan_tabel
db ={}


def lihat_dokter():
    baris = []
    for i in db["dokter"]:
        baris.append([i["id"], i["nama"], i["spesialisasi"], format_rupiah(i["biaya"])])
    tampilkan_tabel(["ID", "Nama", "Spesialisasi", "Biaya Jasa"], baris)

def lihat_layanan():
    baris = []
    for k in db["layanan"]:
        baris.append([k["id"], k["nama"], k["keterangan"]])
    tampilkan_tabel(["ID", "Layanan", "Keterangan"], baris)
