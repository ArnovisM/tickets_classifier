from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
import pytest
from openai import APITimeoutError
from main import (
    process_single_ticket,
    process_tickets,
    NEW_TICKETS_FOLDER_PATH,
    CLASSIFIED_TICKETS_FOLDER_PATH,
    ERROR_TICKETS_FOLDER_PATH,
)


def test_ticket_success_moves_to_classified():
    """
    ticket_001.txt: La API devuelve 'software'.
    Se debe llamar a move_ticket hacia 'Classified tickets' con la nueva categoría en el nombre.
    """
    ticket_file = NEW_TICKETS_FOLDER_PATH / "ticket_001.txt"
    content = "SAP crashes every time I open transaction ME21N."

    response = Mock()
    response.output_text = "software"

    with patch("pathlib.Path.open", mock_open(read_data=content)):
        with patch("classifier.client.responses.create", return_value=response) as mock_create:
            with patch("main.move_ticket") as mock_move:
                process_single_ticket(
                    ticket_file,
                    CLASSIFIED_TICKETS_FOLDER_PATH,
                    ERROR_TICKETS_FOLDER_PATH,
                )

                mock_create.assert_called_once()
                expected_destination = CLASSIFIED_TICKETS_FOLDER_PATH / "ticket_001 - Category - software.txt"
                mock_move.assert_called_once_with(ticket_file, expected_destination)


def test_ticket_timeout_stays_in_new_tickets():
    """
    ticket_002.txt: La API lanza APITimeoutError.
    El error se captura y NO se debe llamar a move_ticket (permanece en 'New tickets').
    """
    ticket_file = NEW_TICKETS_FOLDER_PATH / "ticket_002.txt"
    content = "Cannot connect to the VPN server."

    timeout_error = APITimeoutError(request=Mock())

    with patch("pathlib.Path.open", mock_open(read_data=content)):
        with patch("classifier.client.responses.create", side_effect=timeout_error) as mock_create:
            with patch("main.move_ticket") as mock_move:
                process_single_ticket(
                    ticket_file,
                    CLASSIFIED_TICKETS_FOLDER_PATH,
                    ERROR_TICKETS_FOLDER_PATH,
                )

                mock_create.assert_called_once()
                mock_move.assert_not_called()


def test_ticket_empty_moves_to_error():
    """
    ticket_003.txt: Está vacío.
    No se debe llamar a la API y se debe llamar a move_ticket hacia 'Error tickets'.
    """
    ticket_file = NEW_TICKETS_FOLDER_PATH / "ticket_003.txt"
    content = ""

    with patch("pathlib.Path.open", mock_open(read_data=content)):
        with patch("classifier.client.responses.create") as mock_create:
            with patch("main.move_ticket") as mock_move:
                process_single_ticket(
                    ticket_file,
                    CLASSIFIED_TICKETS_FOLDER_PATH,
                    ERROR_TICKETS_FOLDER_PATH,
                )

                mock_create.assert_not_called()
                expected_destination = ERROR_TICKETS_FOLDER_PATH / "ticket_003.txt"
                mock_move.assert_called_once_with(ticket_file, expected_destination)


def test_ticket_unexpected_category_moves_to_error():
    """
    Respuesta inesperada: La API devuelve una categoría fuera de catálogo (p. ej. 'network').
    Debe terminar en 'Error tickets'.
    """
    ticket_file = NEW_TICKETS_FOLDER_PATH / "ticket_network.txt"
    content = "The office Wi-Fi is down and router is unresponsive."

    response = Mock()
    response.output_text = "network"

    with patch("pathlib.Path.open", mock_open(read_data=content)):
        with patch("classifier.client.responses.create", return_value=response) as mock_create:
            with patch("main.move_ticket") as mock_move:
                process_single_ticket(
                    ticket_file,
                    CLASSIFIED_TICKETS_FOLDER_PATH,
                    ERROR_TICKETS_FOLDER_PATH,
                )

                mock_create.assert_called_once()
                expected_destination = ERROR_TICKETS_FOLDER_PATH / "ticket_network.txt"
                mock_move.assert_called_once_with(ticket_file, expected_destination)


def test_process_tickets_batch_continues_after_timeout():
    """
    Procesamiento por lotes: comprueba que process_tickets() procesa varios archivos
    y que un ticket con APITimeoutError no impide procesar los siguientes.
    """
    # Archivo 1: provocará APITimeoutError
    file_1 = MagicMock()
    file_1.is_file.return_value = True
    file_1.suffix = ".txt"
    file_1.stem = "ticket_001"
    file_1.name = "ticket_001.txt"
    file_1.open.return_value.__enter__.return_value.read.return_value = "VPN connection failed"

    # Archivo 2: se clasificará exitosamente como 'software'
    file_2 = MagicMock()
    file_2.is_file.return_value = True
    file_2.suffix = ".txt"
    file_2.stem = "ticket_002"
    file_2.name = "ticket_002.txt"
    file_2.open.return_value.__enter__.return_value.read.return_value = "Excel keeps crashing on launch"

    mock_new_dir = MagicMock()
    mock_new_dir.iterdir.return_value = [file_1, file_2]

    response_2 = Mock()
    response_2.output_text = "software"
    timeout_error = APITimeoutError(request=Mock())

    with patch("classifier.client.responses.create", side_effect=[timeout_error, response_2]) as mock_create:
        with patch("main.move_ticket") as mock_move:
            process_tickets(
                new_tickets_dir=mock_new_dir,
                classified_tickets_dir=CLASSIFIED_TICKETS_FOLDER_PATH,
                error_tickets_dir=ERROR_TICKETS_FOLDER_PATH,
            )

            # Se intentó clasificar ambos tickets (el timeout de file_1 no detuvo el bucle)
            assert mock_create.call_count == 2

            # file_1 NO se movió (permanece en New tickets para futuro reintento)
            # file_2 SÍ se movió a Classified tickets
            expected_destination_2 = CLASSIFIED_TICKETS_FOLDER_PATH / "ticket_002 - Category - software.txt"
            mock_move.assert_called_once_with(file_2, expected_destination_2)

