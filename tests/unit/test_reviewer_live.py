import json
from types import SimpleNamespace

from runtime.reviewer_live import _empty_semantic_diff


def test_empty_semantic_diff_accepts_only_explicit_empty_rows() -> None:
    assert _empty_semantic_diff(json.dumps({"columns": [], "rows": []}))
    assert _empty_semantic_diff(json.dumps({"result": '{"columns": [], "rows": []}'}))
    assert _empty_semantic_diff(
        [SimpleNamespace(result=json.dumps({"result": '{"columns": [], "rows": []}'}))]
    )
    assert _empty_semantic_diff(
        [
            SimpleNamespace(
                text='{"columns": [], "rows": []}\n'
                '{"result": "{\\"columns\\": [], \\"rows\\": []}"}'
            )
        ]
    )
    assert _empty_semantic_diff("[]")
    assert not _empty_semantic_diff(json.dumps({"rows": [{"issue": "missing"}]}))
    assert not _empty_semantic_diff("query completed")
    assert not _empty_semantic_diff(json.dumps({"status": "ok"}))
