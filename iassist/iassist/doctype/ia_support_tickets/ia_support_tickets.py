# Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname,revert_series_if_last

class IASupportTickets(Document):
	def autoname(self):
		dot_series = f"IAT.-.#####"
		self.name = make_autoname(dot_series)

	def on_trash(self):
		dot_series = f"IAT.-.#####"
		revert_series_if_last(dot_series, self.name)
	
	def on_update(self):
		self.custom_sync_status = "Not Synced"

