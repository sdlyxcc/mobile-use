from minitap.controllers.mobile_command_controller import (
    CoordinatesSelectorRequest,
    IdSelectorRequest,
    PercentagesSelectorRequest,
    SelectorRequestWithCoordinates,
    SelectorRequestWithPercentages,
    TextSelectorRequest,
    format_selector_request_for_yaml,
)


def test_format_selector_with_id():
    request = IdSelectorRequest(id="element-42")
    result = format_selector_request_for_yaml(request)
    assert result == "\n id: element-42\n"


def test_format_selector_with_coordinates():
    request = SelectorRequestWithCoordinates(coordinates=CoordinatesSelectorRequest(x=123, y=456))
    result = format_selector_request_for_yaml(request)
    assert result is not None
    assert result == "\n point: 123,456\n"


def test_format_selector_with_percentages():
    request = SelectorRequestWithPercentages(
        percentages=PercentagesSelectorRequest(x_percent=50, y_percent=25)
    )
    result = format_selector_request_for_yaml(request)
    assert result == "\n point: 50%,25%\n"


def test_format_selector_with_text():
    request = TextSelectorRequest(text="Click me")
    result = format_selector_request_for_yaml(request)
    assert result is not None
    assert result == "\n text: Click me\n"
