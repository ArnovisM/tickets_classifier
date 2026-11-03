from pathlib import Path
import shutil
from classifier import classify_tickets
from openai import APITimeoutError

NEW_TICKETS_FOLDER_PATH = Path("./New tickets")
CLASSIFIED_TICKETS_FOLDER_PATH = Path("./Classified tickets")
ERROR_TICKETS_FOLDER_PATH = Path("./Error tickets")


def move_ticket(source, destination):
    try:
        shutil.move(str(source), str(destination))
        print(f"File moved succesfully, new location is: {str(destination)}")
        return True
    except PermissionError as error:
        print(f"File could not be moved, error: {error}")
        return False

def move_ticket_to_error(file, error_folder):
    destination = error_folder / file.name
    moved = move_ticket(file, destination)

    if moved:
        print("File moved due to error, please review")
    else:
        print("Tried to move file due to error, action not performed, it is in original folder, please review")


def process_single_ticket(file, classified_folder, error_folder):
    with file.open("r", encoding="utf-8") as ticket:
        ticket_content = ticket.read().strip()

    if ticket_content:
        try:
            category = classify_tickets(ticket_content)
            if category != "Category not defined":
                print(f"The category for ticket {file} is {category}")
                new_filename = f"{file.stem} - Category - {category}{file.suffix}"
                moved = move_ticket(file, destination)
                if moved:
                    print("Transaction succesfull, moving to next ticket")
                else:
                    print("Transaction not succesfull, leaving ticket on same folder for review")
            else:
                print(f"Error classifing ticket: {file.name}")
                destination = error_folder / file.name
                move_ticket_to_error(file, error_folder)
        except APITimeoutError as error:
            print(f"Error with API: {error}")
    else:
        print("Error: content is empty")
        move_ticket_to_error(file, error_folder)


def process_tickets(
    new_tickets_dir=NEW_TICKETS_FOLDER_PATH,
    classified_tickets_dir=CLASSIFIED_TICKETS_FOLDER_PATH,
    error_tickets_dir=ERROR_TICKETS_FOLDER_PATH,
):
    new_tickets_dir.mkdir(parents=True, exist_ok=True)
    classified_tickets_dir.mkdir(parents=True, exist_ok=True)
    error_tickets_dir.mkdir(parents=True, exist_ok=True)

    for file in list(new_tickets_dir.iterdir()):
        if file.is_file() and file.suffix == ".txt":
            process_single_ticket(file, classified_tickets_dir, error_tickets_dir)


if __name__ == "__main__":
    process_tickets()


            
