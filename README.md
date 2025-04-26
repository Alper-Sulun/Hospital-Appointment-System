# 🏥 Hospital Appointment System

## 📚 Proje Hakkında
Bu proje, web tabanlı bir **Hastane Randevu Sistemi** geliştirmeyi amaçlamaktadır.  
Kullanıcılar (hastalar, doktorlar, yöneticiler) için farklı yetkilerle oturum yönetimi ve randevu işlemleri sunar.

---

## 🚀 Özellikler
- 👤 Kullanıcı oturum yönetimi (Kayıt Ol / Giriş Yap / Çıkış Yap)
- 🩺 Hasta, Doktor ve Yönetici rollerine özel işlevler
- 💾 SQLite veritabanı ile dinamik veri yönetimi
- 🌐 Flask tabanlı web arayüzü
- 🔒 Yetkilendirme sistemi

---

## 🛠️ Kullanılan Teknolojiler
- **Programlama Dili**: Python 🐍
- **Web Framework**: Flask ⚡
- **Veritabanı**: SQLite 📂
- **Harici Kütüphaneler**: `flask`, `sqlite3`

---

## 🏗️ Proje Yapısı
- **Kullanıcı Arayüzü**: Basit ve kullanıcı dostu HTML + Flask şablonları
- **Veritabanı Tabloları**:
  - `users` — Kullanıcı temel bilgileri
  - `patient` — Hasta bilgileri
  - `doctor` — Doktor bilgileri
  - `admin` — Yönetici bilgileri
- **Ana Fonksiyonlar**:
  - `init_db()` — Veritabanını başlatır ve gerekli tabloları oluşturur
  - Kullanıcı oturumları için Flask `session` kullanımı

---

