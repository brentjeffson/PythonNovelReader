def plog(title, msg=''):
    title = ''.join([f"[{i.upper()}]" for i in title])
    print(f'{title} {str(msg)}')