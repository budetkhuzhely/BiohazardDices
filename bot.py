import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)

print("=== СТАРТ БОТА ===", flush=True)
sys.stdout.flush()

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import random
import re

# ========== ТОКЕН И ID ВСТАВЛЕНЫ ПРЯМО В КОД ==========
TOKEN = "vk1.a.BQNUXyUGWegQC6-uB1wbfClkvEagySal9MypPT5cCQg3EkhTrGw_tnzJZFw7HVzjWmp1Pgv7BpqAiHrpQhhZy5jH-lyq51RG5QzRwIYM0249vDf0Lc6rTJ9QlikstPlwPCD8beOLo3npnjuGx3hoPif0nwupTDAoej7UhKUGVUATtwg_iZ5V6DKL29Ur4uTJEgIa5rXV-MS0NxSNfSz7KQ"
GROUP_ID = 237191512

print(f"1. TOKEN вставлен: {'ДА' if TOKEN else 'НЕТ'}")
print(f"2. GROUP_ID = {GROUP_ID}")

def parse_and_roll(command):
    command = command.lower().strip()
    
    if command.startswith('('):
        command = command[1:]
    
    patterns = [
        (r'^(дпре|дпом)(\d+)([+-]\d+)$', 'advantage_mod'),
        (r'^(дпре|дпом)([+-]\d+)$', 'advantage_mod_simple'),
        (r'^(дпре|дпом)(\d+)$', 'advantage'),
        (r'^(дпре|дпом)$', 'advantage_simple'),
        (r'^(\d*)д(\d+)([+-]\d+)$', 'dice_mod'),
        (r'^д(\d+)([+-]\d+)$', 'single_dice_mod'),
        (r'^(\d+)д([+-]\d+)$', 'd20_mod'),
        (r'^д([+-]\d+)$', 'single_d20_mod'),
        (r'^(\d*)д(\d+)$', 'dice'),
        (r'^д(\d+)$', 'single_dice'),
        (r'^(\d+)д$', 'd20_multi'),
        (r'^д$', 'd20_single'),
    ]
    
    for pattern, action in patterns:
        match = re.match(pattern, command)
        if match:
            return handle_match(match, action)
    
    return None, None

def handle_match(match, action):
    if action == 'dice':
        num = match.group(1)
        sides = int(match.group(2))
        if num == "":
            num = 1
        else:
            num = int(num)
        
        if num > 100:
            return None, "❌ Слишком много кубов (максимум 100)"
        if sides > 1000:
            return None, "❌ Слишком много граней (максимум 1000)"
        
        results = [random.randint(1, sides) for _ in range(num)]
        total = sum(results)
        
        if num == 1:
            return total, f"🎲 {total} [{results[0]}]"
        else:
            return total, f"🎲 {total} [{', '.join(map(str, results))}]"
    
    if action == 'single_dice':
        sides = int(match.group(1))
        if sides > 1000:
            return None, "❌ Слишком много граней (максимум 1000)"
        result = random.randint(1, sides)
        return result, f"🎲 {result}"
    
    if action == 'd20_multi':
        num = int(match.group(1))
        if num > 100:
            return None, "❌ Слишком много кубов (максимум 100)"
        results = [random.randint(1, 20) for _ in range(num)]
        total = sum(results)
        if num == 1:
            return total, f"🎲 {total} [{results[0]}]"
        else:
            return total, f"🎲 {total} [{', '.join(map(str, results))}]"
    
    if action == 'd20_single':
        result = random.randint(1, 20)
        return result, f"🎲 {result}"
    
    if action == 'dice_mod':
        num = match.group(1)
        sides = int(match.group(2))
        mod = int(match.group(3))
        if num == "":
            num = 1
        else:
            num = int(num)
        
        if num > 100:
            return None, "❌ Слишком много кубов (максимум 100)"
        if sides > 1000:
            return None, "❌ Слишком много граней (максимум 1000)"
        
        results = [random.randint(1, sides) for _ in range(num)]
        total = sum(results) + mod
        sign = "+" if mod > 0 else ""
        
        if num == 1:
            return total, f"🎲 {total} [{results[0]} {sign}{mod}]"
        else:
            return total, f"🎲 {total} [{', '.join(map(str, results))} {sign}{mod}]"
    
    if action == 'single_dice_mod':
        sides = int(match.group(1))
        mod = int(match.group(2))
        if sides > 1000:
            return None, "❌ Слишком много граней (максимум 1000)"
        result = random.randint(1, sides)
        total = result + mod
        sign = "+" if mod > 0 else ""
        return total, f"🎲 {total} [{result} {sign}{mod}]"
    
    if action == 'd20_mod':
        num = int(match.group(1))
        mod = int(match.group(2))
        if num > 100:
            return None, "❌ Слишком много кубов (максимум 100)"
        results = [random.randint(1, 20) for _ in range(num)]
        total = sum(results) + mod
        sign = "+" if mod > 0 else ""
        if num == 1:
            return total, f"🎲 {total} [{results[0]} {sign}{mod}]"
        else:
            return total, f"🎲 {total} [{', '.join(map(str, results))} {sign}{mod}]"
    
    if action == 'single_d20_mod':
        mod = int(match.group(1))
        result = random.randint(1, 20)
        total = result + mod
        sign = "+" if mod > 0 else ""
        return total, f"🎲 {total} [{result} {sign}{mod}]"
    
    if action == 'advantage':
        adv_type = match.group(1)
        sides = int(match.group(2))
        if sides > 1000:
            return None, "❌ Слишком много граней (максимум 1000)"
        roll1 = random.randint(1, sides)
        roll2 = random.randint(1, sides)
        
        if adv_type == "дпре":
            best = max(roll1, roll2)
            return best, f"🎲 Преимущество: {best} [броски: {roll1}, {roll2}]"
        else:
            worst = min(roll1, roll2)
            return worst, f"🎲 Помеха: {worst} [броски: {roll1}, {roll2}]"
    
    if action == 'advantage_simple':
        adv_type = match.group(1)
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        
        if adv_type == "дпре":
            best = max(roll1, roll2)
            return best, f"🎲 Преимущество: {best} [броски: {roll1}, {roll2}]"
        else:
            worst = min(roll1, roll2)
            return worst, f"🎲 Помеха: {worst} [броски: {roll1}, {roll2}]"
    
    if action == 'advantage_mod':
        adv_type = match.group(1)
        sides = int(match.group(2))
        mod = int(match.group(3))
        if sides > 1000:
            return None, "❌ Слишком много граней (максимум 1000)"
        roll1 = random.randint(1, sides)
        roll2 = random.randint(1, sides)
        sign = "+" if mod > 0 else ""
        
        if adv_type == "дпре":
            best = max(roll1, roll2) + mod
            return best, f"🎲 Преимущество: {best} [броски: {roll1}, {roll2} {sign}{mod}]"
        else:
            worst = min(roll1, roll2) + mod
            return worst, f"🎲 Помеха: {worst} [броски: {roll1}, {roll2} {sign}{mod}]"
    
    if action == 'advantage_mod_simple':
        adv_type = match.group(1)
        mod = int(match.group(2))
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        sign = "+" if mod > 0 else ""
        
        if adv_type == "дпре":
            best = max(roll1, roll2) + mod
            return best, f"🎲 Преимущество: {best} [броски: {roll1}, {roll2} {sign}{mod}]"
        else:
            worst = min(roll1, roll2) + mod
            return worst, f"🎲 Помеха: {worst} [броски: {roll1}, {roll2} {sign}{mod}]"
    
    return None, None

