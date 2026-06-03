from pathlib import Path

from jianying_subtitle_proofread.cli import run


CHUNK_SEPARATOR = "\n===CHUNK===\n"


FAKE_OUTPUT_A = """[1] Hello大家好
[2] 今天我们来聊聊Claude Code
[3] 还有Gemini和ChatGPT
[4] 以及DeepSeek这些模型
[5] 我觉得最近变化特别快
[6] 这个产品其实很强
[7] 然后我们可以看一下
[8] 它会不会替代一部分工作
[9] 比如说你在用Cursor的时候
[10] 是不是会顺手打开Claude
[11] 或者Gemini再对比一下
[12] 那这里其实有个很大的误区
[13] 就是很多人把Agent
[14] 和 workflow混在一起
[15] 我经常会说一句话叫
[16] 不要拿传统自动化去理解Agent
[17] 因为他们根本不是
[18] 一回事
[19] 你如果真的做过RAG
[20] Agent或者multi-Agent
[21] 你就知道这里面的坑很多
[22] 最常见的一个坑就是提示词太虚
[23] 第二个坑是评测标准没有
[24] 第三个坑是上下文窗口根本不够
[25] 所以你最后会发现
[26] Demo很好看
[27] 上线全完蛋
[28] 我不是说不能做
[29] 我是说你要先把问题拆清楚
[30] 比如你的目标到底是省时间
[31] 还是提高质量
[32] 还是让新人更快上手
[33] 这三件事情其实完全不一样
[34] 然后还有一种情况是
[35] 老板只会跟你说一句
[36] 你给我上AI
[37] 这句话听起来很简单
[38] 但其实信息量几乎为零
[39] 你总得知道他要的是Copilot
[40] 还是Chatbot
[41] 还是一个能串工具的Agent
[42] 再比如很多人会把MCP
[43] 说成什么模型控制协议
[44] 其实它是Model Context Protocol
[45] 如果你连名字都讲不清楚
[46] 后面沟通一定会出问题
[47] 还有OpenAI和Anthropic
[48] 这两个公司的风格就很不一样
[49] OpenAI更像产品驱动
[50] Anthropic更强调安全
[51] 但你在做选型的时候
[52] 不能只看谁发布会更热闹
[53] 你要看延迟价格稳定性
[54] 以及工具调用支不支持
[55] 那如果回到个人使用场景
[56] 我会建议大家先练一个能力
[57] 就是把模糊问题问清楚
[58] 比如不要上来就问
[59] 哪个模型最好
[60] 你至少要先说清楚
[61] 你是写代码
[62] 写论文
[63] 做表格
[64] 还是做视频脚本
[65] 需求不同答案就不同
[66] 最后再补一句
[67] 别把提示词神化
[68] 真正拉开差距的往往是
[69] 数据
[70] 流程
[71] 评测
[72] 还有你的产品判断
[73] 如果这些东西没有
[74] 你prompt写得再花
[75] 也很难稳定
[76] 所以我最后的建议是
[77] 先做小闭环
[78] 再慢慢扩大
[79] 不要一上来就想做平台
[80] 这样成功率会高很多"""

FAKE_OUTPUT_B = """[81] 比如你在用Kimi K2的时候
[82] 也可能顺手拿Qwen试一下
[83] 或者拿GLM做个对照
[84] 再把Tongyi Qianwen写成通义千问
[85] 有人还会把Perplexity听成Public City
[86] 把Midjourney写成Midjourney
[87] 甚至把Runway写成Runway
[88] 还有人把ComfyUI拆开写
[89] 把LangChain也拆开写
[90] 或者把Llama说成Lama
[91] 把Mistral写成Mistal
[92] 这些都很常见"""

