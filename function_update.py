import os, sys, requests, ftplib, base64, qrcode, pyshorteners, bcrypt, re
import requests
from tabulate import tabulate
import matplotlib.pyplot as plt
from colorama import Fore
from getpass import getpass
from tqdm import tqdm
from sertifikat_generate import generate_certificate, upload_sertifikat

sesi_nim = None

# Fungsi untuk menyimpan sesi NIM
def check_name(input_name):
    if re.search(r'\d', input_name):
        return False
    else:
        return True
    

def simpan_sesi_nim(nim):
    global sesi_nim
    sesi_nim = nim
    
def cek_format_tanggal(date_string):
    try:
        day, month, year = date_string.split('-')
        day = int(day)
        month = int(month)
        year = int(year)

        if day < 1 or month < 1 or month > 12 or year <= 2022:
            return False

        # Validasi hari berdasarkan bulan
        if month == 2:  # Februari
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                # Tahun kabisat
                if day > 29:
                    return False
            else:
                # Bukan tahun kabisat
                if day > 28:
                    return False
        elif month in [4, 6, 9, 11]:  # April, Juni, September, November
            if day > 30:
                return False
        else:
            if day > 31:
                return False

        return True
    except ValueError:
        return False

def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if arr[j][2] < arr[j + 1][2]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def shorten_url(url):
    shortener = pyshorteners.Shortener()
    short_url = shortener.tinyurl.short(url)
    return short_url

def print_table(data):
    table = tabulate(data, headers=["No", "Menu"], tablefmt="grid")
    print(table)

def is_data_empty(data):
    if not data:
        return True
    elif isinstance(data, str) and data.strip() == '':
        return True
    elif isinstance(data, (list, dict, set, tuple)) and len(data) == 0:
        return True
    else:
        return False

def authenticate(nim, pin):
    # URL skrip PHP untuk memverifikasi PIN
    url = 'https://api-kelompok6.darkclownsecurity.id/inc/verify_pin.php'
    
    # Data yang akan dikirim melalui permintaan POST
    data = {
        'nim': nim,
        'pin': pin
    }
    
    # Mengirim permintaan POST menggunakan requests
    response = requests.post(url, data=data)
    
    # Memeriksa kode status respons
    if response.status_code == 200:
        return True
    else:
        return False
    
def validate_date(date_string):
    try:
        day, month, year = date_string.split('-')
        day = int(day)
        month = int(month)
        year = int(year)

        if day < 1 or month < 1 or month > 12 or year < 1980 or year > 2008:
            return False

        # Validasi hari berdasarkan bulan
        if month == 2:  # Februari
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                # Tahun kabisat
                if day > 29:
                    return False
            else:
                # Bukan tahun kabisat
                if day > 28:
                    return False
        elif month in [4, 6, 9, 11]:  # April, Juni, September, November
            if day > 30:
                return False
        else:
            if day > 31:
                return False

        return True
    except ValueError:
        return False


def authenticate_nim(nim):
    # URL skrip PHP untuk memverifikasi NIM
    url = 'https://api-kelompok6.darkclownsecurity.id/inc/verify_nim.php'
    
    # Data yang akan dikirim melalui permintaan POST
    data = {
        'nim': nim
    }
    
    # Mengirim permintaan POST menggunakan requests
    response = requests.post(url, data=data)
    
    # Memeriksa kode status respons
    if response.status_code == 200:
        response_data = response.json()
        if response_data['status'] == 'success':
            return True
        else:
            return False
    else:
        return False
    
def generate_qr_code(nim):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    sample_string_bytes = nim.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    qr.add_data("https://api-kelompok6.darkclownsecurity.id/?nim={}".format(base64_string))
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")
    qr_img.save(f"qrcodes/{nim}.png")

def upload_qr_code_to_server(nim):
    # Konfigurasi FTP
    ftp_host = '89.116.179.142'
    ftp_username = 'admin_aryasec1'
    ftp_password = 'uv8cKql-5g%*pDjb'
    ftp_directory = 'qrcodes'

    # Membuat koneksi FTP
    ftp = ftplib.FTP(ftp_host)
    ftp.login(ftp_username, ftp_password)

    # Beralih ke direktori tujuan
    ftp.cwd(ftp_directory)

    # Membuat direktori qrcodes jika belum ada
    qrcodes_directory = 'qrcodes'
    if qrcodes_directory not in ftp.nlst():
        ftp.mkd(qrcodes_directory)
    ftp.cwd(qrcodes_directory)

    # Mengunggah file QR code ke server
    qr_code_file = f"qrcodes/{nim}.png"
    with open(qr_code_file, 'rb') as file:
        ftp.storbinary(f"STOR {nim}.png", file)

    # Menutup koneksi FTP
    ftp.quit()
    
def check_duplicate_name(nama):
    # Endpoint URL
    url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"

    # API key
    apikey = "YXJ5YXNlYw=="

    # Membuat parameter untuk request
    params = {
        "all": apikey
    }

    # Mengirimkan request GET ke endpoint
    response = requests.get(url, params=params)

    # Mengecek status kode respons
    if response.status_code == 200:
        data = response.json()

        # Mendapatkan daftar nama mahasiswa dari respons
        nama_mahasiswa = [mahasiswa['nama'].lower() for mahasiswa in data]

        # Memeriksa keberadaan nama dalam daftar nama mahasiswa
        if nama.lower() in nama_mahasiswa:
            return True  # Nama sudah ada dalam database
        else:
            return False  # Nama belum ada dalam database
    else:
        return None  # Gagal mengambil data dari API


def menu_utama():
    clear()
    print(Fore.WHITE + "================ MENU UTAMA ================")
    data  = [["No","Menu"],[1,"Masuk"],[2,"Daftar"],[3,"Keluar Program"]
    ]
    table = tabulate(data, headers="firstrow", tablefmt="grid",numalign="center", stralign="left")
    print(table)
    while True:
        input_pilih = input(Fore.WHITE + "Masukkan Pilihan : ")
        if input_pilih.isdigit():
            pilih = int(input_pilih)
            while True:
                if pilih == 1:
                    if check_internet():
                        login()
                    else:
                        print(Fore.RED + "Tidak Ada Koneksi Internet")
                        break
                elif pilih == 2 :
                    if check_internet():
                        regist_mahasiswa(nim="",password="",pin="",nama="")
                    else:
                        print(Fore.RED + "Tidak Ada Koneksi Internet")
                        break
                elif pilih == 3 :
                    sys.exit()
                else : 
                    print(Fore.YELLOW + "Pilihan Tidak Ada")
                    break
        else :  
            print(Fore.YELLOW + "Input harus berupa angka. Silakan coba lagi.")
            
def check_internet():
    try:
       response = requests.get("http://google.com", timeout=5)
       return True
    except requests.ConnectionError:
        return False

def login():
    
    url = "https://api-kelompok6.darkclownsecurity.id/users.php"
    clear()
    print(Fore.CYAN + "=======================\n        LOGIN        \n=======================\n")
    print(Fore.YELLOW + "Ketik (b) untuk kembali")
    while True:
        input_nim = input(Fore.CYAN + "NIM : ")

        if is_data_empty(input_nim):
            print(Fore.RED + "Inputan Tidak Boleh Kosong...")
        
        elif not input_nim.isdigit() :
            if input_nim.lower() == "b":
                return menu_utama()
            else:
                print(Fore.YELLOW + "NIM harus berupa angka ...")
        
        if len(input_nim) != 11 :
            print(Fore.YELLOW + "NIM tidak terdiri dari 11 digit ... (Periksa Kembali NIM anda)")
            continue
            
        else :
            # Membuat parameter untuk NIM
            params = {"nim": input_nim}
            # Mengirim permintaan GET ke API
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and data['message'] == "NIM tidak ditemukan di database.":
                    print( Fore.RED + "NIM tidak ada di database!")
                    continue
                else :
                    password_count = 0
                    while True:
                        password = getpass(Fore.CYAN + "Password : ")
                        
                        if bcrypt.checkpw(password.encode('utf-8'), data['password'].encode('utf-8')):
                            if 'role' in data and data['role'] == "admin":
                                menu_admin(nim=input_nim)
                            elif 'role' in data and data['role'] == "mahasiswa": # Simpan sesi NIM setelah login
                                menu_mahasiswa(nim=input_nim,data=data)
                        else:
                            if password_count < 4:
                                password_count += 1
                                print(Fore.RED + "Password salah. Silakan coba lagi. ({} / 3)".format(password_count))
                                if password_count == 3:
                                    print(Fore.RED + "Anda telah salah memasukkan password sebanyak 3 kali.")
                                    update_password_menu(nim=input_nim)
                                continue
            else :
                print("Terjadi kesalahan dalam melakukan permintaan ke API.")
            
def menu_mahasiswa(nim,data):
        clear()
        print(Fore.CYAN + "========= SELAMAT DATANG DI APLIKASI WISUDA =========")
        cek_kehadiran(nim)
        print(Fore.LIGHTBLUE_EX + "=====================================================" + Fore.WHITE)
        options = [
            ["1", "Profile"],
            ["2", "Undangan Wisuda"],
            ["3", "Ubah Password"],
            ["4", "QR Code"],
            ["5", "Sertifikat Wisuda"],
            ["6", "Logout"]
        ]
        print(tabulate(options, headers=["No", "Menu"], tablefmt="grid"))
        while True:
            pilihan = input(Fore.WHITE + "Masukkan Pilihan : ")
            while True:
                if is_data_empty(pilihan):
                    print(Fore.RED + "Anda Belum Memasukkan Pilihan...")
                    break
                
                elif not pilihan.isdigit():
                    print(Fore.YELLOW + "Pilihan Harus Berupa Angka !!! ")
                    break 
                
                else:
                    if pilihan == "1":
                        clear()
                        profile(nim)
                    elif pilihan == "2":
                        clear()
                        undangan_wisuda(nim)
                    elif pilihan == "3":
                        update_password_mahasiswa(nim)
                    elif pilihan == "4":
                        clear()
                        tampil_qrcode(nim,data)
                    elif pilihan == "5":
                        tampil_sertifikat(nim)    
                    elif pilihan == "6":
                        menu_utama()
                    else:
                        print(Fore.YELLOW + "Angka yang dimasukkan Tidak ada")
                        break

