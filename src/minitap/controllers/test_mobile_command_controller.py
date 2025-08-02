from minitap.controllers.mobile_command_controller import (
    CoordinatesSelectorRequest,
    PercentagesSelectorRequest,
    SelectorRequest,
    format_selector_request_for_yaml,
)


def test_format_selector_with_id():
    request = SelectorRequest(id="element-42")
    result = format_selector_request_for_yaml(request)
    assert result == "\n id: element-42\n"


def test_format_selector_with_coordinates():
    request = SelectorRequest(coordinates=CoordinatesSelectorRequest(x=123, y=456))
    result = format_selector_request_for_yaml(request)
    assert result is not None
    assert result == "\n point: 123,456\n"


def test_format_selector_with_percentages():
    request = SelectorRequest(percentages=PercentagesSelectorRequest(x_percent=50, y_percent=25))
    result = format_selector_request_for_yaml(request)
    assert result == "\n point: 50%,25%\n"


def test_format_selector_with_text():
    request = SelectorRequest(text="Click me")
    result = format_selector_request_for_yaml(request)
    assert result is not None
    assert result == "\n text: Click me\n"


def test_format_selector_with_nothing():
    request = SelectorRequest()
    result = format_selector_request_for_yaml(request)
    assert result is None


def test_format_selector_prioritizes_id_over_others():
    request = SelectorRequest(
        id="high-priority", coordinates=CoordinatesSelectorRequest(x=1, y=2), text="fallback"
    )
    result = format_selector_request_for_yaml(request)
    assert result is not None
    assert result == "\n id: high-priority\n"


def test_format_selector_prioritizes_coordinates_over_text():
    request = SelectorRequest(coordinates=CoordinatesSelectorRequest(x=10, y=20), text="tap here")
    result = format_selector_request_for_yaml(request)
    assert result is not None
    assert result == "\n point: 10,20\n"
