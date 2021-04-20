"""
@author: Arku Xu
@date: 2021-03-31 23:52:31
@Email: arku.xu@gmail.com
@brief: 加解密模块基类
"""
# _*_ coding: utf-8 _*_
import hashlib
import base64
from Crypto.Cipher import AES
from backend.config.configbase import ConfigBase
from backend.modules.logopr.logbase import Log

log = Log(__name__).config()

class CypherBase:
    """""
    加解密模块基类
    加密密钥限定在16位
    -------------
    encrypt_AES: AES加密
    decrypt_AES: AES 解密
    hash: 加哈希值
    """""
    __key = "the_default_key+".encode('utf-8')  # 默认密钥，不推荐使用
    __mod = AES.MODE_CBC    # 加密模式
    __hash = hashlib.sha256()  # 哈希
    __salt = "the_default_salt" # 哈希盐值

    def __init__(self, key=None, salt=None):
        """""
        初始化函数
        ------------
        @param: key     传入的密钥x，限长16，不够补齐
        @param: salt    哈希盐值
        @return: 
        """""
        # 检查key的合法性并设置key
        cur_key = self.__generate_key__(key)
        if cur_key == None:
            log.debug("Use the default key.")
        else:
            self.__key = cur_key 

        # 设置哈希盐值
        if type(salt) != str:
            log.debug("Use the default salt.")
        else:
            self.__salt = salt
    
    def __fill_AES__(self, text, fill=None):
        """""
        AES加密，字节补充到16的倍数长度
        ------------
        @param: text 文本
        @return: 成功返回文本bytes 失败返回None
        """""
        if type(text) != str:
            log.debug("Invalid text.")
            return None
        if type(fill) != str or len(fill) != 1:
            fill_char = '\0'
        else:
            fill_char = fill
        text = text.encode('utf-8')

        # 补充文本长度
        ext = len(text) % 16
        if ext:
            add = 16 - ext
        else:
            add = 0
        return text + (fill_char * add).encode('utf-8')
    
    def __generate_key__(self, key):
        """""
        生成密钥
        ------------
        @param: key 传入的密钥，限长16，不够补齐
        @return: 成功返回密钥，失败返回None
        """""
        # 检查key的合法性
        if key == None:
            return None
        elif type(key) != str:
            return None
        # key长度超过16截断，不够补齐
        elif len(key) > 16:
            log.debug("Key is longer than 16 words, use the first 16 words.")
            return key[:16].encode('utf-8')
        else:
            return self.__fill_AES__(key, 'b')
    
    def set_key(self, key=None):
        """""
        设置新的密钥
        ------------
        @param: key 传入的密钥，限长16，不够补齐
        @return: 
        """""
        cur_key = self.__generate_key__(key)
        if cur_key == None:
            log.debug("Invalid Key. Use the current one.")
        else:
            self.__key = cur_key
    
    def set_salt(self, salt=None):
        """""
        设置新哈希盐值
        ------------
        @param: 
        @return: 
        """""
        if type(salt) != str:
            log.debug("Invalid salt. Use the current one.")
            return
        self.__salt = salt

    def encrypt_AES(self, text, key=None):
        """""
        AES加密
        ------------
        @param: text:   明文
        @param: key:    传入的密钥x，限长16，不够补齐
        @return: 成功返回密文 失败返回None
        """""
        if type(text) != str:
            log.debug("Invalid text.")
            return None
        
        # 确定密钥
        cur_key = self.__generate_key__(key)
        if cur_key == None:
            cur_key = self.__key

        # 加密
        cyphor = AES.new(cur_key, self.__mod, cur_key)
        text = self.__fill_AES__(text)  # 返回bytes
        c_text = cyphor.encrypt(text)

        # 编码
        return base64.b64encode(c_text).decode('utf-8')

    def decrypt_AES(self, text, key=None): 
        """""
        AES 解密
        ------------
        @param: text:   密文
        @param: key:    传入的密钥x并更新，限长16，不够补齐
        @return: 成功返回明文 失败返回None
        """""
        if type(text) != str:
            log.debug("Invalid text.")
            return None

        # 确定密钥
        cur_key = self.__generate_key__(key)
        if cur_key == None:
            cur_key = self.__key
        
        # 解码
        text = base64.b64decode(text.encode('utf-8'))
        
        # 解密
        cyphor = AES.new(cur_key, self.__mod, cur_key)
        m_text = cyphor.decrypt(text)
        return bytes.decode(m_text).rstrip('\0')

    def hash(self, text, salt=None):
        """
        加哈希值
        ------------
        @param: 哈希加盐
        @return: 成功返回哈希值 失败返回None
        """
        if type(text) != str:
            log.debug("Invalid text.")
            return None
        
        # 确定盐值
        if salt == None or type(salt) != str:
            hash_salt = self.__salt
        else:
            hash_salt = salt
        text = text + hash_salt

        # 哈希
        hhash = hashlib.sha256()
        hhash.update(text.encode('utf-8'))
        return str(hhash.hexdigest())
        # self.__hash.update(text.encode('utf-8'))
        # return self.__hash.hexdigest()

if __name__ == "__main__":
    cyphor = CypherBase()
    # mtext = "thisismykey123456"
    mtext = "16"
    print("original text: {}\nlength: {}".format(mtext, len(mtext)))
    ctext = cyphor.encrypt_AES(mtext)
    print("encrypt text: {}\nlength: {}".format(ctext, len(ctext)))
    mtext = cyphor.decrypt_AES(ctext)
    print("decrypt text: {}\nlength: {}".format(mtext, len(mtext)))
    hash_mtext = cyphor.hash(mtext)
    print("hash text: {}\nlength: {}".format(hash_mtext, len(hash_mtext)))
    hash_ctext = cyphor.hash(ctext)
    print("hash the encypt text: {}\nlength: {}".format(hash_ctext, len(hash_ctext)))
