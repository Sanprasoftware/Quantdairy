from . import __version__ as app_version

app_name = "quantdairy"
app_title = "quantdairy"
app_publisher = "quantdairy"
app_description = "quantdairy"
app_email = "21pradipjadhav@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/quantdairy/css/quantdairy.css"
# app_include_js = "/assets/quantdairy/js/quantdairy.js"

# include js, css files in header of web template
# web_include_css = "/assets/quantdairy/css/quantdairy.css"
# web_include_js = "/assets/quantdairy/js/quantdairy.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "quantdairy/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "quantdairy.utils.jinja_methods",
#	"filters": "quantdairy.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "quantdairy.install.before_install"
# after_install = "quantdairy.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "quantdairy.uninstall.before_uninstall"
# after_uninstall = "quantdairy.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "quantdairy.utils.before_app_install"
# after_app_install = "quantdairy.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "quantdairy.utils.before_app_uninstall"
# after_app_uninstall = "quantdairy.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "quantdairy.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"quantdairy.tasks.all"
#	],
#	"daily": [
#		"quantdairy.tasks.daily"
#	],
#	"hourly": [
#		"quantdairy.tasks.hourly"
#	],
#	"weekly": [
#		"quantdairy.tasks.weekly"
#	],
#	"monthly": [
#		"quantdairy.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "quantdairy.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "quantdairy.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "quantdairy.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["quantdairy.utils.before_request"]
# after_request = ["quantdairy.utils.after_request"]

# Job Events
# ----------
# before_job = ["quantdairy.utils.before_job"]
# after_job = ["quantdairy.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"quantdairy.auth.validate"
# ]



fixtures = [
    {
        "doctype": "Server Script",
        "filters": [
            ["name", "in", ["Apply Deduction For Transporter", "Create Deduction Entry"]],
        ],
    },
]