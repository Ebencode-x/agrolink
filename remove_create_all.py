content = open('app.py', encoding='utf-8').read()
content = content.replace('with app.app_context():\n    db.create_all()\n', '')
open('app.py', 'w', encoding='utf-8').write(content)
print('DONE!')
