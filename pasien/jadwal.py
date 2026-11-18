from modules import tampilkan_tabel, cari

db = {}

def lihat_jadwal():
    baris = []
    for j in db["jadwal_dokter"]:
        dokter = cari("dokter", j["id_dokter"])
        baris.append([j["id"], dokter["nama"], dokter["spesialisasi"], j["hari"],
                      f"{j['jam_mulai']}-{j['jam_selesai']}", j["kuota"]])
    tampilkan_tabel(["ID", "Dokter", "Spesialisasi", "Hari", "Jam", "Kuota/hari"], baris)


