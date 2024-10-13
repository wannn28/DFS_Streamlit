import streamlit as st
import pandas as pd
from dfs import add_relation, get_ancestors, get_descendants
from config import driver
from neo4j_operations import add_person_to_neo4j, add_relation_to_neo4j

# Streamlit GUI
st.title("Sistem Silsilah Keluarga Interaktif")

# Input untuk memilih atau menambah individu baru
st.header("Input Individu")
new_person_name = st.text_input("Nama individu baru:", key="new_person")  # Input untuk memasukkan nama individu baru
new_person_gender = st.selectbox("Jenis kelamin individu baru:", ("male", "female"), key="new_gender")  # Pilihan jenis kelamin untuk individu baru

# Tombol untuk menambah individu baru ke dalam sistem
if st.button("Tambah Individu"):
    if new_person_name:
        add_person_to_neo4j(new_person_name, new_person_gender)  # Tambahkan individu ke Neo4j
        st.success(f"{new_person_name} ({new_person_gender}) telah ditambahkan ke dalam sistem.")
    else:
        st.error("Nama individu tidak boleh kosong.")

# Tampilkan struktur keluarga jika ada individu yang dipilih
family_tree = {}
with driver.session() as session:
    result = session.run(
        "MATCH (p:Person) "
        "OPTIONAL MATCH (p)-[r]->(related) "
        "RETURN p.name AS person_name, p.gender AS gender, type(r) AS relation, related.name AS related_name, related.gender AS related_gender"
    )
    for record in result:
        name = record["person_name"]
        gender = record["gender"]
        relation = record["relation"]
        related_name = record["related_name"]
        related_gender = record["related_gender"]

        if name not in family_tree:
            family_tree[name] = {
                "father": None, "mother": None, "children": [], "spouse": None, "gender": gender
            }

        if related_name:
            if relation == "HAS_FATHER":
                family_tree[name]["father"] = related_name
                if related_name not in family_tree:
                    family_tree[related_name] = {"father": None, "mother": None, "children": [name], "spouse": None, "gender": "male"}
                else:
                    if name not in family_tree[related_name]["children"]:
                        family_tree[related_name]["children"].append(name)
            elif relation == "HAS_MOTHER":
                family_tree[name]["mother"] = related_name
                if related_name not in family_tree:
                    family_tree[related_name] = {"father": None, "mother": None, "children": [name], "spouse": None, "gender": "female"}
                else:
                    if name not in family_tree[related_name]["children"]:
                        family_tree[related_name]["children"].append(name)
            elif relation == "HAS_CHILD":
                if related_name not in family_tree[name]["children"]:
                    family_tree[name]["children"].append(related_name)
                if related_name not in family_tree:
                    family_tree[related_name] = {"father": None, "mother": None, "children": [], "spouse": None, "gender": related_gender}
            elif relation == "HAS_SPOUSE":
                family_tree[name]["spouse"] = related_name
                if related_name not in family_tree:
                    family_tree[related_name] = {"father": None, "mother": None, "children": [], "spouse": name, "gender": related_gender}
                else:
                    family_tree[related_name]["spouse"] = name

# Menampilkan informasi individu yang dipilih
if new_person_name:
    if new_person_name in family_tree:
        current_person_data = family_tree[new_person_name]
        st.write(f"Individu saat ini: **{new_person_name}** ({current_person_data['gender']})")
        spouse = current_person_data.get("spouse")
        spouse_info = f"Pasangan: {spouse} ({family_tree[spouse]['gender']})" if spouse else "Tidak ada pasangan"
        st.write(spouse_info)
        st.json(current_person_data)
    else:
        st.error(f"{new_person_name} tidak ditemukan dalam sistem.")

# Opsi untuk menambah relasi
st.subheader("Tambahkan Relasi")
relation_type = st.selectbox("Pilih jenis relasi:", ("Ayah", "Ibu", "Anak", "Suami", "Istri"), key="relation_type")  # Pilihan jenis relasi yang ingin ditambahkan
relation_name = st.text_input(f"Nama {relation_type.lower()}:", key="relation_name")  # Input untuk nama relasi yang ditambahkan
relation_gender = st.selectbox(
    "Jenis kelamin:", ("male", "female"), key="relation_gender"
) if relation_type in ["Anak", "Suami", "Istri"] else None  # Pilihan jenis kelamin untuk relasi tertentu

