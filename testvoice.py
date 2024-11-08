from hikerapi import Client
import json
import time
cl = Client(token="m3cv7VvTr7vMUphO9JQmLJjsqQyc10DH")
data = {}
max_id = None
total = 0
while True:
    # 每一次请求的时候都读取一下文件中的max_id
    with open('max_id.txt', 'r') as f:
        max_id = f.read()
    if max_id == None or max_id == '':
        result = cl.hashtag_medias_top_chunk_v1('xlim')
        # 第一次写入
        with open('max_id.txt', 'w') as f:
            f.write(result[1])
    else:
        try:
            result = cl.hashtag_medias_top_chunk_v1('xlim', max_id=max_id)
            for item in result[0]:
                tempdata = {
                    'post_id':item['id'],
                    'post_code':item['code'],
                    'post_thumbnail_url':item['thumbnail_url'], 
                    'post_user':item['user']['username'],
                    'post_caption':item['caption_text']
                    }
                data[item['id']] = tempdata
            print(len(data))
            print(total)
            max_id = result[1]
            print(max_id)
            # 第二次写入
            with open('max_id.txt', 'w') as f:
                f.write(max_id)
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            # 监控到异常，暂停5秒接着开始
            time.sleep(5)
            print("碰到异常了休眠5秒再开始")