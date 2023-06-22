import codecs
import json
import base64
import struct
import binascii
# public static Map<Integer, String> decode(String qrCodeBase64) {
#     Map<Integer, String> result = new HashMap<>();
#     byte[] bytes = decodeFromBase64(qrCodeBase64);
#     int currentPosition = 0;
#     while (currentPosition < bytes.length) {
#       int tagNumber = Byte.toUnsignedInt(bytes[currentPosition]);
#       log.debug("tagNumber: {}", Integer.valueOf(tagNumber));


#       currentPosition++;
#       int length = Byte.toUnsignedInt(bytes[currentPosition]);
#       log.debug("length: {}", Integer.valueOf(length));
#       currentPosition++;
#       int lastPosition = currentPosition + length;
#       byte[] messageBytes = Arrays.copyOfRange(bytes, currentPosition, lastPosition);
#       String message = new String(messageBytes, StandardCharsets.UTF_8);
#       log.debug("message: {}", message);
#       currentPosition += length;
#       result.put(Integer.valueOf(tagNumber), message);
#     } 
#     return result;
#   }




# package com.zatca.sdk.qrcode;

# import com.zatca.sdk.util.ECDSAUtil;
# import java.nio.charset.StandardCharsets;
# import java.util.List;
# import org.apache.logging.log4j.LogManager;
# import org.apache.logging.log4j.Logger;

# public class QrCodeEncoder {
#   private static final Logger log = LogManager.getLogger(QrCodeDecoder.class);
  
#   public static byte[] encode(String... parameters) throws Exception {
#     int length = getBufferLength(parameters[0], parameters[1], parameters[2], parameters[3], parameters[4], parameters[5], parameters[6], parameters[7]);
#     byte[] buffer = new byte[length];
#     int i = 0;
#     int j = 0;
#     while (i < length) {
#       buffer[i] = (byte)(j + 1);
#       int len = (parameters[j].getBytes()).length;
#       buffer[i + 1] = (byte)len;
#       System.arraycopy(parameters[j].getBytes(StandardCharsets.UTF_8), 0, buffer, i + 2, len);
#       i += 2 + len;
#       j++;
#     } 
#     return buffer;
#   }
  
#   public static byte[] encode(List<TLVMessage> msgs) throws Exception {
#     int length = getBufferLength(msgs);
#     log.info("buffer length: {}", Integer.valueOf(length));
#     byte[] buffer = new byte[length];
#     int i = 0;
#     int j = 0;
#     while (j < msgs.size()) {
#       if (((TLVMessage)msgs.get(j)).getTagName().equals("signature")) {
#         log.info("encoding the signature of length: {}", Integer.valueOf((((TLVMessage)msgs.get(j)).getValue().getBytes()).length));
#         byte[] r = ECDSAUtil.extractR(((TLVMessage)msgs.get(j)).getValue());
#         byte[] s = ECDSAUtil.extractS(((TLVMessage)msgs.get(j)).getValue());
#         buffer[i] = (byte)((TLVMessage)msgs.get(j)).getTag();
#         buffer[i + 1] = (byte)r.length;
#         log.info("inserting R with tag: {}", Integer.valueOf(((TLVMessage)msgs.get(j)).getTag()));
#         System.arraycopy(r, 0, buffer, i + 2, r.length);
#         i += 2 + r.length;
#         buffer[i] = (byte)(((TLVMessage)msgs.get(j)).getTag() + 1);
#         buffer[i + 1] = (byte)s.length;
#         log.info("inserting R with tag: {}", Integer.valueOf(((TLVMessage)msgs.get(j)).getTag() + 1));
#         System.arraycopy(s, 0, buffer, i + 2, s.length);
#         i += 2 + s.length;
#         j++;
#         continue;
#       } 
#       buffer[i] = (byte)((TLVMessage)msgs.get(j)).getTag();
#       int len = (((TLVMessage)msgs.get(j)).getValue().getBytes()).length;
#       buffer[i + 1] = (byte)len;
#       System.arraycopy(((TLVMessage)msgs.get(j)).getValue().getBytes(StandardCharsets.UTF_8), 0, buffer, i + 2, len);
#       i += 2 + len;
#       j++;
#     } 
#     return buffer;
#   }
  
