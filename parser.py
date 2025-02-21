from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class NoteImage:
    url: str
    width: int
    height: int
    scene: str

@dataclass
class NoteUser:
    user_id: str
    nickname: str
    avatar: str

@dataclass
class Note:
    note_id: str
    title: str
    type: str
    likes: int
    user: NoteUser
    cover: NoteImage
    created_at: Optional[datetime] = None

@dataclass
class UserInfo:
    user_id: str
    nickname: str
    avatar: str
    description: str
    follows: int
    fans: int
    likes: int

class XHSParser:
    @staticmethod
    def parse_image(cover_data: dict) -> NoteImage:
        info = cover_data['info_list'][0]
        return NoteImage(
            url=info['url'],
            width=cover_data['width'],
            height=cover_data['height'],
            scene=info['image_scene']
        )

    @staticmethod
    def parse_user(user_data: dict) -> NoteUser:
        return NoteUser(
            user_id=user_data['user_id'],
            nickname=user_data['nickname'],
            avatar=user_data['avatar']
        )

    @staticmethod
    def parse_notes(response_data: dict) -> List[Note]:
        notes = []
        for note_data in response_data['notes']:
            note = Note(
                note_id=note_data['note_id'],
                title=note_data['display_title'],
                type=note_data['type'],
                likes=int(note_data['interact_info']['liked_count']),
                user=XHSParser.parse_user(note_data['user']),
                cover=XHSParser.parse_image(note_data['cover'])
            )
            notes.append(note)
        return notes

    @staticmethod
    def parse_notes_simple(response_data: dict) -> tuple[str, str, List[tuple[int, str, str]]]:
        """返回: (昵称, 用户ID, [(序号, note_id, 标题), ...])"""
        if not response_data['notes']:  # 处理空笔记情况
            return "未知用户", "unknown", []
            
        user = response_data['notes'][0]['user']  # 从第一条笔记获取用户信息
        notes = [
            (idx + 1, note['note_id'], note['display_title'])
            for idx, note in enumerate(response_data['notes'])
        ]
        return user['nickname'], user['user_id'], notes

    @staticmethod
    def parse_user_info(response_data: dict) -> UserInfo:
        if 'data' not in response_data:
            data = response_data
        else:
            data = response_data['data']
        
        basic_info = data['basic_info']
        interactions = {i['type']: int(i['count']) for i in data['interactions']}
        
        return UserInfo(
            user_id=basic_info.get('user_id', ''),  # 优先使用 user_id
            nickname=basic_info['nickname'],
            avatar=basic_info['images'],
            description=basic_info['desc'],
            follows=interactions.get('follows', 0),
            fans=interactions.get('fans', 0),
            likes=interactions.get('interaction', 0)
        )

# 使用示例:
"""
response = xhs_client.get_user_notes(user_id)
notes = XHSParser.parse_notes(response['data'])
for note in notes:
    print(f"标题: {note.title}")
    print(f"作者: {note.user.nickname}")
    print(f"点赞数: {note.likes}")
    print(f"封面图: {note.cover.url}")
    print("---")

for idx, note_id, title in XHSParser.parse_notes_simple(response['data']):
    print(f"{idx}. {note_id} - {title}")
""" 