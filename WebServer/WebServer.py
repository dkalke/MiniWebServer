
import socket
import os
import time

HOST = '127.0.0.1'
PORT = 59487

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)

def GetTokens(msg):
  return msg.split('\r\n')

def GetMethod(tokens):
  if len(tokens) > 0:    
    if len(tokens[0].split()) > 0:
      return tokens[0].split()[0]
    else:
      raise ERROR_400("無法取得請求方法! 請吃400")
  else:
    raise ERROR_400("無法取得請求方法! 請吃400")

def GetPath(tokens):
  if len(tokens[0]) > 1:
    return tokens[0].split()[1][1:]
  else:
    raise ERROR_400("無法取得請求路徑! 請吃400")

def GetVersion(tokens):
  if len(tokens[0]) > 2:
    if tokens[0].split()[2] == 'HTTP/1.1':
      return True
    else:
      raise ERROR_505("版本錯誤，請吃505!")
  else:
    raise ERROR_400("無法取得版本! 請吃400")

def LoginCheck(tokens):
  auth = ''
  for i in tokens:
    if i.find('Cookie') == 0:
      auth = i[8:]
      if auth.find('auth') == 0:
        auth = auth[6:-1]
  return auth


class ERROR_400(Exception):
    def __init__(self,msg):
        self.message=msg

class ERROR_404(Exception):
    def __init__(self,msg):
        self.message=msg

class ERROR_505(Exception):
    def __init__(self,msg):
        self.message=msg

while True:

    method = ''
    header = ''
    content = ''
    cookies = ''
    client, address = server.accept()
    clientMessage = str(client.recv(4096), encoding='utf-8')
    print(clientMessage)
    tokens = GetTokens(clientMessage)
    status = ''
    try:
      try:
        method = GetMethod(tokens)
        if method == 'GET':
          print(os.getcwd())
          path = GetPath(tokens) # 檢查檔案是否存在
          GetVersion(tokens) # 檢查版本，除了1.1其他都給我吃505
          if os.path.exists(path):
            # 設定那些頁面要重新導向，檢查cookies
            if path == 'index.html':
              auth = LoginCheck(tokens)
              if auth == 'X1kfBJZGXH0ZMn5':
                path = 'file_list.html'
              status = '200 OK'

            elif path == 'file_list.html':
              auth = ''
              auth = LoginCheck(tokens)
              if not auth == 'X1kfBJZGXH0ZMn5':
                path = 'index.html'
              status = '200 OK'
            elif path == '301-auto.html':
              status = '301 Moved Permanently'
            elif path == '301-manual.html':
              status = '301 Moved Permanently'
            else:
              status = '200 OK'

            # 載入資料
            with open(path, 'rb') as file:
              content = file.read()
          else:
            raise ERROR_404("找不到檔案路徑!")

        elif method == 'POST':
          path = GetPath(tokens) # 檢查檔案是否存在
          GetVersion(tokens) # 檢查版本，除了1.1其他都給我吃505
          if os.path.exists(path):
            if path == 'index.html':
              try:
                # 解析帳號密碼
                (user_name , user_password) = (tokens[-1].split('&'))
                user_name = user_name [9:]
                user_password = user_password [9:]
                status = '200 OK'
                if ( user_name == 'aaa' and user_password == 'bbb' ):
                  cookies = 'Set-Cookie: auth=\'X1kfBJZGXH0ZMn5\'; Max-Age=3600; Version=1'
                  with open('file_list.html', 'rb') as file:
                    content = file.read()
                else:
                  with open('index_post_fail.html', 'rb') as file:
                    content = file.read()
              except:
                raise ERROR_400("解析錯誤，請吃400!")
            else:
              raise ERROR_404("找不到檔案路徑!")
          else:
              raise ERROR_404("找不到檔案路徑!")
              
        elif method == 'HEAD':
          try:
            path = GetPath(tokens) # 檢查檔案是否存在
            GetVersion(tokens) # 檢查版本，除了1.1其他都給我吃505
            if os.path.exists(path):
              status = '200 OK'
            else:
              raise ERROR_404("找不到檔案路徑!")
          except:
            raise ERROR_400("解析錯誤，請吃400!")
          if path == 'index.html':
            pass
          else:
            raise ERROR_404("找不到檔案路徑!")

        elif method == 'PUT':
          try:
            # 取得路徑
            path = GetPath(tokens) # 檢查檔案是否存在
            # 取得資料
          
            with open(path, 'wb') as file:
              print(clientMessage[clientMessage.find('\r\n\r\n')+4:])
              file.write(clientMessage[clientMessage.find('\r\n\r\n')+4:].encode())

            status = '200 OK'
            content = '檔案新增完成\r\n'.encode()
          except Exception as e:
            print(e)
            raise ERROR_400("解析錯誤，請吃400!")

        elif method == 'DELETE':
          try:
            path = GetPath(tokens)  # 取得路徑
            if os.path.exists(path): # 檢查檔案是否存在
              # 刪檔案
              os.remove(path)

            status = '200 OK'
            content = '檔案刪除完成\r\n'.encode()
          except OSError as e:
            print(e)
          except:
            raise ERROR_400("解析錯誤，請吃400!")
        else:
          raise ERROR_400("看不懂方法! 請吃400")

      except ERROR_400 as error:
        status = '400 Bad Request'
        print(error)
        with open('400.html', 'rb') as file:
          content = file.read()
        raise error
      except ERROR_404 as error:
        status = '404 Not Found'
        with open('404.html', 'rb') as file:
          content = file.read()
        print(error)
        raise error
      except ERROR_505 as error:
        status = '505 HTTP Version Not Supported'
        with open('505.html', 'rb') as file:
          content = file.read()
        print(error)
        raise error

      header = 'HTTP/1.1 ' + status + '\r\n'
      header += 'Server: longmoServer/0.0.1\r\n'
      header += 'Date: ' + time.ctime() + '\r\n'
    

      # header 額外資訊、型態

      # 設定cookies
      if not cookies == '': 
        header += cookies + '\r\n'
  
      
      if path == '301-auto.html':
        header += 'Content-Type: text/html\r\n'
        header += 'Location: index.html\r\n'
      elif path == '301-manual.html':
        header += 'Content-Type: text/html\r\n'
        status = '301 Moved Permanently'
      elif path == '400.html':
        header += 'Content-Type: text/html\r\n'
        status = '400 Bad Request'
      elif path == '404.html':
        header += 'Content-Type: text/html\r\n'
        status = '404 Not Found'
      elif path == '505.html':
        #header += 'Content-Type: text/html\r\n'
        status = '505 HTTP Version Not Supported'
      elif path == 'horo.png':
        header += 'Content-Type: image/png\r\n'
    except (ERROR_400, ERROR_404, ERROR_505) as error:
      header = 'HTTP/1.1 ' + status + '\r\n'
      header += 'Server: longmoServer/0.0.1\r\n'
      header += 'Date: ' + time.ctime() + '\r\n'
      header += 'Content-Type: text/html\r\n'

    
    if method == 'GET' or method == 'POST':
      text_content = header.encode() + '\r\n'.encode() + content
    elif method == 'HEAD':
      text_content = header.encode() + '\r\n'.encode()
    elif method == 'PUT':
      text_content = header.encode() + '\r\n'.encode() + content
    elif method == 'DELETE':
      text_content = header.encode() + '\r\n'.encode() + content
    
    client.sendall(text_content)
    client.close()
