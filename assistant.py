from collections import UserDict
from datetime import datetime as dtdt
from datetime import timedelta

from colorama import Fore, Style


def input_error(func):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
            # if type(result) is tuple and func.__name__ != 'valid_contact':
            #     output(*result)
            #     return result
            # else:
            #     return result
        except IndexError:
            return "Invalid data.", "error"
        except KeyError:
            return "No contact with that name.", "warning"
        except ValueError:
            return "Invalid command.", "error"
    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate(value)

    @input_error
    def validate(self, name):
        if name.isalpha():
            self.value = name.lower()
        else:
            self.value = None
            return "Please enter a valid contact name.", "warning"


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate(value)

    @input_error
    def validate(self, phone):
        if phone.isdigit() and len(phone) == 10:
            self.value = phone
        else:
            self.value = None


class Birthday(Field):
    def __init__(self, value):
        self.value = None
        self.validate_bd(value)

    @input_error
    def validate_bd(self, birthday):
        self.value = dtdt.strptime(birthday, "%d.%m.%Y").date()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p.value) for p in self.phones)}"

    @input_error
    def add_phone(self, phone):
        phone = Phone(phone)
        if phone.value is None:
            return "Please enter a valid phone number.", "warning"
        elif phone.value not in [i.value for i in self.phones]:
            self.phones.append(phone)
            return "Phone added.", "success"
        else:
            return "Phone already exists.", "warning"

    @input_error
    def remove_phone(self, phone_rm):
        for phone in self.phones:
            if phone_rm == phone.value:
                self.phones.remove(phone)
                return f"Phone {phone_rm} removed.", "success"

        return "No such phone exists.", "warning"

    @input_error
    def edit_phone(self, old_phone, new_phone):
        new_phone = Phone(new_phone)

        if new_phone.value is None:
            return "Please enter a valid phone number.", "warning"

        for phone in self.phones:
            if old_phone == phone.value and new_phone.value:
                phone.value = new_phone
                return f"Phone {old_phone} changed to {new_phone}.", "success"

        return "No such phone exists.", "warning"

    @input_error
    def find_phone(self, phone_to_find):
        for phone in self.phones:
            if phone_to_find == phone.value:
                return phone

    @input_error
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        if self.birthday.value is None:
            return "Invalid date format. Try DD.MM.YYYY.", "warning"
        return "Birthday added.", "success"

    @input_error
    def show_birthday(self):
        return f"{self.name.value.capitalize()}'s birthday: {dtdt.strftime(self.birthday.value, '%d.%m.%Y')}"


class AddressBook(UserDict):
    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record
        return "Record added.", "success"

    @input_error
    def find(self, name):
        return self.data[name.lower()]

    @input_error
    def delete(self, name):
        self.data.pop(name.lower())
        return "Record deleted.", "success"

    @input_error
    def get_upcoming_birthdays(self):
        today = dtdt.now().date()
        d7 = today + timedelta(days=7)
        lst = ["Next week You need to congratulate:"]
        for user in self.data.values():
            bday = user.birthday.value.replace(year=today.year)
            if bday <= today:
                bday = bday.replace(year=today.year + 1)
            if today <= bday <= d7:
                if bday.weekday() == 5:
                    bday = bday + timedelta(days=2)
                if bday.weekday() == 6:
                    bday = bday + timedelta(days=1)
                user_bday = f"{user.name.value.capitalize()}: {dtdt.strftime(bday, '%d.%m.%Y')}"
                lst.append(user_bday)
        return lst, "common list"


def output(message: str, mtype: str):
    if mtype == 'success':
        print(Fore.GREEN + message + Style.RESET_ALL)
    elif mtype == 'warning':
        print(Fore.YELLOW + message + Style.RESET_ALL)
    elif mtype == 'error':
        print(Fore.RED + message + Style.RESET_ALL)
    elif mtype == 'common list':
        for m in message:
            print(Fore.BLUE + m + Style.RESET_ALL)
    elif mtype == 'common':
        print(Fore.BLUE + message + Style.RESET_ALL)
    else:
        print(message)


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    if type(record) is tuple:
        record = Record(name)
        message = record.add_phone(phone)
        book.add_record(record)
    else:
        message = record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if type(record) is not tuple:
        message = record.edit_phone(old_phone, new_phone)
        return message
    else:
        return record


@input_error
def show_phone(args, book):
    name, *_ = args
    record = book.find(name)
    if type(record) is not tuple:
        phones = [i.value for i in record.phones]
        return phones, "common list"
    else:
        return record


@input_error
def show_all(book):
    phones = []
    for rec in book.values():
        rec_phones = ", ".join([i.value for i in rec.phones])
        phones.append(f"{rec.name.value.capitalize()}: {rec_phones}")
    return phones, "common list"


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if type(record) is not tuple:
        message = record.add_birthday(birthday)
        return message
    else:
        return record


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if type(record) is not tuple:
        message = record.show_birthday()
        return message, "common"
    else:
        return record


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        command = input("Write a command: ")
        command = command.lower().split(' ')

        match command[0]:
            case 'exit' | 'close':
                print("Good bye!")
                break
            case 'hello':
                print("How can I help you?")
            case 'add':
                output(*add_contact(command[1:], book))
            case 'change':
                output(*change_contact(command[1:], book))
            case 'phone':
                output(*show_phone(command[1:], book))
            case 'add-birthday':
                output(*add_birthday(command[1:], book))
            case 'show-birthday':
                output(*show_birthday(command[1:], book))
            case 'birthdays':
                output(*book.get_upcoming_birthdays())
            case 'all':
                output(*show_all(book))
            case _:
                output("Invalid command.", "error")


if __name__ == '__main__':
    main()