# Tombol untuk menambahkan relasi
if st.button(f"Tambahkan {relation_type}"):
    if relation_name:
        add_relation_to_neo4j(new_person_name, relation_type, relation_name, relation_gender)  # Tambahkan relasi ke Neo4j
        st.success(
            f"{relation_type} {relation_name} telah ditambahkan untuk {new_person_name}."
        )
        st.experimental_rerun()  # Refresh aplikasi setelah menambahkan relasi
    else:
        st.error(f"Nama {relation_type.lower()} tidak boleh kosong.")

# Tampilkan struktur keluarga yang telah dimasukkan
st.header("Struktur Keluarga Saat Ini")  # Menampilkan header untuk struktur keluarga saat ini
st.json(family_tree)  # Menampilkan struktur keluarga dalam format JSON

# Menampilkan Daftar Semua Individu untuk Verifikasi
st.header("Daftar Semua Individu")  # Header untuk daftar semua individu
all_individuals = list(family_tree.keys())  # Mengambil semua individu yang ada dalam sistem
st.write("**Individu yang ada dalam sistem:**")
st.write(", ".join(all_individuals))  # Menampilkan semua individu dalam format teks

# Opsi untuk beralih ke mode pencarian
st.header("Cari dan Tampilkan Silsilah")  # Header untuk pencarian dan menampilkan silsilah
if all_individuals:
    # Membuat dropdown untuk memilih individu yang ada
    person_name = st.selectbox("Pilih nama individu yang ingin ditelusuri:", options=all_individuals, key="search_person_select")
    
    # Opsi untuk memilih apa yang ingin ditampilkan
    display_option = st.selectbox(
        "Pilih apa yang ingin ditampilkan:",
        ("Relasi Keluarga", "Langkah-langkah Proses DFS", "Keduanya"),
        key="display_option"
    )
    
    # Jika memilih "Relasi Keluarga" atau "Keduanya", tampilkan opsi relasi
    if display_option in ["Relasi Keluarga", "Keduanya"]:
        relation_options = st.multiselect(
            "Pilih relasi yang ingin ditampilkan:",
            ["Leluhur", "Keturunan", "Saudara", "Paman/Bibi", "Sepupu", "Keponakan", "Cucu"],
            default=["Leluhur", "Keturunan"]
        )  # Pilihan relasi yang ingin ditampilkan
        view_type = st.radio("Pilih tipe tampilan:", ("Teks", "Tabel"), key="view_type")  # Pilihan tampilan dalam format teks atau tabel
    else:
        relation_options = []
        view_type = "Teks"  # Default

    # Tombol untuk menampilkan hasil pencarian
    if st.button("Tampilkan Silsilah dan Proses DFS"):
        if person_name in all_individuals:
            results = {}
            dfs_steps = []

            # Menggunakan DFS untuk mencari leluhur
            if "Leluhur" in relation_options:
                ancestors = get_ancestors(family_tree, person_name, dfs_steps=dfs_steps if display_option in ["Langkah-langkah Proses DFS", "Keduanya"] else None)
                if ancestors:
                    results["Leluhur"] = ancestors
            
            # Menggunakan DFS untuk mencari keturunan
            if "Keturunan" in relation_options:
                descendants = get_descendants(family_tree, person_name, dfs_steps=dfs_steps if display_option in ["Langkah-langkah Proses DFS", "Keduanya"] else None)
                if descendants:
                    results["Keturunan"] = descendants
            
            # Tampilkan relasi yang dipilih
            if results:
                for relation, data in results.items():
                    st.write(f"**{relation} dari {person_name}:**")
                    if view_type == "Tabel":
                        df = pd.DataFrame(data)
                        st.table(df)
                    else:
                        for item in data:
                            st.write(f"{item['Relasi']}: {item['Nama']}")
            else:
                if display_option in ["Relasi Keluarga", "Keduanya"]:
                    st.write(f"Tidak ada data relasi yang dipilih untuk {person_name}.")

            # Menampilkan langkah-langkah DFS jika dipilih
            if display_option in ["Langkah-langkah Proses DFS", "Keduanya"]:
                if dfs_steps:
                    st.write("**Langkah-langkah Proses DFS:**")
                    dfs_steps_df = pd.DataFrame(dfs_steps)
                    st.table(dfs_steps_df)
                else:
                    st.write("Tidak ada langkah DFS yang dapat ditampilkan.")
