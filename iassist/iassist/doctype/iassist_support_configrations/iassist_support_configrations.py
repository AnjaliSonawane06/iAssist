# Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class IAssistSupportConfigrations(Document):
	pass

def check_active_plan(doc,method):
	if not doc:
		return
	