import csv
import requests
import json


class GenerateEmails:
    """
    Generates and checks emails for contacts. Writes result to data3.csv
    """

    @staticmethod
    def __getApiKey__():
        """
        yields next api key to use. Make sure there is always enough in mailboxlayerKeys.txt!
        """
        with open('mailboxlayerKeys.txt') as fp:
            for line in fp:
                yield line

    def __init__(self):
        """
        Introduces email conventions generation code.
        """
        self.newApiKey = self.__getApiKey__()
        self.API_KEY = self.newApiKey.__next__()
        with open('usablePatternsCode.json') as fp:
            self.usable_patterns_code = json.load(fp)

    def run(self):
        """
        Runs email generation and checking. Writes results to data3.csv
        :return:
        """
        phones = dict()
        with open('data.csv', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                phones[row[0]] = eval(row[7])
        with open('data2.csv', newline='') as file:
            csv_reader = csv.reader(file)
            with open('data3.csv', 'w', newline='') as file_f:
                csv_writer = csv.writer(file_f)
                csv_writer.writerow(
                    ['Searched Company Name', 'Found Company Name', 'City', 'State', 'Country', 'First Name',
                     'Last Name',
                     'Title', 'Updated', 'Phone', 'Email', 'Domain MX Record', 'SMTP Check', 'Email Score'])
                for row in csv_reader:
                    if row[3] in ('MA', 'CT'):  # Add other states here.
                        phone = phones.get(row[0], {}).get(row[2], '')
                        if row[7].split('@')[0].lower() in self.usable_patterns_code.keys():
                            f = row[5].lower()  # Those two
                            l = row[6].lower()  # are used in eval
                            pattern_start, pattern_end = row[7].split('@')
                            mail = eval(self.usable_patterns_code[pattern_start.lower()]) + '@' + pattern_end

                            def check_mail(api_key, email):
                                ans = requests.get(
                                    "http://apilayer.net/api/check?access_key=%s&email=%s" % (api_key, email))
                                return json.loads(ans.text)

                            resp = check_mail(self.API_KEY, mail)
                            if not bool(resp.get("success", True)) and resp['error']['code'] == 104:
                                self.API_KEY = self.newApiKey.__next__()
                                resp = check_mail(self.API_KEY, mail)
                            mx, smtp, score = resp['mx_found'], resp['smtp_check'], resp['score']
                        else:
                            mail, mx, smtp, score = '', '', '', ''
                        new_row = row[:7]
                        new_row.extend(row[8:])
                        new_row.extend([phone, mail, mx, smtp, score])
                        csv_writer.writerow(new_row)
