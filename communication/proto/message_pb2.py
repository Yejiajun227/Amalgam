# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: message.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rmessage.proto\"X\n\x0bRequestBody\x12\x0b\n\x03src\x18\x01 \x01(\t\x12\x0b\n\x03\x64st\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\x05\x12\x0b\n\x03key\x18\x04 \x01(\t\x12\x14\n\x0cpython_bytes\x18\x06 \x01(\x0c\"\x1a\n\x08Response\x12\x0e\n\x06status\x18\x01 \x01(\t2Z\n\rServerService\x12\"\n\x05SayHi\x12\x0c.RequestBody\x1a\t.Response\"\x00\x12%\n\x08PushData\x12\x0c.RequestBody\x1a\t.Response\"\x00\x62\x06proto3')



_REQUESTBODY = DESCRIPTOR.message_types_by_name['RequestBody']
_RESPONSE = DESCRIPTOR.message_types_by_name['Response']
RequestBody = _reflection.GeneratedProtocolMessageType('RequestBody', (_message.Message,), {
  'DESCRIPTOR' : _REQUESTBODY,
  '__module__' : 'message_pb2'
  # @@protoc_insertion_point(class_scope:RequestBody)
  })
_sym_db.RegisterMessage(RequestBody)

Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), {
  'DESCRIPTOR' : _RESPONSE,
  '__module__' : 'message_pb2'
  # @@protoc_insertion_point(class_scope:Response)
  })
_sym_db.RegisterMessage(Response)

_SERVERSERVICE = DESCRIPTOR.services_by_name['ServerService']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REQUESTBODY._serialized_start=17
  _REQUESTBODY._serialized_end=105
  _RESPONSE._serialized_start=107
  _RESPONSE._serialized_end=133
  _SERVERSERVICE._serialized_start=135
  _SERVERSERVICE._serialized_end=225
# @@protoc_insertion_point(module_scope)
