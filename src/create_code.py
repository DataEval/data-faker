import json
import random
from faker import Faker
import itertools

fake = Faker()


def generate_broken_code(lang="python"):
    """生成包含错误的代码片段"""
    errors = {
        "python": [
            lambda: f"print('{fake.word()}'",  # 未闭合括号
            lambda: f"{fake.word()} = {random.randint(1, 100)}",  # 无效变量名
            lambda: "\n".join([f"if {random.choice([True, False])}:", "  " + fake.sentence()]),  # 非法缩进
            lambda: f"import {fake.word()}; {fake.word()}.{fake.word()}()",  # 假模块调用
            lambda: f"0x{fake.hexify()}",  # 非法十六进制
            lambda: f"{fake.word()}({fake.word()}={fake.word()}"  # 缺失括号和参数
        ],
        "javascript": [
            lambda: f"console.log('{fake.sentence()}')",  # 中文引号
            lambda: f"function {fake.word()}({fake.word()}) {{ {fake.sentence()} ",  # 未闭合函数
            lambda: f"let {fake.word()} = `${{{fake.word()}}}`"  # 嵌套模板字符串
        ],
        "html": [
            lambda: f"<{fake.word()} {fake.word()}='{fake.word()}'>",  # 无效标签
            lambda: "<!DOCTYPE " + fake.word().upper(),  # 错误的DOCTYPE
            lambda: f"<div>{fake.sentence()}</{fake.word()}>"  # 不匹配的闭合标签
        ]
    }
    return random.choice(errors.get(lang, errors["python"]))()


def generate_code_with_noise():
    """生成带噪音的代码（如混入文本、特殊字符）"""
    code = generate_broken_code(random.choice(["python", "javascript", "html"]))
    noise_ops = [
        lambda x: x[:len(x) // 2] + fake.sentence() + x[len(x) // 2:],  # 中间插入文本
        lambda x: x.replace(random.choice(x), random.choice(['\x00', '\ufffd', '�'])),  # 插入非法字符
        lambda x: x + " " + "/".join(fake.words(3))  # 追加无关文本
    ]
    return random.choice(noise_ops)(code)


def generate_mixed_text(num_paragraphs=3):
    """生成混合低质量文本和代码的内容"""
    output = []
    for _ in range(num_paragraphs):
        choice = random.random()
        if choice < 0.4:  # 40%概率插入破损代码块
            output.append(f"```\n{generate_broken_code()}\n```")  # Markdown代码块
        elif choice < 0.7:  # 30%概率插入行内代码
            output.append(fake.sentence() + f" `{generate_code_with_noise()}` " + fake.sentence())
        else:  # 30%概率纯文本但含代码关键词
            tech_words = ["NULL", "NaN", "<script>", "++i", "0xDEADBEEF"]
            output.append(fake.text().replace(".", f" {random.choice(tech_words)} "))

    # 故意添加文档结构错误
    if random.random() > 0.5:
        output.insert(random.randint(0, len(output)),
                      f"/* {fake.sentence()} */\n#{fake.word()} {fake.sentence()}\n```\n{fake.sentence()}\n```")

    return "\n\n".join(output)


if __name__ == '__main__':
    # # 生成5个测试样例
    # for i in range(5):
    #     print(f"=== 测试样例 {i + 1} ===")
    #     print(generate_mixed_text())
    #     print("\n" + "=" * 40 + "\n")

    for i in range(100):
        with open('badcase_code.jsonl', 'a', encoding='utf-8') as f:
            data = {
                'id': i+1,
                'content': generate_mixed_text(5)
            }
            str_data = json.dumps(data, ensure_ascii=False)
            f.write(str_data + '\n')