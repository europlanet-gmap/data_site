from flask_login import current_user
from flask_table import Table, Col, DateCol, ButtonCol, BoolCol
from flask import Markup, url_for


class UserCol(Col):
    def td_format(self, content):
       return content.username

class EditCol(ButtonCol):
    allow_sort=False
    def td_format(self, content):
        # if current_user ==
        return content

    def td_contents(self, item, attr_list):
        # print(self.from_attr_list(item, attr_list))
        # return Markup.escape(self.from_attr_list(item, attr_list))
        if item.editable:
            return ButtonCol.td_contents(self, item, attr_list)
        else:
            return ""

        return m

class ToolCol(Col):
    def td_contents(self, item, attr_list):
        # print(self.from_attr_list(item, attr_list))
        # return Markup.escape(self.from_attr_list(item, attr_list))
        o = ""
        for tool in item.tools:
            if tool.is_allowed(item):
                link = tool.get_link(item)
                o += f' <a type="submit" class="btn btn-outline-danger" href="{link}"> {tool.display_name} </a>'

        return o




class PackageItemTable(Table):
    classes = ['table', "table-dark"]

    name = Col('Name')
    creation_date = DateCol('Creation Date')
    creator_id = Col('Creator')
    creator = UserCol("User")
    # allow_sort = True
    tools = ToolCol("Tools")


    # def __init__(self,  items):
    #     super(PackageItemTable, self).__init__(items)
    #     if not current_user.is_anonymous:
    #         self.add_column("editable", BoolCol("Editable"))
    #         self.add_column("edit_url", EditCol("Edit", "blog.update", url_kwargs=dict(id='id') , button_attrs={"class": "btn btn-outline-danger"}))
    #

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('blog.index', sort=col_key, direction=direction)

# class="btn btn-outline-danger"










