# This has worked for all my CSVs. If there are issues we can consider adding a sniffer for
# the CSV dialect.

import csv
import os
import sys
import argparse
import PySimpleGUI as sg

layout = [
    [sg.Text("Source CSV file:")],
    [
        sg.Input(key="in_file", enable_events=True),
        sg.FileBrowse(file_types=(("csv", "*.csv"),)),
    ],
    [
        sg.Checkbox(
            "CSV has a header row.", default=True, key="header_row", enable_events=True
        )
    ],
    [
        sg.Text("Text Column:", size=(18, 1)),
        sg.Drop(
            key="text_field",
            disabled=True,
            size=(30, 5),
            enable_events=True,
        ),
    ],
    [
        sg.Text("Filename Column:", size=(18, 1)),
        sg.Drop(
            key="key_field",
            disabled=True,
            size=(30, 5),
            enable_events=True,
        ),
    ],
    [sg.Text("Destination Directory:")],
    [
        sg.Input(key="out_directory", disabled=True, enable_events=True),
        sg.FolderBrowse(key="folder_browse", disabled=True),
    ],
    [
        sg.Checkbox(
            "Overwrite files",
            key="overwrite",
            default=False,
            tooltip="Overwrite files in write directory.",
        )
    ],
    [sg.Text(text="Instructions:")],
    [sg.Text(text="", key="instructions", size=(50, 2), background_color="white")],
    [
        sg.Push(),
        sg.Button("Cancel", key="cancel", enable_events=True),
        sg.Button(
            "OK",
            key="ok",
            disabled=True,
            disabled_button_color="grey25",
            enable_events=True,
        ),
    ],
]

instructions = {
    "in_file": "Select a CSV file.",
    "text_field": "Select the column that contains the texts.",
    "key_field": "Select the column that contains the names for the files or use row numbers.",
    "out_directory": "Select or create the directory that will contain the text files",
    "ok": "Click OK.",
}


def update_fields_dropdown(window, header_row, use_header_row):
    if not use_header_row:
        row = [f"Column {i}" for i in range(1, len(header_row) + 1)]
    else:
        row = header_row
    window["text_field"].update(values=row, value=None)
    window["key_field"].update(values=["Use Row Numbers"] + row, value=None)


def extract_files(
    filename,
    out_directory,
    key_field,
    text_field,
    overwrite=False,
):
    assert os.path.isdir(
        out_directory
    ), f"{out_directory} is not a valid destination directory."
    with open(filename, "r", encoding="utf-8-sig") as input_file:
        input_csv = csv.DictReader(input_file)
        input_fields = input_csv.fieldnames
        if key_field != "Use Row Numbers":
            assert (
                key_field in input_fields
            ), f"Field {key_field} does not appear in header row of file {filename}."
        assert (
            text_field in input_fields
        ), f"Field {text_field} does not appear in header row of file {filename}."
        for row_number, row in enumerate(input_csv, start=2):
            name = row_number if key_field == "Use Row Numbers" else row[key_field]
            out_path = os.path.join(out_directory, name + ".txt")
            if not overwrite:
                assert not os.path.exists(
                    out_path
                ), f'Writing {key_field+".txt"} would result in overwriting.'
            with open(out_path, "w") as out_file:
                out_file.write(row[text_field])


def gui():
    window = sg.Window("csv2folder", layout, finalize=True)
    header_row = []
    window["instructions"].update(instructions["in_file"], text_color="green")
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "cancel" or event == "ok":
            break
        if event == "header_row" and header_row != []:
            update_fields_dropdown(window, header_row, values["header_row"])
        if event == "in_file" and values["in_file"] != "":
            if values["in_file"][-4:] != ".csv":
                window["instructions"].update(
                    "Must select a .csv file.",
                    text_color="red",
                )
                continue
            try:
                with open(values["in_file"], "r") as in_file:
                    in_csv = csv.reader(in_file)
                    header_row = in_csv.__next__()
                update_fields_dropdown(window, header_row, values["header_row"])
                window["text_field"].update(disabled=False)
            except:
                window["instructions"].update(
                    "Invalid CSV file.",
                    text_color="red",
                )

        if event == "text_field" and values["text_field"] != "":
            window["key_field"].update(disabled=False)
        if event == "key_field" and values["key_field"] != "":
            window["out_directory"].update(disabled=False)
            window["folder_browse"].update(disabled=False)
        if values["out_directory"] != "":
            window["ok"].update(disabled=False)

        if (
            not window["key_field"].Disabled
            and values["text_field"] == values["key_field"]
        ):
            window["instructions"].update(
                "Must select different columns for text and file name.",
                text_color="red",
            )
            window["ok"].update(disabled=True)
            continue
        for element in reversed(instructions):
            if not window[element].Disabled:
                window["instructions"].update(instructions[element], text_color="green")
                break
    return values


def command_line():
    parser = argparse.ArgumentParser(
        description="Takes a csv file with a header and names for key and text "
        "columns and produces 1 file per row with name from the key column and contents from the text"
    )
    parser.add_argument(
        "in_file",
        help="Name of input .csv file. "
        "CSV files are expected to have a header row. Empty cells in the header "
        "row are ignored. Cells in columns with empty header cells are recorded as extra fields.",
    )
    parser.add_argument(
        "out_directory", help="Output drectory. Must exist.", required=True
    )
    parser.add_argument(
        "key_field",
        help="Column from csv header that uniquely indentifies rows. "
        'May be "Use Row Numbers" to indicate that row numbers should be used.',
        required=True,
    )
    parser.add_argument(
        "text_field",
        help="Column from csv header that contains text files.",
        required=True,
    )
    parser.add_argument(
        "--overwrite",
        help="By default the program will not overwrite an existing file.",
        action="store_true",
    )
    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = command_line()
    else:
        args = gui()

    extract_files(
        args["in_file"],
        args["out_directory"],
        args["key_field"],
        args["text_field"],
        args["overwrite"],
    )
