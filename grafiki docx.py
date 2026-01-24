import matplotlib.pyplot as plt
import numpy as np

# --- Данные по документам ---
documents = [
    {"name": "Руководство системного программиста", "pages": 50, "docx_hours": 40, "asciidoc_hours": 26, "savings": 35},
    {"name": "Руководство администратора", "pages": 130, "docx_hours": 104, "asciidoc_hours": 60, "savings": 42},
    {"name": "Руководство пользователя", "pages": 50, "docx_hours": 40, "asciidoc_hours": 22, "savings": 45}
]

# Подготовка данных для графика
labels = [d["name"] for d in documents]
docx_values = [d["docx_hours"] for d in documents]
asciidoc_values = [d["asciidoc_hours"] for d in documents]
x_pos = np.arange(len(labels))

# Создание графика
fig, ax = plt.subplots(figsize=(12, 7))

# Столбцы: DOCX и AsciiDoc
bar_width = 0.35
bars1 = ax.bar(x_pos - bar_width/2, docx_values, bar_width, label='DOCX (традиционно)', color='#e74c3c', edgecolor='black', linewidth=0.8)
bars2 = ax.bar(x_pos + bar_width/2, asciidoc_values, bar_width, label='AsciiDoc (Docs-as-Code)', color='#2ecc71', edgecolor='black', linewidth=0.8)

# Добавление текста с процентами экономии над столбцами AsciiDoc
for i, (docx, asc, saving) in enumerate(zip(docx_values, asciidoc_values, [d["savings"] for d in documents])):
    ax.text(x_pos[i] + bar_width/2, asc + 1, f'−{saving}%', ha='center', va='bottom', fontweight='bold', fontsize=11, color='#27ae60')

# Настройки графика
ax.set_xlabel('Тип документа', fontsize=14, fontweight='bold')
ax.set_ylabel('Время подготовки (часы)', fontsize=14, fontweight='bold')
ax.set_title('Сравнение эффективности Docs-as-Code для документов разного типа\n(Экономия времени за счёт автоматизации)', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=12)
ax.legend(fontsize=12, loc='upper right')
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Улучшение внешнего вида
plt.tight_layout()

# Отображение графика
plt.show()

# --- Дополнительно: сохранить график как PNG ---
# plt.savefig('docs_as_code_comparison.png', dpi=300, bbox_inches='tight')