with open('bot.py', 'rb') as f:
    data = f.read()
data = data.decode('latin-1').encode('utf-8')
with open('bot.py', 'wb') as f:
    f.write(data)
print('Done! Now run: py bot.py')