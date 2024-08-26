class DetailedTestException(Exception):
    def __init__(self, original_exception, path_context, operation, record, field=None, field_value=None):
        self.original_exception = original_exception
        self.operation = operation
        self.path_context = path_context
        self.record = record
        self.field = field
        self.field_value = field_value
        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"\n\n"
            f"{'Operation:', 'yellow'} {self.operation}\n"
            f"{'Record:', 'yellow'} {self.record}\n"
            # f"{colored('Field:', 'yellow')} {str(self.field)}\n" if self.field else ""
            # f"{colored('Field_value:', 'yellow')} {str(self.field_value)}\n" if self.field_value else ""
            # f"{colored('Error:', 'yellow')} {str(self.original_exception)}\n"
            f"{'Path Tree:', 'light_grey'}\n {str(self.path_context)}\n"
        )

# class DetailedJsonException(Exception):
#     def __init__(self, original_exception, path_contex):
#         self.original_exception = original_exception
#         self.path_context = path_context
#         super().__init__(self.__str__())
#
#     def __str__(self):
#         return (
#             f"\n\n"
#             f"{colored('Operation:', 'yellow')} {self.operation}\n"
#             f"{colored('Record:', 'yellow')} {self.record}\n"
#             # f"{colored('Field:', 'yellow')} {str(self.field)}\n" if self.field else ""
#             # f"{colored('Field_value:', 'yellow')} {str(self.field_value)}\n" if self.field_value else ""
#             # f"{colored('Error:', 'yellow')} {str(self.original_exception)}\n"
#             f"{colored('Path Tree:', 'light_grey')}\n {str(self.path_context)}\n"
#         )
#


def locateJsonError(path_json, ):
    with open('data.json', 'r') as file:
        data = json.load(file)

    # Locate the row and column
    for row in data:
        if row['name'] == 'Bob':
            print("Row found:", row)
            print("Bob's city:", row['city'])
            break
