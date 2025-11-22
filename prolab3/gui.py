import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import mysql.connector
import smtplib
from email.mime.text import MIMEText
import random
import string

class DiyabetTakipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diyabet Takip Sistemi")
        self.root.configure(bg="#f0f0f0")
        self.kullanici_id = None
        self.rol = None
        self.isim = None
        self.soyisim = None
        self.eposta = None
        self.profil_resmi = None
        self.kan_sekeri_verileri = []
        self.belirtiler = []
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Kalemlik.71",
                database="diyabet_takip"
            )
            self.cursor = self.db.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı bağlantı hatası: {err}")
            self.root.destroy()
            return
        self.giris_ekrani()

    def giris_ekrani(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("400x300")
        frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        frame.grid(row=0, column=0, sticky="nsew")
        tk.Label(frame, text="Diyabet Takip Sistemi", font=("Arial", 14, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(frame, text="T.C. Kimlik No:", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
        self.tc_entry = tk.Entry(frame)
        self.tc_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="Şifre:", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
        self.sifre_entry = tk.Entry(frame, show="*")
        self.sifre_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="Giriş Yap", command=self.giris_kontrol, bg="#4CAF50", fg="white", padx=10).grid(row=3, column=0, columnspan=2, pady=15)
        tk.Button(frame, text="Şifremi Unuttum", command=self.sifremi_unuttum, bg="#FF9800", fg="white", padx=10).grid(row=4, column=0, columnspan=2, pady=5)

    def sifremi_unuttum(self):
        tc = simpledialog.askstring("T.C. Kimlik No", "T.C. Kimlik Numaranızı Girin:")
        if not tc:
            return
        query = "SELECT eposta FROM Kullanicilar WHERE tc_kimlik = %s"
        self.cursor.execute(query, (tc,))
        user = self.cursor.fetchone()
        if not user:
            messagebox.showerror("Hata", "Bu T.C. Kimlik Numarası kayıtlı değil!")
            return
        eposta = user['eposta']
        sifirlama_kodu = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        gecerlilik = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "UPDATE Kullanicilar SET sifirlama_kodu = %s, sifirlama_gecerlilik = %s WHERE tc_kimlik = %s"
        self.cursor.execute(query, (sifirlama_kodu, gecerlilik, tc))
        self.db.commit()
        mesaj = f"Şifre sıfırlama kodunuz: {sifirlama_kodu}\nBu kod 10 dakika boyunca geçerlidir."
        self.mail_gonder("Şifre Sıfırlama Kodu", mesaj, eposta)
        kod = simpledialog.askstring("Sıfırlama Kodu", "E-postanıza gelen sıfırlama kodunu girin:")
        if not kod:
            return
        query = "SELECT sifirlama_kodu, sifirlama_gecerlilik FROM Kullanicilar WHERE tc_kimlik = %s"
        self.cursor.execute(query, (tc,))
        user = self.cursor.fetchone()
        if user['sifirlama_kodu'] != kod:
            messagebox.showerror("Hata", "Geçersiz sıfırlama kodu!")
            return
        gecerlilik = datetime.strptime(user['sifirlama_gecerlilik'], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - gecerlilik).seconds > 600:
            messagebox.showerror("Hata", "Sıfırlama kodunun süresi dolmuş!")
            return
        yeni_sifre = simpledialog.askstring("Yeni Şifre", "Yeni şifrenizi girin:", show="*")
        if not yeni_sifre:
            return
        query = "UPDATE Kullanicilar SET sifre = AES_ENCRYPT(%s, 'your_secure_key_32_bytes_long!!!'), sifirlama_kodu = NULL, sifirlama_gecerlilik = NULL WHERE tc_kimlik = %s"
        self.cursor.execute(query, (yeni_sifre, tc))
        self.db.commit()
        messagebox.showinfo("Başarılı", "Şifreniz başarıyla değiştirildi!")

    def giris_kontrol(self):
        tc = self.tc_entry.get()
        sifre = self.sifre_entry.get()
        if not tc or not sifre:
            messagebox.showerror("Hata", "T.C. Kimlik No ve Şifre boş olamaz!")
            return
        if not (tc.isdigit() and len(tc) == 11):
            messagebox.showerror("Hata", "T.C. Kimlik No 11 haneli bir sayı olmalıdır!")
            return
        query = """
        SELECT kullanici_id, rol, isim, soyisim, eposta,
               AES_DECRYPT(sifre, 'your_secure_key_32_bytes_long!!!') AS sifre
        FROM Kullanicilar
        WHERE tc_kimlik = %s
        """
        try:
            self.cursor.execute(query, (tc,))
            user = self.cursor.fetchone()
            if user and user['sifre'].decode('utf-8') == sifre:
                self.kullanici_id = user['kullanici_id']
                self.rol = user['rol']
                self.isim = user['isim']
                self.soyisim = user['soyisim']
                self.eposta = user['eposta']
                if self.rol == "Doktor":
                    self.doktor_ekrani()
                else:
                    self.hasta_ekrani()
            else:
                messagebox.showerror("Hata", "Geçersiz T.C. Kimlik No veya Şifre!")
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı hatası: {err}")
        except UnicodeDecodeError:
            messagebox.showerror("Hata", "Şifre çözümleme hatası, anahtarı kontrol edin!")

    def hasta_ekrani(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("700x900")
        frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        frame.grid(row=0, column=0, sticky="nsew")
        tk.Label(frame, text="Hasta Ekranı", font=("Arial", 14, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Şifremi Değiştir", command=self.sifre_degistir, bg="#FF9800", fg="white", padx=10).grid(row=0, column=2, pady=5)
        tk.Label(frame, text="Kan Şekeri Değeri (mg/dL):", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
        self.kan_sekeri_entry = tk.Entry(frame)
        self.kan_sekeri_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="Ölçüm Tipi:", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
        self.olcum_tipi = tk.StringVar(value="Sabah")
        tk.OptionMenu(frame, self.olcum_tipi, "Sabah", "Öğle", "İkindi", "Akşam", "Gece").grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="Kan Şekeri Kaydet", command=self.kan_sekeri_kaydet, bg="#4CAF50", fg="white", padx=10).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Günlük Ortalama", command=self.gunluk_kan_sekeri_ortalamasi, bg="#2196F3", fg="white", padx=10).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Grafik Göster", command=self.grafik_goster, bg="#2196F3", fg="white", padx=10).grid(row=5, column=0, columnspan=2, pady=5)
        tk.Label(frame, text="Belirtiler:", bg="#ffffff").grid(row=6, column=0, padx=5, pady=5)
        self.belirti_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Belirti Seç", variable=self.belirti_var, command=self.belirti_secenek_goster, bg="#ffffff").grid(row=6, column=1, sticky="w")
        self.belirti_frame = tk.Frame(frame, bg="#ffffff")
        self.belirti_frame.grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Belirtileri Kaydet", command=self.belirti_kaydet, bg="#4CAF50", fg="white", padx=10).grid(row=8, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Diyet/Egzersiz Yüzdeleri", command=self.diyet_egzersiz_yuzdeleri, bg="#2196F3", fg="white", padx=10).grid(row=9, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="İnsülin Önerileri", command=self.insulin_onerileri, bg="#2196F3", fg="white", padx=10).grid(row=10, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Diyet Kaydet", command=self.diyet_kaydet, bg="#4CAF50", fg="white", padx=10).grid(row=11, column=0, pady=5)
        self.diyet_turu = tk.StringVar(value="Az Şekerli Diyet")
        tk.OptionMenu(frame, self.diyet_turu, "Az Şekerli Diyet", "Şekersiz Diyet", "Dengeli Beslenme").grid(row=11, column=1, pady=5)
        tk.Button(frame, text="Egzersiz Kaydet", command=self.egzersiz_kaydet, bg="#4CAF50", fg="white", padx=10).grid(row=12, column=0, pady=5)
        self.egzersiz_turu = tk.StringVar(value="Yürüyüş")
        tk.OptionMenu(frame, self.egzersiz_turu, "Yürüyüş", "Bisiklet", "Klinik Egzersiz").grid(row=12, column=1, pady=5)
        self.durum_var = tk.StringVar(value="Uygulandı")
        tk.OptionMenu(frame, self.durum_var, "Uygulandı", "Uygulanmadı").grid(row=13, column=1, pady=5)
        self.grafik_frame = tk.Frame(frame, bg="#ffffff")
        self.grafik_frame.grid(row=14, column=0, columnspan=2, pady=10)
        tk.Label(frame, text=f"Profil: {self.isim} {self.soyisim}", font=("Arial", 12), bg="#ffffff").grid(row=15, column=0, columnspan=2, pady=10)

    def sifre_degistir(self):
        eski_sifre = simpledialog.askstring("Eski Şifre", "Mevcut şifrenizi girin:", show="*")
        if not eski_sifre:
            return
        query = "SELECT AES_DECRYPT(sifre, 'your_secure_key_32_bytes_long!!!') AS sifre FROM Kullanicilar WHERE kullanici_id = %s"
        self.cursor.execute(query, (self.kullanici_id,))
        user = self.cursor.fetchone()
        if user['sifre'].decode('utf-8') != eski_sifre:
            messagebox.showerror("Hata", "Eski şifre yanlış!")
            return
        yeni_sifre = simpledialog.askstring("Yeni Şifre", "Yeni şifrenizi girin:", show="*")
        if not yeni_sifre:
            return
        query = "UPDATE Kullanicilar SET sifre = AES_ENCRYPT(%s, 'your_secure_key_32_bytes_long!!!') WHERE kullanici_id = %s"
        self.cursor.execute(query, (yeni_sifre, self.kullanici_id))
        self.db.commit()
        messagebox.showinfo("Başarılı", "Şifreniz başarıyla değiştirildi!")

    def belirti_secenek_goster(self):
        for widget in self.belirti_frame.winfo_children():
            widget.destroy()
        if self.belirti_var.get():
            belirtiler = ["Yorgunluk", "Baş Ağrısı", "Polidipsi", "Hiçbiri"]
            self.secili_belirtiler = []
            for i, belirti in enumerate(belirtiler):
                var = tk.BooleanVar()
                tk.Checkbutton(self.belirti_frame, text=belirti, variable=var, bg="#ffffff", command=lambda v=var, b=belirti: self.belirti_sec(v, b)).grid(row=i//2, column=i%2, padx=5, pady=2)

    def belirti_sec(self, var, belirti):
        if var.get():
            if belirti != "Hiçbiri" and "Hiçbiri" not in self.secili_belirtiler:
                self.secili_belirtiler.append(belirti)
            elif belirti == "Hiçbiri":
                self.secili_belirtiler = ["Hiçbiri"]
        else:
            if belirti in self.secili_belirtiler:
                self.secili_belirtiler.remove(belirti)
            if "Hiçbiri" in self.secili_belirtiler:
                self.secili_belirtiler.remove("Hiçbiri")

    def kan_sekeri_kaydet(self):
        deger = self.kan_sekeri_entry.get()
        if not deger:
            messagebox.showerror("Hata", "Kan şekeri değeri boş olamaz!")
            return
        try:
            deger = int(deger)
            if deger < 0 or deger > 1000:
                messagebox.showerror("Hata", "Kan şekeri 0-1000 mg/dL arasında olmalıdır!")
                return
            olcum_tipi = self.olcum_tipi.get()
            tarih = datetime.now()
            saat = tarih.hour
            saat_araliklari = {"Sabah": (7, 8), "Öğle": (12, 13), "İkindi": (15, 16), "Akşam": (18, 19), "Gece": (22, 23)}
            baslangic, bitis = saat_araliklari[olcum_tipi]
            if not (baslangic <= saat <= bitis):
                messagebox.showwarning("Uyarı", f"{olcum_tipi} ölçümü {baslangic}:00 - {bitis}:00 arasında yapılmalıdır.")
            query = "INSERT INTO KanSekeriOlcumleri (hasta_id, olcum_degeri, olcum_tipi, olcum_tarihi) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (self.kullanici_id, deger, olcum_tipi, tarih))
            self.db.commit()
            messagebox.showinfo("Başarılı", f"Kan Şekeri Değeri: {deger} mg/dL, Ölçüm Tipi: {olcum_tipi}, Tarih: {tarih.strftime('%d.%m.%Y %H:%M:%S')} kaydedildi.")
            uyari_tipi, mesaj = self.uyari_olustur(deger)
            if uyari_tipi:
                self.mail_gonder(uyari_tipi, mesaj)
                messagebox.showinfo("Uyarı", f"Uyarı Türü: {uyari_tipi}\nMesaj: {mesaj}")
        except ValueError:
            messagebox.showerror("Hata", "Kan şekeri pozitif bir tamsayı olmalıdır!")
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def gunluk_kan_sekeri_ortalamasi(self):
        bugun = datetime.now().date()
        query = "SELECT olcum_degeri FROM KanSekeriOlcumleri WHERE hasta_id = %s AND DATE(olcum_tarihi) = %s"
        self.cursor.execute(query, (self.kullanici_id, bugun))
        veriler = self.cursor.fetchall()
        if not veriler:
            messagebox.showinfo("Uyarı", "Henüz ölçüm kaydedilmedi.")
            return
        degerler = [v['olcum_degeri'] for v in veriler]
        ortalama = sum(degerler) / len(degerler)
        messagebox.showinfo("Günlük Ortalama", f"Bugünkü ortalama kan şekeri: {ortalama:.1f} mg/dL (Toplam {len(degerler)} ölçüm)")

    def grafik_goster(self):
        query = "SELECT olcum_tarihi, olcum_degeri FROM KanSekeriOlcumleri WHERE hasta_id = %s"
        self.cursor.execute(query, (self.kullanici_id,))
        veriler = self.cursor.fetchall()
        if veriler:
            tarihler = [v['olcum_tarihi'] for v in veriler]
            degerler = [v['olcum_degeri'] for v in veriler]
            fig, ax = plt.subplots()
            ax.plot(tarihler, degerler)
            ax.set_title("Kan Şekeri Değişimi")
            ax.set_xlabel("Zaman")
            ax.set_ylabel("Kan Şekeri (mg/dL)")
            plt.xticks(rotation=45)
            for widget in self.grafik_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.grafik_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            messagebox.showinfo("Uyarı", "Ölçüm kaydedilmedi, grafik oluşturulamadı.")

    def diyet_egzersiz_yuzdeleri(self):
        query = "SELECT diyet_turu, durum FROM DiyetTakibi WHERE hasta_id = %s"
        self.cursor.execute(query, (self.kullanici_id,))
        diyet_veriler = self.cursor.fetchall()
        uygula = sum(1 for d in diyet_veriler if d['durum'] == 'Uygulandı')
        toplam = len(diyet_veriler) if diyet_veriler else 1
        diyet_yuzde = (uygula / toplam) * 100 if toplam > 0 else 0

        query = "SELECT egzersiz_turu, durum FROM EgzersizTakibi WHERE hasta_id = %s"
        self.cursor.execute(query, (self.kullanici_id,))
        egzersiz_veriler = self.cursor.fetchall()
        uygula = sum(1 for e in egzersiz_veriler if e['durum'] == 'Yapıldı')
        toplam = len(egzersiz_veriler) if egzersiz_veriler else 1
        egzersiz_yuzde = (uygula / toplam) * 100 if toplam > 0 else 0
        messagebox.showinfo("Yüzdeler", f"Diyet Yüzdeleri: {diyet_yuzde:.1f}% Uygulandı\nEgzersiz Yüzdeleri: {egzersiz_yuzde:.1f}% Yapıldı")

    def insulin_onerileri(self):
        bugun = datetime.now().date()
        query = "SELECT olcum_degeri FROM KanSekeriOlcumleri WHERE hasta_id = %s AND DATE(olcum_tarihi) = %s"
        self.cursor.execute(query, (self.kullanici_id, bugun))
        veriler = self.cursor.fetchall()
        if veriler:
            degerler = [v['olcum_degeri'] for v in veriler]
            ortalama = sum(degerler) / len(degerler)
            insulin = self.insulin_onerisi(ortalama)
            messagebox.showinfo("İnsülin Önerileri", f"Önerilen İnsülin: {insulin} ml")
        else:
            messagebox.showinfo("Uyarı", "Bugün için ölçüm yok.")

    def diyet_kaydet(self):
        tarih = datetime.now()
        query = "INSERT INTO DiyetTakibi (hasta_id, diyet_turu, durum, tarih) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (self.kullanici_id, self.diyet_turu.get(), self.durum_var.get(), tarih))
            self.db.commit()
            messagebox.showinfo("Başarılı", f"Diyet Türü: {self.diyet_turu.get()}, Durum: {self.durum_var.get()}, Tarih: {tarih.strftime('%d.%m.%Y %H:%M:%S')} kaydedildi.")
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def egzersiz_kaydet(self):
        tarih = datetime.now()
        query = "INSERT INTO EgzersizTakibi (hasta_id, egzersiz_turu, durum, tarih) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (self.kullanici_id, self.egzersiz_turu.get(), self.durum_var.get(), tarih))
            self.db.commit()
            messagebox.showinfo("Başarılı", f"Egzersiz Türü: {self.egzersiz_turu.get()}, Durum: {self.durum_var.get()}, Tarih: {tarih.strftime('%d.%m.%Y %H:%M:%S')} kaydedildi.")
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def belirti_kaydet(self):
        if self.belirti_var.get() and self.secili_belirtiler:
            self.belirtiler = self.secili_belirtiler
            tarih = datetime.now()
            for belirti in self.belirtiler:
                if belirti != "Hiçbiri":
                    query = "INSERT INTO Belirtiler (hasta_id, belirti_turu, tarih) VALUES (%s, %s, %s)"
                    try:
                        self.cursor.execute(query, (self.kullanici_id, belirti, tarih))
                        self.db.commit()
                    except mysql.connector.Error as err:
                        messagebox.showerror("Hata", f"Veritabanı hatası: {err}")
                        return
            messagebox.showinfo("Başarılı", f"Belirtiler: {', '.join(self.belirtiler)}, Tarih: {tarih.strftime('%d.%m.%Y %H:%M:%S')} kaydedildi.")
        else:
            messagebox.showinfo("Bilgi", "Belirti seçilmedi veya boş bırakıldı.")

    def doktor_ekrani(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("800x1000")
        frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        frame.grid(row=0, column=0, sticky="nsew")
        tk.Label(frame, text="Doktor Ekranı", font=("Arial", 14, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Şifremi Değiştir", command=self.sifre_degistir, bg="#FF9800", fg="white", padx=10).grid(row=0, column=2, pady=5)
        tk.Button(frame, text="Hasta Ekle", command=self.hasta_ekle, bg="#4CAF50", fg="white", padx=10).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Hasta Verilerini Görüntüle", command=self.hasta_verileri_goruntule, bg="#2196F3", fg="white", padx=10).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Kan Şekeri Takip", command=self.kan_sekeri_takip, bg="#2196F3", fg="white", padx=10).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Diyet/Egzersiz Geçmişi", command=self.diyet_egzersiz_gecmisi, bg="#2196F3", fg="white", padx=10).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Kan Şekeri ve İlişki Grafiği", command=self.kan_sekeri_iliiski_grafik, bg="#2196F3", fg="white", padx=10).grid(row=5, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Gün Bazlı Uyarilar", command=self.gun_bazli_uyarilar, bg="#FF9800", fg="white", padx=10).grid(row=6, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Filtreleme Uygula", command=self.filtrele, bg="#2196F3", fg="white", padx=10).grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Öneriler Ver", command=self.oneriler_ver, bg="#4CAF50", fg="white", padx=10).grid(row=8, column=0, columnspan=2, pady=5)
        tk.Label(frame, text=f"Profil: {self.isim} {self.soyisim}", font=("Arial", 12), bg="#ffffff").grid(row=15, column=0, columnspan=2, pady=10)

    def oneriler_ver(self):
        hasta_id = simpledialog.askinteger("Hasta ID", "Öneriler için Hasta ID'sini girin:")
        if hasta_id:
            query = "SELECT olcum_degeri FROM KanSekeriOlcumleri WHERE hasta_id = %s ORDER BY olcum_tarihi DESC LIMIT 1"
            try:
                self.cursor.execute(query, (hasta_id,))
                son_veri = self.cursor.fetchone()
                if son_veri:
                    deger = son_veri['olcum_degeri']
                    if deger < 70:
                        oneriler = "Acil: Şeker alımı yapın, doktora başvurun."
                    elif 70 <= deger <= 110:
                        oneriler = "Normal seviye, devam edin."
                    elif 111 <= deger <= 150:
                        oneriler = "Diyet kontrolü önerilir, hafif egzersiz yapın."
                    elif 151 <= deger <= 200:
                        oneriler = "İnsülin kontrolü ve diyet düzenlemesi önerilir."
                    else:
                        oneriler = "Acil: Doktora başvurun, insülin dozu artırılabilir."
                    messagebox.showinfo("Öneriler", f"Son Değer: {deger} mg/dL\nÖneri: {oneriler}")
                else:
                    messagebox.showinfo("Uyarı", "Bu hasta için veri yok.")
            except mysql.connector.Error as err:
                messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def hasta_ekle(self):
        tc = simpledialog.askstring("Hasta T.C.", "Hastanın T.C. Kimlik No'sunu girin:")
        sifre = simpledialog.askstring("Şifre", "Hastanın şifresini girin:")
        dogum_tarihi = simpledialog.askstring("Doğum Tarihi", "Doğum tarihini girin (DD.MM.YYYY):")
        cinsiyet = simpledialog.askstring("Cinsiyet", "Cinsiyeti girin (Erkek/Kadın/Diğer):")
        eposta = simpledialog.askstring("E-posta", "E-postayı girin:")
        isim = simpledialog.askstring("İsim", "Hastanın ismini girin:")
        soyisim = simpledialog.askstring("Soyisim", "Hastanın soyismini girin:")
        if not all([tc, sifre, dogum_tarihi, cinsiyet, eposta, isim, soyisim]):
            messagebox.showerror("Hata", "Tüm alanlar doldurulmalıdır!")
            return
        if not (tc.isdigit() and len(tc) == 11):
            messagebox.showerror("Hata", "T.C. Kimlik No 11 haneli bir sayı olmalıdır!")
            return
        try:
            dogum_tarihi_sql = datetime.strptime(dogum_tarihi, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Hata", "Doğum tarihi DD.MM.YYYY formatında olmalıdır!")
            return
        if not "@" in eposta or not "." in eposta:
            messagebox.showerror("Hata", "Geçersiz e-posta formatı!")
            return
        query_kullanici = """
        INSERT INTO Kullanicilar (tc_kimlik, sifre, rol, dogum_tarihi, cinsiyet, eposta, isim, soyisim, kayit_tarihi)
        VALUES (%s, AES_ENCRYPT(%s, 'your_secure_key_32_bytes_long!!!'), %s, %s, %s, %s, %s, %s, %s)
        """
        query_hasta = "INSERT INTO Hastalar (doktor_id, tc_kimlik) VALUES (%s, %s)"
        try:
            self.cursor.execute(query_kullanici, (tc, sifre, 'Hasta', dogum_tarihi_sql, cinsiyet, eposta, isim, soyisim, datetime.now()))
            self.cursor.execute(query_hasta, (self.kullanici_id, tc))
            self.db.commit()
            self.mail_gonder("Yeni Hasta Kaydı", f"Hasta {isim} {soyisim} sisteme eklendi.\nKullanıcı Adı (T.C.): {tc}\nŞifre: {sifre}", eposta)
            messagebox.showinfo("Başarılı", f"Hasta eklendi: T.C.: {tc}, İsim: {isim} {soyisim}")
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def hasta_verileri_goruntule(self):
        query = """
        SELECT K.tc_kimlik, K.isim, K.soyisim, DATE_FORMAT(K.dogum_tarihi, '%d.%m.%Y') AS dogum_tarihi, K.cinsiyet, K.eposta
        FROM Kullanicilar K
        JOIN Hastalar H ON K.tc_kimlik = H.tc_kimlik
        WHERE K.rol = 'Hasta' AND H.doktor_id = %s
        """
        try:
            self.cursor.execute(query, (self.kullanici_id,))
            hastalar = self.cursor.fetchall()
            if not hastalar:
                messagebox.showinfo("Bilgi", "Bu doktora atanmış hasta bulunamadı.")
                return
            veriler = "\n".join([f"T.C.: {h['tc_kimlik']}, İsim: {h['isim']} {h['soyisim']}, Doğum Tarihi: {h['dogum_tarihi']}, Cinsiyet: {h['cinsiyet']}, E-posta: {h['eposta']}" for h in hastalar])
            messagebox.showinfo("Hasta Verileri", veriler)
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def kan_sekeri_takip(self):
        hasta_id = simpledialog.askinteger("Hasta ID", "Takip etmek için Hasta ID'sini girin:")
        if hasta_id:
            query = "SELECT olcum_degeri, olcum_tipi, DATE_FORMAT(olcum_tarihi, '%d.%m.%Y %H:%M:%S') AS olcum_tarihi FROM KanSekeriOlcumleri WHERE hasta_id = %s ORDER BY olcum_tarihi"
            try:
                self.cursor.execute(query, (hasta_id,))
                veriler = self.cursor.fetchall()
                if veriler:
                    veriler_str = "\n".join([f"Değer: {v['olcum_degeri']} mg/dL, Tip: {v['olcum_tipi']}, Tarih: {v['olcum_tarihi']}" for v in veriler])
                    messagebox.showinfo("Kan Şekeri Takip", veriler_str)
                else:
                    messagebox.showinfo("Uyarı", "Bu hasta için veri bulunamadı.")
            except mysql.connector.Error as err:
                messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def diyet_egzersiz_gecmisi(self):
        hasta_id = simpledialog.askinteger("Hasta ID", "Geçmişi görmek için Hasta ID'sini girin:")
        if hasta_id:
            query_diyet = "SELECT diyet_turu, durum, DATE_FORMAT(tarih, '%d.%m.%Y %H:%M:%S') AS tarih FROM DiyetTakibi WHERE hasta_id = %s"
            query_egzersiz = "SELECT egzersiz_turu, durum, DATE_FORMAT(tarih, '%d.%m.%Y %H:%M:%S') AS tarih FROM EgzersizTakibi WHERE hasta_id = %s"
            try:
                self.cursor.execute(query_diyet, (hasta_id,))
                diyet_veriler = self.cursor.fetchall()
                self.cursor.execute(query_egzersiz, (hasta_id,))
                egzersiz_veriler = self.cursor.fetchall()
                diyet_str = "\n".join([f"Tür: {v['diyet_turu']}, Durum: {v['durum']}, Tarih: {v['tarih']}" for v in diyet_veriler]) if diyet_veriler else "Yok"
                egzersiz_str = "\n".join([f"Tür: {v['egzersiz_turu']}, Durum: {v['durum']}, Tarih: {v['tarih']}" for v in egzersiz_veriler]) if egzersiz_veriler else "Yok"
                uygula_diyet = sum(1 for d in diyet_veriler if d['durum'] == 'Uygulandı')
                toplam_diyet = len(diyet_veriler) if diyet_veriler else 1
                diyet_yuzde = (uygula_diyet / toplam_diyet) * 100 if toplam_diyet > 0 else 0
                uygula_egzersiz = sum(1 for e in egzersiz_veriler if e['durum'] == 'Yapıldı')
                toplam_egzersiz = len(egzersiz_veriler) if egzersiz_veriler else 1
                egzersiz_yuzde = (uygula_egzersiz / toplam_egzersiz) * 100 if toplam_egzersiz > 0 else 0
                messagebox.showinfo("Geçmiş ve Yüzdeler", f"Diyet Geçmişi:\n{diyet_str}\nDiyet Uygulama Oranı: {diyet_yuzde:.1f}%\nEgzersiz Geçmişi:\n{egzersiz_str}\nEgzersiz Yapma Oranı: {egzersiz_yuzde:.1f}%")
            except mysql.connector.Error as err:
                messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def kan_sekeri_iliiski_grafik(self):
        hasta_id = simpledialog.askinteger("Hasta ID", "Grafik için Hasta ID'sini girin:")
        if hasta_id:
            query_kan = "SELECT olcum_tarihi, olcum_degeri FROM KanSekeriOlcumleri WHERE hasta_id = %s"
            query_diyet = "SELECT tarih FROM DiyetTakibi WHERE hasta_id = %s AND durum = 'Uygulandı'"
            query_egzersiz = "SELECT tarih FROM EgzersizTakibi WHERE hasta_id = %s AND durum = 'Yapıldı'"
            try:
                self.cursor.execute(query_kan, (hasta_id,))
                kan_veriler = self.cursor.fetchall()
                self.cursor.execute(query_diyet, (hasta_id,))
                diyet_veriler = [v['tarih'] for v in self.cursor.fetchall()]
                self.cursor.execute(query_egzersiz, (hasta_id,))
                egzersiz_veriler = [v['tarih'] for v in self.cursor.fetchall()]
                if kan_veriler:
                    tarihler = [v['olcum_tarihi'] for v in kan_veriler]
                    degerler = [v['olcum_degeri'] for v in kan_veriler]
                    fig, ax = plt.subplots()
                    ax.plot(tarihler, degerler, label="Kan Şekeri", color="blue")
                    for t in diyet_veriler:
                        ax.axvline(x=t, color="green", linestyle="--", label="Diyet" if t == diyet_veriler[0] else "")
                    for t in egzersiz_veriler:
                        ax.axvline(x=t, color="orange", linestyle="--", label="Egzersiz" if t == egzersiz_veriler[0] else "")
                    ax.set_title("Kan Şekeri ve Diyet/Egzersiz İlişkisi")
                    ax.set_xlabel("Zaman")
                    ax.set_ylabel("Kan Şekeri (mg/dL)")
                    plt.xticks(rotation=45)
                    ax.legend()
                    for widget in self.grafik_frame.winfo_children():
                        widget.destroy()
                    canvas = FigureCanvasTkAgg(fig, master=self.grafik_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack()
                else:
                    messagebox.showinfo("Uyarı", "Ölçüm bulunamadı, grafik oluşturulamadı.")
            except mysql.connector.Error as err:
                messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def gun_bazli_uyarilar(self):
        bugun = datetime.now().date()
        query = """
        SELECT olcum_degeri, olcum_tarihi, hasta_id
        FROM KanSekeriOlcumleri
        WHERE hasta_id IN (SELECT tc_kimlik FROM Hastalar WHERE doktor_id = %s)
        AND DATE(olcum_tarihi) = %s
        """
        try:
            self.cursor.execute(query, (self.kullanici_id, bugun))
            veriler = self.cursor.fetchall()
            uyarilar = []
            if not veriler:
                uyarilar.append("Ölçüm Eksik Uyarısı - Gün boyu ölçüm yapılmadı.")
            elif len(veriler) < 3:
                uyarilar.append("Ölçüm Yetersiz Uyarısı - 3'ten az ölçüm girildi.")
            for v in veriler:
                if v['olcum_degeri'] < 70:
                    uyarilar.append(f"Hipoglisemi Uyarısı - Hasta ID: {v['hasta_id']}, Kan şekeri {v['olcum_degeri']} mg/dL - {v['olcum_tarihi']}")
                elif v['olcum_degeri'] >= 200:
                    uyarilar.append(f"Hiperglisemi Uyarısı - Hasta ID: {v['hasta_id']}, Kan şekeri {v['olcum_degeri']} mg/dL - {v['olcum_tarihi']}")
            if uyarilar:
                self.mail_gonder("Günlük Uyarilar", "\n".join(uyarilar))
                messagebox.showinfo("Gün Bazlı Uyarilar", "\n".join(uyarilar))
            else:
                messagebox.showinfo("Bilgi", "Uyarı yok, tüm ölçümler normal.")
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def filtrele(self):
        hasta_id = simpledialog.askinteger("Hasta ID", "Filtrelemek için Hasta ID'sini girin:")
        min_deger = simpledialog.askinteger("Minimum Değer", "Minimum kan şekeri değerini girin (mg/dL):")
        max_deger = simpledialog.askinteger("Maksimum Değer", "Maksimum kan şekeri değerini girin (mg/dL):")
        belirti = simpledialog.askstring("Belirti", "Filtrelemek için belirti girin (isteğe bağlı):")
        if hasta_id and min_deger is not None and max_deger is not None:
            query = """
            SELECT olcum_degeri, olcum_tipi, DATE_FORMAT(olcum_tarihi, '%d.%m.%Y %H:%M:%S') AS olcum_tarihi
            FROM KanSekeriOlcumleri K
            LEFT JOIN Belirtiler B ON K.hasta_id = B.hasta_id AND DATE(B.tarih) = DATE(K.olcum_tarihi)
            WHERE K.hasta_id = %s AND olcum_degeri BETWEEN %s AND %s
            """
            params = [hasta_id, min_deger, max_deger]
            if belirti:
                query += " AND B.belirti_turu = %s"
                params.append(belirti)
            try:
                self.cursor.execute(query, params)
                veriler = self.cursor.fetchall()
                sonuc = [f"Değer: {v['olcum_degeri']} mg/dL, Tip: {v['olcum_tipi']}, Tarih: {v['olcum_tarihi']}" for v in veriler]
                messagebox.showinfo("Filtreleme Sonucu", "\n".join(sonuc) if sonuc else "Hiçbir veri bulunamadı.")
            except mysql.connector.Error as err:
                messagebox.showerror("Hata", f"Veritabanı hatası: {err}")

    def mail_gonder(self, konu, mesaj, alici=None):
        if not alici:
            query = "SELECT eposta FROM Kullanicilar WHERE kullanici_id = %s"
            self.cursor.execute(query, (self.kullanici_id,))
            user = self.cursor.fetchone()
            if not user or not user['eposta']:
                messagebox.showerror("Hata", "E-posta adresi bulunamadı!")
                return
            alici = user['eposta']
        gonderici = "simal411975@gmail.com"
        sifre = "xayb yrts zqmk shcs"
        msg = MIMEText(mesaj)
        msg['Subject'] = konu
        msg['From'] = gonderici
        msg['To'] = alici
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gonderici, sifre)
            server.sendmail(gonderici, alici, msg.as_string())
            server.quit()
            messagebox.showinfo("Başarılı", f"E-posta {alici} adresine gönderildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"E-posta gönderim hatası: {e}")

    def uyari_olustur(self, kan_sekeri):
        if kan_sekeri < 70:
            return "Acil Uyarı", "Hastanın kan şekeri 70 mg/dL'nin altına düştü. Hipoglisemi riski! Hızlı müdahale gerekebilir."
        elif kan_sekeri >= 200:
            return "Acil Müdahale Uyarısı", "Hastanın kan şekeri 200 mg/dL'nin üzerinde. Hiperglisemi durumu. Acil müdahale gerekebilir."
        elif 111 <= kan_sekeri <= 150:
            return "Takip Uyarısı", "Hastanın kan şekeri 111-150 mg/dL arasında. Durum izlenmeli."
        elif 151 <= kan_sekeri <= 200:
            return "İzleme Uyarısı", "Hastanın kan şekeri 151-200 mg/dL arasında. Diyabet kontrolü gereklidir."
        return None, None

    def insulin_onerisi(self, ortalama_kan_sekeri):
        if ortalama_kan_sekeri < 70:
            return "Yok"
        elif 70 <= ortalama_kan_sekeri <= 110:
            return "Yok"
        elif 111 <= ortalama_kan_sekeri <= 150:
            return "1 ml"
        elif 151 <= ortalama_kan_sekeri <= 200:
            return "2 ml"
        else:
            return "3 ml"