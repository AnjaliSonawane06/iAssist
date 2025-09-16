# Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
from iassist.iassist.api.api import set_token_daily


class IAssistSupportConfigurations(Document):
	def validate(self):
		if self.is_multiple_users:
			self.username = None
			self.password = None
			self.api_key = None
			self.api_secret = None

			for user in self.ics_multi_user_details:
				username = user.username
				password = user.get_password("password") if user.password else None
				if username and password:
					check_login(self, username, password)
		else:
			self.ics_multi_user_details = []
			username = self.username
			password = self.get_password("password") if self.password else None
			if username and password:
				check_login(self, username, password)

def check_login(self,username, password):
		if not self.central_support_url:
			return
		try:
			login_url = f"{self.central_support_url}/api/method/login"
			response = requests.post(login_url, data={"usr": username, "pwd": password}, timeout=10)
			if response.status_code != 200:
				frappe.throw(f"Invalid Login Credentials for user {username}")
		except requests.exceptions.RequestException as e:
			frappe.throw(f"Could not connect to Central Support system: {e}")

@frappe.whitelist()
def generate_token_on_custom_button():
	return set_token_daily()