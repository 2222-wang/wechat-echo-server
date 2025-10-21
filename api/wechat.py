from http.server import BaseHTTPRequestHandler
import json
import hashlib
import time
import xml.etree.ElementTree as ET
import os
import urllib.parse

class WeChatHandler:
    def __init__(self):
        self.token = os.environ.get('WECHAT_TOKEN', 'your_default_token_123')
    
    def verify_signature(self, signature, timestamp, nonce):
        """验证微信签名"""
        try:
            arr = [self.token, timestamp, nonce]
            arr.sort()
            combined = ''.join(arr)
            
            sha1 = hashlib.sha1()
            sha1.update(combined.encode('utf-8'))
            calculated_signature = sha1.hexdigest()
            
            return calculated_signature == signature
        except Exception as e:
            print(f"签名验证错误: {e}")
            return False
    
    def parse_wechat_message(self, xml_data):
        """解析微信XML消息"""
        try:
            root = ET.fromstring(xml_data)
            message = {}
            
            for child in root:
                message[child.tag] = child.text
            
            return message
        except Exception as e:
            print(f"解析XML错误: {e}")
            return {}
    
    def generate_reply_xml(self, received_msg, content):
        """生成回复XML"""
        return f"""<xml>
<ToUserName><![CDATA[{received_msg.get('FromUserName', '')}]]></ToUserName>
<FromUserName><![CDATA[{received_msg.get('ToUserName', '')}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
    
    def handle_request(self, method, query_params, body):
        """处理请求"""
        # GET请求 - 验证接口
        if method == 'GET':
            signature = query_params.get('signature', [''])[0]
            timestamp = query_params.get('timestamp', [''])[0]
            nonce = query_params.get('nonce', [''])[0]
            echostr = query_params.get('echostr', [''])[0]
            
            if self.verify_signature(signature, timestamp, nonce):
                return {
                    'status': 200,
                    'headers': {'Content-Type': 'text/plain'},
                    'body': echostr
                }
            else:
                return {
                    'status': 403,
                    'headers': {'Content-Type': 'text/plain'},
                    'body': '验证失败'
                }
        
        # POST请求 - 处理消息
        elif method == 'POST':
            try:
                xml_data = body
                message = self.parse_wechat_message(xml_data)
                
                msg_type = message.get('MsgType', 'text')
                user_content = message.get('Content', '')
                
                # 原样返回用户消息
                if msg_type == 'text':
                    reply_content = f"您说: {user_content}"
                else:
                    reply_content = f"收到{msg_type}类型消息: {user_content or '无内容'}"
                
                reply_xml = self.generate_reply_xml(message, reply_content)
                
                return {
                    'status': 200,
                    'headers': {'Content-Type': 'application/xml'},
                    'body': reply_xml
                }
                
            except Exception as e:
                print(f"处理消息错误: {e}")
                return {
                    'status': 500,
                    'headers': {'Content-Type': 'text/plain'},
                    'body': '服务器错误'
                }
        
        else:
            return {
                'status': 405,
                'headers': {'Content-Type': 'text/plain'},
                'body': 'Method Not Allowed'
            }

# Vercel Serverless Function 入口
def main(request, response):
    handler = WeChatHandler()
    
    # 解析查询参数
    parsed_path = urllib.parse.urlparse(request.path)
    query_params = urllib.parse.parse_qs(parsed_path.query)
    
    # 获取请求体
    body = request.body.decode('utf-8') if request.body else ''
    
    # 处理请求
    result = handler.handle_request(request.method, query_params, body)
    
    # 设置响应
    response.status_code = result['status']
    for key, value in result['headers'].items():
        response.headers[key] = value
    response.body = result['body']