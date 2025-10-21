from http.server import BaseHTTPRequestHandler
import json
import hashlib

def handler(request, response):
    """Vercel Serverless Function 处理微信请求"""
    
    # 设置CORS头部
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response.status_code = 200
        for key, value in headers.items():
            response.headers[key] = value
        return
    
    # GET请求 - 微信验证
    if request.method == 'GET':
        signature = request.query.get('signature', [''])[0]
        timestamp = request.query.get('timestamp', [''])[0]
        nonce = request.query.get('nonce', [''])[0]
        echostr = request.query.get('echostr', [''])[0]
        
        # 验证签名
        token = 'your_custom_token_123'  # 与微信配置一致
        arr = [token, timestamp, nonce]
        arr.sort()
        combined = ''.join(arr)
        sha1 = hashlib.sha1(combined.encode('utf-8')).hexdigest()
        
        if sha1 == signature:
            response.status_code = 200
            response.body = echostr
        else:
            response.status_code = 403
            response.body = '验证失败'
    
    # POST请求 - 处理消息
    elif request.method == 'POST':
        try:
            # 这里简化处理，实际需要解析XML
            response.status_code = 200
            response.headers['Content-Type'] = 'application/xml'
            response.body = '''<xml>
<ToUserName><![CDATA[用户OpenID]]></ToUserName>
<FromUserName><![CDATA[公众号ID]]></FromUserName>
<CreateTime>12345678</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[服务器运行正常！]]></Content>
</xml>'''
        except Exception as e:
            response.status_code = 500
            response.body = f'服务器错误: {str(e)}'
    
    else:
        response.status_code = 405
        response.body = 'Method Not Allowed'
    
    # 设置响应头
    for key, value in headers.items():
        response.headers[key] = value