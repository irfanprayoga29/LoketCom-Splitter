from flask import Flask, request, render_template, redirect, url_for, flash, send_file
import PyPDF2
import os
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia Anda untuk keamanan sesi

# Function to split PDF
def split_pdf(input_pdf_path, output_folder, nama_list):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with open(input_pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        current_page = 0

        for nama, jumlah_halaman in nama_list:
            output_pdf_path = os.path.join(output_folder, f"{nama.replace(' ', '_')}.pdf")
            pdf_writer = PyPDF2.PdfWriter()

            for i in range(jumlah_halaman):
                if current_page < total_pages:
                    pdf_writer.add_page(pdf_reader.pages[current_page])
                    current_page += 1
                else:
                    print(f"Halaman habis sebelum semua nama diproses.")
                    return

            with open(output_pdf_path, 'wb') as output_pdf_file:
                pdf_writer.write(output_pdf_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    pdf_file = request.files['pdf']
    output_folder = os.path.join('output_files')
    output_zip_path = 'output_files.zip'

    # Buat folder `uploads` untuk menyimpan file sementara
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Buat folder output_files jika belum ada
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        # Hapus semua isi folder output_files untuk memastikan folder bersih
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Hapus file
            except Exception as e:
                flash(f'Terjadi kesalahan saat menghapus file: {str(e)}')

    if pdf_file.filename == '':
        flash('No file selected!')
        return redirect(url_for('index'))

    # Save the uploaded PDF temporarily
    input_pdf_path = os.path.join('uploads', pdf_file.filename)
    pdf_file.save(input_pdf_path)

    try:
        # Ambil input nama dan tiket dari form
        nama = request.form.getlist('nama[]')
        tiket = request.form.getlist('tiket[]')
        
        # Buat daftar nama dan jumlah tiket
        nama_list = [(n, int(t)) for n, t in zip(nama, tiket)]
        
        # Jalankan fungsi split_pdf hanya dengan nama dan tiket yang diinput oleh pengguna
        split_pdf(input_pdf_path, output_folder, nama_list)
        
        # Buat file ZIP dari output_folder
        shutil.make_archive('output_files', 'zip', output_folder)
        
        flash('PDF berhasil dipisahkan dan disimpan di folder output!')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}')
    finally:
        # Hapus file PDF sementara setelah proses selesai
        if os.path.exists(input_pdf_path):
            os.remove(input_pdf_path)

    return redirect(url_for('download_zip'))

@app.route('/download')
def download_zip():
    # Pastikan file ZIP sudah ada sebelum mengunduh
    output_zip_path = 'output_files.zip'
    if os.path.exists(output_zip_path):
        return send_file(output_zip_path, as_attachment=True, download_name='output_files.zip')
    else:
        flash("Zip file tidak ditemukan. Silakan coba lagi.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
