
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime , timedelta


app = Flask(__name__) # Flask uygulaması oluşturulur
app.secret_key = 'supersecretkey'  # Bu anahtar oturum verilerini güvenli tutmak için kullanılır


# SQLite veritabanı oluşturma ve tabloları oluşturma
def init_db():
    connection = sqlite3.connect("database.db") # database.db adındaki SQLite veritabanına bağlanır mevcut değilse oluşturur
    connection.execute("PRAGMA foreign_keys = 1;")  # Yabancı anahtarları etkinleştirir
    cursor = connection.cursor() # Veritabanı üzerinde işlem yapmak için bir imleç oluşturur

    # Gerekli Tabloların Oluşturulması
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        email TEXT PRIMARY KEY,
                        name TEXT,
                        password TEXT,
                        job TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS patient (
                        name TEXT,
                        surname TEXT,
                        email TEXT,
                        password TEXT,
                        patientID INTEGER PRIMARY KEY AUTOINCREMENT,
                        FOREIGN KEY (email) REFERENCES users(email),
                        FOREIGN KEY (password) REFERENCES users(password)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS doctor (
                        name TEXT,
                        surname TEXT,
                        email TEXT,
                        workHours TEXT,
                        department TEXT,
                        contact_info TEXT,
                        doctorID INTEGER PRIMARY KEY AUTOINCREMENT,
                        FOREIGN KEY (email) REFERENCES users(email)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                        email TEXT,
                        password TEXT,
                        adminID INTEGER PRIMARY KEY AUTOINCREMENT,
                        FOREIGN KEY (email) REFERENCES users(email)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS appointment (
                        appointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
                        patientID INTEGER,
                        doctorID INTEGER,
                        status TEXT ,
                        date TEXT,
                        time TEXT,
                        FOREIGN KEY (patientID) REFERENCES patient(patientID),
                        FOREIGN KEY (doctorID) REFERENCES doctor(doctorID)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS departments (
                        departmentID INTEGER PRIMARY KEY AUTOINCREMENT,
                        departmentName TEXT UNIQUE
                    )''')


    connection.commit()
    connection.close()

# Veritabanı tablolarını oluştur
init_db()

# Veritabanına rastgele doktorlar ekleme
def addDoctors():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Doktorlar
    doctors = [
        ("doctor1@gmail.com", "Doctor1", "Doctor1Name", "Doctor1SurName", "09:00-21:00", "Cardiology","123456789"),
        ("doctor2@gmail.com", "Doctor2", "Doctor2Name", "Doctor2SurName", "09:00-21:00", "Dermatology","123456789"),
        ("doctor3@gmail.com", "Doctor3", "Doctor3Name", "Doctor3SurName", "21:00-09:00", "Cardiology","123456789"),
        ("doctor4@gmail.com", "Doctor4", "Doctor4Name", "Doctor4SurName", "21:00-09:00", "Dermatology","123456789"),
        ("doctor5@gmail.com", "Doctor5", "Doctor5Name", "Doctor5SurName", "09:00-17:00", "Brain Surgery","123456789"),
        ("doctor6@gmail.com", "Doctor6", "Doctor6Name", "Doctor6SurName", "09:00-17:00", "General Surgery","123456789"),
        ("doctor7@gmail.com", "Doctor7", "Doctor7Name", "Doctor7SurName", "21:00-09:00", "Brain Surgery","123456789"),
        ("doctor8@gmail.com", "Doctor8", "Doctor8Name", "Doctor8SurName", "21:00-09:00", "General Surgery","123456789"),
        ("doctor9@gmail.com", "Doctor9", "Doctor9Name", "Doctor9SurName", "09:00-17:00", "KBB","123456789"),
        ("doctor10@gmail.com", "Doctor10", "Doctor10Name", "Doctor10SurName", "21:00-09:00", "KBB","123456789"),
    ]

    for doctor in doctors:
        email = doctor[0]
        
        # Email adresinin veritabanında olup olmadığını kontrol et
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # User tablosuna doktoru ekle
            cursor.execute("INSERT INTO users (email, name, password, job) VALUES (?, ?, ?, ?)", 
                           (email, doctor[1], '1234', 'doctor'))
            # Doktoru doctor tablosuna ekle
            cursor.execute("INSERT INTO doctor (name, surname, email, workHours, department , contact_info) VALUES (?, ?, ?, ?, ?, ?)",
                           (doctor[2], doctor[3], email, doctor[4], doctor[5], doctor[6]))

    connection.commit()
    connection.close()

# Doktorları veritabanına ekle
addDoctors()

# Admin ekleme
def addAdmin():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Admin bilgileri
    admin = ("admin@gmail.com", "admin")

    # Admin e-posta adresini al
    email = admin[0]

    # Admin eklerken e-posta adresinin zaten var olup olmadığını kontrol et
    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if not existing_user:
        # Admini users tablosuna ekle
        cursor.execute("INSERT INTO users (email, name, password, job) VALUES (?, ?, ?, ?)", 
                        (email, 'admin', admin[1], 'admin'))
        # Admini admin tablosuna ekle
        cursor.execute("INSERT INTO admin (email, password) VALUES (?, ?)", (email, admin[1]))

    connection.commit()
    connection.close()

# Admini veritabanına ekle
addAdmin()

# Departmanları veritabanına ekleme
def addDepartments():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Departments
    departments = ["Cardiology", "Dermatology", "Brain Surgery", "General Surgery", "KBB"]

    # Veritabanındaki mevcut departmanları kontrol et
    cursor.execute("SELECT departmentName FROM departments")
    existing_departments = cursor.fetchall()

    # Eğer departman veritabanında yoksa departmanı ekle
    for department in departments:
        if (department,) not in existing_departments:
            cursor.execute("INSERT INTO departments (departmentName) VALUES (?)", (department,))

    connection.commit()
    connection.close()

# Departmanları veritabanına ekle
addDepartments()

# Anasayfa yönlendirmesi
@app.route("/")
def home():
    return render_template("index.html")

# Kayıt sayfası yönlendirmesi
@app.route("/register")
def register():
    return render_template("register.html")

# Kayıt işlemi
@app.route("/register", methods=["POST"])
def register_post():
    # register.html deki formdan gelen verileri al
    email = request.form["email"]
    name = request.form["name"]
    surname = request.form["surname"]
    password = request.form["password"]
    password2 = request.form["password2"]
    
    # Eğer şifreler eşleşmiyorsa hata döndür
    if password != password2:
        return "Şifreler eşleşmiyor"

    # Veritabanına bağlan
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    job = "patient"  # Kullanıcı rolü (hasta)
    cursor.execute("INSERT INTO users (email, name, password, job) VALUES (?, ?, ?, ?)", (email, name, password, job)) # Kullanıcıyı users tablosuna ekle

    # Eğer kullanıcı daha önce kayıtlı değilse, hasta tablosuna ekle
    cursor.execute("INSERT INTO patient (name, surname, email ,password) VALUES (?, ?, ?, ?)", (name, surname, email, password))

    connection.commit()
    connection.close()

    # Kayıt işlemi başarılıysa, login sayfasına yönlendir
    return redirect(url_for("login"))

# Giriş sayfası yönlendirmesi
@app.route("/login")
def login():
    return render_template("loginForm.html")

# Giriş işlemi
@app.route("/login", methods=["POST"])
def login_post():
    # Formdan gelen verileri al
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Kullanıcı bilgilerini al
        cursor.execute("SELECT email, password, job FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        # Eğer kullanıcı bulunamadıysa, admin kontrolü yapılır
        if not user:
            cursor.execute("SELECT email, password FROM admin WHERE email = ?", (email,))
            admin = cursor.fetchone()
            if admin and admin[1] == password:
                # Yönetici oturumunu başlat
                session["admin_email"] = email # Admin için oturumda email saklanır
                connection.close()
                return redirect(url_for("admin_menu")) # Admin sayfasına yönlendirme

        # Kullanıcı bilgileri bulunduysa, kullanıcı oturumu başlatılır
        if user and user[1] == password:  # Veritabanındaki şifreyi kontrol eder
            job = user[2]  # Kullanıcının 'job' bilgisi (doktor, hasta, admin)

            # Kullanıcı oturumu başlatma
            session["user_email"] = email

            # Kullanıcı rolüne göre yönlendirme
            if job == "doctor":
                session["doctor_email"] = email  # Doktor için oturumda email saklanır
                return redirect(url_for("doctor_menu")) # Doktor sayfasına yönlendirme
            elif job == "patient":
                return redirect(url_for("patient_menu")) # Hasta sayfasına yönlendirme
            elif job == "admin":
                session["admin_email"] = email  # Admin için oturumda email saklanır
                return redirect(url_for("admin_menu")) # Admin sayfasına yönlendirme
            else:
                return "Bilinmeyen iş tipi", 400  # Geçersiz bir iş türü durumunda hata döndürüyoruz.

        else:
            # Giriş başarısız olduysa
            connection.close() # Veritabanı bağlantısını kapat
            return "Giriş işlemi başarısız. Hatalı giriş", 401

    return render_template("loginForm.html") # Giriş sayfasına yönlendirme

# Hasta menüsü
@app.route("/patientMenu")
def patient_menu():
    # Eğer oturumda kullanıcı e-posta yoksa, login sayfasına yönlendir
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    return render_template("patientMenu.html") # Hasta menüsüne yönlendirme

# Admin menüsü
@app.route("/adminMenu")
def admin_menu():
    if "admin_email" not in session:  # Admin oturumu kontrolü
        return redirect(url_for("login"))  # Admin değilse login sayfasına yönlendir
    
    return render_template("adminMenu.html") # Admin menüsüne yönlendirme

# Randevu alma sayfası
@app.route("/bookAppointment", methods=["GET", "POST"])
def book_appointment():
    # Formdan gelen verileri al
    if request.method == "POST":
        department = request.form["department"]
        doctor_id = request.form["doctor"]
        date = request.form["date"]
        time = request.form["time"]

        # Oturumdan giriş yapan kullanıcının email adresini al
        user_email = session.get('user_email')

        if user_email is None:
            return redirect(url_for('login'))  # Eğer oturumda e-posta yoksa, login sayfasına yönlendir

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Kullanıcının patientID'sini al
        cursor.execute("SELECT patientID FROM patient WHERE email = ?", (user_email,))
        patient = cursor.fetchone()

        if patient is None: # Eğer hasta veritabanında bulunamazsa
            return redirect(url_for("book_appointment", error_message="Hasta veritabanında bulunamadı."))

        patient_id = patient[0] # Hasta ID'si

        # Bugünün tarihi ve saati
        today = datetime.today().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M')  # Mevcut saat (şu anki saat)

        # Randevu tarihi ve saati
        appointment_datetime = f"{date} {time}"
        appointment_datetime_obj = datetime.strptime(appointment_datetime, '%Y-%m-%d %H:%M') 

        # Randevuyu veritabanına eklemeden önce, aynı gün aynı doktor için bir çakışma olup olmadığını kontrol et
        cursor.execute("""
            SELECT date, time 
            FROM appointment 
            WHERE doctorID = ? AND date = ? AND status != 'İptal Edildi'
        """, (doctor_id, date))
        existing_appointments = cursor.fetchall()

        # Eğer aynı gün aynı doktor için başka bir randevu varsa, randevular arasında en az 1 saatlik bir fark olmalıdır
        for app in existing_appointments:
            existing_appointment_datetime = datetime.strptime(f"{app[0]} {app[1]}", '%Y-%m-%d %H:%M')
            time_difference = abs(appointment_datetime_obj - existing_appointment_datetime)

            # Eğer randevular arasında 1 saatten daha az fark varsa
            if time_difference < timedelta(hours=1):
                connection.close()
                return redirect(url_for("book_appointment", error_message="Randevular arasında en az 1 saatlik bir fark olmalıdır."))

        # Eğer randevu tarihi geçmişse status 'Deaktif', aksi takdirde 'Onaylandı' olacak
        if date < today:
            status = 'Deaktif'
        else:
            status = 'Onaylandı'

        # Randevuyu veritabanına ekleme
        cursor.execute(
            "INSERT INTO appointment (patientID, doctorID, date, time, status) VALUES (?, ?, ?, ?, ?)",
            (patient_id, doctor_id, date, time, status),
        )
        connection.commit()
        connection.close()

        return redirect(url_for("book_appointment", success_message="Randevunuz başarıyla oluşturuldu!"))

    else:
        
        error_message = request.args.get('error_message', '')
        success_message = request.args.get('success_message', '')

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Tüm bölümleri al
        cursor.execute("SELECT DISTINCT department FROM doctor")
        departments = [row[0] for row in cursor.fetchall()]

        # Doktorları ve bölümleri al
        cursor.execute("SELECT doctorID, name, surname, department FROM doctor")
        doctors = cursor.fetchall()

        connection.close()

        # Bugünün tarihini ve mevcut saati HTML sayfasına iletmek için
        today = datetime.today().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M')

        # Randevu alma sayfasına verileri gönder
        return render_template(
            "bookAppointment.html",
            departments=departments,
            doctors=doctors, # Doktorları ve bölümleri gönderiyoruz
            today_date=today,  # Bugünün tarihini template'e gönderiyoruz
            current_time=current_time,  # Mevcut saati template'e gönderiyoruz
            error_message=error_message,
            success_message=success_message,
        )

# Randevuları görüntüleme
@app.route("/viewAppointments")
def view_appointments():
    # Kullanıcının oturum bilgisi var mı diye kontrol et
    user_email = session.get('user_email')

    if not user_email:
        return redirect(url_for("login"))  # Eğer oturumda email yoksa, login sayfasına yönlendir

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Kullanıcının patientID'sini almak
    cursor.execute("SELECT patientID FROM patient WHERE email = ?", (user_email,))
    patient = cursor.fetchone()

    if patient is None:
        return "Patient not found in the database."

    patient_id = patient[0]

    # Gelecek randevuları al (bugünden itibaren)
    cursor.execute("""
        SELECT appointment.appointmentID, doctor.name, doctor.surname, appointment.date, appointment.time, appointment.status
        FROM appointment
        JOIN doctor ON appointment.doctorID = doctor.doctorID
        WHERE appointment.patientID = ? AND appointment.date >= date('now')
    """, (patient_id,))
    upcoming_appointments = cursor.fetchall()

    # Geçmiş randevuları al (bugünden önceki randevular)
    cursor.execute("""
        SELECT appointment.appointmentID, doctor.name, doctor.surname, appointment.date, appointment.time, appointment.status
        FROM appointment
        JOIN doctor ON appointment.doctorID = doctor.doctorID
        WHERE appointment.patientID = ? AND appointment.date < date('now')
    """, (patient_id,))
    past_appointments = cursor.fetchall()

    connection.close()

    # Randevuları görüntüleme sayfasına verileri gönder
    return render_template(
        "viewAppointments.html",
        upcoming_appointments=upcoming_appointments,
        past_appointments=past_appointments,
    )

# Randevu iptal etme
@app.route("/cancelAppointment", methods=["GET", "POST"])
def cancel_appointment():
    if request.method == "POST":
        # Kullanıcı oturumundan e-posta bilgisi alınır
        user_email = session.get('user_email')
        
        if not user_email:
            return redirect(url_for('login'))  # Eğer kullanıcı giriş yapmamışsa, login sayfasına yönlendir

        # Formdan gelen appointmentID
        appointment_id = request.form["appointmentID"]

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Kullanıcının patientID'sini al
        cursor.execute("SELECT patientID FROM patient WHERE email = ?", (user_email,))
        patient = cursor.fetchone()

        if patient is None:
            return "Patient not found in the database."

        patient_id = patient[0]

        # İptal edilmek istenen randevuyu bul
        cursor.execute("""
            SELECT appointmentID, patientID, doctorID, date, time
            FROM appointment
            WHERE appointmentID = ? AND patientID = ?
        """, (appointment_id, patient_id))
        
        appointment = cursor.fetchone()

        if not appointment:
            return "Appointment not found."

        # Randevuyu iptal et
        cursor.execute("DELETE FROM appointment WHERE appointmentID = ?", (appointment_id,))

        connection.commit()
        connection.close()

        return "Randevunuz başarıyla iptal edilmiştir."

    else:
        user_email = session.get('user_email')

        if not user_email:
            return redirect(url_for('login'))

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Kullanıcının patientID'sini almak
        cursor.execute("SELECT patientID FROM patient WHERE email = ?", (user_email,))
        patient = cursor.fetchone()

        if patient is None:
            return "Patient not found in the database."

        patient_id = patient[0]

        # Gelecek randevuları al
        cursor.execute("""
            SELECT appointmentID, doctor.name, doctor.surname, appointment.date, appointment.time
            FROM appointment
            JOIN doctor ON appointment.doctorID = doctor.doctorID
            WHERE appointment.patientID = ? AND appointment.date >= date('now')
        """, (patient_id,))
        upcoming_appointments = cursor.fetchall()

        connection.close()

        # İptal edilecek randevuları göster
        return render_template("cancelAppointment.html", upcoming_appointments=upcoming_appointments)

# Çıkış işlemi
@app.route("/logout", methods=["GET", "POST"])
def logout():
    # Oturumu temizle
    session.clear()
    
    # Kullanıcıyı login sayfasına yönlendir
    return redirect(url_for('login'))

# Doktor menüsü yönlendirmesi
@app.route("/doctorMenu")
def doctor_menu():
    if "doctor_email" not in session:  # doctor_email oturumda bulunmalı
        print("Oturumda doktor bilgisi bulunamadı!")
        return redirect(url_for("login"))
    
    print(f"Oturumda bulunan doktor email: {session['doctor_email']}")
    return render_template("doctorMenu.html")

# Doktorun randevuları
@app.route("/doctorAppointments")
def doctor_appointments():
    if "user_email" not in session:
        return redirect(url_for("login"))

    # Oturumdan doktor e-posta adresini al
    user_email = session["user_email"]
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Doktor ID'sini al
    cursor.execute("SELECT doctorID FROM doctor WHERE email = ?", (user_email,))
    doctor = cursor.fetchone()

    if not doctor:
        return "Doktor bulunamadı."

    doctor_id = doctor[0]

    # Bugünkü, gelecek ve geçmiş randevuları al
    cursor.execute("""
        SELECT patient.name, patient.surname, appointment.date, appointment.time, appointment.status
        FROM appointment
        JOIN patient ON appointment.patientID = patient.patientID
        WHERE appointment.doctorID = ? AND appointment.date >= date('now')
        ORDER BY appointment.date, appointment.time
    """, (doctor_id,))
    upcoming_appointments = cursor.fetchall()

    # Geçmiş randevular
    cursor.execute("""
        SELECT patient.name, patient.surname, appointment.date, appointment.time, appointment.status
        FROM appointment
        JOIN patient ON appointment.patientID = patient.patientID
        WHERE appointment.doctorID = ? AND appointment.date < date('now')
        ORDER BY appointment.date DESC
    """, (doctor_id,))
    past_appointments = cursor.fetchall()

    # Bugünkü randevular
    cursor.execute("""
        SELECT patient.name, patient.surname, appointment.time, appointment.status
        FROM appointment
        JOIN patient ON appointment.patientID = patient.patientID
        WHERE appointment.doctorID = ? AND appointment.date = date('now')
        ORDER BY appointment.time
    """, (doctor_id,))
    todays_appointments = cursor.fetchall()

    connection.close()

    # Doktorun randevu sayfasına verileri gönder
    return render_template("doctorAppointments.html", upcoming_appointments=upcoming_appointments,
                           past_appointments=past_appointments, todays_appointments=todays_appointments)

# Doktor profilini görüntüleme
@app.route("/doctorProfile")
def doctor_profile():
    if "doctor_email" not in session:
        return redirect(url_for("login"))

    user_email = session["doctor_email"]
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Doktor bilgilerini al
    cursor.execute("SELECT * FROM doctor WHERE email = ?", (user_email,))
    doctor = cursor.fetchone()

    # Departmanları al
    cursor.execute("SELECT departmentID, departmentName FROM departments")  # department tablosundan id ve name alıyoruz
    departments = cursor.fetchall()

    connection.close()

    # Eğer doktor bilgisi varsa
    if doctor:
        # Doktor bilgilerini görüntüleme sayfasına verileri gönder
        return render_template(
            "doctorProfile.html",
            doctor={ 
                "name": doctor[0],
                "surname": doctor[1],
                "department": doctor[4],  
                "workHours": doctor[3],
                "contact_info": doctor[5],
            },
            departments=departments  # Departmanları da template'e gönderiyoruz
        )
    else:
        return "Doktor bilgisi bulunamadı."

# Doktor profilini güncelleme
@app.route("/updateDoctorProfile", methods=["POST"])
def update_doctor_profile():
    if "doctor_email" not in session:
        return redirect(url_for("login"))

    # Formdan gelen verileri al
    user_email = session["doctor_email"]
    department_name = request.form["department"]
    workHours = request.form["workHours"]
    contact_info = request.form["contact_info"]

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Departman adını al
    cursor.execute("SELECT departmentID FROM departments WHERE departmentName = ?", (department_name,))
    department_id = cursor.fetchone()

    if department_id:
        department_id = department_id[0]
    else:
        return "Geçersiz departman adı"

    # Doktor bilgilerini güncelle
    cursor.execute("""
        UPDATE doctor
        SET department = ?, workHours = ?, contact_info = ?
        WHERE email = ?
    """, (department_name, workHours, contact_info, user_email))

    connection.commit()
    connection.close()

    # Doktor profil sayfasına yönlendir
    return redirect(url_for("doctor_profile"))

# Tarihi geçmiş randevuları 'Deaktif' olarak güncelleme
def update_inactive_appointments():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Bugünün tarihini al (yyyy-mm-dd formatında)
    today_date = datetime.today().strftime('%Y-%m-%d')

    # Tarih formatını kontrol et
    cursor.execute("""
        SELECT date FROM appointment LIMIT 1
    """)
    date_sample = cursor.fetchone()

    if date_sample:
        print(f"Tarih formatı kontrolü: {date_sample[0]}")
    
    # Geçmiş tarihlerdeki randevuları 'Deaktif' olarak güncelle
    cursor.execute("""
        UPDATE appointment
        SET status = 'Deaktif'
        WHERE date < ? AND status != 'Deaktif'
    """, (today_date,))

    connection.commit()
    connection.close()

    print("Geçmiş tarihlerdeki randevular Deaktif olarak güncellendi.")

# Admin işlemleri
# Admin randevu yönetimi
@app.route("/appointments")
def appointments():
    if "admin_email" not in session:  # Admin oturumu kontrolü
        return redirect(url_for("login"))
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Tüm randevuları al
    cursor.execute("SELECT appointmentID, patient.name, patient.surname, doctor.name, doctor.surname, appointment.date, appointment.time, appointment.status "
                   "FROM appointment "
                   "JOIN patient ON appointment.patientID = patient.patientID "
                   "JOIN doctor ON appointment.doctorID = doctor.doctorID")
    appointments = cursor.fetchall()

    connection.close()

    # Randevular sayfasına verileri gönder
    return render_template("appointments.html", appointments=appointments)

# Admin randevu düzenleme
@app.route("/editAppointment/<int:appointment_id>", methods=["GET", "POST"]) # Randevu ID'sini alır
def edit_appointment(appointment_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Randevu bilgilerini al
    cursor.execute("SELECT appointmentID, patientID, doctorID, date, time, status FROM appointment WHERE appointmentID = ?", (appointment_id,))
    appointment = cursor.fetchone()
    
    if request.method == "POST":
        # Form verilerini al
        new_date = request.form["date"]
        new_time = request.form["time"]
        new_status = request.form["status"]

        # Veritabanını güncelle
        cursor.execute("UPDATE appointment SET date = ?, time = ?, status = ? WHERE appointmentID = ?",
                       (new_date, new_time, new_status, appointment_id))
        connection.commit()
        connection.close()

        return redirect(url_for("appointments"))  # Randevular sayfasına geri yönlendir

    connection.close()
    return render_template("editAppointment.html", appointment=appointment) # Randevu düzenleme sayfasına verileri gönder

# Admin randevu silme
@app.route("/deleteAppointment/<int:appointment_id>", methods=["POST"])
def delete_appointment(appointment_id):
    if "admin_email" not in session:
        return redirect(url_for("login"))
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Randevuyu sil
    cursor.execute("DELETE FROM appointment WHERE appointmentID = ?", (appointment_id,))
    connection.commit()
    connection.close()

    return redirect(url_for("appointments"))

# Admin doktor yönetimi
@app.route("/doctors")
def doctors():
    if "admin_email" not in session:
        return redirect(url_for("login"))
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Doktorları al
    cursor.execute("SELECT doctorID, name, surname, email ,department, workHours , contact_info FROM doctor")
    doctors = cursor.fetchall()

    connection.close()

    # Doktorlar sayfasına verileri gönder
    return render_template("doctors.html", doctors=doctors)

# Admin doktor ekleme
@app.route("/addDoctor", methods=["GET", "POST"])
def add_doctor():
    if "admin_email" not in session:
        return redirect(url_for("login"))
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Tüm departmanları al
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()

    if request.method == "POST":
        # Formdan gelen verileri al
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        workHours = request.form["workHours"]
        department = request.form["department"]
        contact_info = request.form["contact_info"]

        # Doktoru doctor tablosuna ekle
        cursor.execute('''INSERT INTO doctor (name, surname, email, workHours, department, contact_info)
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (name, surname, email, workHours, department, contact_info))
        
        # Doktoru users tablosuna ekle
        cursor.execute('''INSERT INTO users (email, name, password, job)
                          VALUES (?, ?, ?, ?)''', 
                       (email, name, "1234", "doctor"))

        connection.commit()
        connection.close()

        return redirect(url_for("doctors"))  # Doktorlar sayfasına yönlendirme

    connection.close()

    return render_template("addDoctor.html", departments=departments) # Doktor ekleme sayfasına verileri gönder

# Admin doktor düzenleme
@app.route("/editDoctor/<int:doctor_id>", methods=["GET", "POST"])
def edit_doctor(doctor_id):
    if "admin_email" not in session:
        return redirect(url_for("login"))
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Doktor bilgilerini al
    cursor.execute("SELECT * FROM doctor WHERE doctorID = ?", (doctor_id,))
    doctor = cursor.fetchone()

    if not doctor:
        return "Doctor not found."

    # Tüm departmanları al
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()

    if request.method == "POST":
        # Formdan gelen verileri al
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        workHours = request.form["workHours"]
        department_name = request.form["department"]  # Kullanıcının seçtiği departman adı
        contact_info = request.form["contact_info"]

        
        # Doktorun bilgilerini güncelle
        cursor.execute('''UPDATE doctor
                          SET name = ?, surname = ?, email = ?, workHours = ?, department = ?, contact_info = ?
                          WHERE doctorID = ?''', 
                       (name, surname, email, workHours, department_name, contact_info, doctor_id))
        connection.commit()
        connection.close()

        return redirect(url_for("admin_menu")) # Admin menüsüne yönlendirme
    
    connection.close()

    return render_template("editDoctor.html", doctor=doctor, departments=departments) # Doktor düzenleme sayfasına verileri gönder

# Admin doktor silme
@app.route("/deleteDoctor/<int:doctor_id>", methods=["POST"])
def delete_doctor(doctor_id):
    if "admin_email" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Doktoru sil
    cursor.execute("DELETE FROM doctor WHERE doctorID = ?", (doctor_id,))
    connection.commit()
    connection.close()

    return redirect(url_for("doctors"))

# Admin bölüm yönetimi
@app.route("/departments", methods=["GET", "POST"])
def departments():
    if "user_email" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    if request.method == "POST":
        department = request.form["department"]

        # Yeni departmanı veritabanına ekleme
        cursor.execute("INSERT INTO departments (departmentName) VALUES (?)", (department,))
        connection.commit()
        connection.close()

        return redirect(url_for("departments"))  # Aynı sayfaya yönlendirerek yeni departmanı gösterme

    # Tüm departmanları al
    cursor.execute("SELECT departmentName FROM departments")
    departments = cursor.fetchall()

    connection.close()

    return render_template("departments.html", departments=departments) # Departman sayfasına verileri gönder

# Session kontrolü
@app.before_request
def log_session():
    print(f"Session Data: {session}")

# Uygulamayı çalıştır
if __name__ == "__main__":
    app.run(debug=True) #Debug modunda çalıştır



