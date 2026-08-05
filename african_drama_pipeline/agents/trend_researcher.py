"""Agent 1: Trend Researcher.

Discovers trending drama premises for the target region/genre.
"""

from interfaces import TrendResearchInterface
from mocks import MockTrendResearcher
from models import ProjectState, TrendSignal
from config import settings
import logging

logger = logging.getLogger(__name__)


class TrendResearcher:
    def __init__(self, trend_api: TrendResearchInterface | None = None):
        self.trend_api = trend_api or MockTrendResearcher()

    def run(self, state: ProjectState) -> ProjectState:
        logger.info(f"[TrendResearcher] region={state.region}, genre={state.genre}")
        trends = self.trend_api.get_trending_premises(state.region, state.genre, limit=10)
        state.trends = trends
        state.chosen_trend = trends[0] if trends else None
        logger.info(f"[TrendResearcher] selected: {state.chosen_trend.hook if state.chosen_trend else 'NONE'}")
        return state
