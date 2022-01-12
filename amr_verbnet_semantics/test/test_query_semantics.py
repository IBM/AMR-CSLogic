from amr_verbnet_semantics.service.verbnet import query_semantics

verbnet_version = 'verbnet3.4'

verbnet_id = 'escape-51.1'
semantics = query_semantics(verbnet_id, verbnet_version)
print(semantics)

verbnet_id = 'spray-9.7-2'
semantics = query_semantics(verbnet_id, verbnet_version)
print(semantics)

verbnet_id = 'build-26.1-1'
semantics = query_semantics(verbnet_id, verbnet_version)
print(semantics)

verbnet_id = 'stop-55.4-1-1'
semantics = query_semantics(verbnet_id, verbnet_version)
print(semantics)




