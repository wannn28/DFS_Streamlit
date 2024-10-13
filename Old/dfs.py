def add_relation(family_tree, person, relation, name, gender):
    if person not in family_tree:
        family_tree[person] = {
            "father": None, "mother": None, "children": [], "spouse": None, "gender": "unknown"
        }
    
    if relation == "Ayah":
        # Tambahkan ayah ke individu dan tambahkan anak ke ayah
        family_tree[person]["father"] = name
        if name not in family_tree:
            family_tree[name] = {
                "father": None, "mother": None, "children": [person], "spouse": None, "gender": "male"
            }
        else:
            family_tree[name]["children"].append(person)
        
        # Cek apakah ibu sudah ada, jika iya, maka jadikan pasangan suami-istri
        mother = family_tree[person].get("mother")
        if mother:
            family_tree[name]["spouse"] = mother
            family_tree[mother]["spouse"] = name
    
    elif relation == "Ibu":
        # Tambahkan ibu ke individu dan tambahkan anak ke ibu
        family_tree[person]["mother"] = name
        if name not in family_tree:
            family_tree[name] = {
                "father": None, "mother": None, "children": [person], "spouse": None, "gender": "female"
            }
        else:
            family_tree[name]["children"].append(person)
        
        # Cek apakah ayah sudah ada, jika iya, maka jadikan pasangan suami-istri
        father = family_tree[person].get("father")
        if father:
            family_tree[name]["spouse"] = father
            family_tree[father]["spouse"] = name

# Fungsi untuk mendapatkan leluhur dari individu menggunakan DFS
def get_ancestors(family_tree, person, dfs_steps=None):
    ancestors = []
    visited = set()
    stack = [person]

    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            father = family_tree[current].get("father")
            mother = family_tree[current].get("mother")
            if father:
                ancestors.append({"Relasi": "Ayah", "Nama": father})
                stack.append(father)
                if dfs_steps is not None:
                    dfs_steps.append({"Action": "Visit", "Person": father})
            if mother:
                ancestors.append({"Relasi": "Ibu", "Nama": mother})
                stack.append(mother)
                if dfs_steps is not None:
                    dfs_steps.append({"Action": "Visit", "Person": mother})

    return ancestors

# Fungsi untuk mendapatkan keturunan dari individu menggunakan DFS
def get_descendants(family_tree, person, dfs_steps=None):
    descendants = []
    visited = set()
    stack = [person]

    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            children = family_tree[current].get("children", [])
            for child in children:
                descendants.append({"Relasi": "Anak", "Nama": child})
                stack.append(child)
                if dfs_steps is not None:
                    dfs_steps.append({"Action": "Visit", "Person": child})

    return descendants