import json
import random
import sympy
from faker import Faker

fake = Faker()


def generate_broken_math_expression():
    """生成有问题的数学表达式"""
    errors = [
        lambda: f"x^{random.randint(1, 10)}",  # 未闭合括号
        lambda: f"sqrt({random.randint(1, 100)}",  # 未闭合根号
        lambda: f"\\frac{{1}}{{'hello'}}",  # 类型错误
        lambda: f"{random.choice(['α', 'β', 'γ'])} = {fake.random_number()}",  # 混入unicode
        lambda: "".join(random.choices("+-*/=()[]{}^_", k=10)),  # 随机符号堆砌
        lambda: f"{fake.word()} + {fake.word()}",  # 文本代替数字
    ]
    return random.choice(errors)()


def generate_broken_latex():
    """生成破损的LaTeX公式"""
    templates = [
        "\\[ " + generate_broken_math_expression() + " \\]",  # 未闭合环境
        "$" + fake.sentence() + "$",  # 文本伪装公式
        "\\begin{equation}" + str(fake.random_number()) + "\\end",  # 不完整环境
        "\\" + fake.word() + "{" + str(fake.random_number()) + "}",  # 无效命令
        "\\sqrt{" + fake.text(max_nb_chars=10).replace(" ", "") + "}"  # 根号内文本
    ]
    return random.choice(templates)


def generate_mixed_text(num_paragraphs=3):
    """生成混合低质量文本和数学公式的内容"""
    output = []
    for _ in range(num_paragraphs):
        # 随机选择插入内容类型
        choice = random.random()
        if choice < 0.3:  # 30%概率插入破损公式
            output.append(generate_broken_latex())
        elif choice < 0.6:  # 30%概率插入正常文本+破损内联公式
            output.append(fake.sentence() + f" ${generate_broken_math_expression()}$ " + fake.sentence())
        else:  # 40%概率纯文本但含数学符号
            output.append(fake.text().replace(".", f" {random.choice(['±', '×', '÷'])} ") + str(fake.random_number()))

    # 故意添加典型错误
    if random.random() > 0.5:
        output.insert(random.randint(0, len(output)),
                      "\\begin{document}" + fake.sentence() + "\\end{document}")

    return "\n\n".join(output)


if __name__ == '__main__':
    # # 生成5个测试样例
    # for i in range(100):
    #     print(f"=== 测试样例 {i + 1} ===")
    #     print(generate_mixed_text(5))
    #     print("\n" + "=" * 40 + "\n")

    for i in range(100):
        with open('badcase_formula.jsonl', 'a', encoding='utf-8') as f:
            data = {
                'id': i+1,
                'content': generate_mixed_text(5)
            }
            str_data = json.dumps(data, ensure_ascii=False)
            f.write(str_data + '\n')