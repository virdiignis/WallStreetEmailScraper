import csv


class GetUniqueEmailPatterns:
    """
    Returns all unique email conventions from data.csv
    """

    @staticmethod
    def get_unique_email_patterns():
        patterns = set()
        with open('data.csv', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                patterns.add(row[2].split('@')[0])
        return patterns