#   private static int getBufferLength(String sellerName, String vatRegistrationNumber, String timeStamp, String invoiceTotal, String vatTotal, String hashedXml, String key, String signature) throws Exception {
#     int sellerNameLength = (sellerName.getBytes()).length;
#     int vatRegistrationNumberLength = (vatRegistrationNumber.getBytes()).length;
#     int timeStampLength = (timeStamp.getBytes()).length;
#     int invoiceTotalLength = (invoiceTotal.getBytes()).length;
#     int vatTotalLength = (vatTotal.getBytes()).length;
#     int hashedXmlLength = (hashedXml.getBytes()).length;
#     int keyLength = (key.getBytes()).length;
#     int rLength = (ECDSAUtil.extractR(signature)).length;
#     int sLength = (ECDSAUtil.extractS(signature)).length;
#     int totalLenth = sellerNameLength + vatRegistrationNumberLength + timeStampLength + invoiceTotalLength + vatTotalLength + hashedXmlLength + keyLength + rLength + sLength + 18;
#     return totalLenth;
#   }
  
#   private static int getBufferLength(List<TLVMessage> msgs) throws Exception {
#     int valuesLenth = ((Integer)msgs.stream().filter(msg -> !msg.getTagName().equals("signature")).map(msg -> Integer.valueOf((msg.getValue().getBytes()).length)).reduce(Integer.valueOf(0), Integer::sum)).intValue();
#     int totalLenth = valuesLenth + msgs.size() * 2 + 64 + 2;
#     return totalLenth;
#   }
# }


def toUnsignedInt (byte):
    # value = struct.unpack('B', bytes(str(byte).encode()))[0]
    value = byte
    # print ("value => " ,value)
    return value


base_64_str = """ATvYtNix2YPYqSDZhdix2YHZgiDZhNil2K/Yp9ix2Kkg2Ygg2KrYtNi62YrZhCDYp9mE2YXYsdin2YHZggIPMzEwMzQ1NTAyMzAwMDAzAxwyMDIxLTExLTMwVDE1OjQ3OjQxLjk5MzAwMDBaBAM3NTAFBDU3NTA="""



base_64_str = "AQxCb2JzIFJlY29yZHMCDzMxMDEyMjM5MzUwMDAwMwMUMjAyMi0wNC0yNVQxNTozMDowMFoEBzEwMDAuMDAFBjE1MC4wMA=="


data_bytes = base64.b64decode(base_64_str)
print ("data => " ,data_bytes)
# print ("data => " ,len(data_bytes))

currentPosition = 0
result=[]
while currentPosition < len(data_bytes):
    # print ("currentPosition => " , currentPosition)
    tagNumber  = toUnsignedInt(data_bytes[currentPosition])
    # print ("tagNumber => " , data_bytes[currentPosition])
    currentPosition += 1
    length = toUnsignedInt(data_bytes[currentPosition])
    print ("length => " , data_bytes[currentPosition])
    currentPosition += 1
    lastPosition  = currentPosition + length
    messageBytes = data_bytes[currentPosition:lastPosition]
    message = messageBytes.decode("utf-8")
    currentPosition+=length
    result.append({
        "tagNumber":tagNumber,
        "message":message
    })



for i in result :
    print ("******************** "+str(i["tagNumber"])+" *************************")
    # print ("tagNumber => " , i["tagNumber"])
    print ("message => " , i["message"])

# print ("result => " , result)




result_a = {"taxid" :1254997 , "payername" : u"شركة مرفق لإدارة و تشغيل المرافق" ,  
           "date" : "2021-11-20T15:47:41.999Z"  , "total" : 1500  , "tax":150 } 
