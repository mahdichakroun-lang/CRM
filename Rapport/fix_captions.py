"""
Deplace \\caption et \\label depuis apres \\end{tabular*}
vers avant \\begin{tabular*} dans les environnements table.
Approche ligne par ligne.
"""
import os, glob

CHAPTER_DIR = r"c:\Users\Lenovo\Desktop\crm\Rapport\chapter"

TABULAR_ENVS = ("tabular", "tabularx", "tabular*", "longtable")

def fix_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    changed = False

    while i < len(lines):
        line = lines[i]

        # Detect start of a table environment
        if "\\begin{table" in line:
            # Collect lines until \end{table}
            table_block = []
            while i < len(lines):
                table_block.append(lines[i])
                if "\\end{table}" in lines[i]:
                    i += 1
                    break
                i += 1

            # Now process table_block: find \caption and \label AFTER \end{tabular*}
            # Strategy: scan for lines with \caption or \label that come AFTER
            # any \end{tabular...} line, and move them right before the
            # corresponding \begin{tabular...} line.

            # Find all \end{tabular...} positions
            end_tabular_indices = []
            for j, tl in enumerate(table_block):
                for env in TABULAR_ENVS:
                    if ("\\end{" + env + "}") in tl:
                        end_tabular_indices.append(j)

            # Find \begin{tabular...} positions
            begin_tabular_indices = []
            for j, tl in enumerate(table_block):
                for env in TABULAR_ENVS:
                    if ("\\begin{" + env) in tl:
                        begin_tabular_indices.append(j)

            if end_tabular_indices and begin_tabular_indices:
                last_end = end_tabular_indices[-1]
                first_begin = begin_tabular_indices[0]

                # Collect \caption and \label lines after last \end{tabular}
                # but before \end{table}
                cap_label_lines = []
                other_after = []
                end_table_line = ""

                j = last_end + 1
                while j < len(table_block):
                    tl = table_block[j].strip()
                    if tl.startswith("\\caption") or tl.startswith("\\label"):
                        cap_label_lines.append(table_block[j])
                    elif "\\end{table}" in table_block[j]:
                        end_table_line = table_block[j]
                    elif tl == "":
                        pass  # skip blank lines between caption/label
                    else:
                        other_after.append(table_block[j])
                    j += 1

                if cap_label_lines:
                    # Rebuild block: everything before \begin{tabular}, then
                    # caption+label, then the tabular block, then \end{table}
                    before_tabular = table_block[:first_begin]
                    tabular_section = table_block[first_begin:last_end + 1]

                    new_block = (
                        before_tabular
                        + cap_label_lines
                        + tabular_section
                        + other_after
                        + ([end_table_line] if end_table_line else [])
                    )
                    new_lines.extend(new_block)
                    changed = True
                    continue

            new_lines.extend(table_block)
            continue

        new_lines.append(line)
        i += 1

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("  OK Modifie : " + os.path.basename(filepath))
    else:
        print("  -- Inchange : " + os.path.basename(filepath))

files = glob.glob(os.path.join(CHAPTER_DIR, "*.tex"))
print("Traitement de " + str(len(files)) + " fichiers...\n")
for fp in sorted(files):
    fix_file(fp)
print("\nTermine.")
