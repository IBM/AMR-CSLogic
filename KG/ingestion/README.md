This directory contains both code and input data for the generation of ULKB.

Code in ulkb_generate_unified_mapping.py generates the excel ULKB_UnifiedMapping_V1.xlsx directly from the input files. It carries out a phantom generation of the graph that, instead of writing to .ttl, it produces an excel that can be easily modified and changed. This allows us to correct the generation quickly. 

The file ULKB_UnifiedMapping_V1.xlsx contains the analysis of mappings of verbs and constraints from the version V4. Of particular interest is the red column in UM_RAW_V1, which indicates vocabulary in the mapping that doesn't exist in the target class. This means the mapping cannot lead to a successful grounding. 

Once this mapping is curated, the excel is used in the ingestion, instead of Semlink versions and Propbank. The code in ulkb_ingest_PB_VN.py does this. It takes the excel above, plus all the versions of Verbnet and Propbank to generate UL_KB_V5. 
