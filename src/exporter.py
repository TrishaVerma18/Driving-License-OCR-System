import json
import csv
import io


def export_json(details):
    """
    Convert extracted details to JSON.
    """
    return json.dumps(details, indent=4)


def export_csv(details):
    """
    Convert extracted details to CSV without using pandas.
    """

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=details.keys()
    )

    writer.writeheader()
    writer.writerow(details)

    return output.getvalue()