import pytest
from classifier import classify_tickets
from unittest.mock import Mock, patch
from pathlib import Path

def test_classifies_software_issue():
    response = Mock()
    response.output_text= "software"

    with patch("classifier.client.responses.create", return_value = response) as Mock_create:
        result = classify_tickets("SAP crashes every time I open transaction ME21N. I have restarted the application, but the same error keeps appearing.") 
        
        assert result == "software"

        Mock_create.assert_called_once()

def test_classifies_hardware_issues():
    response = Mock()
    response.output_text= "hardware"

    with patch("classifier.client.responses.create", return_value = response) as Mock_create:
        result = classify_tickets("The printer on the third floor is powered on but does not print any documents sent from my computer.")

        assert result == "hardware"

        Mock_create.assert_called_once()        

def test_empty_ticket_raises_error():
    with patch("classifier.client.responses.create") as Mock_create:
        with pytest.raises(ValueError):
            classify_tickets("")

        Mock_create.assert_not_called()

def test_category_not_defined():
    response = Mock()
    response.output_text = "Category not defined"

    with patch("classifier.client.responses.create", return_value = response) as Mock_create:
        result = classify_tickets("The user wants to know where to buy lunch near the office.")

        assert result == "Category not defined"

        Mock_create.assert_called_once()



    

