from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import ftplib
import os

def generate_certificate(nim, keterangan1,keterangan2,keterangan3, output_folder,nama):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Menentukan nama file berdasarkan nama yang diberikan
    output_path = os.path.join(output_folder, f"{nim}_Sertifikat.pdf")

    # Membuat objek canvas PDF dengan ukuran halaman Letter
    c = canvas.Canvas(output_path, pagesize=landscape(A4))

    # Menambahkan latar belakang
    background_path = "sertifikat.png"  # Ganti dengan path ke file gambar latar belakang
    img = ImageReader(background_path)
    c.drawImage(img, 0, 0, width=A4[1], height=A4[0])

    c.setFont("Helvetica-BoldOblique", 36)
    c.setFillColor(colors.black)

    # Mengatur posisi teks agar berada di tengah kertas
    x = A4[0] / 2

    # Mengatur posisi y agar teks berada di tengah kertas
    y = A4[1] / 2

    # Menambahkan teks ke halaman
    c.drawCentredString(x + 4.2 * cm, y-5* cm, nama)
    

    c.setFont("Times-Roman", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(x + 4.2*cm, y - 7*cm, keterangan1)
    c.drawCentredString(x + 4.2*cm, y- 7.7*cm, keterangan2)
    c.drawCentredString(x + 4.2*cm, y- 8.4*cm, keterangan3)



    # Menyimpan halaman sebagai file PDF
    c.save()
    return 0

def upload_sertifikat(nim):
    # Konfigurasi FTP
    ftp_host = '89.116.179.142'
    ftp_username = 'admin_aryasec1'
    ftp_password = 'uv8cKql-5g%*pDjb'
    ftp_directory = 'certificate'

    # Membuat koneksi FTP
    ftp = ftplib.FTP(ftp_host)
    ftp.login(ftp_username, ftp_password)

    # Beralih ke direktori tujuan
    ftp.cwd(ftp_directory)

    # Membuat direktori qrcodes jika belum ada
    sertifikat_folder = 'certificate'
    if sertifikat_folder not in ftp.nlst():
        ftp.mkd(sertifikat_folder)
    ftp.cwd(sertifikat_folder)

    # Mengunggah file QR code ke server
    sertfikat_file = f"sertifikat/{nim}_sertifikat.pdf"
    with open(sertfikat_file, 'rb') as file:
        ftp.storbinary(f"STOR {nim}_sertifikat.pdf", file)

    # Menutup koneksi FTP
    ftp.quit()