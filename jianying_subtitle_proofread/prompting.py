from __future__ import annotations

from typing import Iterable, Optional

from .models import FlattenedLine


def render_numbered_lines(lines: Iterable[FlattenedLine]) -> str:
    return "\n".join(f"[{line.line_id}] {line.text}" for line in lines)


def build_proofread_prompt(lines: Iterable[FlattenedLine], reference_text: Optional[str] = None, pass_name: str = "A") -> str:
    reference_section = ""
    if reference_text:
        reference_section = (
            "[参考文稿]（本视频专属，用于识别视频中出现的品牌名、产品名、专有名词）:\n"
            "文稿中出现的词就是本视频的正确写法。字幕中出现与这些词发音相近或拼写相似的表达时，"
            "应主动按文稿纠正——即便那个近音词本身是合法词汇，也不能放过。"
            "不可直接按文稿措辞改写字幕内容。\n"
            f"{reference_text.strip()}\n\n"
        )
    return (
        f"你正在执行第 {pass_name} 轮字幕校对。\n"
        "你会收到按编号排列的字幕文本，请在不改编号、不增删编号的前提下，逐行返回校对结果。\n"
        "严格只输出编号行，不要输出说明、总结、前后缀。\n"
        "不要合并或拆分编号。第二轮也必须基于原始输入独立判断。\n\n"
        "[纠错目标] 错别字、英文大小写、专有名词、口语重复清理、相邻行断句优化。请积极修复明显可修问题，但不要改变原意。\n\n"
        "[标点规则]\n"
        "不要随意新增标点。原字幕没有句号、逗号、问号、感叹号时，默认保持不新增；但遇到明显需要的语气停顿，可以谨慎补一个逗号。\n"
        "字幕行末尾如有句号（。）、逗号（，）、顿号（、）、问号（？）、感叹号（！）等标点，应主动删除，保持行末无标点。\n\n"
        "[重复清理]\n"
        "如果出现口吃式重复、ASR 重复、口语卡顿重复，如'我我我觉得'、'这个这个产品'、'然后然后'、'它它它'，应去掉冗余重复，只保留自然表达。\n\n"
        "[AI 专有名词规范]\n"
        "字幕处于 AI 工具、模型、公司、产品语境时，主动修正专有名词的误识别与大小写错误。\n"
        "如果在 AI 助手、任务执行、工具调用、多智能体协作语境里出现 agent，一般规范为 Agent；multi agent 一般规范为 multi-Agent。\n"
        "常见正确写法（结合上下文判断，不是硬映射）：\n"
        "  模型/产品：Claude、Claude Code、Gemini、ChatGPT、DeepSeek、Grok、Kimi、Qwen、GLM、Llama、Mistral\n"
        "  公司/平台：OpenAI、Anthropic、Cursor、Copilot、Midjourney、Runway、Perplexity、ComfyUI、LangChain\n"
        "  概念/技术：MCP、Model Context Protocol、RAG、workflow、Agent、multi-Agent、Skill、Chatbot\n"
        "大小写与拆写纠错——遇到以下写法，上下文明确时主动改正：\n"
        "  cloud code -> Claude Code、chat gpt -> ChatGPT、deep seek -> DeepSeek\n"
        "  gimini / gemni -> Gemini、claud -> Claude、work flow -> workflow\n"
        "  agent -> Agent（AI 协作/任务执行语境）、a gent -> Agent、multi agent -> multi-Agent\n"
        "  skill -> Skill（AI 助手插件/技能包语境）、scale -> Skill（当上下文是 AI 技能/插件产品，而非'规模'含义时）\n"
        "重点复查这些 Agent 相关近音和拆写：agent、a gent、multi agent。\n"
        "英文单词（包括专有名词）与紧邻的中文之间保留一个空格是正常排版，不要删去；"
        "但不要在纯中文词语之间、或中文句子中间插入多余空格；不要为了规范专有名词而过度给整句中文新增空格。\n\n"
        "[断句优化]\n"
        "如果某两行明显是被错误断开的短语，可以在保持编号不变的前提下，主动在相邻编号间移动字词，使断句更自然。\n"
        "例如：[1] 他觉得这不是一 / [2] 个好的事情，可以改成 [1] 他觉得这不是 / [2] 一个好的事情。\n"
        "如果术语被错误拆开（如 work flow、a gent、multi agent），也应按常见写法修正。\n"
        "判断原则是：宁可保留原意，也不要保留明显错误。\n\n"
        f"{reference_section}"
        "待校对字幕:\n"
        f"{render_numbered_lines(lines)}\n"
    )


def build_reference_clean_prompt(raw_text: str) -> str:
    return (
        "以下是一篇视频的原始文稿，其中混有图片文件名（如 image.png）、动图文件名（如 xxx_rec_.gif）、"
        "URL 链接、[画面提示] 标注、案例操作说明等非正文内容。\n"
        "请仔细阅读理解这篇文稿的内容和叙述逻辑，然后重新整理输出一篇完整、逻辑通顺的逐字稿正文。\n"
        "要求：\n"
        "1. 去掉所有图片/视频文件名、URL 链接、[画面提示] 等非正文内容\n"
        "2. 去掉重复出现的段落或案例说明（正文已描述、案例部分再次重复的内容，只保留一份）\n"
        "3. 完整保留并准确呈现所有专有名词、品牌名、产品名\n"
        "4. 保持原文的叙述逻辑和内容完整性，不要压缩、删减、改写原文观点\n"
        "5. 直接输出整理后的文稿正文，不要加任何说明、前缀或标题\n\n"
        "原始文稿：\n"
        f"{raw_text.strip()}\n"
    )


def build_retry_prompt(original_prompt: str, previous_output: str) -> str:
    return (
        original_prompt
        + "\n你刚才的结果过于保守。请重新检查是否存在这些漏改问题：重复词未清理、AI 专有名词误识别、英文大小写错误、术语拆写错误、相邻编号断句不自然、行末标点未删除。"
        + "\n'我我我觉得'、'这个这个'、'然后然后'、'它它它' 这类重复，默认应清理为自然说法。"
        + "\n像 cloud code、claud、gimini、gemni、chat gpt、deep seek、work flow、skill、scale（AI 插件语境下）、agent、a gent、multi agent 这类写法，若上下文明确，应主动规范；AI 语境里的 agent 应优先改为 Agent。"
        + "\n如果参考文稿中有明确的品牌名或产品名，字幕中出现近音词时也应主动纠正，不要因为近音词本身是合法词汇就放过。"
        + "\n行末如有句号、逗号等标点，必须删除。"
        + "\n仍然不要随意新增标点，不要在纯中文词语之间插入多余空格，不要为了规范专有名词而给整句中文过度加空格，只能输出编号结果，不能加解释。"
        + "\n上一次输出如下：\n"
        + previous_output
        + "\n请重新输出最终编号文本。\n"
    )
