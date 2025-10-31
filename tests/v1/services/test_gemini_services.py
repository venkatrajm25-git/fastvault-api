from unittest.mock import patch, MagicMock
from services.v1.gemini_services import Gemini_Services, clean_json_response


def test_clean_json_response_valid():
    raw_text = """```json
    [{"business_risk": "Fraud", "description": "Test", "default_risk_rating": "High"}]
    ```"""
    result = clean_json_response(raw_text)
    assert isinstance(result, list)
    assert result[0]["business_risk"] == "Fraud"


def test_clean_json_response_invalid_json():
    raw_text = """```json
    {bad json response]
    ```"""
    result = clean_json_response(raw_text)
    assert isinstance(result, list)
    assert "error" in result[0]


@patch("services.v1.gemini_services.model.generate_content")
def test_get_risk_details_success(mock_generate):
    mock_generate.return_value.text = """[{
        "business_risk": "AI Abuse",
        "description": "Bad AI",
        "default_risk_rating": "High"
    }]"""

    crg = ("Usecase", "Domain", "Country", "Gov")
    result = Gemini_Services.get_risk_details("Category", "NO", crg)
    assert isinstance(result, list)
    assert result[0]["business_risk"] == "AI Abuse"


@patch("services.v1.gemini_services.model.generate_content")
def test_get_result_summary_recommendation(mock_generate):
    mock_generate.return_value.text = "This is a recommendation"
    crg = ("Usecase", "Domain", "Country", "Gov")
    result = Gemini_Services.get_result_summary_recommendation(["risk1", "risk2"], crg)
    assert isinstance(result, str)


@patch("services.v1.gemini_services.model.generate_content")
def test_get_combined_abr_recommendation(mock_generate):
    mock_generate.return_value.text = "Combined summary"
    crg = ("Usecase", "Domain", "Country", "Gov")
    recs = [[("Text A",), ("Text B",)]]
    result = Gemini_Services.get_combined_abr_recommendation(recs, crg)
    assert isinstance(result, str)


@patch("services.v1.gemini_services.model.generate_content")
def test_gemini_abr_recommendation_data_valid_json(mock_generate):
    mock_response = MagicMock()
    mock_response.candidates[0].content.parts[
        0
    ].text = """```json
    {
        "impacts": ["Impact1", "Impact2"],
        "mitigation_sentences": ["Mitigate1", "Mitigate2"],
        "how_to_mitigate": [["Step1"], ["Step2"]]
    }
    ```"""
    mock_generate.return_value = mock_response

    crg = ("Usecase", "Domain", "Country", "Gov")
    result = Gemini_Services.gemini_abr_recommendation_data(
        crg, "RiskType", ["Risk1", "Risk2"], db=None
    )
    assert isinstance(result, dict)
    assert "impacts" in result


@patch("services.v1.gemini_services.model.generate_content")
def test_gemini_abr_recommendation_data_invalid_json(mock_generate):
    mock_response = MagicMock()
    mock_response.candidates[0].content.parts[0].text = "Invalid Response"
    mock_generate.return_value = mock_response

    crg = ("Usecase", "Domain", "Country", "Gov")
    try:
        Gemini_Services.gemini_abr_recommendation_data(
            crg, "RiskType", ["Risk1"], db=None
        )
    except ValueError as e:
        assert "Could not extract JSON block" in str(e)
