from jianying_subtitle_proofread.flatten import flatten_lines
from jianying_subtitle_proofread.prompting import build_proofread_prompt, build_retry_prompt
from jianying_subtitle_proofread.srt_io import parse_srt


COVERAGE_SRT = """1
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

13
00:00:24,000 --> 00:00:26,000
就是很多人把agent

14
00:00:26,000 --> 00:00:28,000
和 work flow 混在一起

16
00:00:30,000 --> 00:00:32,000
不要拿传统自动化去理解agent

20
00:00:38,000 --> 00:00:40,000
a gent或者multi agent

41
00:01:20,000 --> 00:01:22,000
还是一个能串工具的agent

42
00:01:22,000 --> 00:01:24,000
再比如很多人会把mcp

44
00:01:26,000 --> 00:01:28,000
其实它是model context protocol

47
00:01:32,000 --> 00:01:34,000
还有open ai和anthropic
"""


def test_coverage_prompt_contains_capitalized_agent_guidance():
    blocks = parse_srt(COVERAGE_SRT)
    prompt = build_proofread_prompt(flatten_lines(blocks), pass_name="A")
    assert "Agent" in prompt
    assert "multi-Agent" in prompt
    assert "如果在 AI 助手、任务执行、工具调用、多智能体协作语境里出现 agent，一般规范为 Agent" in prompt
    assert "agent、a gent、multi agent" in prompt


def test_coverage_prompt_contains_expected_misrecognition_examples():
    blocks = parse_srt(COVERAGE_SRT)
    prompt = build_proofread_prompt(flatten_lines(blocks), pass_name="A")
    assert "cloud code" in prompt
    assert "gimini" in prompt
    assert "chat gpt" in prompt
    assert "deep seek" in prompt
    assert "work flow" in prompt
    assert "model context protocol" in prompt
    assert "open ai" in prompt
    assert "anthropic" in prompt


def test_retry_prompt_reinforces_capitalized_agent_policy():
    retry = build_retry_prompt("原始prompt", "[1] 很多人把agent和 work flow 混在一起")
    assert "AI 语境里的 agent 应优先改为 Agent" in retry
    assert "agent、a gent、multi agent" in retry
