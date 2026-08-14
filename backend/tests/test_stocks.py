

def _cast(y, m, d):
    from app import engine
    from app.rules import graph
    return graph.cast_chart(engine.compute(y, m, d, 9, 15, 5.5,
                                           13.0827, 80.2707))


def test_union_is_same_rasi_and_finds_the_taught_pairs():
    """[C2 @ 02:22-03:22] 'if there is a union between Venus and Moon,
    only then these things will happen' (ITC); 'Saturn plus Mercury ...
    then Adhani Pots will be good on that day'."""
    from app.rules import stocks
    united = dict((s, pair) for s, pair, _ in
                  stocks.united_stocks(_cast(2022, 1, 7)))
    assert "ADANIPORTS" in united
    assert set(united["ADANIPORTS"].split(" + ")) == {"Saturn", "Mercury"}
    # every reported pair really does share one rasi
    for stock, pair, rasi in stocks.united_stocks(_cast(2022, 1, 7)):
        occupants = stocks.conjunctions(_cast(2022, 1, 7))[rasi]
        for p in pair.split(" + "):
            assert p in occupants


def test_a_stock_with_one_owner_never_counts_as_united():
    """A union needs two planets; RELIANCE (Sun alone) can never have
    one, however crowded its rasi is."""
    from app.rules import stocks
    for y, m, d in [(2021, 2, 10), (2022, 1, 7), (2021, 5, 5)]:
        names = [s for s, _, _ in stocks.united_stocks(_cast(y, m, d))]
        assert "RELIANCE" not in names      # Sun only
        assert "COALINDIA" not in names     # Saturn only


def test_a_stellium_reports_degeneracy_instead_of_picks():
    """2021-02-10 has six grahas in Makara, uniting the owners of 26 of
    the 50 stocks. Presenting that as a stock list would read as 26
    picks; the rule has stopped discriminating and must say so."""
    from app.rules import stocks
    fs = stocks.conjunction_rules(_cast(2021, 2, 10))
    assert len(fs) == 1
    assert "not selective" in fs[0].title
    # ITC / Adani Ports may appear as the teacher's cited examples; what
    # must NOT appear is the dump of qualifying tickers
    for ticker in ("KOTAKBANK", "HINDUNILVR", "INFY", "TECHM"):
        assert ticker not in fs[0].detail


def test_conjunction_findings_disown_signal_status():
    from app.rules import stocks
    for y, m, d in [(2021, 2, 10), (2022, 1, 7)]:
        for f in stocks.conjunction_rules(_cast(y, m, d)):
            d_ = f.detail.lower()
            assert "not a signal" in d_ or "distinguishes nothing" in d_
