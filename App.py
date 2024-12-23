from flask import Flask, render_template, request, redirect, url_for
import numpy as np

app = Flask(__name__)

def northwest_corner_supply_demand(pasokan, permintaan, biaya):
    n, m = len(pasokan), len(permintaan)
    alokasi = np.zeros((n, m))
    i, j = 0, 0
    
    while i < n and j < m:
        dialokasikan = min(pasokan[i], permintaan[j])
        alokasi[i, j] = dialokasikan
        pasokan[i] -= dialokasikan
        permintaan[j] -= dialokasikan
        
        if pasokan[i] == 0:
            i += 1
        if permintaan[j] == 0:
            j += 1
    return alokasi

def hitung_biaya_total(alokasi, biaya):
    return np.sum(alokasi * biaya)

def vogel_approximation_method(pasokan, permintaan, biaya):
    n, m = len(pasokan), len(permintaan)
    alokasi = np.zeros((n, m))
    
    while np.sum(pasokan) > 0 and np.sum(permintaan) > 0:
        # Menghitung perbedaan biaya minimum untuk setiap baris dan kolom
        penalti_baris = [sorted(biaya[i, :])[1] - sorted(biaya[i, :])[0] for i in range(n)]
        penalti_kolom = [sorted(biaya[:, j])[1] - sorted(biaya[:, j])[0] for j in range(m)]
        
        if max(penalti_baris) > max(penalti_kolom):
            i = penalti_baris.index(max(penalti_baris))
            j = np.argmin(biaya[i, :])
        else:
            j = penalti_kolom.index(max(penalti_kolom))
            i = np.argmin(biaya[:, j])
        
        dialokasikan = min(pasokan[i], permintaan[j])
        alokasi[i, j] = dialokasikan
        pasokan[i] -= dialokasikan
        permintaan[j] -= dialokasikan
        
        # Mengupdate biaya setelah alokasi
        biaya[i, j] = 9999  # Set nilai biaya yang sudah dialokasikan menjadi angka besar
    
    return alokasi

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        jumlah_pabrik = int(request.form['jumlah_pabrik'])
        jumlah_gudang = int(request.form['jumlah_gudang'])
        return redirect(url_for('input_kapasitas', pabrik=jumlah_pabrik, gudang=jumlah_gudang))
    return render_template('input.html')

@app.route('/kapasitas/<int:pabrik>/<int:gudang>', methods=['GET', 'POST'])
def input_kapasitas(pabrik, gudang):
    if request.method == 'POST':
        pasokan = list(map(int, request.form.getlist('pasokan')))
        permintaan = list(map(int, request.form.getlist('permintaan')))
        biaya = []

        for i in range(pabrik):
            biaya.append(list(map(int, request.form.getlist(f'baris_biaya_{i}'))))
        
        biaya = np.array(biaya)

        alokasi_nwc = northwest_corner_supply_demand(pasokan.copy(), permintaan.copy(), biaya.copy())
        total_biaya_nwc = hitung_biaya_total(alokasi_nwc, biaya)


        alokasi_vam = vogel_approximation_method(pasokan.copy(), permintaan.copy(), biaya.copy())
        total_biaya_vam = hitung_biaya_total(alokasi_vam, biaya)

        return render_template('hasil.html', 
                               alokasi_nwc=alokasi_nwc, 
                               total_biaya_nwc=total_biaya_nwc, 
                               alokasi_vam=alokasi_vam, 
                               total_biaya_vam=total_biaya_vam, 
                               biaya=biaya)

    return render_template('kapasitas.html', pabrik=pabrik, gudang=gudang)

@app.route('/kembali')
def kembali_ke_menu():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
