class Logic:
    def __init__(self):
        self.diyet_egzersiz_kurallari = {
            (0, 70): [("Nöropati", "Polifaji", "Yorgunluk"), "Dengeli Beslenme", "Yok"],
            (70, 110): [("Yorgunluk", "Kilo Kaybı"), "Az Şekerli Diyet", "Yürüyüş"],
            (70, 110): [("Polifaji", "Polidipsi"), "Dengeli Beslenme", "Yürüyüş"],
            (110, 180): [("Bulanık Görme", "Nöropati"), "Az Şekerli Diyet", "Klinik Egzersiz"],
            (110, 180): [("Poliüri", "Polidipsi"), "Şekersiz Diyet", "Klinik Egzersiz"],
            (110, 180): [("Yorgunluk", "Nöropati", "Bulanık Görme"), "Az Şekerli Diyet", "Yürüyüş"],
            (180, float('inf')): [("Yaraların Yavaş İyileşmesi", "Polifaji", "Polidipsi"), "Şekersiz Diyet", "Klinik Egzersiz"],
            (180, float('inf')): [("Yaraların Yavaş İyileşmesi", "Kilo Kaybı"), "Şekersiz Diyet", "Yürüyüş"]
        }

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

    def diyet_egzersiz_onerisi(self, kan_sekeri, belirtiler):
        for (min_seker, max_seker), (belirti_listesi, diyet, egzersiz) in self.diyet_egzersiz_kurallari.items():
            if min_seker <= kan_sekeri < max_seker:
                if any(belirti in belirtiler for belirti in belirti_listesi):
                    return diyet, egzersiz
        return "Dengeli Beslenme", "Yürüyüş"