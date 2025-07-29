import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests


        
def map_valid_fields(doctype, data):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name"]
    return {key: value for key, value in data.items() if key in valid_fieldnames}


def get_doc_payload(doctype, doc):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name", "doctype"]

    doc_dict = doc if isinstance(doc, dict) else doc.as_dict()

    return {key: value for key, value in doc_dict.items() if key in valid_fieldnames}


def get_create_url(doctype):
    if not doctype:
        return
    url=""
    if doctype=="Issue":
        url = "/api/method/icentral_support.icentral_support.api.issue.create_issue"
    elif doctype=="HD Ticket":
        url = "/api/method/icentral_support.icentral_support.api.hd_ticket.create_hd_ticket"
    return url



def get_update_url(doctype):
    if not doctype:
        return
    url=""
    if doctype=="Issue":
        url = "/api/method/icentral_support.icentral_support.api.issue.update_issue"
    elif doctype=="HD Ticket":
        url = "/api/method/icentral_support.icentral_support.api.hd_ticket.update_hd_ticket"
    return url


@frappe.whitelist(allow_guest=True)
def generate_token(data=None):
    data = frappe.request.get_json()

    username = data.get("username")
    password = data.get("password")
    login_url = f"{frappe.utils.get_url()}/api/method/login"
    response = requests.post(login_url, data={"usr": username, "pwd": password})
    if response.status_code == 200:
        user_doc = frappe.get_doc("User", username)
        user_doc.api_key = frappe.generate_hash(length=15)
        user_doc.api_secret = frappe.generate_hash(length=15)
        user_doc.save(ignore_permissions=True)
        
        return {
        "status": 200,
        "api_key": user_doc.api_key,
        "api_secret": user_doc.get_password("api_secret")
        }

    return {"status": 401, "message": "Invalid login"}

def set_token_daily():
   
    config = frappe.get_single("IAssist Support Configurations")
    base_url = config.central_support_url.rstrip("/")
    token_url = f"{base_url}/api/method/icentral_support.icentral_support.api.issue.generate_token"
  
    data_login = {"username": config.username, "password": config.get_password("password")}
    auth_response = requests.post(token_url, json=data_login) 
    
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        api_key = auth_data["message"]["api_key"]
        api_secret = auth_data["message"]["api_secret"]
        config.api_key = api_key
        config.api_secret= api_secret
        config.save()
