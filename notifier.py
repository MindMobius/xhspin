import logging
from models import User, init_db

class Notifier:
    def __init__(self):
        logging.basicConfig(
            filename='changes.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            encoding='utf-8'
        )
        self.db = init_db()
        
    def notify_user_change(self, user_info, changes):
        changes_str = ", ".join([f"{field}: {old} -> {new}" for field, (old, new) in changes.items()])
        msg = f"用户信息变化: {user_info['nickname']}, 变化: {changes_str}"
        logging.info(msg)
        print(msg)

    def notify_notes_change(self, user_id, changes):
        # 从数据库获取用户昵称
        user = self.db.query(User).filter_by(user_id=user_id).first()
        nickname = user.nickname if user else user_id
        
        for change in changes:
            notes_str = ", ".join([f"{note['title']}" for note in change['notes']])
            msg = f"用户 {nickname} 的笔记{change['type']}: {notes_str}"
            logging.info(msg)
            print(msg) 