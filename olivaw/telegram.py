'''
Copyright 2016-2017 Benjamin Elder (BenTheElder) All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import json

from olivaw.compat import to_bytes, request, request_urlopen

def do_request(api_key, method, data):
    url = "https://api.telegram.org/bot"+api_key+"/"+method
    req = request.Request(url, data=to_bytes(json.dumps(data), 'utf-8'))
    req.add_header('Content-Type', 'application/json')
    with request_urlopen(req) as f:
        print(f.read().decode('utf-8'))

def set_webhook(api_key, url):
    do_request(api_key, "setWebhook", {"url": url})

def send_message(api_key, chat_id, text):
    data = {"chat_id": chat_id, "text": text}
    do_request(api_key, "sendMessage", data)

def send_reply(api_key, msg, text):
    send_message(api_key, msg.chat_id(), text)

class Chat(object):
    def __init__(self, json):
        self.id = json["id"]
        if isinstance(self.id, float):
            self.id = int(self.id)
        self.type = json["type"]
        self.title = json.get("title", None)
        self.username = json.get("username", None)
        self.first_name = json.get("first_name", None)
        self.last_name = json.get("last_name", None)
        self.all_members_are_administrators = json.get("all_members_are_administrators", None)

class User(object):
    def __init__(self, json):
        self.id = json["id"]
        if isinstance(self.id, float):
            self.id = int(self.id)
        self.first_name = json["first_name"]
        self.last_name = json.get("last_name", None)
        self.username = json.get("username", None)

class Message(object):
    def __init__(self, json):
        self.message_id = json["message_id"]
        if isinstance(self.message_id, float):
            self.message_id = int(self.message_id)
        self.text = json.get("text", None)
        from_json = json.get("from", None)
        self.from_user = None
        if from_json:
            self.from_user = User(from_json)
        chat = json.get("chat", None)
        self.chat = None
        if chat:
            self.chat = Chat(chat)
        self.date = json["date"]
        if isinstance(self.date, float):
            self.date = int(self.date)
        # TODO: remaining fields from:
        # https://core.telegram.org/bots/api/#message

    def chat_id(self):
        if self.chat:
            return self.chat.id
        if self.from_user:
            return self.from_user.id
        return None

class Update(object):
    def __init__(self, json):
        self.update_id = json["update_id"]
        if isinstance(self.update_id, float):
            self.update_id = int(self.update_id)
        msg = json.get("message", None)
        self.message = None
        if msg:
            self.message = Message(msg)
        edited_msg = json.get("edited_message", None)
        self.edited_message = None
        if edited_msg:
            self.edited_message = Message(edited_msg)
        # TODO: InlineQuery, ChosenInlineResult, CallbackQuery
