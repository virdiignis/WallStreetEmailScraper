from GetLinks import GetLinks
from GetData import GetData
from Register import Register
from GetContacts import GetContacts
from GetUniqueEmailPatterns import GetUniqueEmailPatterns
from GenerateEmails import GenerateEmails

if __name__ == '__main__':
    GetLinks.get_links()
    GetData().run()
    Register.register()
    GetContacts().run(4)
    print(GetUniqueEmailPatterns.get_unique_email_patterns())
    input('Now you should write code for found email patterns. Enter when ready.')
    GenerateEmails().run()



