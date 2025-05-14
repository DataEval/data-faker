import json
import random
from faker import Faker
import itertools

fake = Faker()


def generate_broken_table():
    """生成破损的表格结构"""
    # 表格格式选项（含错误）
    formats = [
        "markdown",  # Markdown表格
        "csv",  # CSV格式
        "html",  # HTML表格
        "unicode",  # 伪表格（用符号拼凑）
        "no_border"  # 无边界表格
    ]
    format_choice = random.choice(formats)

    # 生成随机表格数据（2-4列，3-6行）
    num_cols = random.randint(2, 4)
    num_rows = random.randint(3, 6)
    headers = [fake.word().upper() for _ in range(num_cols)]
    data = [
        [fake.word() if random.random() > 0.3 else str(fake.random_number())
         for _ in range(num_cols)]
        for _ in range(num_rows)
    ]

    # 按选定格式生成表格（故意引入错误）
    if format_choice == "markdown":
        # Markdown表格（可能缺失对齐行或边界）
        table = []
        if random.random() > 0.2:  # 80%概率有表头
            table.append("| " + " | ".join(headers) + " |")
            if random.random() > 0.3:  # 70%概率有对齐行
                table.append("|" + "|".join(["---"] * num_cols) + "|")
        for row in data:
            if random.random() > 0.1:  # 90%概率正常行
                table.append("| " + " | ".join(row) + " |")
            else:  # 10%概率插入破损行
                table.append(" ".join(row))  # 无边界符
        return "\n".join(table)

    elif format_choice == "csv":
        # CSV格式（可能缺失引号或混用分隔符）
        sep = random.choice([",", ";", "\t", "|"])
        quote = random.choice(['"', "'", ""])
        rows = []
        if random.random() > 0.2:
            rows.append(sep.join(headers))
        for row in data:
            if random.random() > 0.7:  # 30%概率混用分隔符
                row[-1] = row[-1].replace(sep, random.choice([",", "|"]))
            rows.append(sep.join([f"{quote}{cell}{quote}" if random.random() > 0.6 else cell
                                  for cell in row]))
        return "\n".join(rows)

    elif format_choice == "html":
        # HTML表格（可能缺失闭合标签）
        html = []
        if random.random() > 0.3:
            html.append("<table>")
            if random.random() > 0.5:
                html.append("  <thead><tr>")
                html.append("    " + "".join(f"<th>{h}</th>" for h in headers))
                html.append("  </tr></thead>")
        html.append("  <tbody>")
        for row in data:
            html.append("    <tr>")
            for cell in row:
                if random.random() > 0.8:  # 20%概率缺失闭合标签
                    html.append(f"      <td>{cell}")
                else:
                    html.append(f"      <td>{cell}</td>")
            if random.random() > 0.9:  # 10%概率缺失</tr>
                html.append("    <tr>")
            else:
                html.append("    </tr>")
        if random.random() > 0.7:  # 30%概率缺失</tbody>或</table>
            html.append("  <tbody>")
        else:
            html.append("  </tbody>")
            html.append("</table>")
        return "\n".join(html)

    elif format_choice == "unicode":
        # 用Unicode符号拼凑的伪表格
        borders = random.choice(["┃", "│", "║", "|"])
        sep = random.choice(["━", "─", "=", ":"])
        header_sep = random.choice(["┳", "╋", "┼", "+"])
        parts = []
        if random.random() > 0.4:
            parts.append(borders + borders.join(headers) + borders)
            parts.append(borders + header_sep.join([sep * len(h) for h in headers]) + borders)
        for row in data:
            parts.append(borders + borders.join(row) + borders)
        return "\n".join(parts)

    else:  # no_border
        # 无边界表格（仅用空格对齐）
        col_widths = [max(len(h), *[len(row[i]) for row in data])
                      for i, h in enumerate(headers)]
        lines = []
        if random.random() > 0.3:
            lines.append("  ".join(h.ljust(w) for h, w in zip(headers, col_widths)))
        for row in data:
            lines.append("  ".join(cell.ljust(w) for cell, w in zip(row, col_widths)))
        return "\n".join(lines)


def inject_table_errors(table_text):
    """在已生成的表格中注入额外错误"""
    errors = [
        lambda x: x.replace("\n", " "),  # 移除换行符
        lambda x: x + fake.sentence(),  # 追加无关文本
        lambda x: x[:len(x) // 2] + "..." + x[len(x) // 2:],  # 截断内容
        lambda x: x.replace(random.choice(x.split()), str(fake.random_number())),  # 替换随机单元格
        lambda x: x + "\n" + "|".join([fake.word() for _ in range(random.randint(2, 5))])  # 追加破损行
    ]
    return random.choice(errors)(table_text)


def generate_mixed_text(num_paragraphs=3):
    """生成混合低质量文本和表格的内容"""
    output = []
    for _ in range(num_paragraphs):
        choice = random.random()
        if choice < 0.4:  # 40%概率插入破损表格
            table = generate_broken_table()
            if random.random() > 0.3:
                table = inject_table_errors(table)
            output.append(table)
        elif choice < 0.7:  # 30%概率文本中混入表格片段
            output.append(fake.sentence() + ":\n" + "\n".join(generate_broken_table().split("\n")[:2]))  # 只取表格前两行
        else:  # 30%概率纯文本但含表格关键词
            table_words = ["COLUMN", "ROW", "MERGE", "PIVOT", "||"]
            output.append(fake.text().replace(".", f" {random.choice(table_words)} "))

            # 故意添加文档结构错误
            if random.random() > 0.5:
                output.insert(random.randint(0, len(output)),
                              f"## {fake.word().upper()} TABLE\n" +
                              "|".join(["---"] * random.randint(3, 6)) + "\n" +
                              fake.sentence())

    return "\n\n".join(output)


if __name__ == '__main__':
    # # 生成5个测试样例
    # for i in range(5):
    #     print(f"=== 测试样例 {i + 1} ===")
    #     print(generate_mixed_text())
    #     print("\n" + "=" * 40 + "\n")

    for i in range(100):
        with open('badcase_table.jsonl', 'a', encoding='utf-8') as f:
            data = {
                'id': i+1,
                'content': generate_mixed_text(5)
            }
            str_data = json.dumps(data, ensure_ascii=False)
            f.write(str_data + '\n')