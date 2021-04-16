from flask_table import Table, Col, DateCol


class UserCol(Col):
    def td_format(self, content):
       return content.username

class PackageItemTable(Table):
    classes = ['table', "table-dark"]

    name = Col('Id')
    creation_date = DateCol('Creation Date')
    creator_id = Col('Creator')
    creator = UserCol("User")
