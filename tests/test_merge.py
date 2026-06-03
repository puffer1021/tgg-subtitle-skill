from jianying_subtitle_proofread.merge import merge_candidates


def test_merge_candidates_uses_shared_value_when_identical():
    merged, decisions = merge_candidates({1: "Beijing"}, {1: "Beijing"})
    assert merged == {1: "Beijing"}
    assert decisions[0].source == "both"


def test_merge_candidates_can_choose_b_when_reference_matches():
    merged, decisions = merge_candidates({1: "Ternas"}, {1: "Ternus"}, reference_text="John Ternus 是苹果高管")
    assert merged[1] == "Ternus"
    assert decisions[0].source == "B"


def test_merge_candidates_avoids_adding_punctuation_when_only_difference_is_punctuation():
    merged, decisions = merge_candidates({1: "一个好的事情"}, {1: "一个好的事情。"})
    assert merged[1] == "一个好的事情"
    assert "不新增标点" in decisions[0].reason
