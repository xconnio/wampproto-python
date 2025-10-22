import threading

import pytest

from wampproto.idgen import generate_session_id, SessionScopeIDGenerator, ID_MAX


def test_generate_session_id():
    for _ in range(100):
        session_id = generate_session_id()
        assert 1 <= session_id <= ID_MAX


@pytest.mark.parametrize("id_generator", [SessionScopeIDGenerator(), SessionScopeIDGenerator(use_lock=True)])
def test_next(id_generator):
    ids = [id_generator.next() for _ in range(5)]
    assert ids == [1, 2, 3, 4, 5]
    assert id_generator.id == 5


@pytest.mark.parametrize("id_generator", [SessionScopeIDGenerator(), SessionScopeIDGenerator(use_lock=True)])
def test_next_max_value(id_generator: SessionScopeIDGenerator):
    id_generator.id = ID_MAX
    result = id_generator.next()
    assert result == 1


@pytest.mark.parametrize("id_generator", [SessionScopeIDGenerator(), SessionScopeIDGenerator(use_lock=True)])
def test_thread_safety(id_generator: SessionScopeIDGenerator):
    results = []

    def worker():
        for _ in range(1000):
            results.append(id_generator.next())

    threads = [threading.Thread(target=worker) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 100000
    assert len(set(results)) == 100000
