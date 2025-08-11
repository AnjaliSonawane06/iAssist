# Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests


class IAssistSupportConfigurations(Document):
	def validate(self):
		if self.central_support_url and self.username and self.password:
			username = self.username
			password = self.get_password("password")
			login_url = f"{self.central_support_url}/api/method/login"
			response = requests.post(login_url, data={"usr": username, "pwd": password})
			if not response.status_code == 200:
				frappe.throw("Invalid Login Credentials")