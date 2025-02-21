import time
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import asdict
import json

from models import User, Note, init_db
from parser import XHSParser
from notifier import Notifier  # 你需要实现这个通知模块

class XHSMonitor:
    def __init__(self, xhs_client, user_ids: List[str]):
        self.client = xhs_client
        self.user_ids = user_ids
        self.db = init_db()
        self.notifier = Notifier()
    
    def check_user_changes(self, user_id: str, response_data: Dict[str, Any]) -> bool:
        user_info = XHSParser.parse_user_info(response_data)
        # 使用传入的 user_id 覆盖
        user_info.user_id = user_id
        
        user = self.db.query(User).filter_by(user_id=user_id).first()
        if not user:
            print(f"数据库中未找到用户: {user_id}")  # debug
            return True
            
        print(f"数据库中的user_id: {user.user_id}")  # debug
            
        # 规范化比较
        def normalize_value(v):
            if isinstance(v, (int, float)):
                return str(v)
            return str(v).strip() if v else ''
            
        fields_to_compare = ['nickname', 'avatar', 'description', 'follows', 'fans', 'likes']
        user_dict = asdict(user_info)
        
        for field in fields_to_compare:
            old_val = normalize_value(getattr(user, field))
            new_val = normalize_value(user_dict[field])
            if old_val != new_val:
                print(f"字段 {field} 发生变化: {old_val} -> {new_val}")  # debug用
                return True
                
        return False

    def check_notes_changes(self, user_id: str, new_notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        existing_notes = self.db.query(Note).filter_by(user_id=user_id).all()
        existing_note_ids = {note.note_id for note in existing_notes}
        new_note_ids = {note['note_id'] for note in new_notes}
        
        added_notes = new_note_ids - existing_note_ids
        removed_notes = existing_note_ids - new_note_ids
        
        changes = []
        if added_notes:
            changes.append({"type": "added", "notes": added_notes})
        if removed_notes:
            changes.append({"type": "removed", "notes": removed_notes})
        return changes

    def update_user(self, response_data: Dict[str, Any], user_id: str):
        user_info = XHSParser.parse_user_info(response_data)
        user_info.user_id = user_id
        user_dict = asdict(user_info)
        user_dict['raw_info'] = response_data
        
        user = self.db.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = User(**user_dict)
            self.db.add(user)
        else:
            for key, value in user_dict.items():
                setattr(user, key, value)
        self.db.commit()

    def update_notes(self, notes: List[Dict[str, Any]]):
        for note_info in notes:
            try:
                # 转换数据格式
                note_data = {
                    'note_id': note_info['note_id'],
                    'user_id': note_info['user']['user_id'],
                    'title': note_info['title'],
                    'type': note_info['type'],
                    'likes': note_info['likes'],
                    'user_nickname': note_info['user']['nickname'],
                    'user_avatar': note_info['user']['avatar'],
                    'cover_url': note_info['cover']['url'],
                    'cover_width': note_info['cover']['width'],
                    'cover_height': note_info['cover']['height'],
                    'raw_info': note_info
                }
                
                note = self.db.query(Note).filter_by(note_id=note_data['note_id']).first()
                if not note:
                    note = Note(**note_data)
                    self.db.add(note)
                else:
                    for key, value in note_data.items():
                        setattr(note, key, value)
            except Exception as e:
                print(f"处理笔记数据时出错: {e}, 笔记数据: {note_info}")
                continue
            
        self.db.commit()

    def monitor(self, interval: int = 300):
        while True:
            for user_id in self.user_ids:
                try:
                    print(f"开始检查用户: {user_id}")
                    
                    # 获取用户信息
                    user_info_response = self.client.get_user_info(user_id)
                    user_info = XHSParser.parse_user_info(user_info_response)  # 解析用户信息
                    
                    if self.check_user_changes(user_id, user_info_response):
                        self.update_user(user_info_response, user_id)
                        self.notifier.notify_user_change(asdict(user_info))

                    # 获取用户笔记前先休眠一下，避免请求太快
                    time.sleep(2)
                    
                    # 获取用户笔记
                    try:
                        notes_data = self.client.get_user_notes(user_id)
                        print(f"笔记API返回数据: {json.dumps(notes_data, ensure_ascii=False, indent=2)}")
                        
                        if notes_data and isinstance(notes_data, dict) and 'notes' in notes_data:
                            notes = XHSParser.parse_notes(notes_data)  # 直接传入 notes_data
                            notes_dict = [asdict(note) for note in notes]
                            
                            changes = self.check_notes_changes(user_id, notes_dict)
                            if changes:
                                self.update_notes(notes_dict)
                                self.notifier.notify_notes_change(user_id, changes)
                        else:
                            print(f"笔记数据格式异常: {notes_data}")
                    except Exception as note_error:
                        print(f"获取笔记失败: {note_error}")
                        import traceback
                        print(f"错误堆栈: {traceback.format_exc()}")

                except Exception as e:
                    print(f"监控用户 {user_id} 时发生错误: {e}")
                    import traceback
                    print(f"错误详情: {traceback.format_exc()}")

                # 每个用户检查完后休眠
                time.sleep(5)
            
            # 所有用户检查完后休眠
            print(f"完成一轮检查，休眠 {interval} 秒")
            time.sleep(interval) 