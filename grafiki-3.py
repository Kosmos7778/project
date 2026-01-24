import matplotlib.pyplot as plt
import numpy as np

# --- Данные по документам ---
documents = [
    {"name": "Руководство системного программиста", "pages": 50, "docx_hours": 40, "asciidoc_hours": 26, "savings": 35},
    {"name": "Руководство администратора", "pages": 130, "docx_hours": 104, "asciidoc_hours": 60, "savings": 42},
    {"name": "Руководство пользователя", "pages": 50, "docx_hours": 40, "asciidoc_hours": 22, "savings": 45}
]

labels = [d["name"] for d in documents]
docx_values = [d["docx_hours"] for d in documents]
asciidoc_values = [d["asciidoc_hours"] for d in documents]
x_pos = np.arange(len(labels))

fig, ax = plt.subplots(figsize=(14, 8))
bar_width = 0.35

bars1 = ax.bar(x_pos - bar_width/2, docx_values, bar_width, label='DOCX (традиционно)', color='#e74c3c', edgecolor='black', linewidth=0.1)
bars2 = ax.bar(x_pos + bar_width/2, asciidoc_values, bar_width, label='AsciiDoc (Docs-as-Code)', color='#2ecc71', edgecolor='black', linewidth=0.1)

def format_value(val):
    if val >= 1000:
        return f"{val/1000:.1f} тыс."
    else:
        return str(int(val))

for i, (docx, asc) in enumerate(zip(docx_values, asciidoc_values)):
    ax.text(x_pos[i] - bar_width/2, docx + 1, format_value(docx),
            ha='center', va='bottom', fontsize=12, fontweight='bold', color='white',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#e74c3c', edgecolor='none', alpha=0.8))
    ax.text(x_pos[i] + bar_width/2, asc + 1, format_value(asc),
            ha='center', va='bottom', fontsize=12, fontweight='bold', color='white',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#2ecc71', edgecolor='none', alpha=0.8))

for i, saving in enumerate([d["savings"] for d in documents]):
    ax.text(x_pos[i] + bar_width/2, asciidoc_values[i] + 6, f'−{saving}%',
            ha='center', va='bottom', fontweight='bold', fontsize=12, color='#27ae60')

ax.set_title('Сравнение эффективности Docs-as-Code для документов разного типа',
             fontsize=18, fontweight='bold', pad=40)

# Легенда справа
ax.legend(title='', fontsize=12, loc='center left', bbox_to_anchor=(1, 0.5))

max_val = max(max(docx_values), max(asciidoc_values))
y_step = 20
y_ticks = np.arange(0, max_val + y_step, y_step)
ax.set_ylabel('Время подготовки, ч', fontsize=10, fontweight='bold', color="#0C0000", labelpad=15, rotation=90)
ax.set_xlabel('Тип документа', fontsize=14, fontweight='bold', labelpad=15)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, ha='center', fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.6, color='#cccccc')

plt.tight_layout(rect=[0,0,0.85,1])  # Оставляем место справа для легенды (0.85 - сжимаем основную область)
plt.show()

# --- Для сохранения графика ---
# plt.savefig('docs_as_code_comparison.png', dpi=300, bbox_inches='tight')