lst_str = ""


payername_bytes = base64.b64encode( result_a.get("payername").encode("utf-8") )
payername_bytes_length = str(len(payername_bytes))
payername_bytes_tag = str(1)


payername_bytes_str = (payername_bytes_tag+payername_bytes_length+result_a.get("payername")).encode("utf-8")


# lst_str += str(base64.b64encode(
#     bytes(str(len(payername_bytes)),encoding="utf-8")
#     ))
# lst_str += str(len(payername_bytes))
# lst_str += str(payername_bytes)
# print ("payername_bytes => " , payername_bytes_str)
# print ("payername_bytes_length => " , payername_bytes_length)

# lst_str =  base64.b64encode(
# payername_bytes_str
# )
# print ("lst_str => " , lst_str)


# payername = "Bobs Records".encode("utf-8").hex()
# payername_len = hex(12).replace('x','')
# payername_tag = hex(1).replace('x','')


# bytes_str = "" #bytearray([1,12,"Bobs Records"],encoding="utf-8").hex()
# total_payername_str = payername_tag + payername_len+payername
# hexa_tag = total_payername_str.encode("utf-8") #binascii.hexlify()




# print ("bytes_str => " , bytes_str)
# print ("payername_tag => " , payername_tag)
# print ("payername_len => " , payername_len)
# print ("payername => " , payername)
# print ("total_payername_str => ",total_payername_str)
# print ("hexa_tag => " , hexa_tag)




data_dict = [
    {
        "tagNumber" : 1 ,
        "value" : "Bobs Records"
    },
    {
        "tagNumber" : 2 ,
        "value" : "310122393500003"
    },
    {
        "tagNumber" : 3 ,
        "value" : "2022-04-25T15:30:00Z"
    },
    {
        "tagNumber" : 4 ,
        "value" : "1000.00"
    },
    {
        "tagNumber" : 5 ,
        "value" : "150.00"
    },
]

total_hex = ""
count = 1
for row in data_dict :
    value = row["value"].encode("utf-8").hex()
    if len(row["value"]) > 15:
        value_len = hex(len(row["value"])).replace('0x','')
    else :
        value_len = hex(len(row["value"])).replace('x','')
    # value_len = hex(len(row["value"])).replace('0x','')
    tagNumber = hex(row['tagNumber']).replace('x','')
    # tagNumber = hex(count).replace('0x','')
    count +=1

    total_hex_str = str(tagNumber + value_len+value)

    hexa_tag = total_hex_str.encode("utf-8")
    total_hex += total_hex_str
    print ("**********************************************")
    print (row["value"])
    print ("value => " , value)
    print ("value_len => " , value_len)
    print ("tagNumber => " , tagNumber)
    print ("total_hex_str => ", total_hex_str)
    # print ("hexa_tag => ", hexa_tag)









# finalhex = """010c426f6273205265636f726473020F333130313232333933353030303033|0314|323032322d30342d32355431353a33303a30305a0407313030302e303005063135302e3030"""
finalhex = """010c426f6273205265636f726473020F3331303132323339333530303030330314323032322d30342d32355431353a33303a30305a0407313030302e303005063135302e3030"""



print ('*********  Final ***********************')

print ("total_hex => ", total_hex)

print ("total_hex equal => ", total_hex == finalhex)
print ("total_hex type equal => ", type(total_hex) == type(finalhex))

total_hex_bytes = bytes(finalhex,encoding="utf-8")
total_hex_64 = base64.b64encode(total_hex_bytes)



b64 = codecs.encode(codecs.decode(finalhex, 'hex'), 'base64').decode('utf-8')
b642 = codecs.encode(codecs.decode(total_hex, 'hex'), 'base64').decode('utf-8')



print ("total_hex_64 => ", total_hex_64)
print ("b64 => ", b64)
print ("b642 => ", b642)














# for i in  result :



# for key,value in result_a.items() :

