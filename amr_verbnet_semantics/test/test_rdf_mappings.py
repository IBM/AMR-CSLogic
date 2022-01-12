
import requests

url_query = "http://goedel.sl.cloud9.ibm.com:9999/blazegraph/namespace/VerbnetAndGroupings/#query"

# To query verbs in Propbank WITHOUT counterparts in Verbnet
query_str_1 = """
prefix rrp:<http://www.ibm.com/RRP#>
prefix glo:<http://www.ibm.com/GLO_V2#>
prefix ulvn: <http://www.ibm.com/UL_VN#>
SELECT DISTINCT ?PropbankMapID  WHERE {
  ?mappingGroup a rrp:MappingGroup .
  ?mappingGroup rrp:hasComponent ?mapping .
  #Verbnet _1
  FILTER NOT EXISTS {
  	?mapping rrp:mapsTo ?vnsense .
  	ulvn:VerbNet rrp:hasComponent ?vnsense.
  	?vnsense rrp:identifier ?VerbnetMapID .
  }
  #PropBank
  ?mapping rrp:mapsTo ?pbsense .
  ulvn:PropBank rrp:hasComponent ?pbsense.
  ?pbsense rrp:identifier ?PropbankMapID .
  ?mappingGroup rdfs:label ?mappingGroupName .
  } ORDER BY ?target
"""

# To query examples of Propbank with at least two Verbnets
query_str_2 = """
prefix rrp:<http://www.ibm.com/RRP#>
prefix glo:<http://www.ibm.com/GLO_V2#>
prefix ulvn: <http://www.ibm.com/UL_VN#>
SELECT DISTINCT ?mappingGroupName ?PropbankMapID ?VerbnetMapID_1 ?VerbnetMapID_2 WHERE {
  ?mappingGroup a rrp:MappingGroup .
  ?mappingGroup rrp:hasComponent ?mapping .
  #Verbnet _1
  ?mapping rrp:mapsTo ?vnsense .
  ulvn:VerbNet rrp:hasComponent ?vnsense.
  ?vnsense rrp:identifier ?VerbnetMapID_1 .
  #Verbnet _1
  ?mapping rrp:mapsTo ?vnsense_2 .
  ulvn:VerbNet rrp:hasComponent ?vnsense_2.
  ?vnsense_2 rrp:identifier ?VerbnetMapID_2 .
  #PropBank
  ?mapping rrp:mapsTo ?pbsense .
  ulvn:PropBank rrp:hasComponent ?pbsense.
  ?pbsense rrp:identifier ?PropbankMapID .
  FILTER(?vnsense != ?vnsense_2)
  ?mappingGroup rdfs:label ?mappingGroupName .
  } ORDER BY ?target
"""

# To query all PropBank and VerbNet mappings
query_mapping_str = """
prefix rrp:<http://www.ibm.com/RRP#>
prefix glo:<http://www.ibm.com/GLO_V2#>
prefix ulvn: <http://www.ibm.com/UL_VN#>
SELECT DISTINCT ?mappingGroupName ?PropbankMapID ?VerbnetMapID WHERE {
  ?mappingGroup a rrp:MappingGroup .
  ?mappingGroup rrp:hasComponent ?mapping .
  
  #Verbnet _1
  ?mapping rrp:mapsTo ?vnsense .
  ulvn:VerbNet rrp:hasComponent ?vnsense.
  ?vnsense rrp:identifier ?VerbnetMapID .

  #PropBank
  ?mapping rrp:mapsTo ?pbsense .
  ulvn:PropBank rrp:hasComponent ?pbsense.
  ?pbsense rrp:identifier ?PropbankMapID .

  ?mappingGroup rdfs:label ?mappingGroupName .
  } ORDER BY ?mappingGroupName
"""


def request_wrapper(url, query, result_type="json"):
    try:
        print("query:", query)
        return requests.get(url, params={'format': result_type, 'query': query})
    except requests.exceptions.Timeout:
        print("TIMEOUT while processing \n" + query)
        return
    except requests.exceptions.TooManyRedirects:
        print("WRONG URL while processing \n" + query)
        return
    except requests.exceptions.RequestException as e:
        print("CATASTROPHIC ERROR " + str(e) + " while processing \n" + query)
        return
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Unknown error " + str(e) + " while processing  \n" + query)
        return


if __name__ == '__main__':
    print(request_wrapper(url_query, query_str_1).json())
    input()
    print(request_wrapper(url_query, query_str_2).json())