def cek_kehadiran(nim):
    url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
    params = {
        "nim": nim
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'message' in data and data['message'] == "Data tidak ditemukan.":
            print("NIM tidak ditemukan.")
        else:
            nama = data['nama']
            hadir = data['hadir']
            if hadir == "Y":
                print(Fore.WHITE + "Yth. {}\nTerimakasih sudah ".format(nama) + Fore.GREEN + "HADIR" + Fore.WHITE + " di acara wisuda.")
            elif hadir == "P":
                print(Fore.WHITE + "Yth. {}\nanda ".format(nama) + Fore.YELLOW + "BELUM HADIR" + Fore.WHITE + " di acara wisuda." + Fore.YELLOW + "\n(Jangan Lupa Gunakan QRCODE untuk absen)")
            elif hadir == "T":
                print(Fore.WHITE + "Yth. {}\nanda ".format(nama) + Fore.RED + "TIDAK HADIR" + Fore.WHITE + " di acara wisuda.")
            else:
                print(Fore.WHITE + "Yth. {}\nanda ".format(nama) + Fore.RED + "TIDAK DIUNDANG" + Fore.WHITE + " di acara wisuda.")
    else:
        print("Terjadi kesalahan dalam melakukan permintaan ke API.")
        
def profile(nim):
    url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
    params = {"nim": nim}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print("=========== DATA MAHASISWA ===========")
        options = [
            ['Nama: ', "{}".format(data['nama'])],
            ['NIM: ', "{}".format(data['nim'])],
            ['Fakultas: ', "{}".format(data['fakultas'])],
            ['Program Studi: ', "{}".format(data['jurusan'])],
            ['Tanggal Lahir: ', "{}".format(data['ttl'])],
            ['NIK: ', "{}".format(data['nik'])],
            ['SKS: ', "{}".format(data['sks'])],
            ['IPK: ', "{}".format(data['ipk'])]
        ]
        print(tabulate(options, tablefmt="grid"))
        while True:
            pilihan = input('Ingin mengujungi menu lain? (y): ')
            if pilihan.lower() == 'y':
                clear()
                menu_mahasiswa(nim,data)
            else:
                print("Pilihan Tidak ada !!!")
    else:
        print("RestApi Bermasalah")
        
def undangan_wisuda(nim):
    url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
    params = {"informasi": "YXJ5YXNlYw=="}

    # Mengirim permintaan GET ke API
    response = requests.get(url, params=params)
    # Memeriksa kode status response
    if response.status_code == 200:
    # Mengambil data JSON dari response
        data = response.json()
            
        url1 = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
        params1 = {"nim": nim}

        # Mengirim permintaan GET ke API
        response1 = requests.get(url1, params=params1)
        # Memeriksa kode status response
        if response1.status_code == 200:
            # Mengambil data JSON dari response
            data1 = response1.json()

            if data1['status_lulus'] == "T":
                options = [
                    [Fore.WHITE + "Status: " + Fore.RED + "Anda Tidak di undang karena Tidak Lulus" + Fore.WHITE],
                    ["Note: " + Fore.RED + "QR Code Tidak akan Diberikan" + Fore.WHITE]
                ]
                headers = ["Status Undangan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Ketik (y) untuk kembali ke Menu Utama : ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan Tidak Ada ...")
                        
            elif data1['undangan'] == 'P':
                options = [
                    [Fore.WHITE + "Status: " + Fore.YELLOW + "Undangan Belum Dikirim" + Fore.WHITE]
                ]
                headers = ["Status Undangan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Ketik (y) untuk kembali ke Menu Utama : ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan Tidak Ada ...")
            
            elif data1['undangan'] == 'Y':
                print("============= UNDANGAN WISUDA =============")
                p = [
                    ["Hari/Tanggal", "{} / {}".format(data[0]['hari'], data[0]['tanggal'])],
                    ["Tempat", "{}".format(data[0]['tempat'])],
                    ["Pukul/Jam", "{}".format(data[0]['jam'])],
                    ["Maps", "{}".format(data[0]['maps'])]]
                print(tabulate(p))
                while True:
                    pilihan1 = input(Fore.WHITE + "Ketik (y) untuk kembali ke Menu Utama : ")
                    if pilihan1.lower() == 'y':
                        clear()
                        return menu_mahasiswa(nim,data) # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan Tidak Ada ...")
        else:
            print("API ERROR")
    else:
        print("Gagal mengambil data dari API")

def update_password_mahasiswa(nim):
    pin_count = 0
    print(Fore.RED + "Note: Untuk memastikan bahwa ini anda, silahkan masukan PIN untuk mengkonfirmasi." + Fore.GREEN)
    while True:    
        pin = getpass(Fore.WHITE + "Ketik (b) untuk kembali kemenu Mahasiswa.\nMasukkan PIN : ")
        # Memverifikasi PIN
        if authenticate(nim, pin):
            new_password = getpass("Masukkan password baru: ")

            # Mengenkripsi password baru menggunakan Bcrypt
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            # URL skrip PHP yang dituju
            url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_password.php'

            # Data yang akan dikirim melalui permintaan POST
            data = {
                'nim': nim,
                'new_password': hashed_password.decode('utf-8')  # Mengubah byte menjadi string sebelum dikirim
            }

            # Mengirim permintaan POST menggunakan requests
            response = requests.post(url, data=data)

            # Memeriksa kode status respons
            if response.status_code == 200:
                print(Fore.GREEN + 'Password berhasil diperbarui.')
            else:
                print(Fore.RED + 'Gagal memperbarui password.')
                
        elif is_data_empty(pin):
            print(Fore.RED + "Data Tidak Boleh Kosong...")
            
        elif not pin.isdigit:
            if pin.lower() == "b":
                menu_mahasiswa(nim,data)
            else :
                print(Fore.YELLOW + "Inputan Harus Angka....") 

        elif len(pin) != 5:
            print(Fore.YELLOW + "PIN Terdiri harus dari 5 digit.")
        
        elif pin_count < 6:
            pin_count += 1
            print(Fore.RED + "Pin yang Dimasukkan Salah, ({}/5)".format(pin_count))
            if pin_count == 5:    
                print(Fore.YELLOW + "ANDA SUDAH MEMASUKKAN PIN SEBANYAK 5 kali\nHUBUNGI ADMIN UNTUK MENGUBAH PASSWORD DAN PIN ...\nEmail : customarecare@esaunggul.ac.id")
                menu_utama()
            continue
        else:
            print(Fore.RED + 'PIN salah. Autentikasi gagal.')

        while True:
            pilihan1 = input(Fore.WHITE + "Ketik (y) untuk kembali ke Menu Utama : ")
            if pilihan1.lower() == 'y':
                menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
            else:
                print("Pilihan Tidak Ada ...")

def update_password_menu(nim):
    pin_count = 0
    print(Fore.YELLOW + "Note: Untuk memastikan bahwa akun ini punya anda, silahkan masukan PIN untuk mengkonfirmasi." + Fore.GREEN)
    while True:    
        pin = getpass(Fore.WHITE + "Masukkan PIN : ")
        # Memverifikasi PIN
        if is_data_empty(pin):
            print("Data Kosong...")
        elif not pin.isdigit():
            print ("PIN Harus Berupa Angka ...")
        elif len(pin) != 5:
            print("PIN Terdiri dari 5 digit.")
        else:
            if authenticate(nim, pin):
                new_password = getpass("Masukkan password baru: ")

                # Mengenkripsi password baru menggunakan Bcrypt
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                # URL skrip PHP yang dituju
                url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_password.php'

                # Data yang akan dikirim melalui permintaan POST
                data = {
                    'nim': nim,
                    'new_password': hashed_password.decode('utf-8')  # Mengubah byte menjadi string sebelum dikirim
                }

                # Mengirim permintaan POST menggunakan requests
                response = requests.post(url, data=data)

                # Memeriksa kode status respons
                if response.status_code == 200:
                    print(Fore.GREEN + 'Password berhasil diperbarui.')
                    print(Fore.YELLOW + 'Silahkan Login Ulang ...')
                    menu_utama()
                else:
                    print(Fore.YELLOW + 'Gagal memperbarui password.')

            elif pin_count < 6:
                    pin_count += 1
                    print(Fore.RED + "Pin yang Dimasukkan Salah, ({}/5)".format(pin_count))
                    if pin_count == 5:    
                        print(Fore.YELLOW + "ANDA SUDAH MEMASUKKAN PIN SEBANYAK 5 kali\nHUBUNGI ADMIN UNTUK MENGUBAH PASSWORD DAN PIN ...\nEmail : customarecare@esaunggul.ac.id")
                        while True:
                            pilih = input(Fore.WHITE+"Masukkan (y) untuk kemenu utama : ")
                            if pilih == 'y':
                                menu_utama()
                            else:
                                print("Pilihan Tidak Ada")
                    continue

def tampil_qrcode(nim,data):
        url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
        # Membuat parameter untuk NIM
        params = {"nim": nim}
        # Mengirim permintaan GET ke API
        response = requests.get(url, params=params)
        # Memeriksa kode status response
        if response.status_code == 200:
        # Mengambil data JSON dari response
            data = response.json()
            stored_nim = data['nim']
            if data['qrcode'] == "T":
                options = [[Fore.WHITE + "Status: " + Fore.RED + "Anda Tidak di undang karena tidak memenuhi syarat kelulusan.." + Fore.WHITE],
                            [Fore.WHITE + "Note: " + Fore.RED + "QR Code Tidak akan diberikan" + Fore.WHITE]]
                headers = ["Status QR CODE Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input("Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
            
            elif data['hadir'] == 'Y':
                options = [[Fore.WHITE + "Status: " + Fore.GREEN + "Anda Sudah Melakukan Absensi" + Fore.WHITE],
                            [Fore.WHITE + "Note: " + Fore.YELLOW + "Silahkan Cek Kembali Menu Sertifikat Setelah Selesai Acara." + Fore.WHITE]]
                headers = ["Status QR CODE Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input("Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
            
            elif data['qrcode'] == "Y":
                url = "https://api-daa.darkclownsecurity.id/qrcodes/qrcodes/{}.png".format(stored_nim)
                options = [["QRCODE", "{}".format(shorten_url(url))],
                        ['NOTE', "DIATAS ADALAH QRCODE UNTUK KEHADIRAN \nBUKA LINK DI ATAS LALU TUNJUKAN KE PANITIA \nUNTUK DI SCAN QRCODE NYA"]]
                print_table(options)
                pilihan1 = input("Apakah Anda ingin kembali ke menu lain? (y): ")
                while True:
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
            
            elif data['qrcode'] == 'P':
                options = [[Fore.WHITE + "Status: " + Fore.YELLOW + "Anda di undang" + Fore.WHITE],
                            [Fore.WHITE + "Note: " + Fore.YELLOW + "QR Code akan diberikan H-2 Jam Sebelum Acara" + Fore.WHITE]]
                headers = ["Status QR CODE Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input("Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
                    
            
            
            else :
                options = [[Fore.WHITE + "Status: " + Fore.YELLOW + "QR CODE Belum Di Kirimm" + Fore.WHITE]]
                headers = ["Status QR CODE Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input("Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
                    
def regist_mahasiswa(nim,password,pin,nama):
    clear()
    print (Fore.LIGHTMAGENTA_EX + "===================")
    print ("      REGISTER     ")
    print ("===================")
    while True:
        nim = input(Fore.YELLOW + "Ketik (b) untuk kembali\n" + Fore.WHITE + "Masukkan NIM (11 angka): ")

        #cek apakah file kosong ?
        if is_data_empty(nim):
            print(Fore.RED + "NIM KOSONGG! HARAP ISI BERUPA ANGKA" + Fore.CYAN)   
        
        else:
            url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
                # Membuat parameter untuk nim
            params = {
                "nim": nim
                }
            # Mengirim permintaan GET ke API
            response = requests.get(url, params=params)
            
            if not nim.isdigit():
                if nim.lower() == 'b':
                    return menu_utama()
                else:
                    print( Fore.YELLOW + "Harus Berupa Angka ...")
                    continue
            
            elif len(nim) != 11:
                print("Harus Terdiri dari 11 digit Angka.")
                continue

            elif not authenticate_nim(nim):
                print( Fore.YELLOW + "Gagal menambahkan akun. NIM sudah terdaftar.")
                lagi = input( Fore.WHITE +"Apakah anda ingin melanjutkan di NIM yang berbeda? (y/t): ")
                if lagi.lower() == 'y':
                    return
                elif lagi.lower() == 't':
                    menu_utama()
                else :
                    print("Pilihan Tidak ada ...")

            # Memeriksa kode status response
            if response.status_code == 200:
                # Mengambil data JSON dari response
                data = response.json()
                # Memeriksa apakah NIM ada di dalam data
                if 'message' in data and data['message'] == 'NIM tidak ditemukan di database.':
                    while True:
                        password = getpass("Masukkan Password: ")
                        if is_data_empty(password):
                            print(Fore.RED + "PASSWORD KOSONG! HARAP ISI DENGAN BENAR." + Fore.WHITE)
                            continue
                        
                        else:
                            print(Fore.RED + "Notifikasi: Pastikan Anda mengingat PIN untuk mengubah password")
                            
                            while True:
                                pin = getpass(Fore.GREEN +"Masukkan PIN (5 angka): ", stream=None)
                                if is_data_empty(pin):
                                    print(Fore.RED + "Inputan tidak boleh kosong...")
                                
                                elif not pin.isdigit():
                                    print(Fore.RED + "PIN HARUS BERUPA ANGKA !!!")
                                    continue
                                elif not len(pin) == 5:
                                    print( Fore.YELLOW + "PIN HARUS BERISI 5 DIGIT")
                                    continue
                                else:
                                       while True:
                                            nama_input = input(Fore.WHITE + "Masukkan Nama lengkap : ")
                                            if is_data_empty(nama_input):
                                                print(Fore.RED + "NAMA KOSONG! HARAP ISI DENGAN BENAR." + Fore.YELLOW)
                                                continue
                                            elif not check_name(nama_input):
                                                print(Fore.RED + "Nama Tidak Boleh Terdapat Angka...")
                                                continue
                                            elif check_duplicate_name(nama_input):
                                                nama = nama_input.title()
                                                print(Fore.RED + '[' + Fore.WHITE + 'Oops!' + Fore.RED + ']' + Fore.YELLOW + "Nama Sudah ada dalam database. Silahkan pilih nama lain.")
                                                continue
                                            else:
                                                nama = nama_input.title()
                                                pil_fakultas(nim,password,pin,nama=nama,fakultas="")

def pil_fakultas(nim,password,pin,nama,fakultas):
    options = [["1", "Fakultas Ekonomi dan Bisnis"],
                ["2", "Fakultas Teknik"],
                ["3", "Fakultas Desain & Industri Kreatif"],
                ["4", "Fakultas Ilmu  Ilmu Kesehatan"],
                ["5", "Fakultas Hukum"],
                ["6", "Fakultas Ilmu Komunikasi"],
                ["7", "Fakultas Fisioterapi"],
                ["8", "Fakultas Psikologi"],
                ["9", "Fakultas Ilmu Komputer"],
                ["10", "Fakultas Keguruan dan Ilmu Pendidikan"]]
    headers = ["Pilihan", "Nama Fakultas"]
    clear()
    print(tabulate(options, headers=headers, tablefmt="grid"))
    while True:
        pilfakultas = input("Masukkan Fakultas : ")
        if is_data_empty(pilfakultas):
            print(Fore.RED + "FAKULTAS KOSONG! HARAP ISI DENGAN BENAR." + Fore.WHITE)
            continue
        elif not pilfakultas.isdigit():
            print("Harus Memasukkan Angka .. ")
            continue
        else:
            if pilfakultas == "1":
                fakultas = "Fakultas Ekonomi dan Bisnis"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "2":
                fakultas = "Fakultas Teknik"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "3":
                fakultas = "Fakultas Desain & Industri Kreatif"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "4":
                fakultas = "Fakultas Ilmu  Ilmu Kesehatan"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "5":
                fakultas = "Fakultas Hukum"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "6":
                fakultas = "Fakultas Ilmu Komunikasi"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "7":
                fakultas = "Fakultas Fisioterapi"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "8":
                fakultas = "Fakultas Psikologi"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "9":
                fakultas = "Fakultas Ilmu Komputer"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            elif pilfakultas == "10":
                fakultas = "Fakultas Keguruan dan Ilmu Pendidikan"
                fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan="")
            else:
                print("Data yang Dipilih Tidak Ada")
                return
            
def fakultas_jurusan(nim,password,nama,pin,fakultas,jurusan):
    clear()
    while True:
        if fakultas == "Fakultas Ekonomi dan Bisnis":
            options = [
                ["1", "Manajemen Bisnis"],
                ["2", "Akuntansi Sektor Bisnis"]
            ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Teknik":
            options = [
                ["1", "Teknik Industri"],
                ["2", "Perencanaan Wilayah & Kota"],
                ["3", "Survei dan Pemetaan"],
                ["4", "Teknik Sipil"]
                ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Desain & Industri Kreatif":
            options = [
                ["1", "Desain Komunikasi Visual"],
                ["2", "Desain Produk"],
                ["3", "Desain Interior"]
            ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Ilmu  Ilmu Kesehatan":
            options = [
                ["1", "Kesehatan Masyarakat"],
                ["2", "Ilmu Gizi"],
                ["3", "Profesi Dietisien"],
                ["4", "Ilmu Keperawatan"],
                ["5", "Profesi Ners"],
                ["6", "Rekam Medis"],
                ["7", "Manajemen Informasi Kesehatan"],
                ["8", "Bioteknologi"],
                ["9", "Farmasi"]
            ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Hukum":
            options = [
                ["1", "Hukum"]
                ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Ilmu Komunikasi":
            options = [
                ["1", "Marketing Communication (Periklanan)"],
                ["2", "Jurnalistik"],
                ["3", "Hubungan Masyarakat (Public Relations)"],
                ["4", "Broadcasting (Penyiaran)"]
            ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Fisioterapi":
            options = [
                ["1", "Fisioterapi"],
                ["2", "Profesi Fisioterapi"]
                ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Psikologi":
            options = [
                ["1", "Psikologi"]
                ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Ilmu Komputer":
            options = [
                ["1", "Teknik Informatika"],
                ["2", "Sistem Informasi"]
                ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
    
            print(tabulate(options, headers=headers, tablefmt="grid"))
        elif fakultas == "Fakultas Keguruan dan Ilmu Pendidikan":
            options = [
                ["1", "Pendidikan Guru SD (PGSD)"],
                ["2", "Pendidikan Bahasa Inggris"]
                ]
            headers = ["Pilihan", "Nama Jurusan"]
            clear()
            print(tabulate(options, headers=headers, tablefmt="grid"))
        else:
            print(fakultas)
            print("Fakultas Tidak Valid")
            break
        jurusan = input("Masukkan Program Studi : ")
        if is_data_empty(jurusan):
            print(Fore.RED + "Program Studi KOSONG! HARAP ISI DENGAN BENAR." + Fore.GREEN)
            continue
        else:
            selected_jurusan = [option for option in options if option[0] == jurusan]
            if selected_jurusan:
                jurusan = selected_jurusan[0][1]
                data_pribadi(nim,password,nama,pin,fakultas,jurusan)
            else:
                print("Pilihan Jurusan Tidak Valid")
                continue

def data_pribadi(nim,password,nama,pin,fakultas,jurusan):
    # Validasi tanggal lahir
    clear()
    while True:

        ttl = input(Fore.WHITE + "Masukkan Tanggal Lahir (02-02-2004): ")
        if is_data_empty(ttl):
            print(Fore.RED + "TANGGAL KOSONG! HARAP ISI DENGAN BENAR." + Fore.GREEN)
            continue
        else:
            if not validate_date(ttl):
                print (Fore.YELLOW + "Format tanggal lahir tidak valid")
                    
            else:
                while True:
                    nik = input(Fore.WHITE + "Masukkan NIK anda (16 angka): ")
                    if is_data_empty(nik):
                        print(Fore.RED + "NIK KOSONG! HARAP ISI DENGAN BENAR." + Fore.GREEN)
                        continue
                    elif not nik.isdigit():
                        print(Fore.YELLOW + "NIK harus berupa angka")
                        continue
                    elif len(nik) != 16:
                        print(Fore.YELLOW + "NIK harus 16 Digit.")
                        continue
                    else:
                        while True:
                            skripsi_input = input(Fore.WHITE + "Masukkan Judul Skripsi : ")
                            if is_data_empty(skripsi_input):
                                print(Fore.RED + "SKRIPSI KOSONG! HARAP ISI DENGAN BENAR.")
                                continue
                            else:
                                skripsi = skripsi_input.title()
                                while True:
                                    sks = input(Fore.WHITE + "Masukkan Jumlah SKS : ")
                                    if is_data_empty(sks):
                                        print(Fore.RED + "SKS KOSONG! HARAP ISI DENGAN BENAR.")
                                        continue
                                    elif not sks.isdigit():
                                        print(Fore.YELLOW + "Harus Berupa Angka")
                                        continue
                                    else:
                                        while True:
                                            ipk = input(Fore.WHITE + "Masukkan IPK anda (3,50) : ")
                                            if is_data_empty(ipk):
                                                print(Fore.RED + "IPK KOSONG! HARAP ISI DENGAN BENAR." + Fore.GREEN)
                                                continue
                                        
                                            elif "," not in ipk:
                                                print("\033[91mFormat penulisan IPK salah! Gunakan tanda koma (,)\033[0m")
                                                continue
                            
                                            elif ipk > "4,00" or ipk < "0,00":
                                                print(Fore.YELLOW + "Nominal IPK Tersebut Tidak Ada ... ")
                                                continue
                                            

                                            else:
                                                # Mengenkripsi password menggunakan bcrypt
                                                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                                                if sks >= "144":
                                                    status_lulus = 'Y'
                                                        
                                                else:
                                                    status_lulus = 'T'
                                                    
                                                if ipk > "3,99":
                                                    status_ipk = 'Summa Cumlaude'
                                                elif ipk > "3,79":
                                                    status_ipk = 'Magna Cumlaude'
                                                elif ipk > "3,50":
                                                    status_ipk = 'Cumlaude'
                                                else:
                                                    status_ipk = ''
                                                    
                                                if status_lulus == 'T':
                                                    hadir = 'NULL'
                                                else :
                                                    hadir = 'P'
                                                    
                                                endpoint = "https://api-kelompok6.darkclownsecurity.id/inc/input.php"
                                                # Mengirim permintaan POST ke skrip PHP dengan kunci yang sesuai
                                                response = requests.post(endpoint, data={
                                                    'nama': nama,
                                                    'pin': pin,
                                                    'password_asli': password,
                                                    'password': hashed_password.decode('utf-8'),
                                                    'role': 'mahasiswa',
                                                    'nim': nim,
                                                    'jurusan': jurusan,
                                                    'fakultas': fakultas,
                                                    'ttl': ttl,
                                                    'nik': nik,
                                                    'skripsi': skripsi,
                                                    'sks': sks,
                                                    'ipk': ipk,
                                                    'status_lulus': status_lulus,
                                                    'undangan': 'P',
                                                    'hadir': hadir,
                                                    'qrcode': 'NULL',
                                                    'status_ipk': status_ipk
                                                    })
                                                if response.status_code == 200:
                                                    print(Fore.GREEN + "Berhasil menambahkan data ke database!"+ Fore.GREEN)
                                                    
                                                while True:
                                                    #Tanyakan apakah ingin melakukan registrasi ulang atau kembali ke menu login
                                                    pilihan = input(Fore.WHITE + "Apakah Anda ingin melakukan registrasi ulang? (y/n): ")
                                                    if pilihan.lower() == 'y':
                                                        clear()
                                                        regist_mahasiswa(nim,password,pin,nama)
                                                    elif pilihan.lower() == 'n':
                                                        clear()
                                                        menu_utama()
                                                    else:
                                                        print(Fore.RED + "Pilihan Tidah Ada !!!")

def menu_admin(nim):
    clear()
    options = [
        ["1", "Edit Informasi Wisuda"],
        ["2", "Daftar Peserta Wisuda"],
        ["3", "Laporan Kehadiran"],
        ["4", "Ubah Password"],
        ["5", "Akun Administrator"],
        ["6", "Grafik peserta wisuda"],
        ["7", "Data Mahasiswa"],
        ["8", "Logout"],
        ["9", "Keluar"]
    ]
    print(Fore.WHITE + "============ [ SELAMAT DATANG ADMIN ] ==============")
    print_table(options)
    while True:
        pilihan = input( Fore.WHITE + "Masukan Pilihan: ")
        if is_data_empty(pilihan):
            print(Fore.RED + "Data tidak boleh kosong... ")
        elif not pilihan.isdigit():
            print(Fore.YELLOW + "Harus Berupa Angka")
        elif pilihan == "1":
            edit_informasi_wisuda(nim)
        elif pilihan == "2":
            daftar_peserta_wisuda()
        elif pilihan == "3":
            laporan(nim)
        elif pilihan == "4":
            update_password_admin(nim)
        elif pilihan == "5":
            akun_administrator(nim)
        elif pilihan == "6":
            grafik_wisuda(nim)
        elif pilihan == "7":
            data_mahasiswa(nim)
        elif pilihan == "8":
            menu_utama()
        elif pilihan == "9":
            print("Terima Kasih Telah Menggunakan Aplikasi Kami ...")
            sys.exit()
        else:
            print(Fore.YELLOW + "Angka yang dipilih Tidak Ada ...")
            continue
        
def edit_informasi_wisuda(nim):
    url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
    params = {
        "informasi":"YXJ5YXNlYw=="
    }
    response = requests.get(url,params=params)

    if response.status_code == 200 :
        data = response.json()
        
        data = [
            ["Hari/Tanggal", "{} / {}".format(data[0]['hari'], data[0]['tanggal'])],
            ["Tempat", "{}".format(data[0]['tempat'])],
            ["Pukul/Jam", "{}".format(data[0]['jam'])],
            ["Maps", "{}".format(data[0]['maps'])],
            ["Kuota Real", "{}".format(data[0]['kuota'])],
            ["Note", "{}".format(data[0]['note'])]
            ]
        clear()
        print(Fore.WHITE + "============ [ EDIT INFROMASI WISUDA ] ============")
        print_table(data)
        while True:
            pilihan = input(Fore.WHITE + "Ketik (y) untuk mengedit informasi, Ketik (m) untuk kemenu Admin : ")
            if pilihan.lower() == "y":
                endpoint = "https://api-kelompok6.darkclownsecurity.id/inc/input_informasi.php"
                while True:
                    hari_hari = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu']
                    while True:
                        hari_input = input(Fore.WHITE + "Hari (Senin) : ")
                        if hari_input.title() not in hari_hari:
                            print(Fore.YELLOW + "Yang anda masukkan bukan hari.")
                            continue
                        else :
                            hari = hari_input.title()
                            break
                    while True:
                        input_tanggal = input("Tanggal (17-07-2023) : ")
                        if cek_format_tanggal(input_tanggal):
                            tanggal = input_tanggal
                            break
                        else:
                            print("Format Tanggal yang Anda Masukkan salah.")
                            continue
                    tempat = input("Tempat : ")
                    jam = input("Jam (18.00 - Selesai) : ")
                    maps = input("Maps (maps.google) : ")
                    kuota = input("Kuota : ")
                    note = input("Note : ")

                    # Mengirim permintaan POST ke skrip PHP dengan kunci yang sesuai
                    response = requests.post(endpoint, data={
                            'hari': hari,
                            'tanggal': tanggal,
                            'tempat': tempat,
                            'jam': jam,
                            'maps': maps,
                            'kuota': kuota,
                            'note': note
                    })

                    if response.status_code == 200:
                        print(Fore.GREEN + "Berhasil menambahkan data ke database!")
                        while True:
                            pil = input(Fore.WHITE + "Apakah anda ingin edit lagi? (y/n): ")
                            if pil.lower() == 'y':
                                clear()
                                print(Fore.WHITE + "============ [ EDIT INFROMASI WISUDA ] ============")
                                print_table(data)
                                return 
                            elif pil.lower() == 'n':
                                return edit_informasi_wisuda(nim)
                            else:
                                print(Fore.YELLOW + "Pilihan yang anda Masukkan Tidak Ada.")
                                continue
                    else:
                        print(Fore.RED + "Gagal menambahkan data ke database.")
            elif pilihan.lower() == 'm':
                menu_admin(nim)
            else :
                print(Fore.YELLOW + "Pilihan tersebut tidak ada...")
                continue
    else :
        print("Ada Kesalahan pada API.")
        
        
def peserta_wisuda():
    url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"

    params = {
        "all": "YXJ5YXNlYw=="
    }

    # Mengirim permintaan GET ke API
    response = requests.get(url, params=params)

    # Memeriksa kode status response
    if response.status_code == 200:
        # Mengambil data JSON dari response
        data = response.json()

        # Menyiapkan data untuk tabel
        table_data = []
        for mahasiswa in data:
            nim = '\033[92m' + mahasiswa['nim'] + '\033[0m'  # Warna hijau
            nama = '\033[92m' + mahasiswa['nama'] + '\033[0m'  # Warna hijau
            table_data.append([nim,nama])
            
        headers = ["NIM","NAMA"]
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    
    else:
        print(Fore.RED + "Gagal mengambil data dari API")
    
def daftar_peserta_wisuda():
        url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"

        params = {
            "all": "YXJ5YXNlYw=="
        }

        # Mengirim permintaan GET ke API
        response = requests.get(url, params=params)

        # Memeriksa kode status response
        if response.status_code == 200:
            # Mengambil data JSON dari response
            data = response.json()

            # Menyiapkan data untuk tabel
            table_data = []
            for mahasiswa in data:
                nim = '\033[92m' + mahasiswa['nim'] + '\033[0m'  # Warna hijau
                nama = '\033[92m' + mahasiswa['nama'] + '\033[0m'  # Warna hijau
                fakultas = '\033[92m' + mahasiswa['fakultas'] + '\033[0m'  # Warna hijau
                jurusan = '\033[92m' + mahasiswa['jurusan'] + '\033[0m'  # Warna hijau
                status = mahasiswa['status_lulus']
                undangan = mahasiswa['undangan']
                hadir = mahasiswa['hadir']
                if status == 'Y':
                    status = '\033[92m' + 'Lulus' + '\033[0m'  # Warna hijau
                else:
                    status = '\033[91m' + 'Tidak Lulus' + '\033[0m'  # Warna merah

                if undangan == 'P':
                    undangan = '\033[92m' + 'Ter-undang' + '\033[0m'
                else:
                    undangan = '\033[91m' + 'Menunggu Undangan Terkirim' + '\033[0m'

                if hadir == 'Y':
                    hadir = '\033[92m' + 'Hadir' + '\033[0m'
                else:
                    hadir = '\033[91m' + 'Tidak Hadir' + '\033[0m'

                table_data.append([nim, nama, fakultas, jurusan, status, undangan, hadir])

            # Menentukan header tabel
            headers = ["NIM", "NAMA", "FAKULTAS", "JURUSAN", "STATUS", "UNDANGAN", "HADIR"]

            # Mencetak tabel menggunakan tabulate
            clear()
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

        else:
            print(Fore.RED + "Gagal mengambil data dari API")

        while True:
            lagi = input(Fore.WHITE + "Ketik (y) untuk kembali kemenu : ")
            if lagi.lower() == 'y':
                menu_admin(nim)
            else:
                print(Fore.YELLOW + "Pilihan yang anda input tidak ada.")
                continue

def laporan(nim):
    options = [
        ["1", "Daftar Hadir peserta wisuda"],
        ["2", "Daftar Tidak Hadir peserta wisuda"],
        ["3", "Kembali ke Menu Admin"]
    ]
    clear()
    print(Fore.WHITE + "============= [ DATA KEHADIRAN WISUDA ] ==============")
    print_table(options)
    while True:
        pilihan = input(Fore.WHITE + "Masukkan Pilihan: ")

        if pilihan == "1":
            print("============= [ Daftar HADIR peserta wisuda ] ==============")
            url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"

            params = {
                "all": "YXJ5YXNlYw=="
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                table_data = []

                for mahasiswa in data:
                    nim1 = mahasiswa['nim']
                    nama = mahasiswa['nama']
                    hadir = mahasiswa['hadir']

                    if hadir == "Y":
                        table_data.append([nama, nim1])

                if table_data:
                    headers = ["Nama", "NIM"]
                    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
                else:
                    print(Fore.RED + "Tidak ada mahasiswa yang hadir.")
            else:
                print("Gagal mengambil data dari API")
            while True:
                lagi = input(Fore.WHITE + "Ketik (y) untuk ke Menu Utama, Ketik (b) untuk ke Menu Laporan : ")
                if lagi.lower() == 'y':
                    clear()
                    menu_admin(nim)
                elif lagi.lower() == 'b':
                    laporan(nim)
                else:
                    print(Fore.YELLOW + "Pilihan tidak ada!!!")
                    
        elif pilihan == "2":
            print("============= [ Daftar TIDAK HADIR peserta wisuda ] ==============")
            url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"

            params = {
                "all": "YXJ5YXNlYw=="
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                table_data = []

                for mahasiswa in data:
                    nim = mahasiswa['nim']
                    nama = mahasiswa['nama']
                    hadir = mahasiswa['hadir']

                    if hadir == "T":
                        table_data.append([nama, nim])

                if table_data:
                    headers = ["Nama", "NIM"]
                    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
                else:
                    print(Fore.RED + "Tidak ada mahasiswa yang hadir.")
            else:
                print("Gagal mengambil data dari API")
            while True:
                lagi = input(Fore.WHITE + "Ketik (y) untuk ke Menu Utama, Ketik (b) untuk ke Menu Laporan : ")
                if lagi.lower() == 'y':
                    clear()
                    menu_admin(nim)
                elif lagi.lower() == 'b':
                    laporan(nim)
                else:
                    print(Fore.YELLOW + "Pilihan tidak ada!!!")
                    continue
                
        elif pilihan == "3":
            clear()
            menu_admin(nim)
        else :
            print(Fore.YELLOW + "Pilihan Tidak Ada...")

def update_password_admin(nim):
    pin_count = 0
    clear()
    print(Fore.RED + "Note: Untuk memastikan bahwa ini anda, silahkan masukan PIN untuk mengkonfirmasi.\nKetik (b) lalu enter untuk Kembali Kemenu Admin")
    while True:    
        pin = getpass(Fore.WHITE + "Masukkan PIN : ")
        
        # Memverifikasi PIN
        if authenticate(nim, pin):
            new_password = getpass("Masukkan password baru: ")

            # Mengenkripsi password baru menggunakan Bcrypt
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            # URL skrip PHP yang dituju
            url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_password.php'

            # Data yang akan dikirim melalui permintaan POST
            data = {
                'nim': nim,
                'new_password': hashed_password.decode('utf-8')  # Mengubah byte menjadi string sebelum dikirim
            }

            # Mengirim permintaan POST menggunakan requests
            response = requests.post(url, data=data)

            # Memeriksa kode status respons
            if response.status_code == 200:
                print(Fore.GREEN + 'Password berhasil diperbarui.')
            else:
                print(Fore.YELLOW + 'Gagal memperbarui password.')

        elif is_data_empty(pin):
            print(Fore.RED + "Inputan Tidak Boleh Kosong.")
            continue
        
        elif not pin.isdigit():
            if pin.lower() == "b":
                menu_admin(nim)
            else :
                print(Fore.YELLOW + "Inputan Harus Angka...")
                continue

        elif len(pin) != 5:
            print(Fore.YELLOW + "PIN Terdiri dari 5 digit.")
            continue
        
        elif pin_count < 6:
            pin_count += 1
            print(Fore.RED + "Pin yang Dimasukkan Salah, ({}/5)".format(pin_count))
            if pin_count == 5:    
                print(Fore.YELLOW + "ANDA SUDAH MEMASUKKAN PIN SEBANYAK 5 kali\nHUBUNGI ADMIN LAIN UNTUK MENGUBAH PASSWORD DAN PIN ...")
                while True:
                    pilihan = input(Fore.WHITE + "Ketik (y) untuk kembali kemenu admin : ")
                    if pilihan.lower()  == "y":
                        menu_admin(nim)
                    else:
                        print(Fore.YELLOW + "Pilihan TIdak Ada...")
                continue
        else:
            print(Fore.RED + 'PIN salah. Autentikasi gagal.')


def akun_administrator(nim):
    options = [
    ["1", "Tambah Akun Administrator"],
    ["2", "Lihat Data Administrator"],
    ["3", "Hapus Data Administrator"],
    ["4", "Ubah Data Administrator"],
    ["5", "Lihat Akun Mahasiswa"],
    ["6", "Kembali Ke Menu Admin"]
    ]
    while True:
        clear()
        print(Fore.WHITE + "============ [ AKUN ADMINISTRATOR ] ==============")
        print_table(options)
        while True:
            pilih = input(Fore.WHITE + "Masukkan Pilihan: ")
            
            if is_data_empty(pilih):
                print(Fore.RED + "Inputan Tidak Boleh Kosong...")

            elif not pilih.isdigit():
                print(Fore.YELLOW + "Harus Berupa Angka...")
            
            elif pilih == "1":
                clear()
                tambah_akun_admin()
                        
            elif pilih == "2":
                while True:
                    clear()
                    print("============== [ DATA ADMIN ] ==============")
                    lihat_data_admin()
                    pilih = input("Kembali Kemenu utama Admin Ketik (m), kembali Ketik (b) : ")
                    if pilih.lower() == "m":
                        clear()
                        menu_admin(nim)
                    elif pilih.lower() == "b":
                        clear()
                        return akun_administrator(nim)
                    else: 
                        print("Pilihan Tidak Ada ...")
                        
            elif pilih == "3":
                clear()
                print("================ [ DELETE ADMIN ] ===============")
                delete_admin(nim)
                pilih = input("Kembali Kemenu utama Admin Ketik (m), kembali Ketik (b) : ")
                if pilih.lower() == "m":
                    menu_admin(nim)
                elif pilih.lower() == "b":
                    return akun_administrator(nim)
                else:
                    print("Pilihan Tidak Ada ...")
                    
            elif pilih == "4":
                while True:
                    clear()
                    print("============ [ EDIT ADMIN ] =================")
                    lihat_data_admin()
                    update_admin(nim)
                    while True:
                        pilih = input("Kembali kemenu utama Admin Ketik (m), kembali Ketik (b) : ")
                        if pilih.lower() == "m":
                            menu_admin(nim)
                        elif pilih.lower() == "b":
                            return akun_administrator(nim)
                        else :
                            print("Pilihan tidak ada !!!")
                            continue
            elif pilih == "5":
                while True:
                    clear()
                    print("=============== [ LIHAT AKUN MAHASISWA ] =============")
                    lihat_akun_mahasiswa()
                    while True:
                        pilih = input("Kembali kemenu utama Admin Ketik (m), kembali Ketik (b) : ")
                        if pilih.lower() == "m":
                            menu_admin(nim)
                        elif pilih.lower() == "b":
                            return akun_administrator(nim)
                        else :
                            print("Pilihan tidak ada !!!")
                            continue
            elif pilih == "6":
                    menu_admin(nim)
            else:
                print(Fore.RED + "PILIHAN TIDAK ADA!")

def tambah_akun_admin():
    lihat_data_admin()
    print("============ [ TAMBAH AKUN ADMINISTRATOR ] ==============")
    while True:
        nim = input(Fore.WHITE + "Ketik (b) untuk kembali.\nMasukkan NIM anda : ")
        if is_data_empty(nim):
            print(Fore.RED + "Inputan Tidak Boleh Kosong...")
                    
        elif not nim.isdigit():
            if nim.lower() == "b":
                akun_administrator(nim)
            else:
                print(Fore.YELLOW + "Harus Berupa Angka..")
                continue
                    
        elif not authenticate_nim(nim):
            print(Fore.RED + "Gagal menambahkan akun. NIM sudah terdaftar.")
            while True:
                lagi = input(Fore.WHITE + "Masukkan (y) jika ingin memasukkan kembali NIM yang berbeda, Masukkan (m) jika ingin kembali ke menu Admin : ")
                if lagi.lower() == 'y':
                    break
                elif lagi.lower() == 'm':
                    menu_admin(nim)
                else :
                    print(Fore.YELLOW + "Pilihan Tidak ada ...")
                    continue
        elif len(nim) == 11:
            while True:
                nama_input = input("Masukkan nama: ")
                nama = nama_input.title()
                password = getpass("Masukkan password: ")
                print(Fore.RED + "Note: pastikan Anda ingat PIN untuk mereset password Anda!")
                while True:
                    pin = getpass(Fore.WHITE +"Masukkan PIN (5 angka): ")
                    if not pin.isdigit():
                        print("PIN Harus berupa angka...")
                        continue
                    elif not len(pin) == 5:
                        print("PIN Harus terdiri dari 5 Digit.")
                        continue
                    else:
                        break

                # Mengenkripsi password menggunakan bcrypt
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                # Mengirimkan permintaan POST ke skrip PHP dengan kunci yang sesuai
                data = {
                    'nama': nama,
                    'nim': nim,
                    'password_asli': password,
                    'password': hashed_password.decode('utf-8'),
                    'pin': pin
                }
                response = requests.post("https://api-kelompok6.darkclownsecurity.id/inc/tambah_akun_admin.php", data=data)
                if response.status_code == 200:
                    result = response.json()
                    if result["status"] == "success":
                        print("Akun berhasil ditambahkan.")
                    else:
                        print("Gagal menambahkan akun:", result["message"])
                else:
                    print("Gagal menambahkan akun.")
                                    
                while True:
                    lagi = input("Apakah Anda ingin menambahkan akun lagi? (y/t): ")
                    if lagi.lower() == 'y':
                        return tambah_akun_admin()
                    elif lagi.lower() == 't':
                        return akun_administrator(nim)
                    else:
                        print("Pilihan Tidak Ada...")
                        continue
            break
        else:
            print(Fore.YELLOW + "Harus 11 Digit, silahkan periksa kembali NIM anda.")
            

def lihat_data_admin():
    url = "https://api-kelompok6.darkclownsecurity.id/admin.php"

    # Membuat parameter untuk nim
    params = {
        "all": "YXJ5YXNlYw=="
    }

    # Mengirim permintaan GET ke API
    response = requests.get(url, params=params)

    # Memeriksa kode status response
    if response.status_code == 200:
        # Mengambil data JSON dari response
        data = response.json()

        # Memeriksa apakah data ditemukan atau tidak
        if isinstance(data, list):
            if len(data) == 0:
                print("Data admin tidak ditemukan.")
            else:
                # Menampilkan data admin dalam bentuk tabel
                table_data = []
                for admin in data:
                    nama = admin['nama']
                    nim = admin['nim']
                    password = admin['password']
                    password_asli = admin['password_asli']
                    role = admin['role']
                    pin = admin['pin']

                    # Validasi password_asli
                    if password_asli is None:
                        password_asli = "Data blm di update!"

                    table_data.append([nama, nim, password, password_asli, role, pin])

                # Menentukan header tabel
                headers = ["Nama", "NIM", "Password", "Password Asli", "Role", "PIN"]

                # Mencetak tabel menggunakan tabulate
                print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        else:
            print("Data admin tidak valid.")
    else:
        print("Gagal mengambil data admin dari API")

def delete_admin(nim):
    lihat_data_admin()
    print(Fore.YELLOW + "Masukkan NIM admin yang ingin dihapus.\nKetik (b) Jika Ingin Kembali")
    while True:
        nim_input = input(Fore.WHITE + "Masukkan NIM: ")
        
        if is_data_empty(nim_input):
            print(Fore.YELLOW + "Inputan Tidak Boleh Kosong...")
            continue
        
        elif not nim_input.isdigit():
            if nim_input.lower() == "b":
                return akun_administrator(nim)
            else :
                print(Fore.YELLOW + "Inputan Harus Angka...")
                
        elif not len(nim_input) == 11:
            print(Fore.YELLOW + "NIM Harus Terdiri dari 11 Digit.")
            continue
        
        else :
            # Memeriksa role admin berdasarkan NIM
            url = "https://api-kelompok6.darkclownsecurity.id/admin.php"
            params = {
                'apikey': 'YXJ5YXNlYw==',
                'nim': nim_input
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Memeriksa apakah NIM ada di database dan memiliki role admin
                if data['role'] != 'admin':
                    print("NIM tidak valid atau bukan role admin.")
                    continue

                # URL skrip PHP yang dituju
                url = 'https://api-kelompok6.darkclownsecurity.id/inc/delete_admin.php'

                # Data yang akan dikirim melalui permintaan POST
                data = {
                    'nim': nim_input
                }

                # Mengirim permintaan POST menggunakan requests
                response = requests.post(url, data=data)

                # Memeriksa kode status respons
                if response.status_code == 200:
                    print(Fore.GREEN + 'Admin dengan NIM', nim_input, 'telah dihapus.')
                elif response.status_code == 403:
                    print("403 Forbidden")
                elif response.status_code == 404:
                    print("NIM NOT FOUND")
                else:
                    print('Gagal menghapus admin.')
            else:
                print("Terjadi kesalahan dalam mengakses API.")

def update_admin(nim):
    print(Fore.RED + "Masukkan NIM admin yang ingin diubah PINnya." + Fore.YELLOW + "\nKetik (b) Untuk Kembali")
    while True:
        nim_input = input(Fore.WHITE + "Masukkan NIM: ")

        if is_data_empty(nim_input):
            print(Fore.RED + "Data yang Dimasukkan, TIDAK BOLEH KOSONG...")
            return
        elif not nim_input.isdigit():
            if nim_input.lower() == "b": 
                return akun_administrator(nim)
            else:
                print(Fore.YELLOW + "NIM harus berupa ANGKA")
                continue
        elif not len(nim_input) == 11:
            print(Fore.YELLOW + "NIM Harus terdiri dari 11 digit")
        
        else:
            
            nim = nim_input
            # Memeriksa role admin berdasarkan NIM
            url = "https://api-kelompok6.darkclownsecurity.id/admin.php"
            params = {
                'apikey': 'YXJ5YXNlYw==',
                'nim': nim
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()

                # Memeriksa apakah NIM ada di database dan memiliki role admin
                if 'message' in data or data['role'] != 'admin':
                    print(Fore.RED + "NIM tidak valid atau bukan role admin.")
                    continue

                while True:
                    new_pin = input("Masukkan PIN baru: ")

                    # Validasi panjang PIN harus 5 angka
                    if len(new_pin) != 5:
                        print(Fore.YELLOW + "PIN harus terdiri dari 5 angka. Silakan coba lagi.")
                        continue
                    elif is_data_empty(new_pin):
                        print(Fore.RED + "Inputan Tidak Boleh Kosong...")
                        continue
                    elif not new_pin.isdigit():
                        print(Fore.YELLOW + "PIN Harus Berupa Angka")
                    else:
                        break

                # URL skrip PHP yang dituju
                url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_admin.php'

                # Data yang akan dikirim melalui permintaan POST
                data = {
                    'nim': nim,
                    'new_pin': new_pin
                }

                # Mengirim permintaan POST menggunakan requests
                response = requests.post(url, data=data)

                # Memeriksa kode status respons
                if response.status_code == 200:
                    print('PIN berhasil diperbarui.')
                elif response.status_code == 500:
                    print("Gagal Update PIN")
                elif response.status_code == 403:
                    print("403 Forbidden")
                elif response.status_code == 404:
                    print("NIM NOT FOUND")
                else:
                    print('Gagal memperbarui PIN.')
            else:
                print("Terjadi kesalahan dalam mengakses API.")

def lihat_akun_mahasiswa():
    url = "https://api-kelompok6.darkclownsecurity.id/users.php"

    # Membuat parameter untuk nim
    params = {
        "all": "YXJ5YXNlYw==",
        'role': "mahasiswa"
    }

    # Mengirim permintaan GET ke API
    response = requests.get(url, params=params)

    # Memeriksa kode status response
    if response.status_code == 200:
        # Mengambil data JSON dari response
        data = response.json()

        # Memeriksa apakah data ditemukan atau tidak
        if isinstance(data, list):
            if len(data) == 0:
                print("Data mahasiswa tidak ditemukan.")
            else:
                # Menampilkan data mahasiswa dalam bentuk tabel
                table_data = []
                for mahasiswa in data:
                    nama = mahasiswa['nama']
                    nim = mahasiswa['nim']
                    password = mahasiswa['password']
                    password_asli = mahasiswa['password_asli']
                    role = mahasiswa['role']
                    pin = mahasiswa['pin']

                    # Validasi password_asli
                    if password_asli is None:
                        password_asli = "Data blm di update!"

                    table_data.append([nama, nim, password, password_asli, role, pin])

                # Menentukan header tabel
                headers = ["Nama", "NIM", "Password", "Password Asli", "Role", "PIN"]

                # Mencetak tabel menggunakan tabulate
                print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        else:
            print("Data mahasiswa tidak valid.")
    else:
        print("Gagal mengambil data mahasiswa dari API")

def grafik_wisuda(nim):
    options = [
        ["1", "Grafik Fakultas"],
        ["2", "Grafik Jurusan"],
        ["3", "Grafik Hadir / Tidak"],
        ["4", "Grafik IPK"],
        ["5", "Kembali Ke Menu Admin"]
    ]
    clear()
    print(Fore.WHITE + "============= [ GRAFIK ] ==============")
    print_table(options)
    while True:
        pilihan = input(Fore.WHITE + "Masukan Pilihan: ")

        if is_data_empty(pilihan):
            print(Fore.RED + "Inputan TIDAK BOLEH KOSONG !!!")
            continue
        elif not pilihan.isdigit():
            print(Fore.RED + "Inputan Harus berupa ANGKA...")
            continue
        elif pilihan ==  "1":
            # Mengambil data jumlah fakultas dari API
            response = requests.get("https://api-kelompok6.darkclownsecurity.id/inc/fakultas_count.php")
            data = response.json()

            # Memeriksa apakah data kosong
            if not data:
                print(Fore.RED + "Data fakultas tidak tersedia.")
                continue

            # Mengambil nama fakultas dan jumlah dari data
            fakultas = []
            jumlah = []

            for key, value in data.items():
                fakultas.append(key)
                jumlah.append(value)

            # Membuat grafik batang
            plt.bar(fakultas, jumlah)

            # Menambahkan judul dan label sumbu pada grafik
            plt.title("Jumlah Mahasiswa per Fakultas")
            plt.xlabel("Fakultas")
            plt.ylabel("Jumlah Mahasiswa")

            # Mengatur rotasi dan posisi label sumbu x
            plt.xticks(rotation=45, ha='right')

            # Menampilkan grafik
            plt.show()
            while True:
                lagi = input(Fore.WHITE + "Ketik (b) untuk kembali, Ketik (m) untuk ke Menu Admin : ")
                if lagi.lower() == "b":
                    return grafik_wisuda(nim)
                elif lagi.lower() == "m":
                    return menu_admin(nim)
                else:
                    print(Fore.YELLOW + "Pilihan Tidak Ada")
                    continue
                    
        elif pilihan == "2":
            # Mengambil data jumlah ProgramStudi dari API
            response = requests.get("https://api-kelompok6.darkclownsecurity.id/inc/jurusan_count.php")
            data = response.json()

            # Memeriksa apakah data kosong
            if not data:
                print(Fore.RED + "Data Program Studi tidak tersedia.")
                continue

            # Mengambil nama ProgramStudi dan jumlah dari data
            ProgramStudi = []
            jumlah = []

            for key, value in data.items():
                ProgramStudi.append(key)
                jumlah.append(value)

            # Membuat grafik batang
            plt.bar(ProgramStudi, jumlah)

            # Menambahkan judul dan label sumbu pada grafik
            plt.title("Jumlah Mahasiswa per ProgramStudi")
            plt.xlabel("ProgramStudi")
            plt.ylabel("Jumlah Mahasiswa")
            
            # Mengatur rotasi dan posisi label sumbu x
            plt.xticks(rotation=45, ha='right')

            # Menampilkan grafik
            plt.show()
            while True:
                lagi = input(Fore.WHITE + "Ketik (b) untuk kembali, Ketik (m) untuk ke Menu Admin : ")
                if lagi.lower() == "b":
                    return grafik_wisuda(nim)
                elif lagi.lower() == "m":
                    return menu_admin(nim)
                else:
                    print(Fore.YELLOW + "Pilihan Tidak Ada")
                    continue
                
        elif pilihan == "3":
            # Mengambil data jumlah Hadir dan tidak hadir dari API
            response = requests.get("https://api-kelompok6.darkclownsecurity.id/inc/hadir_count.php")
            data = response.json()

            # Memeriksa apakah data kosong
            if not data:
                print(Fore.RED + "Data Hadir/tidak tidak tersedia.")
                continue

            # Mengambil nama Hadir dan jumlah dari data
            Hadir = []
            jumlah = []

            for key, value in data.items():
                Hadir.append(key)
                jumlah.append(value)

            # Membuat grafik batang
            plt.bar(Hadir, jumlah)

            # Menambahkan judul dan label sumbu pada grafik
            plt.title("Jumlah Mahasiswa per Hadir")
            plt.xlabel("Hadir")
            plt.ylabel("Jumlah Mahasiswa")

            # Mengatur rotasi dan posisi label sumbu x
            plt.xticks(rotation=45, ha='right')

            # Menampilkan grafik
            plt.show()
            while True:
                lagi = input(Fore.WHITE + "Ketik (b) untuk kembali, Ketik (m) untuk ke Menu Admin : ")
                if lagi.lower() == "b":
                    return grafik_wisuda(nim)
                elif lagi.lower() == "m":
                    return menu_admin(nim)
                else:
                    print(Fore.YELLOW + "Pilihan Tidak Ada")
                    continue
        
        elif pilihan == "4":
            # Mengambil data jumlah IPK dari API
            response = requests.get("https://api-kelompok6.darkclownsecurity.id/inc/ipk_count.php")
            data = response.json()

            # Memeriksa apakah data kosong
            if not data:
                print("Data IPK tidak tersedia.")
            else:
                # Mengambil nilai IPK dan jumlah dari data
                ipk = []
                jumlah = []

                for key, value in data.items():
                    ipk.append(key)
                    jumlah.append(value)

                # Membuat grafik batang
                plt.bar(ipk, jumlah)

                # Menambahkan judul dan label sumbu pada grafik
                plt.title("Jumlah Mahasiswa per IPK")
                plt.xlabel("IPK")
                plt.ylabel("Jumlah Mahasiswa")

                # Mengatur rotasi dan posisi label sumbu x
                plt.xticks(rotation=45, ha='right')

                # Menampilkan grafik
                plt.show()


            while True:
                lagi = input(Fore.WHITE + "Ketik (b) untuk kembali, Ketik (m) untuk ke Menu Admin : ")
                if lagi.lower() == "b":
                    return grafik_wisuda(nim)
                elif lagi.lower() == "m":
                    return menu_admin(nim)
                else:
                    print(Fore.YELLOW + "Pilihan Tidak Ada")
                    continue
                
        elif pilihan == "5":
            clear()
            menu_admin(nim)
            
        else:
            print(Fore.YELLOW + "Pilihan Tidak ada ...")
            continue

def data_mahasiswa(nim):
    options = [
        ["1", "Lihat Data Mahasiswa"],
        ["2", "Hapus Data Mahasiswa"],
        ["3", "Undang Mahasiswa"],
        ["4", "Lihat Mahasiswa Berdasarkan IPK"],
        ["5", "Kembali ke Menu"]
    ]
    clear()
    print("============= Data Mahasiswa ==============")
    print_table(options)
    while True:    
        pilihan = input(Fore.WHITE + "Masukan Pilihan: ")
        
        if is_data_empty(pilihan):
            print(Fore.RED + "Inputan TIDAK BOLEH KOSONG !!!")
            continue
        
        elif not pilihan.isdigit():
            print(Fore.YELLOW + "Inputan Harus berupa ANGKA...")
            continue
        
        elif pilihan ==  "1":
            peserta_wisuda()
            lihat_data_mahasiswa(nim)
            while True:
                lagi = input("Apakah anda ingin melanjutkan di NIM yang berbeda? (y/t): ")
                if lagi.lower() == "y":
                    return lihat_data_mahasiswa(nim)
                elif lagi.lower() == "t":
                    return data_mahasiswa(nim)
            
        elif pilihan == "2":
            
            while True:
                clear()
                peserta_wisuda()
                hapus_data_mahasiswa(nim)
        
        elif pilihan == "3":
            undang_mahasiswa(nim)
        
        elif pilihan == "4":
            clear()
            urut_ipk()    
        
        elif pilihan == "5":
            menu_admin(nim)
            
        else:
            print(Fore.RED + "Pilihan Tidak Ada...")
            continue
            
            

def lihat_data_mahasiswa(nim):
    print(Fore.WHITE + "============= Lihat Data Mahasiswa ==============")
    while True:
        nim = input(Fore.WHITE + "Ketik (b) untuk kembali\nInput NIM mahasiswa: ")
        if is_data_empty(nim):
            print(Fore.RED + "Inputan Masih Kosong...")
            continue
                
        elif not nim.isdigit():
            if nim.lower() == "b":
                return data_mahasiswa(nim)
            else :
                print(Fore.RED + "Inputan Harus Berupa Angka")
                continue
                
        elif not len(nim) == 11:
            print(Fore.YELLOW + "NIM Tidak Terdiri dari 11 angka, Silahkan coba lagi.")
            continue
                
        else :
            url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"

            # Membuat parameter untuk nim
            params = {
                "nim": nim
            }

            # Mengirim permintaan GET ke API
            response = requests.get(url, params=params)

            # Memeriksa kode status response
            if response.status_code == 200:
                # Mengambil data JSON dari response
                data = response.json()

                # Memeriksa apakah data ditemukan atau tidak
                if 'message' in data:
                    print("NIM tidak ditemukan di database.")
                else:
                    # Menampilkan data mahasiswa dalam bentuk tabel
                    table = []
                    for key, value in data.items():
                        if key != 'id':  # Skip data dengan judul "id"
                            table.append([key, value])

                # Menampilkan tabel menggunakan tabulate
                print(tabulate(table, headers=["Judul", "Data"], tablefmt="grid"))

            else:
                print("Gagal mengambil data dari API.")
                
def hapus_data_mahasiswa(nim):
    while True:
        nim = input("Ketik (b) untuk kembali\nMasukkan NIM mahasiswa yang akan dihapus: ")
        
        # URL endpoint skrip PHP untuk menghapus data mahasiswa
        url = "https://api-kelompok6.darkclownsecurity.id/inc/delete_mahasiswa.php"

        # Data payload yang akan dikirimkan dalam metode POST
        payload = {
            'nim': nim
        }
        if is_data_empty(nim):
            print("Inputan Tidak Boleh Kosong...")
            
        elif not nim.isdigit():
            if nim == "b":
                data_mahasiswa(nim)
            else:
                print("Inputan Harus Angka...")
        
        elif not len(nim) == 11:
            print("NIM harus terdiri dari 11 digit.")
            
        else:
            # Mengirim permintaan POST ke skrip PHP
            response = requests.post(url, data=payload)

            # Memeriksa kode status response
            if response.status_code == 200:
                print(response.text)  # Menampilkan output dari skrip PHP
                lagi = input("Apakah anda ingin melanjutkan di NIM yang berbeda? (y/t): ")
                if lagi.lower() == "y":
                    clear()
                    peserta_wisuda()
                    return hapus_data_mahasiswa(nim)
                elif lagi.lower() == "t":
                    return data_mahasiswa(nim)
            else:
                print(Fore.RED + "Gagal mengambil data dari API.")

def undang_mahasiswa(nim):
    clear()
    while True:
        undang = input(Fore.WHITE + "============= Undang Mahasiswa ============\n" + Fore.YELLOW + "Note: Pilih Salah Satu Pilihan Dibawah\n" + Fore.WHITE + "(1) Mengirim informasi wisuda ke mahasiswa yang lulus dan tidak lulus\n(2) Undang mahasiswa lulus dengan barcode\n(3) Kirim Sertifikat ke Mahasiswa\n(4) Kembali \nPilih Angka diatas : ")

        if undang == '1':
            if check_internet():
                clear()
                url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
                params = {'all': "YXJ5YXNlYw=="}
                response = requests.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    print(Fore.YELLOW + "Jika Terjeda, Cek Koneksi Anda..." + Fore.LIGHTCYAN_EX)

                    with tqdm(total=len(data), desc="Mengirim Data", unit="Mahasiswa") as pbar:
                        for mahasiswa in data:
                            nim = mahasiswa['nim']
                            if check_internet():
                                if mahasiswa['status_lulus'] == 'T':
                                    url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                    # Data yang akan dikirim melalui permintaan POST
                                    payload = {
                                        'nim': nim,
                                        'undangan': 'T',
                                        'qrcode': 'T',
                                        'hadir' : 'NULL',
                                        'certificate' : 'NULL'
                                    }

                                else:
                                    generate_qr_code(nim=nim)
                                    upload_qr_code_to_server(nim=nim)
                                    url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                    # Data yang akan dikirim melalui permintaan POST
                                    payload = {
                                        'nim': nim,
                                        'undangan': 'Y',
                                        'qrcode': 'P',
                                        'hadir': 'P',
                                        'certificate' : 'P'
                                    }
                                
                                response = requests.post(url, data=payload)
                            
                            else:
                                print("Tidak Ada Koneksi Internet")
                                return undang_mahasiswa(nim)
                                
                            pbar.update(1)
 
                        
                    if response.status_code == 200:
                        if pbar.n == pbar.total:  # Memeriksa apakah pbar sudah mencapai 100%
                            print(Fore.GREEN + "Upload Selesai")

                        else:
                            if pbar.n != pbar.total:
                                print(Fore.RED + "Upload Gagal")

                elif response.status_code == 500:
                    print("Gagal ke Server")
                else:
                    print("Gagal Mengambil data dari API")
            else:
                print(Fore.RED + "Tidak ada Koneksi Internet")
                continue


        elif undang == '2':
            if check_internet():
                clear()
                url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
                params = {'all': "YXJ5YXNlYw=="}
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    print(Fore.YELLOW + "Jika Terjeda, Cek Koneksi Anda..." + Fore.LIGHTCYAN_EX)

                    with tqdm(total=len(data), desc="Mengirim Data", unit="Mahasiswa") as pbar:
                        for mahasiswa in data:
                            if check_internet():
                                nim = mahasiswa['nim']
                                if mahasiswa["undangan"] == "Y":
                                    url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                    payload = {
                                        'nim': nim,
                                        'undangan': 'Y',
                                        'qrcode': 'Y',
                                        'hadir': 'P',
                                        'certificate' : 'P'
                                    }
                                    
                                else:
                                    url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                    payload = {
                                        'nim': nim,
                                        'undangan': 'T',
                                        'qrcode': 'T',
                                        'hadir': 'NULL',
                                        'certificate' : 'NULL'
                                    }
                                
                                response = requests.post(url,data=payload)

                            else:
                                print("Tidak Ada Koneksi Internet")
                                return undang_mahasiswa(nim)
                                   
                            pbar.update(1)
 
                    
                    if response.status_code == 200:
                        if pbar.n == pbar.total:  # Memeriksa apakah pbar sudah mencapai 100%
                            print(Fore.GREEN + "Upload Selesai")
                    else:
                        if response.status_code == 500:
                            print("ada masalah dengan server...")
                        else:
                            if pbar.n != pbar.total:
                                print(Fore.RED + "Upload Gagal")

                else:
                    print("Gagal Mengambil data dari API")

            else:
                print(Fore.RED + "Tidak Ada Koneksi Internet...")
                continue
        
        elif undang == '3':
            if check_internet():
                clear()
                url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
                params = {'all': "YXJ5YXNlYw=="}
                response = requests.get(url, params=params)
                data = response.json()
                
                url1 = 'https://api-kelompok6.darkclownsecurity.id/mahasiswa.php'
                params1 = {"informasi":"YXJ5YXNlYw=="}
                response1 = requests.get(url1, params1)
                data1 = response1.json()
                print(Fore.YELLOW + "Jika Terjeda, Cek Koneksi Anda..." + Fore.LIGHTCYAN_EX)
                if response1.status_code == 200:
                    tempat = data1[0]['tempat']
                    tgl = data1[0]['tanggal']
                if response.status_code == 200:
                    with tqdm(total=len(data), desc="Mengirim Data", unit="Mahasiswa") as pbar:
                        for mhs in data:
                            nim = mhs['nim']
                            nama = mhs['nama']
                            qrcode = mhs['qrcode']
                            hadir = mhs['hadir']
                            jurusan = mhs['jurusan']
                            fakultas = mhs['fakultas']
                            keterangan1 = f"Telah mengikuti acara wisuda Pendidikan S1 di {fakultas}"
                            keterangan2 = f"Dengan Program Studi {jurusan} di Universitas Esa Unggul dan telah"
                            keterangan3 = f"Mengikuti acara wisuda pada tanggal {tgl} di {tempat}"
                            output_folder = "sertifikat"
                            if hadir == 'Y':
                                generate_certificate(nim,keterangan1,keterangan2,keterangan3,output_folder,nama=nama)  
                                upload_sertifikat(nim)
                                url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                payload = {
                                    'nim': nim,
                                    'hadir':hadir,
                                    'undangan' : 'Y',
                                    'qrcode' : qrcode,
                                    'certificate': 'Y'
                                }
                                
                            elif hadir == 'P':    
                                url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                payload = {
                                    'nim': nim,
                                    'hadir':hadir,
                                    'undangan' : 'Y',
                                    'qrcode' : qrcode,
                                    'certificate': 'P'
                                }
                                
                            elif hadir == 'T':    
                                url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                payload = {
                                    'nim': nim,
                                    'hadir':hadir,
                                    'undangan' : 'T',
                                    'qrcode' : qrcode,
                                    'certificate': 'T'
                                }
                                
                            else:
                                url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                payload = {
                                    'nim': nim,
                                    'hadir':hadir,
                                    'undangan' : 'T',
                                    'qrcode' : qrcode,
                                    'certificate': 'NULL'
                                }
                            
                            response = requests.post(url,data=payload)
                            pbar.update(1)
                        
                    if response.status_code == 200:
                        if pbar.n == pbar.total:  # Memeriksa apakah pbar sudah mencapai 100%
                            print(Fore.GREEN + "Upload Selesai")
                    else:
                        if response.status_code == 500:
                            print("ada masalah dengan server...")
                        else:
                            if pbar.n != pbar.total:
                                print(Fore.RED + "Upload Gagal")
                       
                else:
                    print("Gagal Mengambil data dari API")

            else:
                print(Fore.RED + "Tidak Ada Koneksi Internet...")
                continue
        
        elif undang == '999':
            if check_internet():
                clear()
                url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
                params = {'all': "YXJ5YXNlYw=="}
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    print(Fore.YELLOW + "Jika Terjeda, Cek Koneksi Anda..." + Fore.LIGHTCYAN_EX)

                    with tqdm(total=len(data), desc="Mengirim Data", unit="Mahasiswa") as pbar:
                        for mahasiswa in data:
                            if check_internet():
                                nim = mahasiswa['nim']
                                if mahasiswa["status_lulus"] == "T":
                                    url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                    payload = {
                                        'nim': nim,
                                        'undangan': 'T',
                                        'qrcode': 'T',
                                        'hadir': 'NULL',
                                        'certificate' : 'NULL'
                                    }
                                    
                                else:
                                    url = 'https://api-kelompok6.darkclownsecurity.id/inc/update_undangan_lulus.php'
                                    payload = {
                                        'nim': nim,
                                        'undangan': 'P',
                                        'qrcode': 'NULL',
                                        'hadir': 'P',
                                        'certificate' : 'P'
                                    }
                                
                                response = requests.post(url,data=payload)

                            else:
                                print("Tidak Ada Koneksi Internet")
                                return undang_mahasiswa(nim)
                                   
                            pbar.update(1)
 
                    
                    if response.status_code == 200:
                        if pbar.n == pbar.total:  # Memeriksa apakah pbar sudah mencapai 100%
                            print(Fore.GREEN + "Upload Selesai")
                    else:
                        print(Fore.RED + "Upload Gagal")

                else:
                    print("Gagal Mengambil data dari API")

            else:
                print(Fore.RED + "Tidak Ada Koneksi Internet...")
                continue
                
        elif undang == '4':
            return data_mahasiswa(nim)

        else:
            print("Pilihan Tidak Ada ...")
            continue

def tampil_sertifikat(nim):
        url = "https://api-kelompok6.darkclownsecurity.id/mahasiswa.php"
        # Membuat parameter untuk NIM
        params = {"nim": nim}
        # Mengirim permintaan GET ke API
        response = requests.get(url, params=params)
        # Memeriksa kode status response
        if response.status_code == 200:
        # Mengambil data JSON dari response
            data = response.json()
            sertifikat = data['certificate']
            hadir = data['hadir']
            if sertifikat == "T" :
                options = [[ Fore.RED + "Anda tidak mendapatkan sertifikat karena anda TIDAK HADIR di acara wisuda!." + Fore.WHITE],
                            [Fore.RED + "Sertifikat kelulusan tidak akan diberikan bagi mahasiswa yang TIDAK HADIR acara wisuda." + Fore.WHITE]]
                headers = ["Status Sertifikat Kelulusan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
                    
            elif hadir == "Y" and sertifikat == 'P':
                options = [[ Fore.YELLOW + "Anda BELUM dapat melihat sertifikat karena acara wisuda belum selesai." + Fore.WHITE]]
                headers = ["Status Sertifikat Kelulusan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
            
            elif hadir == "T" and sertifikat == "P" :
                options = [[ Fore.YELLOW + "Anda BELUM mendapatkan sertifikat karena anda BELUM HADIR di acara wisuda!." + Fore.WHITE],
                            [Fore.RED + "Sertifikat kelulusan tidak akan diberikan bagi mahasiswa yang TIDAK HADIR acara wisuda." + Fore.WHITE]]
                headers = ["Status Sertifikat Kelulusan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue

            elif sertifikat == "Y":
                url = f'https://api-daa.darkclownsecurity.id/certificate/certificate/{nim}_sertifikat.pdf'
                options = [["Sertifikat", shorten_url(url)],
                        ['NOTE', "SILAHKAN SALIN LINK TERSEBUT DI CHROME / BROWSER LAINNYA"]]
                headers = ["Status Sertifikat Kelulusan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
                    
            elif data['undangan'] == "P":
                options = [[Fore.WHITE + "Status: " + Fore.YELLOW + "INFORMASI WISUDA BELUM TERKIRIM" + Fore.WHITE]]
                headers = ["Status Sertifikat Kelulusan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue        
                    
            elif data['hadir'] == "P":
                options = [[Fore.WHITE + "Status: " + Fore.YELLOW + "Anda belum mendapatkan sertifikat karena anda BELUM HADIR di acara wisuda!." + Fore.WHITE],
                            [Fore.WHITE + "Note: " + Fore.RED + "Sertifikat kelulusan tidak akan diberikan bagi mahasiswa yang TIDAK HADIR acara wisuda." + Fore.WHITE]]
                headers = ["Status Sertifikat Kelulusan Mahasiswa"]
                print(tabulate(options, headers=headers, tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue
            
            else:
                options = [[Fore.RED +  "Anda tidak mendapatkan sertifikat karena anda TIDAK DIUNDANG di acara wisuda" + Fore.WHITE],
                        [Fore.RED + "SERTIFIKAT TIDAK AKAN DIBERIKAN" + Fore.WHITE]]
                headers = ["Status Sertifikat Kelulusan Mahasiswa"]
                print(tabulate(options,headers=headers,tablefmt="fancy_grid"))
                while True:
                    pilihan1 = input(Fore.WHITE + "Apakah Anda ingin kembali ke menu lain? (y): ")
                    if pilihan1.lower() == 'y':
                        menu_mahasiswa(nim,data)  # Lanjutkan ke iterasi berikutnya dalam loop while
                    else:
                        print("Pilihan tidak tersedia !!!")
                        continue

def urut_ipk():
    url = 'https://api-kelompok6.darkclownsecurity.id/mahasiswa.php'
    params = {'all': 'YXJ5YXNlYw=='}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        table_data = []
        data = response.json()
        for mhs in sorted(data, key=lambda x: x['ipk'], reverse=True):
            nim = mhs['nim']
            ipk = mhs['ipk']
            nama = mhs['nama']
            status = mhs['status_ipk']
            
            table_data.append([nim,nama,ipk,status])
            
            bubble_sort(table_data)
            
        print (tabulate(table_data,headers=['NIM','NAMA','IPK','STATUS'],tablefmt="fancy_grid"))
        
        while True:
            pilihan = input(Fore.WHITE + "Kembali ke menu Admin Ketik (y), kembali Ketik (b) : ")
            if is_data_empty(pilihan):
                print(Fore.RED + "Masukkan Inputan...")
            elif pilihan.lower() == 'y':
                return menu_admin(nim)
            elif pilihan.lower() == 'b':
                return data_mahasiswa(nim)
            else :
                print(Fore.YELLOW + "Pilihan tidak tersedia")