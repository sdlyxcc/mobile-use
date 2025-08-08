from pydantic import BaseModel

from minitap.agents.outputter.outputter import outputter
from minitap.config import OutputConfig
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


class MockPydanticSchema(BaseModel):
    color: str
    price: float
    currency_symbol: str
    website_url: str


mock_dict = {
    "color": "green",
    "price": 20,
    "currency_symbol": "$",
    "website_url": "http://superwebsite.fr",
}


class DummyState:
    def __init__(self, messages, initial_goal, agents_thoughts):
        self.messages = messages
        self.initial_goal = initial_goal
        self.agents_thoughts = agents_thoughts


mocked_state = DummyState(
    messages=[],
    initial_goal="Find a green product on my website",
    agents_thoughts=[
        "Going on http://superwebsite.fr",
        "Searching for products",
        "Filtering by color",
        "Color 'green' found for a 20 dollars product",
    ],
)


async def test_outputter_with_pydantic_model():
    logger.info("Starting test_outputter_with_pydantic_model")
    config = OutputConfig(
        structured_output=MockPydanticSchema,
        output_description=None,
    )

    result = await outputter(output_config=config, graph_output=mocked_state)  # type: ignore

    assert isinstance(result, MockPydanticSchema)
    assert result.color.lower() == "green"
    logger.success(str(result))


async def test_outputter_with_dict():
    logger.info("Starting test_outputter_with_dict")
    config = OutputConfig(
        structured_output=mock_dict,
        output_description=None,
    )

    result = await outputter(output_config=config, graph_output=mocked_state)  # type: ignore

    assert isinstance(result, dict)
    assert result.get("color", None) == "green"
    assert result.get("price", None) == 20
    assert result.get("currency_symbol", None) == "$"
    assert result.get("website_url", None) == "http://superwebsite.fr"
    logger.success(str(result))


async def test_outputter_with_natural_language_output():
    logger.info("Starting test_outputter_with_natural_language_output")
    config = OutputConfig(
        structured_output=None,
        output_description="A JSON object with a color, \
        a price, a currency_symbol and a website_url key",
    )

    result = await outputter(output_config=config, graph_output=mocked_state)  # type: ignore
    logger.info(str(result))

    assert isinstance(result, dict)
    assert result.get("color", None) == "green"
    assert result.get("price", None) == 20
    assert result.get("currency_symbol", None) == "$"
    assert result.get("website_url", None) == "http://superwebsite.fr"
    logger.success(str(result))


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_outputter_with_pydantic_model())
    asyncio.run(test_outputter_with_natural_language_output())