def process_message(text):
    text = text.lower().strip()
    
    if not text.startswith('('):
        return None
    
    without_bracket = text[1:]
    
    if without_bracket.count('(') > 0:
        parts = []
        current = ""
        depth = 0
        for char in without_bracket:
            if char == '(':
                if depth == 0 and current:
                    parts.append(current)
                    current = ""
                depth += 1
                current += char
            elif char == ')':
                depth -= 1
                current += char
            else:
                current += char
        if current:
            parts.append(current)
        
        results = []
        total_sum = 0
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if part.startswith('(') and part.endswith(')'):
                cmd = part[1:-1]
            else:
                cmd = part
            
            if ' ' in cmd:
                cmd_part, label = cmd.split(' ', 1)
            else:
                cmd_part = cmd
                label = None
            
            roll_result, message = parse_and_roll(cmd_part)
            if message:
                if label:
                    message = f"{label}: {message}"
                results.append(message)
                if roll_result is not None:
                    total_sum += roll_result
            else:
                results.append(f"❌ Не понял: ({cmd_part})")
        
        if results:
            final = "\n".join(results)
            if len(results) > 1:
                final += f"\n\n📊 Сумма: {total_sum}"
            return final
        return None
    
    else:
        if without_bracket.startswith('(') and without_bracket.endswith(')'):
            cmd = without_bracket[1:-1]
        else:
            cmd = without_bracket
        
        if ' ' in cmd:
            cmd_part, label = cmd.split(' ', 1)
        else:
            cmd_part = cmd
            label = None
        
        roll_result, message = parse_and_roll(cmd_part)
        if message:
            if label:
                return f"{label}: {message}"
            return message
    
    return None

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    try:
        print("3. Подключаемся к VK API...")
        vk_session = vk_api.VkApi(token=TOKEN)
        print("4. VK API подключен. Запускаем LongPoll...")
        longpoll = VkBotLongPoll(vk_session, GROUP_ID)
        print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print(f"ID группы: {GROUP_ID}")

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    msg_text = event.object.message.get('text', '').lower().strip()
                    peer_id = event.object.message.get('peer_id')
                    
                    if not msg_text:
                        continue
                    
                    if msg_text == "(помощь" or msg_text == "(help":
                        help_text = """📚 Доступные команды (через скобки):

Обычные броски:
(д — d20
(3д — три d20
(д12 — d12
(3д6 — три d6

С модификаторами:
(д+2 — d20+2
(д-1 — d20-1

Преимущество/Помеха:
(дпре — преимущество на d20
(дпом — помеха на d20
(дпре8 — преимущество на d8

Подписи (через пробел):
(д-2 ловкость
(дпре сила

Пулл команд:
(д (д-2 (дпре

(помощь — это сообщение"""
                        vk_session.method("messages.send", {
                            "peer_id": peer_id,
                            "message": help_text,
                            "random_id": get_random_id()
                        })
                        continue
                    
                    answer = process_message(msg_text)
                    if answer:
                        vk_session.method("messages.send", {
                            "peer_id": peer_id,
                            "message": answer,
                            "random_id": get_random_id()
                        })
                except Exception as e:
                    print(f"Ошибка при обработке сообщения: {e}")
                    
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")