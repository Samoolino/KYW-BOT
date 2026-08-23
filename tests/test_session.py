from arb_engine.session import ProfitSession, SessionState


def test_session_closes_when_target_is_reached():
    s = ProfitSession(target_profit_usd=10, starter_capital_usd=100)
    s.start()
    assert s.state == SessionState.ACTIVE
    assert not s.record_profit(4)
    assert s.record_profit(6)
    assert s.state == SessionState.TARGET_REACHED
    assert s.target_remaining_usd == 0


def test_target_session_does_not_auto_restart():
    s = ProfitSession(target_profit_usd=1, starter_capital_usd=100)
    s.start()
    assert s.record_profit(1)
    assert s.state == SessionState.TARGET_REACHED
    assert not s.record_profit(1)
