import re
from zlapi import ZaloAPI, ZaloAPIException
from zlapi.models import *
import time
import threading
import json
import datetime
import requests
import os
import random

class Honhattruong(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.dangky_file = 'tx.json'
        self.diemdanh_file = 'diemdanh.json'  
        
        self.bets_file = 'bets.json'  
        self.codes_used = 'codes_used.json'  

    def load_registered_users(self):
        try:
            with open(self.dangky_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    

    def save_registered_user(self, user_id, user_name):
        users = self.load_registered_users()
        users[user_id] = {"name": user_name, "balance": 50}  
        with open(self.dangky_file, 'w', encoding='utf-8') as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
    def load_used_codes(self):
        try:
            with open(self.codes_used, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_used_code(self, user_id, code):
        used_codes = self.load_used_codes()
        used_codes[user_id] = code
        with open(self.codes_used, 'w', encoding='utf-8') as file:
            json.dump(used_codes, file, ensure_ascii=False, indent=4)
    def load_bets(self):
        try:
            with open(self.bets_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    def load_diemdanh(self):
        try:
            with open(self.diemdanh_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_diemdanh(self, user_id, date):
        diemdanh = self.load_diemdanh()
        diemdanh[user_id] = date
        with open(self.diemdanh_file, 'w', encoding='utf-8') as file:
            json.dump(diemdanh, file, ensure_ascii=False, indent=4)

    def save_bet(self, user_id, amount, bet_type):
        bets = self.load_bets()
        bets[user_id] = {"amount": amount, "bet_type": bet_type}
        with open(self.bets_file, 'w', encoding='utf-8') as file:
            json.dump(bets, file, ensure_ascii=False, indent=4)

    def update_user_balance(self, user_id, new_balance):
        users = self.load_registered_users()
        if user_id in users:
            users[user_id]['balance'] = new_balance
            with open(self.dangky_file, 'w', encoding='utf-8') as file:
                json.dump(users, file, ensure_ascii=False, indent=4)
    def handle_menu(self, thread_id, thread_type):
        msg = """
        📝 *Danh sách các lệnh*:
        ➜ 🎯  "tx dk tên" - Đăng ký tên và nhận $50.
        ➜ 🎲  "tx dat số tiền T/X" - Đặt cược Tài (T) hoặc Xỉu (X).
        ➜ 📊  "tx sd" - Xem số dư hiện tại.
        ➜ ♾️  "tx ma" - nhap code
        ➜ 🖊️  "tx diemdanh" - điểm danh nhân quà
        ➜ 💤  "tx ct số tien tên" - Xem số dư hiện tại.
        ➜ 🅰️  "tx bxh" - xem người giàu nhất 
        """
        
        anime = self.get_random_image_from()

        if anime:
            self.sendLocalImage(anime, thread_id=thread_id, thread_type=thread_type, width=2560, height=2560, message=Message(text=msg))
        else:
            self.sendMessage(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

    def get_random_image_from(self, folder_path='anh'):
        try:
            all_files = os.listdir(folder_path)
            image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

            if not image_files:
                return None  

            random_image = random.choice(image_files)
            return os.path.join(folder_path, random_image)
        except Exception:
            return None
    def get_random_image_from_folder(self, folder_path='tx'):
        try:
            all_files = os.listdir(folder_path)
            image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

            if not image_files:
                return None  

            random_image = random.choice(image_files)
            return os.path.join(folder_path, random_image)
        except Exception:
            return None

    def roll_dice(self):
        return [random.randint(1, 6) for _ in range(3)]

    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        if message is None or not isinstance(message, str):
            return

        print(f"\033[32m{message} \033[39m|\033[31m {author_id} \033[39m|\033[33m {thread_id}\033[0m\n")
        if message.startswith("menu"):
            self.handle_menu(thread_id, thread_type)
        if message.startswith("tx dk"):
            user_name = message[len("tx dk "):].strip()
            if not user_name:
                self.replyMessage(Message(text='🚀 Bạn cần cung cấp tên để đăng ký.'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            registered_users = self.load_registered_users()

            if author_id in registered_users:
                self.replyMessage(Message(text='🤡 Bạn đã đăng ký rồi!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            self.save_registered_user(author_id, user_name)
            self.replyMessage(Message(text=f'🥰 Đăng ký thành công! Bạn đã được tặng $50!'), message_object, thread_id=thread_id, thread_type=thread_type)
        elif message.startswith("tx ma"):
            code = message[len("tx ma "):].strip()
            if not code:
                self.replyMessage(Message(text='🚀 Bạn cần nhập mã code!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            
            registered_users = self.load_registered_users()
            if author_id not in registered_users:
                self.replyMessage(Message(text='🤡 Bạn cần đăng ký tài khoản trước khi sử dụng mã code!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            used_codes = self.load_used_codes()
            if author_id in used_codes:
                self.replyMessage(Message(text='🤡 Bạn đã sử dụng mã code này rồi!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if code == "Selenophile":
                self.update_user_balance(author_id, 1000)
                self.save_used_code(author_id, code)
                self.replyMessage(Message(text='🎉 Bạn đã nhận được $1000 với mã code F88!'), message_object, thread_id=thread_id, thread_type=thread_type)
            elif code == "C25":
                current_balance = self.load_registered_users().get(author_id, {}).get("balance", 0)
                new_balance = current_balance * 1000
                self.update_user_balance(author_id, new_balance)
                self.save_used_code(author_id, code)
                self.replyMessage(Message(text=f'🎉 Bạn đã nhân đôi số tiền với mã code C25! Số dư hiện tại của bạn là ${new_balance}!'), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                self.replyMessage(Message(text='❌ Mã code không hợp lệ!'), message_object, thread_id=thread_id, thread_type=thread_type)
            
        elif message.startswith("tx sd"):
            registered_users = self.load_registered_users()
            if author_id in registered_users:
                user_name = registered_users[author_id]['name']
                user_balance = registered_users[author_id]['balance']
                self.replyMessage(Message(text=f'Tên đăng nhập: {user_name}\nSố dư hiện tại: ${user_balance:.2f}'), message_object, thread_id=thread_id, thread_type=thread_type)
            else:
            	
                self.replyMessage(Message(text='🤡 Bạn chưa đăng ký!'), message_object, thread_id=thread_id, thread_type=thread_type)
        elif message.startswith("tx bxh"):
            registered_users = self.load_registered_users()

            
            top_users = sorted(registered_users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]

            if not top_users:
                self.replyMessage(Message(text='🤡 Không có người chơi nào trong danh sách!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            
            leaderboard_message = "🏆 *Top 10 Đại Gia Ngầm*:\n"
            for i, (user_id, user_info) in enumerate(top_users, start=1):
                username = user_info['name']
                balance = user_info['balance']
                leaderboard_message += f"{i}. {username}: ${balance:.2f}\n"

            self.replyMessage(Message(text=leaderboard_message), message_object, thread_id=thread_id, thread_type=thread_type)
        elif message.startswith("tx diemdanh"):
            today = datetime.datetime.now().date()
            diemdanh = self.load_diemdanh()
            registered_users = self.load_registered_users()
            if author_id not in registered_users:
                self.replyMessage(Message(text='🤡 Bạn cần đăng ký tài khoản trước khi điểm danh!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            
            if author_id in diemdanh and diemdanh[author_id] == str(today):
                self.replyMessage(Message(text='🤡 Bạn đã điểm danh hôm nay rồi!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            
            self.save_diemdanh(author_id, str(today))
            current_balance = self.load_registered_users().get(author_id, {}).get("balance", 0)
            new_balance = current_balance + 100  

            self.update_user_balance(author_id, new_balance)
            self.replyMessage(Message(text='🎉 Bạn đã điểm danh thành công và nhận được $100!'), message_object, thread_id=thread_id, thread_type=thread_type)
            

        elif message.startswith("tx ct"):
            parts = message[len("tx ct "):].strip().split()
            if len(parts) != 2:
                self.replyMessage(Message(text='🚀 Bạn cần nhập tên và số tiền để chuyển!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            user_name = parts[0]
            try:
                amount = float(parts[1])
            except ValueError:
                self.replyMessage(Message(text='🚀 Số tiền không hợp lệ!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            registered_users = self.load_registered_users()
            if author_id not in registered_users:
                self.replyMessage(Message(text='🤡 Bạn chưa đăng ký!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            user_balance = registered_users[author_id]['balance']
            if amount > user_balance:
                self.replyMessage(Message(text='🚀 Bạn không đủ tiền để chuyển!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            
            recipient_id = None
            for uid, info in registered_users.items():
                if info['name'] == user_name:
                    recipient_id = uid
                    break
            
            if recipient_id is None:
                self.replyMessage(Message(text='🚀 Không tìm thấy người nhận!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            if recipient_id == author_id:
                self.replyMessage(Message(text='🚀 Bạn không thể chuyển tiền cho chính mình!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
             
            
            self.update_user_balance(author_id, user_balance - amount)
            recipient_balance = registered_users[recipient_id]['balance']
            self.update_user_balance(recipient_id, recipient_balance + amount)

            self.replyMessage(Message(text=f'✅ Đã chuyển {amount} cho {user_name}.\nSố dư hiện tại: ${user_balance - amount:.2f}.'), message_object, thread_id=thread_id, thread_type=thread_type)
        elif message.startswith("tx dat"):
            parts = message[len("tx dat "):].strip().split()
            if len(parts) != 2:
                self.replyMessage(Message(text='🚀 Bạn cần nhập số tiền và loại cược (T hoặc X).'), message_object, thread_id=thread_id, thread_type=thread_type)
                return
            
            try:
                amount = float(parts[0])
                bet_type = parts[1].upper()
            except ValueError:
                self.replyMessage(Message(text='🚀 Số tiền không hợp lệ!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

           
            
            registered_users = self.load_registered_users()
            if author_id not in registered_users:
                self.replyMessage(Message(text='🤡 Bạn chưa đăng ký!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            user_balance = registered_users[author_id]['balance']
            if amount > user_balance:
                self.replyMessage(Message(text='🚀 Bạn không đủ tiền để cược!'), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            
            self.save_bet(author_id, amount, bet_type)

            
            dice_results = self.roll_dice()
            total = sum(dice_results)
            win_condition = (bet_type == 'T' and total > 10) or (bet_type == 'X' and total < 11)

            
            if win_condition:
                new_balance = user_balance + amount
                result_message = f'✅ Bạn đã thắng! Số tiền +{amount}.'
            else:
                new_balance = user_balance - amount
                result_message = f'😢 Bạn đã thua! Số tiền -{amount}.'

            self.update_user_balance(author_id, new_balance)

            
            if total == 7:
                image_path = os.path.join('tx', '7.jpg')
            else:
                image_path = os.path.join('tx', f'{total}.jpg')

            result_text = f"Kết quả xúc xắc: {dice_results} = {total}.\n{result_message}\n💔 Số dư hiện tại: ${new_balance:.2f}."
            if os.path.exists(image_path):
                self.sendLocalImage(image_path, thread_id=thread_id, thread_type=thread_type, message=Message(text=result_text))
            else:
                self.replyMessage(Message(text=result_text), message_object, thread_id=thread_id, thread_type=thread_type)


imei = "7c7bb9b2-08a1-446d-9a75-613d16d64d47-b78b4e2d6c0a362c418b145fe44ed73f"
session_cookies = ({"_ga":"GA1.2.1750407579.1730738316","_gid":"GA1.2.1584871262.1730738316","_ga_VM4ZJE1265":"GS1.2.1730738317.1.0.1730738317.0.0.0","_zlang":"vn","app.event.zalo.me":"7093867920015212027","_gat":"1","zpsid":"H4RE.425362398.1.HzhGWNrH81kZqde2SL4W6mWYKYzFP1CjJs8P8mpe3LjEltY6VAGjCXfH81i","zpw_sek":"nq0p.425362398.a0.HiX5BhLPw0zhsh8Mb5de3yvxZMINOye-WpRVNTO0gMM0AOPvnIk0JjGMXKBIPDKjo2XH8lLg1bSeM1y2d3xe3m"})
honhattruong = Honhattruong('api_key', 'secret_key', imei=imei, session_cookies=session_cookies)
honhattruong.listen()
