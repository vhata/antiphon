"""Tests for scripts.similar — library-overlap annotation logic."""

from __future__ import annotations

from scripts import similar


def test_build_library_index_lowercases_names() -> None:
    top = [
        {"@attr": {"rank": "1"}, "playcount": "5208", "name": "Pink Floyd"},
        {"@attr": {"rank": "2"}, "playcount": "4947", "name": "Velvet Acid Christ"},
    ]
    idx = similar.build_library_index(top)
    assert idx["pink floyd"] == (1, 5208)
    assert idx["velvet acid christ"] == (2, 4947)
    assert "Pink Floyd" not in idx  # only lowercase keys


def test_annotate_marks_in_library_and_gaps() -> None:
    similar_artists = [
        {"name": "Pink Floyd", "match": "0.95"},
        {"name": "Tricky", "match": "0.80"},
    ]
    library = {"pink floyd": (1, 5208)}
    annotated = similar.annotate(similar_artists, library)
    assert annotated == [
        ("Pink Floyd", 95.0, (1, 5208)),
        ("Tricky", 80.0, None),
    ]


def test_annotate_handles_missing_match_field() -> None:
    similar_artists = [{"name": "X"}]
    annotated = similar.annotate(similar_artists, {})
    assert annotated == [("X", 0.0, None)]
