# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections.abc import Sequence
from typing import NamedTuple

import pytest

from card_management.learn_now import filter_cards
from tests.helpers import FilterCardSpec, mock_filter_cards


class FilterScenario(NamedTuple):
    """Specify selected cards and expected results with sibling skipping off and on."""

    cards: Sequence[FilterCardSpec]
    all_new: Sequence[int]
    unique_notes: Sequence[int]


SCENARIOS: dict[str, FilterScenario] = {
    "empty": FilterScenario((), (), ()),
    "single": FilterScenario((FilterCardSpec(1, 10, 2),), (1,), (1,)),
    "lower-ordinal-first": FilterScenario((FilterCardSpec(1, 10, 0), FilterCardSpec(2, 10, 1)), (1, 2), (1,)),
    "lower-ordinal-last": FilterScenario((FilterCardSpec(2, 10, 1), FilterCardSpec(1, 10, 0)), (2, 1), (1,)),
    "separate-notes": FilterScenario((FilterCardSpec(1, 10, 0), FilterCardSpec(2, 20, 0)), (1, 2), (1, 2)),
    "review-sibling": FilterScenario((FilterCardSpec(1, 10, 0, 2, 2), FilterCardSpec(2, 10, 1)), (2,), (2,)),
    "suspended-sibling": FilterScenario((FilterCardSpec(1, 10, 0, 0, -1), FilterCardSpec(2, 10, 1)), (2,), (2,)),
    "buried-sibling": FilterScenario((FilterCardSpec(1, 10, 0, 0, -2), FilterCardSpec(2, 10, 1)), (2,), (2,)),
    "learning-card": FilterScenario((FilterCardSpec(1, 10, 0, 1, 1),), (), ()),
    "non-new-type": FilterScenario((FilterCardSpec(1, 10, 0, 2, 0),), (), ()),
    "same-ordinal": FilterScenario((FilterCardSpec(1, 10, 0), FilterCardSpec(2, 10, 0)), (1, 2), (1,)),
    "interleaved-notes": FilterScenario(
        (FilterCardSpec(1, 10, 2), FilterCardSpec(2, 20, 0), FilterCardSpec(3, 10, 1)),
        (1, 2, 3),
        (3, 2),
    ),
}


class TestFilterCards:
    """Cover lists and one-shot iterators with the package's runtime checks enabled."""

    @pytest.mark.parametrize("scenario", SCENARIOS.values(), ids=SCENARIOS.keys())
    @pytest.mark.parametrize("skip_siblings", [False, True])
    @pytest.mark.parametrize("use_iterator", [False, True], ids=["list", "iterator"])
    def test_filter_cards(self, scenario: FilterScenario, skip_siblings: bool, use_iterator: bool) -> None:
        """Select only eligible cards and optionally keep the lowest selected new sibling per note."""
        cards = list(mock_filter_cards(scenario.cards))
        source = cards
        if use_iterator:
            source = iter(cards)
        expected = scenario.all_new
        if skip_siblings:
            expected = scenario.unique_notes
        assert [card.id for card in filter_cards(source, skip_siblings=skip_siblings)] == list(expected)
