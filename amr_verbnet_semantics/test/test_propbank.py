
from xml.etree import ElementTree

from nltk.corpus import propbank

"""
pb_instances = propbank.instances()
inst = pb_instances[103]
print(inst.fileid, inst.sentnum, inst.wordnum)
print(inst.tagger)
print(inst.inflection)
print(inst.roleset)
print(inst.predicate)
print(inst.arguments)
print("rolesets:", propbank.roleset("enter.01"))
"""

enter_01 = propbank.roleset("enter.01")
for role in enter_01.findall("roles/role"):
    vn_role = role.find('vnrole')
    print("vncls:", vn_role.attrib["vncls"])
    print("vntheta:", vn_role.attrib["vntheta"])
    print(ElementTree.tostring(vn_role).decode('utf8').strip())
    print(role.attrib['n'], role.attrib['descr'])

print("====================")
print(ElementTree.tostring(enter_01).decode('utf8').strip())
# print(ElementTree.tostring(enter_01.find('roles')).decode('utf8').strip())

