# ----------------------------------------------------------------
# Monkey patch the HTML generator for the db manager
# ----------------------------------------------------------------

# http://blog.dscpl.com.au/2015/03/safely-applying-monkey-patches-in-python.html
# https://pypi.python.org/pypi/wrapt


# from db_manager.db_plugins.html_elems import HtmlContent, HtmlSection, HtmlParagraph, HtmlList, HtmlTable, HtmlTableHeader, HtmlTableCol
#
# PGTableInfo.getTableInfo_original = PGTableInfo.getTableInfo
# PGVectorTableInfo.getTableInfo_original = PGTableInfo.getTableInfo
#
#
# def newGetTableInfo(self):
#     QgsMessageLog.logMessage("newGetTableInfo()")
#
#     ret = []
#
#     general_info = self.generalInfo()
#     if general_info is None:
#         pass
#     else:
#         ret.append(HtmlSection(QApplication.translate("DBManagerPlugin", 'General info'), general_info))
#
#     return ret
#
#
# # toHtml_backup = DatabaseInfo.toHtml
#
# PGVectorTableInfo.getTableInfo = newGetTableInfo
# PGTableInfo.getTableInfo = newGetTableInfo
# QgsMessageLog.logMessage("PGTableInfo.getTableInfo() patched.")

import wrapt
import inspect

from qgis.core import QgsMessageLog
from db_manager.db_plugins.postgis.info_model import PGTableInfo


def wrapper(wrapped, instance, args, kwargs):
    return "xxxx"

wrapt.wrap_function_wrapper(PGTableInfo, 'getTableInfo', wrapper)

# @wrapt.decorator
# def universal(wrapped, instance, args, kwargs):
#
#     from qgis.core import QgsMessageLog
#     QgsMessageLog.logMessage(str(inspect.isclass), "General")
#
#     if instance is None:
#         if inspect.isclass(wrapped):
#             # Decorator was applied to a class.
#             return wrapped(*args, **kwargs)
#         else:
#             # Decorator was applied to a function or staticmethod.
#             return wrapped(*args, **kwargs)
#     else:
#         if inspect.isclass(instance):
#             # Decorator was applied to a classmethod.
#             return wrapped(*args, **kwargs)
#         else:
#             # Decorator was applied to an instancemethod.
#             return wrapped(*args, **kwargs)
#
# PGTableInfo.getTableInfo = universal(PGTableInfo.getTableInfo)

# import inspect
# QgsMessageLog.logMessage(str(inspect), "Septima")
#
#
# def wrapper(wrapped, instance, args, kwargs):
#     QgsMessageLog.logMessage("@wrapper", "Septima")
#     return wrapped(*args, **kwargs)
#
# wrapt.wrap_function_wrapper('db_manager.db_plugins.postgis.info_model', 'PGTableInfo.getTableInfo', wrapper)
#
# QgsMessageLog.logMessage("PGTableInfo.getTableInfo() patched.", "Septima")