def test_end_to_end_single_chunk_generates_expected_fixed_srt(tmp_path: Path):
    input_path = tmp_path / "single_chunk_input.srt"
    input_path.write_text(
        """1
00:00:00,000 --> 00:00:02,000
hello大家好

2
00:00:02,000 --> 00:00:04,000
今天我们来聊聊cloud code

3
00:00:04,000 --> 00:00:06,000
还有gimini和chat gpt

4
00:00:06,000 --> 00:00:08,000
以及deep seek这些模型

5
00:00:08,000 --> 00:00:10,000
我我我觉得最近变化特别快

6
00:00:10,000 --> 00:00:12,000
就是很多人把agent

7
00:00:12,000 --> 00:00:14,000
和 work flow 混在一起

8
00:00:14,000 --> 00:00:16,000
a gent或者multi agent

9
00:00:16,000 --> 00:00:18,000
再比如很多人会把mcp

10
00:00:18,000 --> 00:00:20,000
其实它是model context protocol

11
00:00:20,000 --> 00:00:22,000
还有open ai和anthorpic
""",
        encoding="utf-8",
    )

    fake_output = """[1] Hello大家好
[2] 今天我们来聊聊Claude Code
[3] 还有Gemini和ChatGPT
[4] 以及DeepSeek这些模型
[5] 我觉得最近变化特别快
[6] 就是很多人把Agent
[7] 和 workflow混在一起
[8] Agent或者multi-Agent
[9] 再比如很多人会把MCP
[10] 其实它是Model Context Protocol
[11] 还有OpenAI和Anthropic"""

    result = run([
        str(input_path),
        "--fake-output-a",
        fake_output,
        "--fake-output-b",
        fake_output,
    ])

    assert result == 0

    fixed_text = (tmp_path / "single_chunk_input.fixed.srt").read_text(encoding="utf-8")
    report_text = (tmp_path / "single_chunk_input.merge-report.md").read_text(encoding="utf-8")

    expected_snippets = [
        "Hello大家好",
        "今天我们来聊聊Claude Code",
        "还有Gemini和ChatGPT",
        "以及DeepSeek这些模型",
        "我觉得最近变化特别快",
        "就是很多人把Agent",
        "和 workflow混在一起",
        "Agent或者multi-Agent",
        "再比如很多人会把MCP",
        "其实它是Model Context Protocol",
        "还有OpenAI和Anthropic",
    ]

    for snippet in expected_snippets:
        assert snippet in fixed_text

    assert "A/B 一致" in report_text


def test_end_to_end_full_coverage_dataset_supports_chunked_fake_outputs(tmp_path: Path):
    source = Path(__file__).parent / "fixtures" / "coverage_full_input.srt"
    input_path = tmp_path / "coverage_full_input.srt"
    input_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    fake_output_file = tmp_path / "chunked_fake_outputs.txt"
    fake_output_file.write_text(
        CHUNK_SEPARATOR.join([
            FAKE_OUTPUT_A,
            FAKE_OUTPUT_A,
            FAKE_OUTPUT_B,
            FAKE_OUTPUT_B,
            FAKE_OUTPUT_A,
            FAKE_OUTPUT_A,
            FAKE_OUTPUT_B,
            FAKE_OUTPUT_B,
        ]),
        encoding="utf-8",
    )

    result = run([
        str(input_path),
        "--fake-output-file",
        str(fake_output_file),
    ])

    assert result == 0

    fixed_text = (tmp_path / "coverage_full_input.fixed.srt").read_text(encoding="utf-8")

    expected_snippets = [
        "今天我们来聊聊Claude Code",
        "还有Gemini和ChatGPT",
        "以及DeepSeek这些模型",
        "我觉得最近变化特别快",
        "这个产品其实很强",
        "然后我们可以看一下",
        "它会不会替代一部分工作",
        "比如说你在用Cursor的时候",
        "是不是会顺手打开Claude",
        "或者Gemini再对比一下",
        "就是很多人把Agent",
        "和 workflow混在一起",
        "不要拿传统自动化去理解Agent",
        "你如果真的做过RAG",
        "Agent或者multi-Agent",
        "Demo很好看",
        "你总得知道他要的是Copilot",
        "还是Chatbot",
        "还是一个能串工具的Agent",
        "再比如很多人会把MCP",
        "其实它是Model Context Protocol",
        "还有OpenAI和Anthropic",
        "OpenAI更像产品驱动",
        "Anthropic更强调安全",
        "比如你在用Kimi K2的时候",
        "也可能顺手拿Qwen试一下",
        "或者拿GLM做个对照",
        "再把Tongyi Qianwen写成通义千问",
        "有人还会把Perplexity听成Public City",
        "把Midjourney写成Midjourney",
        "甚至把Runway写成Runway",
        "还有人把ComfyUI拆开写",
        "把LangChain也拆开写",
        "或者把Llama说成Lama",
        "把Mistral写成Mistal",
    ]

    for snippet in expected_snippets:
        assert snippet in fixed_text
