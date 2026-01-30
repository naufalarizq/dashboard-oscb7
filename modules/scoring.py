import streamlit as st
import pandas as pd

def calculate_points(df):
    scoring_table = {
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "International"): 45,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "Regional"): 35,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "National"): 25,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "Province"): 20,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "Local/IPB"): 1,

        ("Competition (Kompetisi)", "Juara-2 Perorangan", "International"): 40,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "Regional"): 30,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "National"): 20,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "Province"): 15,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "Local/IPB"): 1,

        ("Competition (Kompetisi)", "Juara-3 Perorangan", "International"): 35,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "Regional"): 25,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "National"): 15,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "Province"): 10,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "Local/IPB"): 1,

        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "International"): 28,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "Regional"): 20,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "National"): 12,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "Province"): 8,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "Local/IPB"): 1,

        ("Competition (Kompetisi)", "Juara-1 Beregu", "International"): 35,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "Regional"): 25,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "National"): 15,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "Province"): 10,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "Local/IPB"): 1,

        ("Competition (Kompetisi)", "Juara-2 Beregu", "International"): 30,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "Regional"): 20,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "National"): 10,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "Province"): 7,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "Local/IPB"): 1,

        ("Competition (Kompetisi)", "Juara-3 Beregu", "International"): 25,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "Regional"): 15,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "National"): 8,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "Province"): 6,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "Local/IPB"): 1,

        ("Competition (Kompetisi)", "Juara Kategori Beregu", "International"): 20,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "Regional"): 13,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "National"): 7,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "Province"): 5,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "Local/IPB"): 1,

        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "International"): 50,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "Regional"): 40,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "National"): 30,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "Province"): 20,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "Local/IPB"): 1,

        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "International"): 25,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "Regional"): 20,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "National"): 15,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "Province"): 10,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "Local/IPB"): 1,

        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "International"): 25,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "Regional"): 20,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "National"): 15,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "Province"): 10,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "Local/IPB"): 1,

        ("Recognition (Pengakuan)", "Moderator", "International"): 20,
        ("Recognition (Pengakuan)", "Moderator", "Regional"): 15,
        ("Recognition (Pengakuan)", "Moderator", "National"): 10,
        ("Recognition (Pengakuan)", "Moderator", "Province"): 5,
        ("Recognition (Pengakuan)", "Moderator", "Local/IPB"): 1,

        ("Recognition (Pengakuan)", "Lainnya", "International"): 20,
        ("Recognition (Pengakuan)", "Lainnya", "Regional"): 15,
        ("Recognition (Pengakuan)", "Lainnya", "National"): 10,
        ("Recognition (Pengakuan)", "Lainnya", "Province"): 5,
        ("Recognition (Pengakuan)", "Lainnya", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Tanda Jasa", "International"): 50,
        ("Award (Penghargaan)", "Tanda Jasa", "Regional"): 40,
        ("Award (Penghargaan)", "Tanda Jasa", "National"): 30,
        ("Award (Penghargaan)", "Tanda Jasa", "Province"): 20,
        ("Award (Penghargaan)", "Tanda Jasa", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "International"): 36,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "Regional"): 30,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "National"): 20,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "Province"): 10,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Grand Final Emas", "International"): 25,
        ("Award (Penghargaan)", "Grand Final Emas", "Regional"): 20,
        ("Award (Penghargaan)", "Grand Final Emas", "National"): 10,
        ("Award (Penghargaan)", "Grand Final Emas", "Province"): 5,
        ("Award (Penghargaan)", "Grand Final Emas", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Grand Final Perak", "International"): 25,
        ("Award (Penghargaan)", "Grand Final Perak", "Regional"): 15,
        ("Award (Penghargaan)", "Grand Final Perak", "National"): 7,
        ("Award (Penghargaan)", "Grand Final Perak", "Province"): 3,
        ("Award (Penghargaan)", "Grand Final Perak", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Grand Final Perunggu", "International"): 20,
        ("Award (Penghargaan)", "Grand Final Perunggu", "Regional"): 10,
        ("Award (Penghargaan)", "Grand Final Perunggu", "National"): 5,
        ("Award (Penghargaan)", "Grand Final Perunggu", "Province"): 3,
        ("Award (Penghargaan)", "Grand Final Perunggu", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Piagam Partisipasi", "International"): 10,
        ("Award (Penghargaan)", "Piagam Partisipasi", "Regional"): 5,
        ("Award (Penghargaan)", "Piagam Partisipasi", "National"): 3,
        ("Award (Penghargaan)", "Piagam Partisipasi", "Province"): 2,
        ("Award (Penghargaan)", "Piagam Partisipasi", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Lainnya", "International"): 10,
        ("Award (Penghargaan)", "Lainnya", "Regional"): 5,
        ("Award (Penghargaan)", "Lainnya", "National"): 3,
        ("Award (Penghargaan)", "Lainnya", "Province"): 2,
        ("Award (Penghargaan)", "Lainnya", "Local/IPB"): 1,
        
        ("Creative Works (Hasil Karya)", "Patent", "International"): 50,
        ("Creative Works (Hasil Karya)", "Patent", "National"): 45,
        ("Creative Works (Hasil Karya)", "Patent Sederhana", "National"): 30,
        ("Creative Works (Hasil Karya)", "Hak Cipta", "National"): 30,
        ("Creative Works (Hasil Karya)", "Buku ber-ISBN penulis utama", "National"): 30,
        ("Creative Works (Hasil Karya)", "Buku ber-ISBN penulis kedua", "National"): 20,
        ("Creative Works (Hasil Karya)", "Penulis utama/korepondensi karya ilmiah bereputasi", "International"): 50,
        ("Creative Works (Hasil Karya)", "Penulis kedua karya ilmiah bereputasi", "International"): 30,
        ("Creative Works (Hasil Karya)", "Lainnya", "National"): 10,

        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "International"): 50,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "National"): 40,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "Province"): 30,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "Local/IPB"): 20,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "Institutional"): 10,

        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "International"): 35,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "National"): 25,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "Province"): 15,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "Local/IPB"): 10,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "Institutional"): 5,

        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "International"): 25,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "National"): 15,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "Province"): 10,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "Local/IPB"): 5,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "Institutional"): 3,


        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "International"): 50,
        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "National"): 40,
        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "Province"): 30,
        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "Local/IPB"): 10,
        
        # === ORGANIZATIONAL CAREER (KARIER ORGANISASI) ===
        ("Organizational Career (Karier Organisasi)", "Ketua", "International"): 50,
        ("Organizational Career (Karier Organisasi)", "Ketua", "Regional"): 40,
        ("Organizational Career (Karier Organisasi)", "Ketua", "National"): 30,
        ("Organizational Career (Karier Organisasi)", "Ketua", "Province"): 20,
        ("Organizational Career (Karier Organisasi)", "Ketua", "Local/IPB"): 10,

        ("Organizational Career (Karier Organisasi)", "Wakil Ketua", "International"): 45,
        ("Organizational Career (Karier Organisasi)", "Wakil Ketua", "Regional"): 35,
        ("Organizational Career (Karier Organisasi)", "Wakil Ketua", "National"): 25,
        ("Organizational Career (Karier Organisasi)", "Wakil Ketua", "Province"): 15,
        ("Organizational Career (Karier Organisasi)", "Wakil Ketua", "Local/IPB"): 8,

        ("Organizational Career (Karier Organisasi)", "Sekretaris", "International"): 40,
        ("Organizational Career (Karier Organisasi)", "Sekretaris", "Regional"): 30,
        ("Organizational Career (Karier Organisasi)", "Sekretaris", "National"): 20,
        ("Organizational Career (Karier Organisasi)", "Sekretaris", "Province"): 10,
        ("Organizational Career (Karier Organisasi)", "Sekretaris", "Local/IPB"): 6,

        ("Organizational Career (Karier Organisasi)", "Bendahara", "International"): 40,
        ("Organizational Career (Karier Organisasi)", "Bendahara", "Regional"): 30,
        ("Organizational Career (Karier Organisasi)", "Bendahara", "National"): 20,
        ("Organizational Career (Karier Organisasi)", "Bendahara", "Province"): 10,
        ("Organizational Career (Karier Organisasi)", "Bendahara", "Local/IPB"): 6,

        ("Organizational Career (Karier Organisasi)", "Di bawah pengurus harian", "International"): 30,
        ("Organizational Career (Karier Organisasi)", "Di bawah pengurus harian", "Regional"): 20,
        ("Organizational Career (Karier Organisasi)", "Di bawah pengurus harian", "National"): 10,
        ("Organizational Career (Karier Organisasi)", "Di bawah pengurus harian", "Province"): 5,
        ("Organizational Career (Karier Organisasi)", "Di bawah pengurus harian", "Local/IPB"): 2,
    }

    required_cols = {"Category", "Achievement", "Level"}
    if not required_cols.issubset(df.columns):
        st.warning("Missing required columns for scoring.")
        df["Points"] = 0
        return df

    def get_score(row):
        if pd.isna(row.get("Category")) or pd.isna(row.get("Achievement")) or pd.isna(row.get("Level")):
            return 0
        key = (row["Category"], row["Achievement"], row["Level"])
        if key in scoring_table:
            return scoring_table[key]
        if row["Category"] in ["Award (Penghargaan)", "Recognition (Pengakuan)"]:
            alt_key = (row["Category"], "Lainnya", row["Level"])
            return scoring_table.get(alt_key, 0)
        return 0

    df["Points"] = df.apply(get_score, axis=1)
    return df
