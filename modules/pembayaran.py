from utils import tampilkan_tabel, format_rupiah


def tampil_transaksi(daftar):
    baris = []
    for t in daftar:
        baris.append([t["id"], t["nomor"], t["tanggal"], nama_dari("pasien", t["id_pasien"]),
                      nama_dari("dokter", t["id_dokter"]), format_rupiah(t["total"]), t["metode"], t["status"]])
    tampilkan_tabel(["ID", "Nomor", "Tanggal", "Pasien", "Dokter", "Total", "Metode", "Status"], baris)
