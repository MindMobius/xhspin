import logging

class Notifier:
    def __init__(self):
        logging.basicConfig(
            filename='changes.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            encoding='utf-8'
        )
        
    def notify_user_change(self, user_info):
        msg = f"用户信息变化: {user_info['nickname']}"
        logging.info(msg)
        print(msg)

    def notify_notes_change(self, user_id, changes):
        for change in changes:
            msg = f"用户 {user_id} 的笔记变化: {change['type']}, 笔记: {change['notes']}"
            logging.info(msg)
            print(msg) 