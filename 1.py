import re
from zlapi import ZaloAPI, ZaloAPIException
from zlapi.models import *
import time
import threading
import json
import datetime
import subprocess
import random 
import requests
from PIL import Image, ImageDraw, ImageFont
import os
#admin:Hồ nhật trường (X)
#xoá 3 comment này là chó
#siuuuuu

class Honhattruong(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.idnguoidung = ['2077544135https06549669']
        self.target_thread_id = [
    '9172487604965494100',
    '5603605490720207067',
    '63697471448816637', 
    '950753419687970094',  
    '810585573676240160'
]
        self.sent_users = set()  
        self.anti_spam_enabled = False  
        self.message_log = {}  
        self.spam_threshold = 5  
        self.excluded_user_ids = ['207754413506549669']  
        self.spamming = False
        self.spam_thread = None
        
        
        self.name_change_thread = None
        self.isUndoLoop = False
        self.xoatn_mode = False
        self.dangky_file = 'tt.txt'
        self.codes = {
            'hzzmonet': 9999999,
            'tanthu': 555555555555555
        }
        self.vip_keys_db = {
            "hzzmonet": {"user_id": None, "functions": 0, "assigned_time": None},
            "tynecotton2": {"user_id": None, "functions": 0, "assigned_time": None},
            "selenophile": {"user_id": None, "functions": 0, "assigned_time": None}
        }
        self.transfer_messages = [
            "Vui lòng chuyển khoản 10k vào số tài khoản 0364990728 - Mb.",
            "Xin hãy nạp 10k vào số 0364990728 - Mb để mua key VIP.",
            "Chuyển 10k vào số điện thoại 0364990728 - Mb để kích hoạt key.",
            "Để mua key VIP, vui lòng nạp 10k vào số 0364990728 - Mb."
        ]
        self.quanli_file = 'quanli.json'
        self.load_key_data()
        self.admin_key = '11009922'
        self.is_admin = False
        self.last_sms_times = {}
        self.random_users = set()  
        self.delete_links = False
        self.reo_spamming = False  
        self.reo_spam_thread = None
        self.Group = False
        self.color_list = [
            "#FFFFFF", "#00FF00", "#EEEEEE", "#DDDDDD", "#CCCCCC", 
            "#BBBBBB", "#AAAAAA", "#999999", "#888888", "#777777", 
            "#666666", "#555555", "#444444", "#333333", "#222222", 
            "#111111", "#000000", "#FF0000", "#EE0000", "#DD0000", 
            "#CC0000", "#BB0000", "#AA0000", "#990000", "#880000", 
            "#770000", "#660000", "#550000", "#440000", "#330000", 
            
        ]
        self.messages_to_delete = []  
        self.admin_file = 'admin.json'  
        self.start_time = datetime.datetime.now()  
        self.banned_word_removal_enabled = False  
        self.banned_words = set([  
            "địt", "lồn", "lol", "đm", "cc", "lon", "đmm", "dm", "dmm", "dit", "cac", "cặc",
            "Lmm", "Óc lợn", "Óc bò", "Djtme", "Nguuuuuuu như ch ó", "Lmm", "dái", "bướm",
            "lỗ nhị", "đéo", "đít", "sex", "chịch", "vú", "đụ", "Dog", "Kẹc", "bím",
            "mẹ mày", "mẹ m", "cha m", "cha mày", "dcu", "đcu", "đcm", "đc", "cmm", "cmm", 
            "cc", "cc", "cặc", "đít", "dcm", "địt"
        ])

    def load_admins(self):
        try:
            with open(self.admin_file, 'r') as admin_file:
                admin_data = json.load(admin_file)
                return set(admin_data.get('idadmin', []))
        except FileNotFoundError:
            return set()
    
    

    def save_admins(self, admins):
        with open(self.admin_file, 'w') as admin_file:
            json.dump({'idadmin': list(admins)}, admin_file)
    def load_registered_users(self):
        try:
            with open(self.dangky_file, 'r', encoding='utf-8') as file:
                return {line.split(',')[0]: (line.strip().split(',')[1], float(line.strip().split(',')[2])) for line in file.readlines() if line.strip()}
        except FileNotFoundError:
            return {}
    
    def load_key_data(self):
        try:
            with open(self.quanli_file, 'r') as file:
                self.vip_keys_db = json.load(file)
        except FileNotFoundError:
            self.vip_keys_db = {
                "hzzmonet": {"user_id": None, "functions": 0, "assigned_time": None},
                "tynecotton2": {"user_id": None, "functions": 0, "assigned_time": None},
                "selenophile": {"user_id": None, "functions": 0, "assigned_time": None}
            }

    def save_key_data(self):
        with open(self.quanli_file, 'w') as file:
            json.dump(self.vip_keys_db, file)

    def check_vip_key(self, user_id):
        for key, data in self.vip_keys_db.items():
            if data["user_id"] == user_id:
                current_time = time.time()
                if data["assigned_time"] is not None:
                    if (current_time - data["assigned_time"]) < (2 * 24 * 60 * 60):
                        return data
                return None
        return None

    def assign_key_to_user(self, user_id, key):
        for data in self.vip_keys_db.values():
            if data["user_id"] == user_id:
                return False
        if key in self.vip_keys_db and self.vip_keys_db[key]["user_id"] is None:
            self.vip_keys_db[key]["user_id"] = user_id
            self.vip_keys_db[key]["assigned_time"] = time.time()
            self.vip_keys_db[key]["functions"] = 0
            self.save_key_data()
            return True
        return False
    def save_registered_user(self, user_id, user_name):
        with open(self.dangky_file, 'a', encoding='utf-8') as file:
            file.write(f"{user_id},{user_name},500000000\n")
    

    def update_user_balance(self, user_id, new_balance):
        users = self.load_registered_users()
        if user_id in users:
            user_name = users[user_id][0]
            with open(self.dangky_file, 'w', encoding='utf-8') as file:
                for uid, (name, balance) in users.items():
                    if uid == user_id:
                        file.write(f"{uid},{name},{new_balance}\n")  
                    else:
                        file.write(f"{uid},{name},{balance}\n")  
                        
    
    def load_mutenguoidung(self):
        try:
            with open('mute.json', 'r') as mute_file:
                mute_config = json.load(mute_file)
                return set(mute_config.get('mutenguoidung', []))
        except FileNotFoundError:
            return set()

    def save_mutenguoidung(self, mutenguoidung):
        with open('mute.json', 'w') as mute_file:
            json.dump({'mutenguoidung': list(mutenguoidung)}, mute_file)
    
     
    def send_private_message_to_user(self, user_id, random_data):
        try:
            message_text = "thông tin nội dung:\n" + "\n".join(random_data)
            private_message = Message(text=message_text)
            self.send(private_message, thread_id=user_id, thread_type=ThreadType.USER)
        except Exception as e:
            print(f"🚫 Lỗi khi gửi tin nhắn: {e}")

    def add_id_to_used_list(self, user_id):
        with open('id.txt', 'a') as id_file:
            id_file.write(user_id + "\n")

    

    def send_lq_accounts(self, author_id, so_luong, thread_id, thread_type, message_object):
        try:
            with open('lq.txt', 'r') as file:
                lines = file.readlines()
            if so_luong > len(lines):
                self.replyMessage(Message(text="Không đủ tài khoản trong file."), message_object, thread_id, thread_type)
                return
            random_accounts = random.sample(lines, so_luong)
            self.send_private_message_to_user(author_id, [account.strip() for account in random_accounts])
            remaining_accounts = [line for line in lines if line not in random_accounts]
            with open('lq.txt', 'w') as file:
                file.writelines(remaining_accounts)
            self.replyMessage(Message(text=f"Đã gửi {so_luong} tài khoản liên quân cho bạn."), message_object, thread_id, thread_type)
        except Exception as e:
            self.replyMessage(Message(text=f"Đã xảy ra lỗi: {e}"), message_object, thread_id, thread_type)
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        print(f"\033[32m{message} \033[39m|\033[31m {author_id} \033[39m|\033[33m {thread_id}\033[0m\n")
        content = message_object.content if message_object and hasattr(message_object, 'content') else ""
        if not isinstance(message, str):
            print(f"{type(message)}")
            return
        
        
        
         
        
        

        message_text = message  
        
        idadmin = self.load_admins()
        if message.startswith(".ask"):
            parts = message.split(' ', 1)
            if len(parts) < 2:
                error_text = "🚫 Vui Lòng nhập nội dung😒."
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="font", size="14", auto_format=False),
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            user_message = parts[1]
            response = self.ask_api(user_message)
            
            style_response = MultiMsgStyle([
                MessageStyle(offset=0, length=6, style="color", color="#00ff00", auto_format=False),
                MessageStyle(offset=6, length=len(response), style="font", size="14", auto_format=False),
            ])

            self.replyMessage(Message(text=f"Response: {response}", style=style_response), message_object, thread_id=thread_id, thread_type=thread_type)
        if isinstance(content, str) and content.lower().startswith((".sdtvip")):
            
            parts = content.split()
            if len(parts) == 1:
                self.replyMessage(Message(text='🚫 Vui lòng nhập số điện thoại sau lệnh .\n'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            attack_phone_number = parts[1]
            if not attack_phone_number.isnumeric() or len(attack_phone_number) != 10:
                self.replyMessage(Message(text='❌ Số điện thoại không hợp lệ! Vui lòng nhập đúng số.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            if attack_phone_number in ['113', '911', '114', '115']:
                self.replyMessage(Message(text="⛔ Số này không thể spam."), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            current_time = datetime.datetime.now()
            if author_id in self.last_sms_times:
                last_sent_time = self.last_sms_times[author_id]
                elapsed_time = (current_time - last_sent_time).total_seconds()
                if elapsed_time < 120:
                    self.replyMessage(Message(text="⏳ vui lòng chờ 120s và thử lại!"), message_object, thread_id=thread_id, thread_type=thread_type)
                    return
            self.last_sms_times[author_id] = current_time
            file_path1 = os.path.join(os.getcwd(), "111.py")
            process = subprocess.Popen(["python", file_path1, attack_phone_number, "7"])
            now = datetime.datetime.now()
            time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            masked_phone_number = f"{attack_phone_number[:3]}***{attack_phone_number[-3:]}"
            msg_content = f'''@Member

     sms và call v2
 
 ᴘʜᴏɴᴇ 📞:
   ├─> {masked_phone_number} 
   ├─────────────⭔
 ᴛɪᴍᴇ ⏰:
   ├─> {time_str} 
   ├─────────────⭔
 ᴄᴏᴏʟᴅᴏᴡɴ 👾:
   ├─> 120
   ├─────────────⭔
 ᴀᴅᴍɪɴ:
   ├─> ʜɴᴛ ᴛᴏᴏʟ hack by X
   └─────────────⭔

    '''
            mention = Mention(author_id, length=len("@Member"), offset=0)
            color_green = MessageStyle(style="color", color="#4caf50", length=300, offset=0, auto_format=False)
            style = MultiMsgStyle([color_green])
            sms_img = "sms.png"
            self.replyMessage(Message(text=msg_content, style=style, mention=mention), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith("jj"):
            self.replyMessage(
                Message(text=f"ID nhóm hiện tại là: {thread_id}"),
                message_object,
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        if message.startswith("admin"):
            

            admin_info = (
                "👤 Thông Tin Admin 👤\n"
                "-----------------------------------\n"
                "👤 Tên: HzzMonet\n"
                "📧 Email: 8a3.18.nguyenanhkiet@gmail.com\n"
                "📚 Kỹ Năng:\n"
                "   - Có vấn đề \n"
                "📖 Đang học:\n"
                "   - Trường C \n"
                "🌐 Mục Đích:\n"
                "   - Just for fun \n"
            )
            
            self.replyMessage(Message(text=admin_info), message_object, thread_id=thread_id, thread_type=thread_type)
            return
        

        
        


        
        if self.anti_spam_enabled:
            self.log_message(author_id, thread_id, message_object)
        
        if message.startswith(".buy"):
            transfer_message = random.choice(self.transfer_messages)
            self.send(Message(text=transfer_message), thread_id=author_id, thread_type=ThreadType.USER)

        elif message.startswith(".nhapkey"):
            command_parts = message.split(" ", 1)

            if len(command_parts) < 2:
                self.replyMessage(
                    Message(text="Vui lòng nhập mã key của bạn sau lệnh .nhapkey."),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
                return

            key_input = command_parts[1].strip()

            if self.assign_key_to_user(author_id, key_input):
                self.replyMessage(
                    Message(text=f"Bạn đã nhập mã key thành công: {key_input}."),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
            else:
                self.replyMessage(
                    Message(text="Mã key không hợp lệ hoặc bạn đã có một key VIP khác."),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )

        elif message.startswith(".shop"):
            command_parts = message.split(" ", 1)

            if len(command_parts) < 2:
                self.replyMessage(
                    Message(
                        text="Vui lòng nhập nội dung VIP cần mua!\nCác nội dung VIP bao gồm:\n    tu_dong_reg_nhom\n    tu_dong_ket_ban\n    .buy\nBạn cần mua key để truy cập."
                    ),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
                return

            requested_vip_content = command_parts[1].strip().lower()

            vip_contents = {
                'tu_dong_ket_ban': "https://www.mediafire.com/file/o4x792f69ya7ebt/bb.py/file",
                'tu_dong_reg_nhom': "https://www.mediafire.com/file/9qjudrpigojl26c/taonhom.py/file",
            }

            if requested_vip_content in vip_contents:
                user_vip_data = self.check_vip_key(author_id)

                if user_vip_data:
                    if user_vip_data["functions"] < 2:
                        self.replyMessage(
                            Message(text="Đang lấy nội dung VIP 🌀..."),
                            message_object,
                            thread_id=thread_id,
                            thread_type=thread_type
                        )
                        
                        time.sleep(2)

                        message_text = f"Thông tin nội dung VIP {requested_vip_content}:\n{vip_contents[requested_vip_content]}"
                        private_message = Message(text=message_text)
                        
                        self.send(private_message, thread_id=author_id, thread_type=ThreadType.USER)
                        
                        self.replyMessage(
                            Message(text=f"Nội dung VIP '{requested_vip_content}' đã được gửi riêng!"),
                            message_object,
                            thread_id=thread_id,
                            thread_type=thread_type
                        )

                        user_vip_data["functions"] += 1
                        self.save_key_data()
                    else:
                        self.replyMessage(
                            Message(
                                text="Bạn đã sử dụng đủ chức năng của key VIP này. Không thể sử dụng thêm."
                            ),
                            message_object,
                            thread_id=thread_id,
                            thread_type=thread_type
                        )
                else:
                    self.replyMessage(
                        Message(
                            text="Key VIP của bạn đã hết hạn hoặc không tồn tại. Vui lòng mua key VIP để truy cập.\nSử dụng lệnh /buy để mua key."
                        ),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
        
        
        if message.startswith(".share"):
                command_parts = message.split(" ", 1)
                
                if len(command_parts) < 2:
                    self.replyMessage(
                        Message(
                            text="Vui lòng nhập nội dung cần share!\nCó 5 nội dung:\n1    ask\n2    war\n3    khanh`\n4    business\n5    doimau"
                        ),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
                    return
                
                requested_content = command_parts[1].strip().lower()
                
                contents = {
                    'ask': "https://www.mediafire.com/file/get568ui534ut02/ask.py/file",
                    'war': "https://www.mediafire.com/file/3nh0w2rfm9vny3h/botzl.zip/file",
                    'khanh': "https://www.mediafire.com/file/3nh0w2rfm9vny3h/botzl.zip/file",
                    'business':"https://www.mediafire.com/file/mzykdneljpbfenu/tudong.py/file",
                    'doimau':"https://www.mediafire.com/file/jgpci3cl77g8sy7/doimau.py/file",
                }

                if requested_content in contents:
                    self.replyMessage(
                        Message(text="Đang lấy nội dung🌀..."),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
                    
                    time.sleep(2)

                    message_text = f"Thông tin nội dung của lệnh {requested_content}:\n{contents[requested_content]}"
                    private_message = Message(text=message_text)
                    
                    self.send(private_message, thread_id=author_id, thread_type=ThreadType.USER)
                    
                    self.replyMessage(
                        Message(text=f"Nội dung '{requested_content}' đã được gửi riêng!"),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
                else:
                    self.replyMessage(
                        Message(text="Nội dung không hợp lệ. Vui lòng chọn 'ask' hoặc '!war'."),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
        if message_text.startswith("oncheck"):
            if author_id not in idadmin:
                self.replyMessage(Message(text="Bạn không có quyền thực hiện điều này!"), message_object, thread_id, thread_type)
                return
            self.banned_word_removal_enabled = True
            self.replyMessage(Message(text="Chức năng lọc từ cấm đã được bật!"), message_object, thread_id, thread_type)

        if message_text.startswith("offcheck"):
            if author_id not in idadmin:
                self.replyMessage(Message(text="Bạn không có quyền thực hiện điều này!"), message_object, thread_id, thread_type)
                return
            self.banned_word_removal_enabled = False
            self.replyMessage(Message(text="Chức năng lọc từ cấm đã được tắt!"), message_object, thread_id, thread_type)

        if self.banned_word_removal_enabled:
            cleaned_message = self.remove_banned_words(message_text)
            if cleaned_message != message_text:
                self.replyMessage(Message(text=""), message_object, thread_id, thread_type)
                self.deleteGroupMsg(message_object.msgId, message_object.uidFrom, message_object.cliMsgId, thread_id)
                print("Tin nhắn đã bị xóa do chứa từ cấm.")
                return
        if "HzzMonet" in message.lower():
            mention = Mention(uid=author_id, offset=0, length=len("HzzMonet"))  
            reply_message = Message(text=f"=) , đẹp trai nhất🥴?", mention=mention)
            self.send(reply_message, thread_id=thread_id, thread_type=thread_type)
            return

        if "lồn" in message.lower():
            mention = Mention(uid=author_id, offset=0, length=len("lồn"))  
            reply_message = Message(text=f"=) văn minh lên con chó?", mention=mention)
            self.send(reply_message, thread_id=thread_id, thread_type=thread_type)
            return

        if message.lower() == "hi":
            mention = Mention(uid=author_id, offset=0, length=len("hi"))  
            reply_message = Message(text=f"Hi, chúc bạn một ngày tốt lành!", mention=mention)
            self.send(reply_message, thread_id=thread_id, thread_type=thread_type)
            return

        
        if "mn ơi" in message.lower():
            mention = Mention(uid=author_id, offset=0, length=len("hi"))  
            reply_message = Message(text=f"Hi , xin chào! Tôi có thể giúp gì cho bạn?", mention=mention)
            self.send(reply_message, thread_id=thread_id, thread_type=thread_type)
            return
        
        
        
        
        if message.startswith(".kick"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            mentions = message_object.mentions
            if not mentions:
                self.replyMessage(Message(text='🚫 Bạn cần đề cập ít nhất một người dùng để kick.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            kicked_users = []
            for mention in mentions:
                mentioned_user_id = mention['uid']
                
                if mentioned_user_id not in self.excluded_user_ids:
                    try:

                        self.kickUsersFromGroup([mentioned_user_id], thread_id)
                        kicked_users.append(str(mentioned_user_id))
                    except Exception as e:
                        self.replyMessage(Message(text=f'🚫 Có lỗi khi kick người dùng {mentioned_user_id}: {str(e)}'), message_object, thread_id=thread_id, thread_type=thread_type)
                else:
                    self.replyMessage(Message(text=f'🚫 Không thể kick {mentioned_user_id} vì người này nằm trong danh sách loại trừ.'), message_object, thread_id=thread_id, thread_type=thread_type)

            if kicked_users:
                kicked_list = ", ".join(kicked_users)
                self.replyMessage(Message(text=f'✅ Đã kick người dùng: {kicked_list}'), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                self.replyMessage(Message(text='🚫 Không có ai bị kick.'), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".dt"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='?? Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            new_group_name = message[4:].strip()  
            if not new_group_name:
                self.replyMessage(Message(text='🚫 Bạn cần cung cấp tên nhóm mới.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            group_id = thread_id  
            result = self.changeGroupName(new_group_name, group_id)
            if result and isinstance(result, Group):
                self.replyMessage(Message(text=f'✅ Đã đổi tên nhóm thành: {new_group_name}'), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                self.replyMessage(Message(text='🚫 Có lỗi khi đổi tên nhóm.'), message_object, thread_id=thread_id, thread_type=thread_type)
        if message.startswith(".random"):
            if author_id in self.random_users:
                self.replyMessage(Message(text="🚫 Bạn đã sử dụng lệnh random rồi!"), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            parts = message.split()
            
            if len(parts) != 2 or not parts[1].isdigit():
                self.replyMessage(Message(text="🚫 Vui lòng cung cấp số lượng hợp lệ (1-150 )."), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            quantity = int(parts[1])
            if 1 <= quantity <= 50:
                random_data = self.get_random_data(quantity)
                if random_data:
                    
                    self.send_private_message_to_user(author_id, random_data)
                    
                    self.random_users.add(author_id)
                    
                    self.send(Message(text="✅ hãy kiểm tra tin nhắn riêng ."), thread_id=thread_id, thread_type=thread_type)
                else:
                    self.replyMessage(Message(text="🚫 File rỗng hoặc không thể đọc dữ liệu."), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                self.replyMessage(Message(text="🚫 Số lượng phải nằm trong khoảng 1 or 50"), message_object, thread_id=thread_id, thread_type=thread_type)
        if content.startswith('.lq'):
            parts = content.split()
            if len(parts) < 2:
                self.replyMessage(Message(text="Vui lòng nhập số lượng tài khoản cần lấy sau lệnh .lq"), message_object, thread_id, thread_type)
                return
            
            try:
                so_luong = int(parts[1])
                if 1 <= so_luong <= 100:
                    self.add_id_to_used_list(author_id)  
                    self.send_lq_accounts(author_id, so_luong, thread_id, thread_type, message_object)
                else:
                    self.replyMessage(Message(text="Số lượng phải từ 1 đến 100."), message_object, thread_id, thread_type)
            except ValueError:
                self.replyMessage(Message(text="Số lượng không hợp lệ."), message_object, thread_id, thread_type)
        
            
        if isinstance(content, str) and content.lower().startswith((".sdt")):
            
            parts = content.split()
            if len(parts) == 1:
                self.replyMessage(Message(text='🚫 Vui lòng nhập số điện thoại sau lệnh .sdt \n'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            attack_phone_number = parts[1]
            if not attack_phone_number.isnumeric() or len(attack_phone_number) != 10:
                self.replyMessage(Message(text='❌ Số điện thoại không hợp lệ! Vui lòng nhập đúng số.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            if attack_phone_number in ['113', '911', '114', '115']:
                self.replyMessage(Message(text="⛔ Số này không thể spam."), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            current_time = datetime.datetime.now()
            if author_id in self.last_sms_times:
                last_sent_time = self.last_sms_times[author_id]
                elapsed_time = (current_time - last_sent_time).total_seconds()
                if elapsed_time < 120:
                    self.replyMessage(Message(text="⏳ vui lòng chờ 120s và thử lại!"), message_object, thread_id=thread_id, thread_type=thread_type)
                    return
            self.last_sms_times[author_id] = current_time
            file_path1 = os.path.join(os.getcwd(), "smsv2.py")
            process = subprocess.Popen(["python", file_path1, attack_phone_number, "7"])
            now = datetime.datetime.now()
            time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            masked_phone_number = f"{attack_phone_number[:3]}***{attack_phone_number[-3:]}"
            msg_content = f'''@Member

    bot spam sms và call
 
 ᴘʜᴏɴᴇ 📞:
   ├─> {masked_phone_number} 
   ├─────────────⭔
 ᴛɪᴍᴇ ⏰:
   ├─> {time_str} 
   ├─────────────⭔
 ᴄᴏᴏʟᴅᴏᴡɴ 👾:
   ├─> 120
   ├─────────────⭔
 ᴀᴅᴍɪɴ:
   ├─> ʜɴᴛ ᴛᴏᴏʟ
   └─────────────⭔

    '''
            mention = Mention(author_id, length=len("@Member"), offset=0)
            color_green = MessageStyle(style="color", color="#4caf50", length=300, offset=0, auto_format=False)
            style = MultiMsgStyle([color_green])
            sms_img = "sms.png"
            self.replyMessage(Message(text=msg_content, style=style, mention=mention), message_object, thread_id=thread_id, thread_type=thread_type)
        
        if message.startswith(".tb"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            parts = message.split(' ', 1)
            if len(parts) < 2:
                self.replyMessage(Message(text='?? Vui lòng cung cấp nội dung.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            success_text = parts[1]
            text_length = len(success_text)

            
            styles = []
            if text_length > 0:
                styles.append(MessageStyle(offset=0, length=min(10, text_length), style="color", color="#ffcc00", auto_format=False))  # Màu vàng cho 10 ký tự đầu
            if text_length > 10:
                styles.append(MessageStyle(offset=10, length=min(10, text_length-10), style="color", color="#28a745", auto_format=False))  # Màu xanh lá cho 10 ký tự tiếp theo
            if text_length > 20:
                styles.append(MessageStyle(offset=20, length=min(7, text_length-20), style="color", color="#007bff", auto_format=False))  # Màu xanh dương cho 7 ký tự cuối

            style_success = MultiMsgStyle(styles)

            
            mention = Mention(uid='-1', offset=0, length=0)  

            
            self.send(
                Message(text=success_text, mention=mention, style=style_success),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return

        
        
        if message.startswith(".rs"):
        	
            parts = message.split(' ', 1)
            if len(parts) < 2:
                self.replyMessage(Message(text='🚫 Vui lòng cung cấp nội dung để phản hồi!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            content_to_reply = parts[1]          
            mention = Mention(uid=author_id, offset=0, length=len(content_to_reply))
            reply_message = Message(text=content_to_reply, mention=mention)
            self.replyMessage(reply_message, message_object, thread_id=thread_id, thread_type=thread_type)
            return
        if message.startswith(".dltt"):
            parts = message.split(" ")
            if len(parts) != 2:
                self.replyMessage(Message(text='🚫 Vui lòng cung cấp đường dẫn video TikTok.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            video_url = parts[1]
            self.download_tiktok_video(video_url, message_object, thread_id, thread_type)
        if message.startswith(".info"):
            self.replyMessage(Message(text=f'ID của bạn: {author_id}'), message_object, thread_id=thread_id, thread_type=thread_type)
        if message.startswith(".gr"):
            self.replyMessage(Message(text=f'ID nhóm của bạn: {thread_id}'), message_object, thread_id=thread_id, thread_type=thread_type)
        
    
        
        if message.startswith(".ghepdoi"):
            mentions = message_object.mentions
            if len(mentions) < 2:
                self.replyMessage(Message(text='🚫 Vui lòng đề cập đến hai người dùng.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            user_id_1 = mentions[0]['uid']
            user_name_1 = mentions[0]['name']  
            user_id_2 = mentions[1]['uid']
            user_name_2 = mentions[1]['name']  

            
            compatibility_percentage = random.randint(0, 100)

            
            if compatibility_percentage < 50:
                response = f"❤️ {user_name_1} và {user_name_2} không hợp nhau lắm đâu! Tỷ lệ hợp nhau chỉ {compatibility_percentage}%. ❤️"
            elif compatibility_percentage >= 50 and compatibility_percentage < 80:
                response = f"❤️ {user_name_1} và {user_name_2} hợp nhau đấy! Tỷ lệ hợp nhau là {compatibility_percentage}%. ❤️"
            else:  
                response = f"❤️ {user_name_1} và {user_name_2} hoàn hảo cho nhau! Tỷ lệ hợp nhau lên tới {compatibility_percentage}%. ❤️"

            
            private_message_1 = Message(text=response)
            private_message_2 = Message(text=response)

            self.send(private_message_1, thread_id=user_id_1, thread_type=ThreadType.USER)
            self.send(private_message_2, thread_id=user_id_2, thread_type=ThreadType.USER)
        if message.startswith(".gay"):
            if not message_object.mentions:
                self.replyMessage(Message(text='🚫 Vui lòng đề cập đến một người dùng.'), message_object, thread_id=thread_id, thread_type=thread_id)
            else:
                user_id = message_object.mentions[0]['uid']
                probability = random.randint(0, 100)  
                response = f"Khả năng <@{user_id}> bị gay là {probability}%."
                mention = Mention(user_id, length=len(f"<@{user_id}>"), offset=response.index(f"<@{user_id}>"))
                self.replyMessage(Message(text=response, mention=mention), message_object, thread_id=thread_id, thread_type=thread_type)
        if message.startswith(".cannang"):
            if not message_object.mentions:
                self.replyMessage(Message(text='🚫 Vui lòng đề cập đến một người dùng.'), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                user_id = message_object.mentions[0]['uid']
                weight = random.randint(30, 100)  

                if weight < 50:
                    response = f"Cân nặng của <@{user_id}> là {weight} kg - Củi khô."
                else:
                    response = f"Cân nặng của <@{user_id}> là {weight} kg - Béo vai lon."

                mention = Mention(user_id, length=len(f"<@{user_id}>"), offset=response.index(f"<@{user_id}>"))
                self.replyMessage(Message(text=response, mention=mention), message_object, thread_id=thread_id, thread_type=thread_type)

            
        if message.startswith(".mau"):
            parts = message.split(' ', 1)
            if len(parts) < 2:
                self.replyMessage(Message(text='🚫 Vui lòng cung cấp nội dung cần tô màu.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            content_to_color = parts[1].strip()
            random_color = random.choice(self.color_list)  
            style = MultiMsgStyle([
                MessageStyle(offset=0, length=len(content_to_color), style="color", color=random_color, auto_format=False),
            ])
            self.replyMessage(Message(text=content_to_color, style=style), message_object, thread_id=thread_id, thread_type=thread_type)
        
        if message.startswith(".reo"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if self.reo_spamming:  
                self.replyMessage(Message(text='🚫 Reo spam đã chạy!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            mentions = message_object.mentions
            if not mentions:
                self.replyMessage(Message(text='🚫 Bạn cần đề cập một người dùng.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            mentioned_user_id = mentions[0]['uid']

            self.reo_spamming = True
            self.reo_spam_thread = threading.Thread(target=self.reo_spam_message, args=(mentioned_user_id, thread_id, thread_type))
            self.reo_spam_thread.start()

        if message.startswith(".stopreo"):
            if not self.reo_spamming:
                self.replyMessage(Message(text='🚫 Không có spam nào đang chạy!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            self.reo_spamming = False
            if self.reo_spam_thread is not None:
                self.reo_spam_thread.join()
            self.replyMessage(Message(text='✅ Đã dừng spam reo.'), message_object, thread_id=thread_id, thread_type=thread_type)
        
        
        if message.startswith(".anime"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            try:
                response = requests.get("https://apiquockhanh.click/images/anime")
                response.raise_for_status()

                image_data = response.json()
                image_url = image_data.get('url', '')

                if image_url:
                    image_response = requests.get(image_url)
                    
                    if image_response.status_code == 200:
                        image_filename = 'temp_anime_image.jpeg'
                        with open(image_filename, 'wb') as image_file:
                            image_file.write(image_response.content)

                        self.sendLocalImage(image_filename, thread_id=thread_id, thread_type=thread_type)

                        success_text = "Tải ảnh thành công!"
                        style_success = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(success_text), style="color", color="#00ff00", auto_format=False), 
                        ])
                        self.replyMessage(Message(text=success_text, style=style_success), message_object, thread_id=thread_id, thread_type=thread_type)

                        os.remove(image_filename)
                    else:
                        error_text = "🚫 Không thể tải hình ảnh, vui lòng thử lại sau."
                        style_error = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                        ])
                        self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
                else:
                    error_text = "🚫 Không tìm thấy hình ảnh."
                    style_error = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                    ])
                    self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

            except requests.exceptions.RequestException as e:
                error_text = f"🚫 Lỗi khi gọi API: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
            except Exception as e:
                error_text = f"🚫 Đã xảy ra lỗi: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
                
                
         
            

            
        
        
   
        if message.startswith(".reo"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if self.reo_spamming:  
                self.replyMessage(Message(text='🚫 Reo spam đã chạy!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            mentions = message_object.mentions
            if not mentions:
                self.replyMessage(Message(text='🚫 Bạn cần đề cập một người dùng.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            mentioned_user_id = mentions[0]['uid']

            self.reo_spamming = True
            self.reo_spam_thread = threading.Thread(target=self.reo_spam_message, args=(mentioned_user_id, thread_id, thread_type))
            self.reo_spam_thread.start()

        if message.startswith(".stopreo"):
        	
            if not self.reo_spamming:
                self.replyMessage(Message(text='🚫 Không có spam nào đang chạy!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            self.reo_spamming = False
            if self.reo_spam_thread is not None:
                self.reo_spam_thread.join()
            self.replyMessage(Message(text='✅ Đã dừng spam reo.'), message_object, thread_id=thread_id, thread_type=thread_type)

        

        if getattr(self, 'banned_word_removal_enabled', False):  
            cleaned_message = self.remove_banned_words(message_text)
            if cleaned_message != message_text:           
                self.replyMessage(Message(text="=)"), message_object, thread_id, thread_type)

                self.deleteGroupMsg(message_object.msgId, message_object.uidFrom, message_object.cliMsgId, thread_id)
                print("Tin nhắn đã bị xóa do chứa từ cấm.")

    



        
        if self.isUndoLoop:
            if author_id in idadmin:
                return
            mutenguoidung = self.load_mutenguoidung()
            if author_id in mutenguoidung:
                self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)

        
        

        
                

            
        
            
            
        
    
    

        if message.startswith("All"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            success_text = "carrot đẹp trai - success - hehe"
            style_success = MultiMsgStyle([
                MessageStyle(offset=0, length=10, style="color", color="#ffcc00", auto_format=False),  
                MessageStyle(offset=10, length=10, style="color", color="#28a745", auto_format=False),  
                MessageStyle(offset=20, length=7, style="color", color="#007bff", auto_format=False),  
            ])

            mention = Mention(uid='-1', offset=0, length=0)
            self.send(Message(text=success_text, mention=mention, style=style_success), thread_id=thread_id, thread_type=thread_type)

        
 
        if message.startswith(".uptime"):
            current_time = datetime.datetime.now()
            uptime = current_time - self.start_time
            days, seconds = uptime.days, uptime.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            start_time_str = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            
            uptime_message = (
                f"Bot đã hoạt động được {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây.\n"
                f"Khởi động từ: {start_time_str}"
            )
            
            style_uptime = MultiMsgStyle([
                MessageStyle(offset=0, length=21, style="font", size="14", auto_format=False),
                MessageStyle(offset=21, length=len(uptime_message) - 21, style="color", color="#2196f3", auto_format=False),
            ])

            self.replyMessage(Message(text=uptime_message, style=style_uptime), message_object, thread_id=thread_id, thread_type=thread_type)

                    
                    
             
        if message.startswith(".sexy"):
   
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            try:
                response = requests.get("https://apiquockhanh.click/video/girlsexy")
                response.raise_for_status()

                image_data = response.json()
                image_url = image_data.get('url', '')

                if image_url:
                    image_response = requests.get(image_url)
                    
                    if image_response.status_code == 200:
                        image_filename = 'temp_du_image.jpeg'
                        with open(image_filename, 'wb') as image_file:
                            image_file.write(image_response.content)

                        self.sendLocalImage(image_filename, thread_id=thread_id, thread_type=thread_type)

                        success_text = "Tải ảnh thành công!"
                        style_success = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(success_text), style="color", color="#00ff00", auto_format=False),  
                        ])
                        self.replyMessage(Message(text=success_text, style=style_success), message_object, thread_id=thread_id, thread_type=thread_type)

                        os.remove(image_filename)
                    else:
                        error_text = "🚫 Không thể tải hình ảnh, vui lòng thử lại sau."
                        style_error = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                        ])
                        self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
                else:
                    error_text = "🚫 Không tìm thấy hình ảnh."
                    style_error = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False), 
                    ])
                    self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

            except requests.exceptions.RequestException as e:
                error_text = f"🚫 Lỗi khi gọi API: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
            except Exception as e:
                error_text = f"🚫 Đã xảy ra lỗi: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False), 
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".du"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            try:
                response = requests.get("https://apiquockhanh.click/images/du")
                response.raise_for_status()

                image_data = response.json()
                image_url = image_data.get('url', '')

                if image_url:
                    image_response = requests.get(image_url)
                    
                    if image_response.status_code == 200:
                        image_filename = 'temp_du_image.jpeg'
                        with open(image_filename, 'wb') as image_file:
                            image_file.write(image_response.content)

                        self.sendLocalImage(image_filename, thread_id=thread_id, thread_type=thread_type)

                        success_text = "Tải ảnh thành công!"
                        style_success = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(success_text), style="color", color="#00ff00", auto_format=False), 
                        ])
                        self.replyMessage(Message(text=success_text, style=style_success), message_object, thread_id=thread_id, thread_type=thread_type)

                        os.remove(image_filename)
                    else:
                        error_text = "🚫 Không thể tải hình ảnh, vui lòng thử lại sau."
                        style_error = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                        ])
                        self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
                else:
                    error_text = "🚫 Không tìm thấy hình ảnh."
                    style_error = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                    ])
                    self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

            except requests.exceptions.RequestException as e:
                error_text = f"🚫 Lỗi khi gọi API: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
            except Exception as e:
                error_text = f"🚫 Đã xảy ra lỗi: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".du"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            try:
                response = requests.get("https://apiquockhanh.click/images/du")
                response.raise_for_status()

                image_data = response.json()
                image_url = image_data.get('url')

                if image_url:
                    image_response = requests.get(image_url)
                    
                    if image_response.status_code == 200:
                        image_filename = 'temp_du_image.jpeg'
                        with open(image_filename, 'wb') as image_file:
                            image_file.write(image_response.content)

                        self.sendLocalImage(image_filename, thread_id=thread_id, thread_type=thread_type)

                        
                        success_text = "Tải ảnh thành công!"
                        style_success = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(success_text), style="color", color="#00ff00", auto_format=False),  
                        ])
                        self.replyMessage(Message(text=success_text, style=style_success), message_object, thread_id=thread_id, thread_type=thread_type)

                        os.remove(image_filename)
                    else:
                        
                        error_text = "🚫 Không thể tải hình ảnh, vui lòng thử lại sau."
                        style_error = MultiMsgStyle([
                            MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                        ])
                        self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
                else:
                
                    error_text = "🚫 Không tìm thấy hình ảnh."
                    style_error = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False), 
                    ])
                    self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

            
                error_text = f"🚫 Lỗi khi gọi API: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
            except Exception as e:
                
                error_text = f"🚫 Đã xảy ra lỗi không mong muốn: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".anh"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            try:
                response = requests.get("https://apiquockhanh.click/images/girl")
                response.raise_for_status()

                image_data = response.json()
                image_url = image_data.get('url')

                if image_url:
                    img_response = requests.get(image_url)
                    img_response.raise_for_status()

                    img_filename = 'temp_image.jpg'
                    with open(img_filename, 'wb') as img_file:
                        img_file.write(img_response.content)

                    self.sendLocalImage(img_filename, thread_id=thread_id, thread_type=thread_type)

                    
                    success_text = "Ảnh đã được tải lên!"
                    style_success = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(success_text), style="color", color="#00ff00", auto_format=False),  
                    ])
                    self.replyMessage(Message(text=success_text, style=style_success), message_object, thread_id=thread_id, thread_type=thread_type)

                    os.remove(img_filename)
                else:
                   
                    error_text = "🚫 Không tìm thấy ảnh."
                    style_error = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False), 
                    ])
                    self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)

            except requests.exceptions.RequestException as e:
                
                error_text = f"🚫 Lỗi khi gọi API: {e}"
                style_error = MultiMsgStyle([
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
            except Exception as e:
               
                error_text = f"🚫 Đã xảy ra lỗi: {e}"
                style_error = MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_text), style="color", color="#ff5555", auto_format=False),  
                ])
                self.replyMessage(Message(text=error_text, style=style_error), message_object, thread_id=thread_id, thread_type=thread_type)
        if message.startswith("menu"):
            menu_text = (
                "Danh sách lệnh:\n"
                "• admin  xem thông tin admin.\n"
                "• .sdtvip:số điện thoại.\n"
                "• .sdt: số điện thoại.\n"
                "• .spam <nội dung>: Bắt đầu spam nội dung.\n"
                "• .nhay: Bắt đầu spam nội dung từ file content.txt.\n"
                "• .stop: Dừng spam.\n"
                "• .del: Xóa các tin nhắn chứa link.\n"
                "• All: Tag ẩn kèm nội dung.\n"
                "• .on : Xóa tất cả tin nhắn sau khi lệnh được sử dụng.\n"
                "• .off: Tắt chế độ xóa tin nhắn.\n"
                "• .admin <user_id>: Thêm người dùng vào admin.\n"
                "• .list: Xem danh sách admin.\n"
                "• .info: Xem ID của người dùng.\n"
                "• .kick @user: Đuổi người dùng khỏi nhóm.\n"
                "• .ask: Trao đổi tin nhắn với bot.\n"
                "• .uptime: Xem thời gian khởi tạo bot.\n"
                "• .anh: Tải ảnh gái.\n"
                "• .anime: Tải ảnh anime.\n"
                "• mute hoăc mu: Mute một thành viên.\n"
                "• un: Gỡ mute.\n"
                "• .du: Xem ảnh du.\n"
                "• .sexy: Xem ảnh sexy.\n"
                
                "• checkon:bật chế độ cấm tục.\n"
                "• checkoff: tắt chế độ cấm tục.\n"
                " • .random + số lượng: random acc golike(newly updated ).\n"
                " • .lq + số lượng(1>=10): random acc liên quân(newly updated ).\n"
                " • .id + idtiktok: xem thông tin nick (newly updated ).\n"
                " • .reo + @metion:spam metion (newly updated ).\n"
                " • .vip sdt : spamvip .\n"
                "• .reo @metion tag metion liên tục.\n"
                "• .stopreo ngừng spam người đó chỉnh delay để nhận lệnh nhanh hơn.\n"
                "• .cannang @metion xem cân nặng người đó\n"
                "• .gay @metion xem độ gay người đó.\n"
                "• .ghepdoi @metion 1 và @metion:xem độ phụ hợp>\n"
                " • .dltt linkvstiktok\n"
                "• .tb tag all với thông báo.\n"
                "• .rs nội dung tag chính bản thân mình.\n"
                "• game chơi game.,\n"
                "• .dt đổi tên nhóm.\n"
                "• .share tren bot.\n"
                "• .shop xem shop .\n"
                "• .nhapkey  nhập key vip.\n"
                
                
            )            
            style_menu = MultiMsgStyle([
                MessageStyle(offset=0, length=15, style="font", size="14", auto_format=False),
                MessageStyle(offset=16, length=len(menu_text) - 16, style="font", size="12", auto_format=False),
                MessageStyle(offset=0, length=len(menu_text), style="color", color="#4caf50", auto_format=False),
            ])          
            self.replyMessage(
                Message(
                    text=menu_text,
                    style=style_menu
                ),
                message_object,
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        elif message.startswith(".id"):
            parts = message.split(maxsplit=1)  
            if len(parts) == 2:
                tiktok_username = parts[1].strip()  
                api_url = f"https://apiquockhanh.click/tiktok?info={tiktok_username}"

                try:
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        data = response.json()

                        if 'data' in data and 'user' in data['data']:
                            
                            user_info = (
                                f"Thông tin TikTok:\n"
                                f"- Nickname: {data['data']['user']['nickname']}\n"
                                f"- Followers: {data['data']['stats']['followerCount']}\n"
                                f"- Following: {data['data']['stats']['followingCount']}\n"
                                f"- Videos: {data['data']['stats']['videoCount']}\n"
                                f"- Heart Count: {data['data']['stats']['heartCount']}\n"
                                f"- Signature: {data['data']['user']['signature']}"
                            )
                            self.replyMessage(
                                Message(text=user_info),
                                message_object,
                                thread_id=thread_id,
                                thread_type=thread_type
                            )
                        else:
                            self.replyMessage(
                                Message(text="Không tìm thấy thông tin cho người dùng TikTok này."),
                                message_object,
                                thread_id=thread_id,
                                thread_type=thread_type
                            )
                    else:
                        self.replyMessage(
                            Message(text="Lỗi khi truy cập API TikTok."),
                            message_object,
                            thread_id=thread_id,
                            thread_type=thread_type
                        )
                except Exception as e:
                    self.replyMessage(
                        Message(text="Đã xảy ra lỗi khi lấy thông tin TikTok."),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
                    print(f"Lỗi khi xử lý lệnh .id: {e}")
            else:
                
                self.replyMessage(
                    Message(text="Sai cú pháp! Vui lòng sử dụng: .id <tiktok_username>"),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
        
        if message.startswith(".admin"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            parts = message.split(' ', 1)
            if len(parts) < 2:
                self.replyMessage(Message(text='🚫 Vui lòng cung cấp user_id để thêm làm admin.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            new_admin_id = parts[1]
            idadmin.add(new_admin_id)
            self.save_admins(idadmin)
            self.replyMessage(Message(text=f'Đã thêm {new_admin_id} vào danh sách admin.'), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".list"):
            admin_list = "\n".join(idadmin)
            self.replyMessage(Message(text=f'Danh sách admin:\n{admin_list}'), message_object, thread_id=thread_id, thread_type=thread_type)

        
        if message.startswith(".del"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            self.delete_links = not self.delete_links
            status = "Bật" if self.delete_links else "Tắt"
            self.replyMessage(Message(text=f'✅ Đã {status} chế độ xóa liên kết.'), message_object, thread_id=thread_id, thread_type=thread_type)

        

        if message.startswith(".spam"):
            if author_id not in idadmin:
                self.replyMessage(Message(text=' Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            if self.spamming:
                self.replyMessage(Message(text='🚫 Spam đang chạy!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            parts = message.split(' ', 1)
            if len(parts) < 2:
                self.replyMessage(Message(text='🚫 Vui lòng cung cấp nội dung đi chứ Admin'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            spam_content = parts[1]
            self.spamming = True
            self.spam_thread = threading.Thread(target=self.spam_message, args=(spam_content, thread_id, thread_type))
            self.spam_thread.start()

        if message.startswith(".nhay"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if self.spamming:
                self.replyMessage(Message(text='🚫 Spam đang chạy!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            try:
                with open('content.txt', 'r', encoding='utf-8') as file:
                    spam_content = file.read()
            except FileNotFoundError:
                self.replyMessage(Message(text='🚫 Không tìm thấy file content.txt.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            self.spamming = True
            self.spam_thread = threading.Thread(target=self.spam_message, args=(spam_content, thread_id, thread_type))
            self.spam_thread.start()

        if message.startswith(".stop"):
            if not self.spamming:
                self.replyMessage(Message(text='🚫 Không có spam nào đang chạy!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            self.spamming = False
            if self.spam_thread is not None:
                self.spam_thread.join()
            self.replyMessage(Message(text='✅ Đã dừng spam.'), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".on"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            self.xoatn_mode = True
            self.replyMessage(Message(text='Im lặng là vàng các e đã bị cấm chat!🤫.'), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".off"):
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            self.xoatn_mode = False
            self.messages_to_delete.clear()
            self.replyMessage(Message(text='Đã tắt chế độ xóa tin nhắn.'), message_object, thread_id=thread_id, thread_type=thread_type)

        if message.startswith(".kick"):
            self.handle_kick(message_object, thread_id, author_id, thread_type)
            
        elif message.startswith("mute") or message.startswith("mu") or message.startswith(" ") or "mute" in message.lower():
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sài lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            mutenguoidung = self.load_mutenguoidung()
            if message_object.mentions and len(message_object.mentions) > 0:
                user_id = message_object.mentions[0]['uid']
                mention = Mention(user_id, length=8, offset=12)
                self.replyMessage(
                    Message(
                        text="Nín Họng Đi @TagName", mention=mention
                    ),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
            else:
                user_id = author_id
                self.replyMessage(
                    Message(
                        text="Bạn Đã Tự Hủy🗿"
                    ),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
            if user_id not in mutenguoidung:
                mutenguoidung.add(user_id)
                self.save_mutenguoidung(mutenguoidung)
            self.isUndoLoop = True

        
        elif message.startswith("unmute") or "unmute" in message.lower():
            if author_id not in idadmin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sài lệnh này.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            mutenguoidung = self.load_mutenguoidung()
            if message_object.mentions and len(message_object.mentions) > 0:
                user_id = message_object.mentions[0]['uid']
                mention = Mention(user_id, length=8, offset=12)
                self.replyMessage(
                    Message(
                        text="Đã hủy câm lặng cho @TagName", mention=mention
                    ),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
            else:
                user_id = author_id
                self.replyMessage(
                    Message(
                        text="Bạn đã tự mở khóa câm lặng"
                    ),
                    message_object,
                    thread_id=thread_id,
                    thread_type=thread_type
                )
            if user_id in mutenguoidung:
                mutenguoidung.remove(user_id)
                self.save_mutenguoidung(mutenguoidung)
            self.isUndoLoop = False
        
            
   
        
        if self.xoatn_mode:
            self.messages_to_delete.append(message_object)

        list_link = ["t.me/", "https://", "http://", "https://zalo.me/g/", "zalo.me/g/", "zalo.me", "https://t.me/", "chinhphu.vn", "edu.vn", "gov.vn", "edu.gov.vn", "youtube", "tiktok", "https://www.youtube.com/"]

        if self.delete_links and any(link in message for link in list_link):
            try:
                self.deleteGroupMsg(
                    msgId=message_object.msgId, 
                    clientMsgId=message_object.cliMsgId, 
                    ownerId=author_id, 
                    groupId=thread_id
                )
            except Exception as e:
                print(f'Error deleting message: {e}')
        
        if self.xoatn_mode and self.messages_to_delete:
            for msg_obj in self.messages_to_delete:
                try:
                    self.deleteGroupMsg(
                        msgId=msg_obj.msgId, 
                        clientMsgId=msg_obj.cliMsgId, 
                        ownerId=author_id, 
                        groupId=thread_id
                    )
                except Exception as e:
                    print(f'Error deleting message: {e}')
            self.messages_to_delete.clear()
        if message.startswith(".tx"):
            menu_text = (
                "ᴅᴀɴʜ ꜱᴀ́ᴄʜ ʟᴇ̣̂ɴʜ:\n"
                        "• .ᴅᴀɴɢᴋʏ ɴᴀᴍᴇ: Đăng ký với tên và nhận 500 triệu.\n"
                        "• .ɢᴀᴍᴇ ᴛ/x/ᴄ/ʟ số tiền: Tham gia game.\n"
                        "• .ᴄᴛ tên số tiền: Chuyển tiền cho người khác.\n"
                        "• .code mã số tiền: Nhập mã code.\n"
                        "• .ꜱᴏᴅᴜ: Xem số dư.\n"
                        "• .ᴀᴅᴍɪɴ key: Trở thành admin.\n"
                        "• .ʙᴜꜰꜰ tên: Buff vô hạn tiền cho người khác (admin).\n"
                        "• .ɴᴏɴᴇ ɴᴀᴍᴇ ꜱᴏ̂́ ᴛɪᴇ̂̀ɴ:ʙᴜꜰꜰ ᴛɪᴇ̂̀ɴ ɴᴏᴏʙ.\n"
            )            
            style_menu = MultiMsgStyle([
                MessageStyle(offset=0, length=15, style="font", size="14", auto_format=False),
                MessageStyle(offset=16, length=len(menu_text) - 16, style="font", size="12", auto_format=False),
                MessageStyle(offset=0, length=len(menu_text), style="color", color="#4caf50", auto_format=False),
            ])          
            self.replyMessage(
                Message(
                    text=menu_text,
                    style=style_menu
                ),
                message_object,
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        elif message.startswith(".dangki"):
            user_name = message[len(".dangki "):].strip()
            if not user_name:
                self.replyMessage(Message(text='🚫 Bạn cần cung cấp tên để đăng ký.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            registered_users = self.load_registered_users()

            if author_id in registered_users:
                self.replyMessage(Message(text='🚫 Bạn đã đăng ký rồi!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            self.save_registered_user(author_id, user_name)
            self.replyMessage(Message(text=f'✅ Đăng ký thành công! Bạn đã được tặng 500 triệu!'), message_object, thread_id=thread_id, thread_type=thread_type)

        elif message.startswith(".code"):
            args = message.split()
            if len(args) != 2:
                self.replyMessage(Message(text='🚫 Vui lòng nhập đúng cú pháp: .code <mã>'), message_object, thread_id, thread_type)
                return
            
            code = args[1].upper()
            if code in self.codes:
                registered_users = self.load_registered_users()
            
                if author_id not in registered_users:
                    self.replyMessage(Message(text='🚫 Bạn cần đăng ký trước khi nhập mã.'), message_object, thread_id, thread_type)
                    return
                
                
                user_name, balance = registered_users[author_id]
                amount = self.codes[code] 
                new_balance = balance + amount
                
                
                self.update_user_balance(author_id, new_balance)
                
                
                self.replyMessage(Message(text=f'✅ Bạn đã nhập mã {code} thành công và nhận được {amount}! Số dư mới của bạn: {new_balance}'), message_object, thread_id, thread_type)
            else:
               
                self.replyMessage(Message(text='🚫 Mã không hợp lệ!'), message_object, thread_id, thread_type)

        elif message.startswith(".game"):
            registered_users = self.load_registered_users()
            if author_id not in registered_users:
                self.replyMessage(Message(text='🚫 Bạn cần đăng ký trước khi chơi game.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            args = message.split()
            if len(args) != 3:
                self.replyMessage(Message(text='🚫 Vui lòng nhập đúng cú pháp: .game <T/X/C/L> <số tiền>'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            bet_type = args[1].upper()
            try:
                bet_amount = int(args[2])
            except ValueError:
                self.replyMessage(Message(text='🚫 Số tiền cược không hợp lệ!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            if bet_amount <= 0:
                self.replyMessage(Message(text='🚫 Số tiền cược phải lớn hơn 0.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            users_balance = registered_users[author_id][1]
            if users_balance < bet_amount:
                self.replyMessage(Message(text='🚫 Bạn không đủ tiền để cược!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            dice_results = [random.randint(1, 6) for _ in range(3)]
            total = sum(dice_results)
            is_even = total % 2 == 0
            win_condition = (bet_type == 'T' and total > 10) or (bet_type == 'X' and total < 11) or \
                            (bet_type == 'C' and is_even) or (bet_type == 'L' and not is_even)

            if win_condition:
                result_text = "chẵn" if is_even else "lẻ"
                self.replyMessage(Message(text=f'🎉 Chúc mừng! Bạn đã thắng! Kết quả: {dice_results} = {total} ({result_text}). Bạn nhận được {bet_amount} tiền!'), message_object, thread_id=thread_id, thread_type=thread_type)
                new_balance = users_balance + bet_amount
            else:
                result_text = "chẵn" if is_even else "lẻ"
                self.replyMessage(Message(text=f'😢 Bạn đã thua! Kết quả: {dice_results} = {total} ({result_text}). Bạn mất {bet_amount} tiền!'), message_object, thread_id=thread_id, thread_type=thread_type)
                new_balance = users_balance - bet_amount

            self.update_user_balance(author_id, new_balance)

        elif message.startswith(".sodu"):
            registered_users = self.load_registered_users()
            if author_id not in registered_users:
                self.replyMessage(Message(text='🚫 Bạn chưa đăng ký!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            user_name, balance = registered_users[author_id]
            self.replyMessage(Message(text=f'💰 Số dư của bạn là: {balance}'), message_object, thread_id=thread_id, thread_type=thread_type)

        elif message.startswith(".ct"):
            registered_users = self.load_registered_users()
            if author_id not in registered_users:
                self.replyMessage(Message(text='🚫 Bạn chưa đăng ký!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            args = message.split()
            if len(args) != 3:
                self.replyMessage(Message(text='🚫 Vui lòng nhập đúng cú pháp: .ct <tên> <số tiền>'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            receiver_name = args[1]
            try:
                transfer_amount = int(args[2])
            except ValueError:
                self.replyMessage(Message(text='🚫 Số tiền không hợp lệ!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if transfer_amount <= 0:
                self.replyMessage(Message(text='🚫 Số tiền phải lớn hơn 0.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            sender_name, sender_balance = registered_users[author_id]
            if sender_balance < transfer_amount:
                self.replyMessage(Message(text='🚫 Bạn không đủ tiền để chuyển!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            recipient_id = next((uid for uid, (name, _) in registered_users.items() if name == receiver_name), None)
            if not recipient_id:
                self.replyMessage(Message(text='🚫 Người nhận không tồn tại!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            recipient_name, recipient_balance = registered_users[recipient_id]
            new_sender_balance = sender_balance - transfer_amount
            new_recipient_balance = recipient_balance + transfer_amount

            self.update_user_balance(author_id, new_sender_balance)
            self.update_user_balance(recipient_id, new_recipient_balance)
            self.replyMessage(Message(text=f'✅ Chuyển tiền thành công! Bạn đã chuyển {transfer_amount} cho {recipient_name}. Số dư mới của bạn: {new_sender_balance}'), message_object, thread_id=thread_id, thread_type=thread_type)

        elif message.startswith("key"):
            key = message[len(".key "):].strip()
            if key == self.admin_key:
                self.is_admin = True
                self.replyMessage(Message(text='🔐 Bạn đã trở thành admin!'), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                self.replyMessage(Message(text='🚫 Sai mật khẩu admin!'), message_object, thread_id=thread_id, thread_type=thread_type)

        elif message.startswith(".neno"):
            
            
            args = message.split()
            if len(args) != 3:
                self.replyMessage(Message(text='🚫 Vui lòng nhập đúng cú pháp: .none <tên> <số tiền>'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            receiver_name = args[1]
            try:
                buff_amount = int(args[2])
            except ValueError:
                self.replyMessage(Message(text='🚫 Số tiền không hợp lệ!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if buff_amount <= 0:
                self.replyMessage(Message(text='🚫 Số tiền phải lớn hơn 0.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            registered_users = self.load_registered_users()
            recipient_id = next((uid for uid, (name, _) in registered_users.items() if name == receiver_name), None)
            if not recipient_id:
                self.replyMessage(Message(text='🚫 Người nhận không tồn tại!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if recipient_id == author_id:
                self.replyMessage(Message(text='🚫 Bạn không thể buff tiền cho chính mình!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            recipient_name, recipient_balance = registered_users[recipient_id]
            new_recipient_balance = recipient_balance + buff_amount
            self.update_user_balance(recipient_id, new_recipient_balance)
            self.replyMessage(Message(text=f'✅ Buff tiền thành công! Bạn đã buff {buff_amount} cho {recipient_name}. Số dư mới của {recipient_name}: {new_recipient_balance}'), message_object, thread_id=thread_id, thread_type=thread_type)


        elif message.startswith(".buff"):
            if not self.is_admin:
                self.replyMessage(Message(text='🚫 Bạn không có quyền sử dụng lệnh này!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            args = message.split()
            if len(args) != 2:
                self.replyMessage(Message(text='🚫 Vui lòng nhập đúng cú pháp: .buff <tên>'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            user_name = args[1].strip()
            registered_users = self.load_registered_users()

            recipient_id = None
            for uid, (name, balance) in registered_users.items():
                if name.lower() == user_name.lower():
                    recipient_id = uid
                    break

            if recipient_id is None:
                self.replyMessage(Message(text=f'🚫 Không tìm thấy người dùng tên {user_name}.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            self.update_user_balance(recipient_id, float('inf'))
            self.replyMessage(Message(text=f'✅ Đã buff tiền vô hạn cho người dùng {user_name}!'), message_object, thread_id=thread_id, thread_type=thread_type)
    def send_private_message_to_user(self, user_id, random_data):
        """Gửi nội dung sau khi random từ file riêng tư đến người dùng."""
        try:
            message_text = f"thông tin nick:\n{random_data}"
            private_message = Message(text=message_text)
            self.send(private_message, thread_id=user_id, thread_type=ThreadType.USER)  
        except Exception as e:
            print(f"🚫 Lỗi khi gửi tin nhắn: {e}")
    
    def get_random_data(self, quantity):
        """Lấy ngẫu nhiên một số lượng dòng từ file gl.txt."""
        try:
            with open("gl.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
                if len(lines) < quantity:
                    return None  
                
                random_lines = random.sample(lines, quantity)
                return ''.join(random_lines)
        except FileNotFoundError:
            print("🚫 File gl.txt không tồn tại.")
            return None
        except Exception as e:
            print(f"🚫 Lỗi khi đọc file: {e}")
            return None
    
    def log_message(self, author_id, thread_id, message_object):
        current_time = time.time()

        
        if author_id in self.message_log:
            self.message_log[author_id].append(current_time)
        else:
            self.message_log[author_id] = [current_time]

        
        self.message_log[author_id] = [t for t in self.message_log[author_id] if current_time - t < 10]

       
        if len(self.message_log[author_id]) >= self.spam_threshold:
            self.handle_spammer(author_id, thread_id, message_object)

    def handle_spammer(self, author_id, thread_id, message_object):
        if author_id not in self.excluded_user_ids:
            try:
                
                self.kickUsersFromGroup([author_id], thread_id)
                self.replyMessage(Message(text=f"🚫 Người dùng {author_id} đã bị kick vì spam!"), message_object, thread_id=thread_id, thread_type=thread_type)
            except Exception as e:
                print(f"Error kicking user: {e}")
        else:
            self.replyMessage(Message(text="🚫 Người dùng này nằm trong danh sách miễn trừ!"), message_object, thread_id=thread_id, thread_type=thread_type)
            
    def reo_spam_message(self, mentioned_user_id, thread_id, thread_type):
        """Spam mentions of a specific user."""
        while self.reo_spamming:
            mention = Mention(uid=mentioned_user_id, offset=0, length=5)
            spam_message = Message(text="@user", mention=mention)  
            self.send(spam_message, thread_id=thread_id, thread_type=thread_type)
            time.sleep(1)
     
    def handle_kick(self, message_object, thread_id, author_id, thread_type):
        
        idadmin = self.load_admins()
        if author_id not in idadmin:
            self.replyMessage(Message(text="🚫 Bạn không có quyền sử dụng lệnh này."), message_object, thread_id=thread_id, thread_type=thread_type)
            return

        mentions = getattr(message_object, 'mentions', None)
        if mentions:
            mentioned_user_id = mentions[0]['uid']
            if mentioned_user_id not in self.excluded_user_ids:
                try:
                    self.kickUsersFromGroup([mentioned_user_id], thread_id)
                    self.replyMessage(Message(text="thanh niên này qua xam lon nên bị kick."), message_object, thread_id=thread_id, thread_type=thread_type)
                except ZaloAPIException:
                    self.replyMessage(Message(text="🚫 Không thể đuổi người dùng."), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                self.replyMessage(Message(text="🚫 Không thể đuổi người dùng này."), message_object, thread_id=thread_id, thread_type=thread_type)
        else:
            self.replyMessage(Message(text="Nhập tên thằng gay muốn kick."), message_object, thread_id=thread_id, thread_type=thread_type)
    
    def ask_api(self, user_message):
        headers = {
            'Content-Type': 'application/json',
        }
        params = {
            'key': 'AIzaSyBDlktMVCY-M4gvxyw3f1yoQMa1mshgis0',  
        }
        json_data = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': user_message,
                        },
                    ],
                },
            ],
        }

        try:
            response = requests.post(
                'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent',
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
            result = response.json()
            print("Phản hồi API:", result) 
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text']
                else:
                    return 'Không có phần nội dung trong phản hồi.'
            else:
                return 'Không có ứng viên nào trong phản hồi.'
        except requests.exceptions.RequestException as e:
            return f'Lỗi yêu cầu API: {e}'
        except Exception as e:
            return f'Đã xảy ra lỗi: {e}'

    def spam_message(self, spam_content, thread_id, thread_type):
        words = spam_content.split()
        while self.spamming:
            for word in words:
                if not self.spamming:
                    break
                mention = Mention(uid='-1', offset=0, length=len(word))
                spam_message = Message(text=word, mention=mention)
                self.send(spam_message, thread_id=thread_id, thread_type=thread_type)
                time.sleep(1)
    def remove_banned_words(self, message):
        cleaned_message = message
        for word in self.banned_words: 
            cleaned_message = cleaned_message.replace (word, "[censored]")
        return cleaned_message
    def add_to_spam_list(self, phone_number):
       
        url = f"https://thanhphucdev.net/api/thanhphuc.php?sdt={phone_number}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return f"✅ Added phone number {phone_number} to the spam list."
            else:
                return "🚫 Could not add phone number to the spam list."
        except requests.exceptions.RequestException as e:
            return f"🚫 Error: {str(e)}"
    def download_tiktok_video(self, video_url, message_object, thread_id, thread_type):
        """Download TikTok video and send details back to user."""
        api_url = f"https://apiquockhanh.click/tiktok?video={video_url}"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                self.replyMessage(Message(text='🚫 Không thể tải video. Vui lòng kiểm tra lại đường dẫn.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            video_data = data.get("data", {})
            title = video_data.get("title", "Không có tiêu đề")
            duration = video_data.get("duration", 0)
            play_url = video_data.get("play", "")
            cover_url = video_data.get("cover", "")
            music_info = video_data.get("music_info", {})
            music_title = music_info.get("title", "Không có tên nhạc")
            music_author = music_info.get("author", "Không có tác giả")
            download_url = play_url  

            message = (
                f"**Tiêu đề:** {title}\n"
                f"**Thời gian:** {duration} giây\n"
                f"**Link video:** {play_url}\n"
                f"**Đường dẫn tải video:** [Tải tại đây]({download_url})\n"  
                f"**Hình ảnh bìa:** {cover_url}\n"
                f"**Tên nhạc:** {music_title}\n"
                f"**Tác giả nhạc:** {music_author}"
            )
            self.replyMessage(Message(text=message), message_object, thread_id=thread_id, thread_type=thread_type)
        
        except requests.RequestException as e:
            print(f"Error fetching video: {e}")
            self.replyMessage(Message(text="🚫 Có lỗi khi lấy video."), message_object, thread_id=thread_id, thread_type=thread_type)
    
    

    def add_to_spam_list(self, phone_number):
        """Add a phone number to the spam list via API call."""
        url = f"https://thanhphucdev.net/api/thanhphuc.php?sdt={phone_number}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return f"✅ Added phone number {phone_number} to the spam list."
            else:
                return "🚫 Could not add phone number to the spam list."
        except requests.exceptions.RequestException as e:
            return f"🚫 Error: {str(e)}"
    def reo_spam_message(self, mentioned_user_id, thread_id, thread_type):
        """Spam mentions of a specific user."""
        while self.reo_spamming:
            mention = Mention(uid=mentioned_user_id, offset=0, length=5)
            spam_message = Message(text="@user", mention=mention)  
            self.send(spam_message, thread_id=thread_id, thread_type=thread_type)
            time.sleep(0)  
    
    def changeGroupName(self, groupName, groupId):
        params = {
            "zpw_ver": 641,
            "zpw_type": 30
        }
        
        payload = {
            "params": self._encode({
                "gname": groupName,  
                "grid": str(groupId)
            })
        }
        
        response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/updateinfo", params=params, data=payload)
        data = response.json()
        results = data.get("data") if data.get("error_code") == 0 else None
        if results:
            results = self._decode(results)
            results = results.get("data") if results.get("data") else results
            if results is None:
                results = {"error_code": 1337, "error_message": "Data is None"}
            
            if isinstance(results, str):
                try:
                    results = json.loads(results)
                except:
                    results = {"error_code": 1337, "error_message": results}
            
            return Group.fromDict(results, None)
        return None
    
	    
	    
    
    

def save_group_ids(group_ids):
    with open('group.json', 'w') as group_file:
        json.dump({"group_ids": group_ids}, group_file, indent=4)

def load_mutenguoidung():
    try:
        with open('mute.json', 'r') as mute_file:
            data = json.load(mute_file)
            if isinstance(data, dict):
                return set(data.get('mutenguoidung', []))
            elif isinstance(data, list):
                return set(data)
            else:
                return set()
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_mutenguoidung(mutenguoidung):
    with open('mute.json', 'w') as mute_file:
        json.dump({'mutenguoidung': list(mutenguoidung)}, mute_file)




imei = "7c7bb9b2-08a1-446d-9a75-613d16d64d47-b78b4e2d6c0a362c418b145fe44ed73f"
session_cookies = ({"_ga":"GA1.2.1750407579.1730738316","_gid":"GA1.2.1584871262.1730738316","_ga_VM4ZJE1265":"GS1.2.1730738317.1.0.1730738317.0.0.0","_zlang":"vn","app.event.zalo.me":"7093867920015212027","_gat":"1","zpsid":"H4RE.425362398.1.HzhGWNrH81kZqde2SL4W6mWYKYzFP1CjJs8P8mpe3LjEltY6VAGjCXfH81i","zpw_sek":"nq0p.425362398.a0.HiX5BhLPw0zhsh8Mb5de3yvxZMINOye-WpRVNTO0gMM0AOPvnIk0JjGMXKBIPDKjo2XH8lLg1bSeM1y2d3xe3m"})

honhattruong = Honhattruong('api_key', 'secret_key', imei=imei, session_cookies=session_cookies)
honhattruong.listen()
