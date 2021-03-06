# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ace.proto

import sys

_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import ACEDoc_pb2 as ACEDoc__pb2

DESCRIPTOR = _descriptor.FileDescriptor(
  name='ace.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\tace.proto\x1a\x0c\x41\x43\x45\x44oc.proto\".\n\x0e\x61\x63\x65\x64oc_request\x12\x0c\n\x04text\x18\x01 \x01(\t\x12\x0e\n\x06\x64oc_id\x18\x02 \x01(\t\"\x19\n\nacedoc_xml\x12\x0b\n\x03xml\x18\x01 \x01(\t2\xb5\x01\n\x03\x61\x63\x65\x12(\n\x0cprocess_text\x12\x0f.acedoc_request\x1a\x07.acedoc\x12\x1f\n\x0bprocess_doc\x12\x07.acedoc\x1a\x07.acedoc\x12#\n\x0bprocess_xml\x12\x0b.acedoc_xml\x1a\x07.acedoc\x12\x1e\n\x06to_xml\x12\x07.acedoc\x1a\x0b.acedoc_xml\x12\x1e\n\x06to_doc\x12\x0b.acedoc_xml\x1a\x07.acedocb\x06proto3')
  ,
  dependencies=[ACEDoc__pb2.DESCRIPTOR,])




_ACEDOC_REQUEST = _descriptor.Descriptor(
  name='acedoc_request',
  full_name='acedoc_request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='text', full_name='acedoc_request.text', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_id', full_name='acedoc_request.doc_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=27,
  serialized_end=73,
)


_ACEDOC_XML = _descriptor.Descriptor(
  name='acedoc_xml',
  full_name='acedoc_xml',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='xml', full_name='acedoc_xml.xml', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=75,
  serialized_end=100,
)

DESCRIPTOR.message_types_by_name['acedoc_request'] = _ACEDOC_REQUEST
DESCRIPTOR.message_types_by_name['acedoc_xml'] = _ACEDOC_XML
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

acedoc_request = _reflection.GeneratedProtocolMessageType('acedoc_request', (_message.Message,), {
  'DESCRIPTOR' : _ACEDOC_REQUEST,
  '__module__' : 'ace_pb2'
  # @@protoc_insertion_point(class_scope:acedoc_request)
  })
_sym_db.RegisterMessage(acedoc_request)

acedoc_xml = _reflection.GeneratedProtocolMessageType('acedoc_xml', (_message.Message,), {
  'DESCRIPTOR' : _ACEDOC_XML,
  '__module__' : 'ace_pb2'
  # @@protoc_insertion_point(class_scope:acedoc_xml)
  })
_sym_db.RegisterMessage(acedoc_xml)



_ACE = _descriptor.ServiceDescriptor(
  name='ace',
  full_name='ace',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=103,
  serialized_end=284,
  methods=[
  _descriptor.MethodDescriptor(
    name='process_text',
    full_name='ace.process_text',
    index=0,
    containing_service=None,
    input_type=_ACEDOC_REQUEST,
    output_type=ACEDoc__pb2._ACEDOC,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='process_doc',
    full_name='ace.process_doc',
    index=1,
    containing_service=None,
    input_type=ACEDoc__pb2._ACEDOC,
    output_type=ACEDoc__pb2._ACEDOC,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='process_xml',
    full_name='ace.process_xml',
    index=2,
    containing_service=None,
    input_type=_ACEDOC_XML,
    output_type=ACEDoc__pb2._ACEDOC,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='to_xml',
    full_name='ace.to_xml',
    index=3,
    containing_service=None,
    input_type=ACEDoc__pb2._ACEDOC,
    output_type=_ACEDOC_XML,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='to_doc',
    full_name='ace.to_doc',
    index=4,
    containing_service=None,
    input_type=_ACEDOC_XML,
    output_type=ACEDoc__pb2._ACEDOC,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_ACE)

DESCRIPTOR.services_by_name['ace'] = _ACE

# @@protoc_insertion_point(module_scope)