from polytropos.tools.qc.outcome import Outcome, ValueMismatch, ValueMatch, MissingValue

def test_empty_outcomes_equal():
    p: Outcome = Outcome()
    q: Outcome = Outcome()
    assert p == q

def test_both_have_same_match_equal():
    p: Outcome = Outcome()
    p_match: ValueMatch = ValueMatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo")
    p.matches.append(p_match)

    q: Outcome = Outcome()
    q_match: ValueMatch = ValueMatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo")
    q.matches.append(q_match)

    assert p == q

def test_each_has_different_match_not_equal():
    p: Outcome = Outcome()
    p_match: ValueMatch = ValueMatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo")
    p.matches.append(p_match)

    q: Outcome = Outcome()
    q_match: ValueMatch = ValueMatch("the_entity_id", "a_different_period", "/path/to/var", "Text", "foo")
    q.matches.append(q_match)

    assert p != q

def test_one_has_match_not_equal():
    p: Outcome = Outcome()
    p_match: ValueMatch = ValueMatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo")
    p.matches.append(p_match)

    q: Outcome = Outcome()

    assert p != q

def test_both_have_same_mismatch_equal():
    p: Outcome = Outcome()
    p_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    p.mismatches.append(p_mismatch)

    q: Outcome = Outcome()
    q_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    q.mismatches.append(q_mismatch)

    assert p == q

def test_one_has_mismatch_not_equal():
    p: Outcome = Outcome()
    p_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    p.mismatches.append(p_mismatch)

    q: Outcome = Outcome()

    assert p != q

def test_one_matches_one_doesnt_not_equal():
    p: Outcome = Outcome()
    p_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    p.mismatches.append(p_mismatch)

    q: Outcome = Outcome()
    q_match: ValueMatch = ValueMatch("the_entity_id", "a_different_period", "/path/to/var", "Text", "foo")
    q.matches.append(q_match)

    assert p != q

def test_each_has_different_mismatch_not_equal():
    p: Outcome = Outcome()
    p_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    p.mismatches.append(p_mismatch)

    q: Outcome = Outcome()
    q_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "BAR")
    q.mismatches.append(q_mismatch)

    assert p != q

def test_both_have_same_missing_equal():
    p: Outcome = Outcome()
    p_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    p.missings.append(p_missing)

    q: Outcome = Outcome()
    q_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    q.missings.append(q_missing)

    assert p == q

def test_one_has_missing_not_equal():
    p: Outcome = Outcome()
    p_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    p.missings.append(p_missing)

    q: Outcome = Outcome()

    assert p != q

def test_each_has_different_missing_not_equal():
    p: Outcome = Outcome()
    p_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    p.missings.append(p_missing)

    q: Outcome = Outcome()
    q_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", "Blah")
    q.missings.append(q_missing)

    assert p != q


def test_both_have_everything_equal():
    p: Outcome = Outcome()

    p_match: ValueMatch = ValueMatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo")
    p.matches.append(p_match)

    p_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    p.mismatches.append(p_mismatch)

    p_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    p.missings.append(p_missing)

    q: Outcome = Outcome()

    q_match: ValueMatch = ValueMatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo")
    q.matches.append(q_match)

    q_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    q.mismatches.append(q_mismatch)

    q_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    q.missings.append(q_missing)

    assert p == q

def test_almost_same_not_equal():
    p: Outcome = Outcome()

    p_match: ValueMatch = ValueMatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo")
    p.matches.append(p_match)

    p_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    p.mismatches.append(p_mismatch)

    p_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    p.missings.append(p_missing)

    q: Outcome = Outcome()

    q_mismatch: ValueMismatch = ValueMismatch("the_entity_id", "the_period", "/path/to/var", "Text", "foo", "bar")
    q.mismatches.append(q_mismatch)

    q_missing: MissingValue = MissingValue("the_entity_id", "the_period", "/path/to/var", "Text", None)
    q.missings.append(q_missing)

    assert p != q
